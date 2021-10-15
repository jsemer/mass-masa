import csv
import copy
from random import shuffle
from z3 import *
from difflib import SequenceMatcher 
from googlesearch import search
import random
#TODO IMPORTANT Dealiased last two columns in the csv source file
random.seed(873)
debug = False  
raw_data = list(csv.DictReader(open("input.csv")))

students = []
mentors = []

#we build lists of people that filled contradictory data, just in case we care about reaching out to them
# confused_students = []
confused_mentors = []
confused_not_interested = []

list_institutions = [] 

# To normalize the institutions we query google with the string provided by the
# users. To avoid requerying google across multiple run of the script we create a persistent local
# cache (Suggestion of J. Emer). The implementation is simply representing the cache as a python dictionary
# stored on disk as json, reopened every time the decorator is called to read or write.
# This minimalist implementation is directly copy/pasted from
# https://stackoverflow.com/questions/16463582/memoize-to-disk-python-persistent-memoization
# TODO: improve on this naive SO implementation by avoiding reopening the file on every query
import json

def persist_to_file(file_name):

    def decorator(original_func):
        try:
            cache = json.load(open(file_name, 'r'))
        except (IOError, ValueError):
            cache = {}

        def new_func(param):
            if param not in cache:
                cache[param] = original_func(param)
                json.dump(cache, open(file_name, 'w'))
            return cache[param]

        return new_func

    return decorator

@persist_to_file('cache.dat')
def normalizedInstitution(inst):
    print(f"Query google for institution of {val['Email']}")
    result = search(inst, tld="com", num=1, stop=1,pause=2.0)
    for r in result:    
        # There should be a single element in that iterator 
        print(f"Obtained: {r}")
        return r
    #This should not be possible
    exit(2)

def is_student_confused(val):
    if not ('N/A' == val['Are you a part of Industry or Academia? We will use this to match with students, as per their preference.']):
        return True
    if not('N/A' == val['Historically, the number of mentees far exceeds the number of available mentors. Up to how many students would you be willing to mentor? (Expectation of each mentoring commitment is 30 minutes in the conference week)']):
        return True 

def is_mentor_confused(val):
    if 'N/A' == val['Are you a part of Industry or Academia? We will use this to match with students, as per their preference.']:
        return True
    if not('N/A' == val['Would you rather be matched with a Senior Researcher in industry or academia as part of the MASA program?']):
        return True

def is_not_interested_confused(val):
    if not ('N/A' == val['Are you a part of Industry or Academia? We will use this to match with students, as per their preference.']):
        return True
    if not('N/A' == val['Historically, the number of mentees far exceeds the number of available mentors. Up to how many students would you be willing to mentor? (Expectation of each mentoring commitment is 30 minutes in the conference week)']):
        return True 
    if not('N/A' == val['Are you a part of Industry or Academia? We will use this to match with students, as per their preference.']):
        return True
    if not('N/A' == val['Would you rather be matched with a Senior Researcher in industry or academia as part of the MASA program?']):
        return True

for idx, val in enumerate(raw_data):
    if 'Student' in val[' The Meet-A-Senior-Architect (MASA) initiative offers mentorship opportunities to students by matching them with researchers in Academia/Industry for 30-minute one-on-one conversations. Are you interested in participating?']:
        if debug:
            print("Found interested student:", val['Email'])
        #if not(is_student_confused(val)):
        institutions = val['Institution / Company Name'].split('/')
        val['Institutions'] = [] 
        #do a google query to identify the institution
        for inst in institutions:
            val['Institutions'] += [ normalizedInstitution(inst) ]

        students += [val]
        # else:
            # print(f"[Critical Warning Student] Contradictory data: {val['Email']} at row {idx + 1}")
            # confused_students += [val]
    elif 'Senior Architect' in val[' The Meet-A-Senior-Architect (MASA) initiative offers mentorship opportunities to students by matching them with researchers in Academia/Industry for 30-minute one-on-one conversations. Are you interested in participating?']:
        if debug:
            print("Found interested mentor:", val['Email'])
        if not(is_mentor_confused(val)):
            institutions = val['Institution / Company Name'].split('/')
            val['Institutions'] = [] 
            #do a google query to identify the institution
            for inst in institutions:
                val['Institutions'] += [ normalizedInstitution(inst) ]
            multiplicity = val['Historically, the number of mentees far exceeds the number of available mentors. Up to how many students would you be willing to mentor? (Expectation of each mentoring commitment is 30 minutes in the conference week)']
            try:
                multiplicity = int(multiplicity)
            except:
                if multiplicity == '':
                    multiplicity = 0
                else:
                    print(f"Senior architect at line {idx + 1} , with email {val['Email']} misspecified their number of mentees, not a number: {multiplicity}")
                    print("Exit early, please double check that entry")
                    exit(1)
                    break
            mentors += [val] * multiplicity
        else:
            print(f"[Critical Warning Mentor] Contradictory data: {val['Email']} at row {idx + 1}")
            confused_mentors += [val]
    else:
        if is_not_interested_confused(val):
             print(f"[Critical Warning Confused Person] Contradictory data: {val['Email']} at row {idx + 1}")
             confused_not_interested += [val]
 
