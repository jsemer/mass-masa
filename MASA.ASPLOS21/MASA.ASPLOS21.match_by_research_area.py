debug = False
import pandas
import numpy as np
from IPython.display import display, HTML
pandas.set_option('display.max_columns', None)  # or 1000
pandas.set_option('display.max_rows', None)  # or 1000
pandas.set_option('display.max_colwidth', None)  # or 199


#################################################
## List of Research Areas
#################################################

research_areas = ['Existing and Emerging Platforms (Embedded to Cloud)',
                  'Cloud, Datacenters, Internet Services',
                  'Parallel, Multicore Architectures & Systems',
                  'Accelerators & Heterogenous Architectures',
                  'Programming Models, Languages and Compilers',
                  'Storage and Compute of Big-Data',
                  'Virtualization',
                  'Memory & Storage',
                  'Power, Energy & Thermals',
                  'Security, Reliability & Availability',
                  'Testing & Verification',
                  'Approximate Computing & Emerging Technology']

#################################################
## Datafiles
#################################################

cvent_datafile = "../../data_dumps/ASPLOS21.cvent.csv" ## Cvent Registration
googleform_datafile = "../../data_dumps/ASPLOS21.googleform.MASA.csv" ## Google Form


#################################################
## Read Dataframes
#################################################

cvent_df = pandas.read_csv(cvent_datafile) 
gf_df = pandas.read_csv(googleform_datafile)
#display (cvent_df)
#display (gf_df)


##############################################################
## Cleanup and Merge Dataframes from Cvent and Google Forms
##############################################################

## ASPLOS Cvent Dataframe
cvent_df[['LastName','FirstName']]   = cvent_df['Full Name'].str.split(', ',expand=True)
cvent_df[['Email']]                  = cvent_df[['Email Address']]
cvent_df[['Affiliation']]            = cvent_df[['Company Name']]
cvent_df['SeniorResearcher/Student'] = cvent_df['Registration Type'].apply(lambda x: 'SeniorResearcher'  if x in ('Non-Member','ACM Professional Member') else 'Student')
cvent_df[['MentorSignup']]           = cvent_df[['The Meet-A-Senior-Architect (MASA) initiative offers mentorship opportunities to students by matching them with researchers in Academia/Industry for 30-minute one-on-one conversations. As a senior researcher in the community, are you willing to meet with a student and share your advice/career experi']]
cvent_df[['NumMentees']]             = cvent_df[['Historically, the number of mentees far exceeds the number of available mentors. Up to how many students would you be willing to mentor? (Expectation of each mentoring commitment is 30 minutes to an hour in the conference week)']]
cvent_df[['AffiliationType']]        = cvent_df[['Are you a part of Industry or Academia? We will use this to match with students, as per their preference.']]
cvent_df[['ResearchArea']]           = cvent_df[['For students or mentors who expressed interest in mentoring: Please provide research areas that best match your interests (Tick all that apply). We will attempt to match students to mentors based on research areas if possible. Else, we will use random matching.']]
cvent_df[['ResearchArea']]           = cvent_df['ResearchArea'].str.replace('Data-center','Datacenter')
cvent_df[['ResearchArea']]           = cvent_df['ResearchArea'].str.replace('Veriﬁcation','Verification')
cvent_df[['MenteeSignup']]           = cvent_df[['The Meet-A-Senior-Architect (MASA) and the Meet-A-Senior-Student (MASS) initiatives offer mentorship opportunities to students by matching them with researchers in Academia/Industry (MASA) and senior PhD students (MASS) for 30-minute one-on-one conversations. If you are a student, are you interested']]

## Google Form Dataframe
gf_df[['FirstName','LastName']]      = gf_df['Full Name'].str.rsplit(' ', 1,expand=True)
gf_df[['Email']]                     = gf_df[['Email address']]
gf_df[['Affiliation']]               = gf_df[['What is your most recent/current institution or company?']]
gf_df[['SeniorResearcher/Student']]  = gf_df['Are you a Senior Researcher (faculty / industry) or a Junior Researcher (student)?'].apply(lambda x: 'SeniorResearcher' if x=='Senior Researcher (faculty / industry-researcher)' else 'Student')
gf_df[['MentorSignup']]              = gf_df[['As a Senior Researcher, are you willing to meet with a student and share your advice/career experience within the context of the MASA Program?']]
gf_df[['NumMentees']]                = gf_df[['Historically, the number of mentees far exceeds the number of available mentors. Up to how many mentees would you be willing to mentor? (The expectation for each mentoring commitment is roughly 30 minutes to 1 hour during the week of the conference.) ']]
gf_df[['AffiliationType']]           = gf_df[['Are you a part of industry or academia? (We will use this to match with students as per their interest)']]
gf_df[['ResearchArea']]              = gf_df['For matching with students, what are your research areas (based on ASPLOS CFP)? Please select all that are applicable.'].fillna(
                                            gf_df['If you desire to be matched by research area, what is your area of interest? (We will try our best to match you by research area, otherwise we default to random)']) 
