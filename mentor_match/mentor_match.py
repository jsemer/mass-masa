#!/usr/bin/env python

import random
import math

from gap import GAP
from stablemarriage import Suitor, Suited, stableMarriage
import parser

# Globals
maximumRank = 8
random.seed(9001)

def matchAffiliation(pref,isacademic):
    if pref == 'Either': return 1
    elif pref == 'Academia': return int(isacademic)
    elif pref == 'Industry': return int(not isacademic)
    else: return 0

def StableMarriageSolve(mentors, students):
    suitors = []
    suiteds = []

    # Assign student preferences
    for student in students:
        mentorPrefs = student.preferenceList
        academic = [m.id for m in mentors if m.id not in mentorPrefs and m.academic]
        industry = [m.id for m in mentors if m.id not in mentorPrefs and not m.academic]
        if student.preference == 'Either':
            remainingMentors  = academic + industry
            random.shuffle(remainingMentors)
        else:
            random.shuffle(academic)
            random.shuffle(industry)
            if student.preference == 'Academia':
                remainingMentors = academic + industry
            else:
                remainingMentors = industry + academic
        # print student.id, "(", len(mentorPrefs + remainingMentors), "): ", mentorPrefs + remainingMentors
        suitors.append(Suitor(student.id, mentorPrefs + remainingMentors))

    # Assign mentor preferences (strictly FCFS)
    for mentor in mentors:
        suiteds.append(Suited(mentor.id, range(len(students)),mentor.capacity))

    marriage = stableMarriage(suitors, suiteds)

    x = [[0] * len(suiteds) for _ in xrange(len(suitors))] # careful!
    for (mentor,assignedStudents) in marriage.iteritems():
        for v in assignedStudents:
            x[v.id][mentor.id] = 1
    return x

def GAPSolve(mentors, students, allMentorsAssignedStudents=True):
    budgets = [m.capacity for m in mentors]
    costs = []
    profits = []
    maxPrefScore = maximumRank + 1
    for s in students:
        profit = [matchAffiliation(s.preference, m.academic) for m in mentors]
        for (r, m) in enumerate(s.preferenceList): profit[m] = maxPrefScore - r
        if s.mentor != -1: profit[s.mentor] = 10000000
        if s.conflict != -1: profit[s.conflict] = -10000000
        factor = 10.0 if s.sigarchMember != 'No' else 100.0
        profit = [(float(len(students) - (s.id) + 1)/factor) * p for p in profit]
        profits.append(profit)

    for i in range(len(profits)):
        elem = [1] * len(mentors)
        costs.append(elem)

    # print budgets
    # for (i,p) in enumerate(profits): print i, ':', p

    (objval, assignment) = GAP(costs, budgets, profits, allMentorsAssignedStudents)
    # print 'objective =', objval
    # print 'x = ['
    # for x_i in assignment:
    #     print '   ', x_i
    # print ']'
    return assignment

def printMatchStats(students, mentors):
    matchStats = [0] * (maximumRank + 2)
    snapshot = list(matchStats)
    quartiles = [len(students) / 4 - 1, len(students) /2 - 1,
                 len(students) * 3/4 - 1, len(students) -1]
    q = 0
    for (s, student) in enumerate(students):
        index = maximumRank + 1
        if student.mentor in student.preferenceList:
            index = student.preferenceList.index(student.mentor)
            assert index < maximumRank
        elif matchAffiliation(student.preference,mentors[student.mentor].academic):
            index = maximumRank
        matchStats[index] += 1

        if s == quartiles[q]:
            diff = [a_i - b_i for a_i, b_i in zip(matchStats, snapshot)]
            print 'Quartile ', q+1, ': ', diff
            snapshot = list(matchStats)
            q = q + 1

    print matchStats

    nonprefStudents = filter(lambda s: (not matchAffiliation(s.preference, \
                                            mentors[s.mentor].academic)) and
                                       s.mentor not in s.preferenceList,
                             students)
    nonrankedStudents = filter(lambda s: s.mentor not in s.preferenceList,
                               students)
    print "Non-preference students: "
    for s in nonprefStudents: print s
    print "Non-rank students: "
    for s in nonrankedStudents: print s


