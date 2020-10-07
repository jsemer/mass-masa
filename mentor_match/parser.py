#!/usr/bin/env python
import csv
from itertools import imap
from datetime import datetime

class Mentor():
    def __init__(self, id, firstname, lastname, email, affiliation, cap):
        def isAcademic(s):
            industries = ['amd','qualcomm','nvidia','hp','baidu','google',\
                          'arm','intel','microsoft','alibaba','hp','tsmc',\
                           'cavium','micron','pacific']
            return not any(imap(s.lower().__contains__, industries))

        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.affiliation = affiliation
        self.academic = isAcademic(affiliation)
        self.capacity = cap
        self.students = []

    def __str__(self):
        return "Mentor " + str(self.id) + ": " + self.firstname + ", " + \
                self.lastname + ", " + self.affiliation + ", " + \
                self.email + ", " + ('academic' if self.academic else 'industry')

class Student():
    def __init__(self, id, timestamp, firstname, lastname, school, email, pref, sigarchMember, preferenceList):
        self.id = id
        self.timestamp = timestamp
        self.firstname = firstname
        self.lastname = lastname
        self.school = school
        self.email = email
        self.preference = pref
        self.sigarchMember = sigarchMember
        self.preferenceList = preferenceList
        self.mentor = -1
        self.conflict = -1

    def __str__(self):
        return "Student" + str(self.id) + ": " + \
                self.firstname + ", " + self.lastname + ", " + \
                self.school + ", " + self.email

def parseMentors(mentorFile):
    mentors = []
    with open(mentorFile, 'rU') as csvfile:
        mentorRows = csv.reader(csvfile, delimiter=',')
        next(mentorRows) # skip header
        for (i, m) in enumerate(mentorRows):
#            mentors.append(Mentor(i, m[0], m[1], m[2], m[5], int(m[7])))
            mentors.append(Mentor(i, m[1], m[0], m[4], m[2], int(m[5])))
    return mentors

def parseStudents(studentFile, ignoreStudents, duplicateStudents):
    students = []
    numIgnored = 0
    with open(studentFile, 'rU') as csvfile:
        studentRows = csv.reader(csvfile, delimiter=',')
        next(studentRows) # skip header
        allRows = [s for s in studentRows]
        nonsigarch = [s for s in allRows if s[7]=='No']
        sigarch = [s for s in allRows if s[7]!='No']
        studentRows = sigarch + nonsigarch
        for (i, s) in enumerate(studentRows):
            preferredMentorsMap = {}
            prefStartIdx = 9
            for c in range(prefStartIdx,len(s)):
                if s[c] != '':
                    rank = s[c][0]
                    preferredMentorsMap[rank] = c - prefStartIdx
            preferredMentors = [preferredMentorsMap[key] for key in \
                                    sorted(preferredMentorsMap.keys())]
            timestamp = datetime.strptime(s[0], '%m/%d/%Y %H:%M:%S')
            sigarchMember = s[7]
            idx = i - numIgnored
            if filter(lambda x: x[0] == s[2] and x[1] == s[3], ignoreStudents):
                numIgnored += 1
                print 'Ignoring student', s[2], s[3], 'while parsing students.'
            elif filter(lambda x: x[0] == s[2] and x[1] == s[3], duplicateStudents) \
                 and filter(lambda x: x.firstname == s[2] and x.lastname == s[3], students):
                numIgnored += 1
                print 'Duplicate student', s[2], s[3], 'while parsing students.'
                # smatch = filter(lambda x: x[0] == s[2] and x[1] == s[3], students)
                smatch = filter(lambda x: x.firstname == s[2] and x.lastname == s[3], students)
                students.remove(smatch[0])
                students.append(Student(smatch[0].id, timestamp, s[2], s[3], s[4], s[1], s[8],\
                                        sigarchMember, preferredMentors))
            else:
                students.append(Student(idx, timestamp, s[2], s[3], s[4], s[1], s[8],\
                                        sigarchMember, preferredMentors))
            # print students[i], s[8], preferredMentors
    return students

def parseBaselineAssignments(baselineFile, mentors, students):
    with open(baselineFile, 'rU') as csvfile:
        studentAssignments = csv.reader(csvfile, delimiter=',')
        next(studentAssignments) # skip header
        for sr in studentAssignments:
            (studfirstname,studlastname) = (sr[0],sr[1])
            (mentfirstname,mentlastname) = (sr[3],sr[4])
            (studemail,mentemail) = (sr[2],sr[5])
            smatch = filter(lambda s : s.firstname == studfirstname and \
                                       s.lastname == studlastname and \
                                       s.email == studemail, students)
            if len(smatch) > 0:
                mmatch = filter(lambda m : m.firstname == mentfirstname and \
                                           m.lastname == mentlastname and \
                                           m.email == mentemail, mentors)
                # if len(smatch) > 1:
                #     students.remove(smatch[0])
                #     smatch.remove(smatch[0])
                assert len(smatch) == 1
                assert len(mmatch) == 1
                # print 'Assigning baseline student', smatch[0].firstname, 'to', mmatch[0].firstname
                smatch[0].mentor = mmatch[0].id
                # mmatch[0].students.append(smatch[0].id)
            else:
                print 'Baseline student match ', studfirstname, 'not found in student'\
                      'list...ignoring assignment, freeing mentor ', mentfirstname,\
                      mentlastname


if __name__ == "__main__":
#    ignoreStudents = [('ken','yoshioka'), ('Seunghwan','Cho')]
    ignoreStudents = []
#    duplicateStudents = [('Zhongyuan','Zhao'), ('cheng','tan')]
    duplicateStudents = []
    mentors = parseMentors('mentors.csv')
    students = parseStudents('students.csv',ignoreStudents, duplicateStudents)
    parseBaselineAssignments('baseline-student-match.csv', mentors, students)

    for m in mentors: print m
    for s in students: print s, s.preferenceList, \
                            mentors[s.mentor] if s.mentor != -1 else ''

