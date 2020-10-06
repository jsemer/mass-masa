import csv
import copy
from random import shuffle

mentors1 = list(csv.DictReader(open("mentors1.csv")))
mentors2 = list(csv.DictReader(open("mentors2.csv")))

mentor_count = len(mentors1)+len(mentors2)
    
#for mentor in mentors:
#    first_name = mentor['FirstName']
#    last_name = mentor['LastName']
#    email = mentor['Email']
#    print(f"{first_name} {last_name} - {email}")

students = list(csv.DictReader(open("students.csv")))
student_count = len(students)
    
#for student in students:
#    first_name = student['FirstName']
#    last_name = student['LastName']
#    email = student['Email']
#    print(f"{first_name} {last_name} - {email}")

print(f"Mentors={mentor_count}")
print(f"Students={student_count}")

shuffle(students)

mentors2a = copy.deepcopy(mentors2)
mentors2b = copy.deepcopy(mentors2)
shuffle(mentors2a)
shuffle(mentors2b)

mentors1 = copy.deepcopy(mentors1)
shuffle(mentors1)

mentors2a.extend(mentors1)
mentors2a.extend(mentors2b)

print(f"Combined mentors = {len(mentors2a)}")

m_matches = {}

for mentor, student in zip(mentors2a, students):

    if not mentor['Email'] in m_matches:
        m = {}
        m['MentorEmail'] = mentor['Email']
        m['MentorFirstName'] = mentor['FirstName']
        m['MentorLastName'] = mentor['LastName']
        m['Student1FirstName'] = student['FirstName']
        m['Student1LastName'] = student['LastName']
        m['Student1Email'] = student['Email']
        m_matches[mentor['Email']] = m
    else:
        m = m_matches[mentor['Email']]
        m['Student2FirstName'] = student['FirstName']
        m['Student2LastName'] = student['LastName']
        m['Student2Email'] = student['Email']

mout = open("mentor_match.csv", "w+")

m = "MentorEmail,MentorFirstName,MentorLastName,"
s1 = "Student1Email,Student1FirstName,Student1LastName,"
s2 = "Student2Email,Student2FirstName,Student2LastName"

mout.write(f"{m}{s1}{s2}\n")

sout = open("student_match.csv", "w+")

s1 = "StudentEmail,StudentFirstName,StudentLastName,"
m = "MentorEmail,MentorFirstName,MentorLastName"

sout.write(f"{s1}{m}\n")

m_count = 0
s_count = 0

for k, v in m_matches.items():
    problem = ""

    m_email = v['MentorEmail']
    m_site = m_email.split('@')[1]

    m_first = v['MentorFirstName']
    m_last = v['MentorLastName']

    s1_email = v['Student1Email']
    s1_site = s1_email.split('@')[1]
    s1_first = v['Student1FirstName']
    s1_last = v['Student1LastName']
    m_count += 1
    if "Student2Email" in v:
        s2_email = v['Student2Email']
        s2_site = s2_email.split('@')[1]
        s2_first = v['Student2FirstName']
        s2_last = v['Student2LastName']
        s_count += 2
    else:
        s2_email = ""
        s2_site = ""
        s2_first = ""
        s2_last = ""
        s_count += 1

    m = f'"{m_email}","{m_first}","{m_last}"'
    s1 = f'"{s1_email}","{s1_first}","{s1_last}"'
    s2 = f'"{s2_email}","{s2_first}","{s2_last}"'

    if m_site != "gmail.com" and (m_site == s1_site or m_site == s2_site):
        problem = "  --- PROBLEM"
        print("PROBLEM")
    else:
        problem = ""

    mout.write(f"{m},{s1},{s2}{problem}\n")

    sout.write(f"{s1},{m}\n")
    if len(s2_email):
        sout.write(f"{s2},{m}\n")
        
print(f"Assigned mentors = {m_count}")
print(f"Assigned students = {s_count}")