gf_df[['MenteeSignup']]              = gf_df[['As a Student, are you interested in matching with a Senior Researcher in industry or academia to gain advice/career experience as a part of MASA program?']]
gf_df[['MenteeSignup']]              = gf_df['MenteeSignup'].apply(lambda x: 'Yes. Mentor from either industry or academia is fine (no strong preference)' if x=='Yes. Either Industry or Academia Mentor is okay (No Strong Preference)' else x)

## Remove duplicates from Google Form Dataframe (HARDCODED):
gf_df = gf_df.drop(gf_df[gf_df['Email'].str.match('delimitrou@cornell.edu|haoranq4@illinois.edu|gtzimpragos@ucsb.edu',na=False)].index)

## Combine Cleaned Dataframes
cvent_df_clean = cvent_df[['FirstName','LastName','Email','Affiliation','SeniorResearcher/Student','MentorSignup','NumMentees',
                 'AffiliationType','ResearchArea','MenteeSignup']]
gf_df_clean    = gf_df[['FirstName','LastName','Email','Affiliation','SeniorResearcher/Student','MentorSignup','NumMentees',
                 'AffiliationType','ResearchArea','MenteeSignup']]
combined_df    = [gf_df_clean,cvent_df_clean]
combined_df    = pandas.concat(combined_df, ignore_index=True)


################################################
## Pre-Process Mentors (Get Ready for Matching)
################################################

## Separate Mentors and Mentees
mentors_df = combined_df.loc[(combined_df['SeniorResearcher/Student'] == 'SeniorResearcher') 
                             & (combined_df['MentorSignup'] == 'Yes')].copy()
mentees_df = combined_df.loc[(combined_df['SeniorResearcher/Student'] == 'Student')
                             & combined_df['MenteeSignup'].isin(('Yes. Mentor from either industry or academia is fine (no strong preference)',
                                                                'Yes. Would prefer a mentor from Academia if possible',
                                                                'Yes. Would prefer a mentor from Industry if possible'))].copy()

## Check for duplicates in combined mentor/mentees dataframes
#print("Duplicates")
#display(mentors_df[mentors_df.duplicated(subset=['Email'])])
#display(mentees_df[mentees_df.duplicated(subset=['Email'])])

## Replicate Mentor Entries Based on NumMentees per Mentor
mentors_2mentees      = mentors_df[mentors_df['NumMentees'] == 'Two']
mentors_3mentees      = mentors_df[mentors_df['NumMentees'] == 'Three']
mentors_replicated_df = [mentors_df,mentors_2mentees,mentors_3mentees, mentors_3mentees]
mentors_replicated_df =  pandas.concat(mentors_replicated_df,ignore_index=True)

## Create Research-Area Specific Lists of Mentors
mentors_by_area = {}
for area in research_areas:
    mentors_by_area[area] = mentors_replicated_df[mentors_replicated_df['ResearchArea'].str.contains(area,regex=False)]

#for area in research_areas:
#    print(area)
#    display(mentors_by_area[area])

## TODO: Shuffle mentors in each area in "mentors_by_area", to avoid bias in starting point
    
## TODO: Create List of Mentors Based on Industry/Academia


##############################################################
## Match Mentees to Mentors By Reserach Area
##############################################################

print("Matching First by Preference of Research Area")

mentee_count=0
num_mentor_commitments = mentors_replicated_df['Email'].count()
mentees_df.loc[:,'MentorAllocated'] = np.nan
mentees_df.loc[:,'MentorName']      = np.nan
mentees_df.loc[:,'MentorEmail']     = np.nan
mentors_replicated_df.loc[:,'MenteeAllocated'] = np.nan
mentors_replicated_df.loc[:,'MenteeName']      = np.nan
mentors_replicated_df.loc[:,'MenteeEmail']     = np.nan