print (f"{len(students)} students and {len(mentors)} mentors to pair")

# Randomization of the data
random.shuffle(students)
random.shuffle(mentors)

# Now generate constraints ( first hard constraints of 1 mentor per student )

# We add a hard constraint on university of origin
# and on at most one mentor per student and one student per mentor
# Then we optimize by lexicographic priority:
# First we optimize on number of relationship made.
# Second we optimize on respecting the choice of pairing Industry/Academic
# Third we optimize on the quality of the relationship ( overlap of interest + disjointness of previous institutions institutions ) 
 
relation_student_mentor = []
opt = Optimize()
opt.set(priority='lex')
for i in range(len(students)):
    line = [] 
    acc = 0
    for j in range(len(mentors)):
        x = Int(f's{i}m{j}')
        # Relationship is boolean encoded as Int between 0 and 1
        opt.add( x >= 0) #, x <=1) 
        # Check university of origin, make sure it is disjoint
        student_institutions = students[i]['Institutions']
        mentor_institutions = mentors[j]['Institutions']
        for inst_s in student_institutions:
            for inst_m in mentor_institutions:
                if inst_s == inst_m :
                    print(f"[Info] Aliased institutions {inst_s} and {inst_m} for conflict computation")
                    opt.add(x == 0)
        acc += x
        line += [x] 
    # At most one mentor per student
    opt.add(acc <= 1)
    relation_student_mentor += [line]

# At most one student per mentor (mentor have been deduplicated) 
# Maximize the number of relationship formed
total_mentees = 0 
for j in range(len(mentors)):
    acc = 0
    for i in range(len(students)):
        acc += relation_student_mentor[i][j]
    opt.add(acc <= 1)
    total_mentees += acc
m = opt.maximize(total_mentees)


# Add new constraint for respect of industry/academic
respect_choice = 0
for i in range(len(students)):
    for j in range(len(mentors)):
        value_relationship = 10
        if students[i]['Would you rather be matched with a Senior Researcher in industry or academia as part of the MASA program?'] == 'Industry' and mentors[j]['Are you a part of Industry or Academia? We will use this to match with students, as per their preference.'] == 'Academia':
            value_relationship = 0
        if students[i]['Would you rather be matched with a Senior Researcher in industry or academia as part of the MASA program?'] == 'Academia' and mentors[j]['Are you a part of Industry or Academia? We will use this to match with students, as per their preference.'] == 'Industry':
            value_relationship = 0
        respect_choice += value_relationship * relation_student_mentor[i][j] 

m_choice_industry_academia = opt.maximize(respect_choice)

def overlapping_interests(s, m):
        si = s['Students Please provide research areas that best match your interests (tick all that apply). We will attempt to match students to mentors based on research areas if possible. Else, we will use random matching.'] 
        mi = m['Please provide research areas that best match your interests (tick all that apply). We will attempt to match students to mentors based on research areas if possible. Else, we will use random matching.']
        # print(si)
        # print(mi)
        if si == ['N/A'] or mi == ['N/A']:
            return 3 
        interests_s = si.split(',')
        interests_m = mi.split(',')
        inter = list(set(interests_s).intersection(set(interests_m)))
        if len(inter) == 0:
            return 0
        elif len(inter) == 1:
            return 5
        else:
            return (5 + len(inter))

students[0]
# Add new constraint for respect of industry/academic
respect_fields = 0
for i in range(len(students)):
    for j in range(len(mentors)):
        value_relationship = overlapping_interests(students[i], mentors[j])
        respect_fields += value_relationship * relation_student_mentor[i][j] 

m_choice_fields = opt.maximize(respect_fields)

# Get the first model available (Do we want to pick one randomly?)
model = None 
if opt.check() == sat:
    final = m.value()
    model = opt.model()

result = []
for i in range(len(students)):
    for j in range(len(mentors)):
        if model[relation_student_mentor[i][j]] == 1:
            result += [ (students[i] , mentors[j]) ]

with open('mentee_match.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["StudentFirstName", "StudentLastName","StudentEmail","MentorFirstName","MentorLastName", "MentorEmail"])
    for i in range(len(students)):
        for j in range(len(mentors)):
            if model[relation_student_mentor[i][j]] == 1:
                writer.writerow([students[i]['First Name'], students[i]['Last Name'], students[i]['Email'],mentors[j]['First Name'], mentors[j]['Last Name'], mentors[j]['Email']])

# Sad people:

with open('not_matched.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["StudentFirstName", "StudentLastName","StudentEmail"])
    countsad = 0
    for i in range(len(students)):
        start = 0
        for j in range(len(mentors)):
            start += model[relation_student_mentor[i][j]].as_long()
        if start == 0 :
            countsad += 1
            writer.writerow([students[i]['First Name'], students[i]['Last Name'], students[i]['Email']])


print(f"Number of relationship formed: {final} score for relationship: {m_choice_industry_academia.value()} with max: { 10 * len(students)}")
print(f"Field score: {m_choice_fields.value()}") 
print(f"We did not manage to match: {countsad}")