def adjustAssignment(students, mentors):
    unassignedMentors = filter(lambda m: not m.students, mentors)
    nonprefStudents = filter(lambda s: (not matchAffiliation(s.preference, \
                                            mentors[s.mentor].academic)) \
                                        and len(mentors[s.mentor].students) > 1,
                             students)
    nonRankedStudents = {}
    for pref in ['Academia', 'Industry', 'Either']:
        nonRankedStudents[pref] = filter(lambda s: s.mentor not in s.preferenceList \
                                                    and s.preference == pref,\
                                         students)
    if len(unassignedMentors): print 'Initial pass had :', len(unassignedMentors), 'unassigned mentors'
    for mentor in unassignedMentors:
        preference = 'Academia' if mentor.academic else 'Industry'
        nonpreference = 'Industry' if mentor.academic else 'Academia'
        npstudents = filter(lambda s: s.preference == preference ,nonprefStudents)
        def assign(student,mentor):
            assert len(mentors[student.mentor].students) > 1
            mentors[student.mentor].students.remove(student.id)
            student.mentor = mentor.id
            mentor.students.append(student.id)
        def prune(studentList):
            studentList[:] = filter(lambda s: len(mentors[s.mentor].students) > 1, studentList)

        if npstudents:
            npstudent = npstudents[0]
            nonprefStudents.remove(npstudent)
            assign(npstudent,mentor)
        elif nonRankedStudents[preference]:
            nrstudent = nonRankedStudents[preference][0]
            nonRankedStudents[preference].remove(nrstudent)
            assign(nrstudent,mentor)
        elif nonRankedStudents['Either']:
            nrstudent = nonRankedStudents['Either'][0]
            nonRankedStudents['Either'].remove(nrstudent)
            assign(nrstudent,mentor)
        elif nonRankedStudents[nonpreference]:
            nrstudent = nonRankedStudents[nonpreference][-1]
            nonRankedStudents[nonpreference].remove(nrstudent)
            assign(nrstudent,mentor)
        else:
            print 'Unable to assign students to mentor: ', mentor

        prune(nonprefStudents)
        for key in nonRankedStudents.keys(): prune(nonRankedStudents[key])

if __name__ == "__main__":

#    ignoreStudents = [('ken','yoshioka'), ('Seunghwan','Cho')]
    ignoreStudents = []

#    duplicateStudents = [('Zhongyuan','Zhao'), ('cheng','tan')]
    duplicateStudents = []

    conflicts = [('Philip','Bedoukian','Adrian','Sampson'),\
                 ('Wenjie','Xiong','Carole-Jean','Wu'),
                 ('Sridhar', 'Akash', 'Heiner', 'Litz'),
                 ( 'Salonik', 'Resch', 'David' , 'Lilja'), 
                 ( 'Yu-Ching', 'Hu', 'Hung-Wei', 'Tseng'), ]

#    mentorBudget = [('Joel','Emer'), ('Daniel','Sanchez')]
    mentorBudget = []

    students = parser.parseStudents('students.csv',ignoreStudents,\
                                    duplicateStudents)
    mentors = parser.parseMentors('mentors.csv')

    parser.parseBaselineAssignments('baseline-student-match.csv', mentors, students)

    for c in conflicts:
        smatch = filter(lambda x: x.firstname == c[0] and x.lastname == c[1], students)
        mmatch = filter(lambda x: x.firstname == c[2] and x.lastname == c[3], mentors)
        if  len(smatch) == 1 and len(mmatch) == 1:
            smatch[0].conflict = mmatch[0].id
        else:
            print("Conflicting student or mentor does not exist")

    for m in mentorBudget:
        mmatch = filter(lambda x: x.firstname == m[0] and x.lastname == m[1], mentors)
        assert len(mmatch) == 1
        mmatch[0].capacity = 1

    allMentorsAssignedStudents = True
    assignment = GAPSolve(mentors, students, allMentorsAssignedStudents)

    for (s,student) in enumerate(assignment):
        for (m,val) in enumerate(student):
            if (val == 1):
                students[s].mentor = m
                mentors[m].students.append(s)

    with open('student-match.csv','w') as studFile:
        header = 'StudentFirstName,StudentLastName,StudentEmail,'\
                 'MentorFirstName,MentorLastName,MentorEmail,Rank\n'
        studFile.write(header)
        for s in students:
            m = mentors[s.mentor]

            def rank(m):
                index = maximumRank + 1
                if m in s.preferenceList:
                    index = s.preferenceList.index(m)
                elif matchAffiliation(s.preference,mentors[m].academic):
                    index = maximumRank
                return index

            line = s.firstname + "," + s.lastname + "," + s.email + "," + \
                   m.firstname + "," + m.lastname + "," + m.email + "," + \
                   str(rank(s.mentor))
            studFile.write(line)
            studFile.write('\n')

    with open('mentor-match.csv','w') as mentorFile:
        header = 'MentorFirstName,MentorLastName,MentorEmail,'\
                 'Student1FirstName,Student1LastName,Student1Email,'\
                 'Student2FirstName,Student2LastName,Student2Email\n'
        mentorFile.write(header)
        for m in mentors:
            line = m.firstname + "," + m.lastname + "," + m.email
            i = 0
            for student in m.students:
                s = students[student]
                line += "," + s.firstname + "," + s.lastname + "," + s.email
                i += 1
            while i < 2:
                line += ",,,"
                i += 1
            mentorFile.write(line)
            mentorFile.write('\n')

    printMatchStats(students, mentors)