## Match using research area (ignore industry/academia preference for now)
for mentee_index, mentee in mentees_df.iterrows():
    mentee_count=mentee_count+1
    if debug: print(mentee_index, mentee['FirstName'], mentee['LastName'])
    
    ## Iterate over mentees research area
    for area in research_areas:
        if(area in mentee['ResearchArea']):
            if debug: print ("MenteeResearchArea: ",area)
            
            #Check if Mentor available in mentee's research area
            if(not mentors_by_area[area].empty):                
                #Get first available mentor
                mentor_chosen = mentors_by_area[area].iloc[0] 
                mentor_chosen_index = int(mentors_by_area[area].index[0])
                if debug: print("Chosen Mentor Index: "+str(mentor_chosen_index))
                if debug: print(mentor_chosen['FirstName'] + " "+mentor_chosen['LastName'] + " MentorResearchAreas: "+mentor_chosen['ResearchArea'])
                
                #Mark mentor as allocated in mentees_df and mentors_replicated_df
                mentees_df.loc[int(mentee_index),'MentorAllocated'] = True
                mentees_df.loc[int(mentee_index),'MentorName']      = mentor_chosen['FirstName'] + " " + mentor_chosen['LastName']
                mentees_df.loc[int(mentee_index),'MentorEmail']     = mentor_chosen['Email']                                
                mentors_replicated_df.loc[mentor_chosen_index,'MenteeAllocated'] = True
                mentors_replicated_df.loc[mentor_chosen_index,'MenteeName']      = mentee['FirstName'] + " " + mentee['LastName']
                mentors_replicated_df.loc[mentor_chosen_index,'MenteeEmail']     = mentee['Email']
                
                #Delete matched mentor from all mentors_by_area, to prevent future hit on this matched mentor-entry
                for temp_area in research_areas:
                    if(mentor_chosen_index in mentors_by_area[temp_area].index):
                        if debug: print("Deleting mentor entry in ResearchArea:"+str(temp_area)+", MentorIndex:"+str(mentor_chosen_index)+", MentorName:"+mentors_by_area[temp_area].loc[mentor_chosen_index,'FirstName'])
                        mentors_by_area[temp_area] = mentors_by_area[temp_area].drop(index=mentor_chosen_index)
                
                #Mentee is matched
                break
    if debug: print ("\n")
    
    ## Stop matching once we hit the number of commitments from mentors
    if(mentee_count >= num_mentor_commitments):
        break
        
## TODO: Match taking into account Industry/Academia Preference.


## Dump csv files for mentors_replicated_df and mentees_df 
mentors_replicated_df.to_csv('mentors_pref.csv', index=False)
mentees_df.to_csv('mentees_pref.csv', index=False)


##############################################################
## Match Leftover Mentees to Mentors Randomly
##############################################################
print("Matching Leftovers Randomly")

mentee_count=0

#Get leftovers
mentors_remaining_df = mentors_replicated_df[mentors_replicated_df['MenteeAllocated']!= True]

#Shuffle leftovers
mentors_remaining_df = mentors_remaining_df.sample(frac=1) 

#Start matching leftovers
for mentee_index, mentee in mentees_df.iterrows():
    mentee_count=mentee_count+1    
    
    #If leftover mentee: Match with first leftover mentor
    if(mentees_df.loc[int(mentee_index),'MentorAllocated'] != True):
        if debug: print(mentee_index, mentee['FirstName'], mentee['LastName'])
        mentor_chosen = mentors_remaining_df.iloc[0]
        mentor_chosen_index = int(mentors_remaining_df.index[0])
        if debug: print("Chosen Mentor Index: "+str(mentor_chosen_index))
        if debug: print(mentor_chosen['FirstName'] + " "+mentor_chosen['LastName'])

        #Mark mentor as allocated in mentees_df and mentors_replicated_df
        mentees_df.loc[int(mentee_index),'MentorAllocated'] = True
        mentees_df.loc[int(mentee_index),'MentorName']      = mentor_chosen['FirstName'] + " " + mentor_chosen['LastName']
        mentees_df.loc[int(mentee_index),'MentorEmail']     = mentor_chosen['Email']                                
        mentors_replicated_df.loc[mentor_chosen_index,'MenteeAllocated'] = True
        mentors_replicated_df.loc[mentor_chosen_index,'MenteeName']      = mentee['FirstName'] + " " + mentee['LastName']
        mentors_replicated_df.loc[mentor_chosen_index,'MenteeEmail']     = mentee['Email']                     
    
        #Remove matched mentor from leftover list
        mentors_remaining_df = mentors_remaining_df.drop(index=mentor_chosen_index)
        
    ## Stop matching once we hit the number of commitments from mentors
    if(mentee_count >= num_mentor_commitments):
        break

        
## Dump csv files for mentors_replicated_df and mentees_df 
mentors_replicated_df.to_csv('mentors_final.csv', index=False)
mentees_df.to_csv('mentees_final.csv', index=False)

## Display Statistics
print("Number of Mentors: " + str(len(mentors_df['Email'].index)))
print("Number of Mentees: " + str(len(mentees_df['Email'].index)))
print("Number of Mentees Allocated: " + str(len(mentees_df[mentees_df['MentorAllocated'] == True].index)))
print("Number of Mentees Remaining: " + str(len(mentees_df[mentees_df['MentorAllocated'] != True].index)))

