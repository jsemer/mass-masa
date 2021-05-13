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
gf_df = gf_df.drop(gf_df[gf_df['Email'].str.match('yipeng.huang@rutgers.edu|sherwood@cs.ucsb.edu',na=False)].index)
gf_df = gf_df.drop(gf_df[gf_df['Email'].str.match('ugupta@g.harvard.edu|shivampotdar99@gmail.com',na=False)].index)

## Remove entries that have conflicting responses (HARDCODED):
#ali.hajiabadi@u.nus.edu: Said "yes" to mentoring, but for how many mentees said "did not sign up as mentor"
cvent_df = cvent_df.drop(cvent_df[cvent_df['Email'].str.match('ali.hajiabadi@u.nus.edu',na=False)].index)

## Remove entries for Moin, Josep and Saman from Cvent. They have updated Google Form responses (HARDCODED):
cvent_df = cvent_df.drop(cvent_df[cvent_df['Email'].str.match('moin@gatech.edu|torrella@illinois.edu|saman@csail.mit.edu',na=False)].index)

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

## Check and Ensure no duplicates in combined mentor/mentees dataframes
assert(mentors_df[mentors_df.duplicated(subset=['Email'])]['Email'].count() == 0)
assert(mentees_df[mentees_df.duplicated(subset=['Email'])]['Email'].count() == 0)
#print("Duplicates")
#display(mentors_df[mentors_df.duplicated(subset=['Email'])])
#display(mentees_df[mentees_df.duplicated(subset=['Email'])])

## Replicate Mentor Entries Based on NumMentees per Mentor
mentors_2mentees      = mentors_df[mentors_df['NumMentees'] == 'Two']
mentors_3mentees      = mentors_df[mentors_df['NumMentees'] == 'Three']
mentors_replicated_df = [mentors_df,mentors_2mentees,mentors_3mentees, mentors_3mentees]
mentors_replicated_df =  pandas.concat(mentors_replicated_df,ignore_index=True)

## Shuffle mentors in mentors_replicated_df to avoid biased starting point.
#mentors_replicated_df = mentors_replicated_df.sample(frac=1)

## Create Research-Area Specific Lists of Mentors
import warnings
warnings.filterwarnings("ignore", 'This pattern has match groups')
mentors_by_area = {}
for area in research_areas:
    mentors_by_area[area] = mentors_replicated_df[mentors_replicated_df['ResearchArea'].str.contains(area,regex=False)]

#for area in research_areas:
#    print(area)
#    display(mentors_by_area[area])
    
## Create List of Mentors Based on Industry/Academia
mentors_by_area_industry = {}
mentors_by_area_academia = {}
for area in research_areas:
    mentors_by_area_industry[area] = mentors_by_area[area][mentors_by_area[area]['AffiliationType'].isin(["Industry", 'Both'])]
    mentors_by_area_academia[area] = mentors_by_area[area][mentors_by_area[area]['AffiliationType'].isin(["Academia", 'Both'])]

## Initialize variables for Matching.
mentee_count=0
num_mentor_commitments = mentors_replicated_df['Email'].count()
mentees_df.loc[:,'MentorAllocated']   = np.nan
mentees_df.loc[:,'MentorName']        = np.nan
mentees_df.loc[:,'MentorEmail']       = np.nan
mentees_df.loc[:,'MentorAffiliation'] = np.nan
mentors_replicated_df.loc[:,'MenteeAllocated']   = np.nan
mentors_replicated_df.loc[:,'MenteeName']        = np.nan
mentors_replicated_df.loc[:,'MenteeEmail']       = np.nan
mentors_replicated_df.loc[:,'MenteeAffiliation'] = np.nan

## Stats for tracking research area and industry/academia preference match success
# For research area preference
num_mentees_want_areamatch = 0  
num_mentees_got_areamatch = 0 
# For Industry/academia preference
num_mentees_want_affiliationtype = 0 
num_mentees_got_affiliationtype = 0


##############################################################
## Function: Research-Area Based Matching with Mentor.
## Inputs: Mode (0 - Industry, 1-Academia, 2-Indifferent)
## Inputs: mentee_index 
## Inputs: mentee
##############################################################

def match_research_area(mode):
    global num_mentees_want_areamatch 
    global num_mentees_got_areamatch  
    global num_mentees_want_affiliationtype
    global num_mentees_got_affiliationtype 

    ## Choose Mentor Pool from which mentors chosen.
    mentors_pool = mentors_by_area
    if(mode == "Industry"):   # industry preference of mentee
        mentors_pool = mentors_by_area_industry
    elif(mode == "Academia"): # academia preference of mentee
        mentors_pool = mentors_by_area_academia
    else :
        mentors_pool = mentors_by_area
      
    ## Get Mentee Preference for Industry/Academia
    if(mode == "Industry"):
        mentee_affiliation_type_pref = 'Yes. Would prefer a mentor from Industry if possible'
    elif (mode == "Academia"):
        mentee_affiliation_type_pref = 'Yes. Would prefer a mentor from Academia if possible'
           
    ## Match using research area
    mentee_count = 0
    for mentee_index, mentee in mentees_df.iterrows():
        mentee_count=mentee_count+1
    
        ## Bools for tracking stats of research area match
        mentee_wants_areamatch = False
        mentee_got_areamatch = False
        
        ## Check if Mentee prefers Industry or Academia as per the mode
        if(((mode == "Industry") and (mentees_df.loc[int(mentee_index),'MenteeSignup'] == mentee_affiliation_type_pref)) |
           ((mode == "Academia") and (mentees_df.loc[int(mentee_index),'MenteeSignup'] == mentee_affiliation_type_pref)) |
           ((mode in ["Industry","Academia"]) != True)):

            #Check if mentee is not allocated:
            if(mentees_df.loc[int(mentee_index),'MentorAllocated'] != True) :                           
                ## Iterate over mentees research area
                for area in research_areas:
                    if(area in mentee['ResearchArea']):
                        if debug: print ("MenteeResearchArea: ",area)
                        mentee_wants_areamatch = True

                        #Check if Mentor available in mentee's research area
                        if(not mentors_pool[area].empty):                
                            #Get first available mentor from mentee's research area
                            mentor_chosen = mentors_pool[area].iloc[0] 
                            mentor_chosen_index = int(mentors_pool[area].index[0])
                            if debug: print("Chosen Mentor Index: "+str(mentor_chosen_index))
                            if debug: print(mentor_chosen['FirstName'] + " "+mentor_chosen['LastName'] + " MentorResearchAreas: "+mentor_chosen['ResearchArea'])

                            #Mark mentor as allocated in mentees_df and mentors_replicated_df
                            mentees_df.loc[int(mentee_index),'MentorAllocated']   = True
                            mentees_df.loc[int(mentee_index),'MentorName']        = mentor_chosen['FirstName'] + " " + mentor_chosen['LastName']
                            mentees_df.loc[int(mentee_index),'MentorEmail']       = mentor_chosen['Email'] 
                            mentees_df.loc[int(mentee_index),'MentorAffiliation'] = mentor_chosen['Affiliation']     
                            mentors_replicated_df.loc[mentor_chosen_index,'MenteeAllocated'] = True
                            mentors_replicated_df.loc[mentor_chosen_index,'MenteeName']      = mentee['FirstName'] + " " + mentee['LastName']
                            mentors_replicated_df.loc[mentor_chosen_index,'MenteeEmail']     = mentee['Email']
                            mentors_replicated_df.loc[mentor_chosen_index,'MenteeAffiliation']     = mentee['Affiliation']                            

                            #Delete matched mentor from all mentors_by_area, to prevent future hit on matched mentor-entry
                            for temp_area in research_areas:
                                if(mentor_chosen_index in mentors_by_area[temp_area].index):
                                    mentors_by_area[temp_area] = mentors_by_area[temp_area].drop(index=mentor_chosen_index)
                                if(mentor_chosen_index in mentors_by_area_industry[temp_area].index):
                                    mentors_by_area_industry[temp_area] = mentors_by_area_industry[temp_area].drop(index=mentor_chosen_index)
                                if(mentor_chosen_index in mentors_by_area_academia[temp_area].index):
                                    mentors_by_area_academia[temp_area] = mentors_by_area_academia[temp_area].drop(index=mentor_chosen_index)

                            #Mentee is matched
                            mentee_got_areamatch = True

                            #Update industry/academia preference match:
                            if (((mentee['MenteeSignup'] == 'Yes. Would prefer a mentor from Academia if possible') and (mentor_chosen['AffiliationType'] in ['Academia','Both'])) or
                               ((mentee['MenteeSignup'] == 'Yes. Would prefer a mentor from Industry if possible') and (mentor_chosen['AffiliationType'] in ['Industry','Both']))):
                                num_mentees_got_affiliationtype += 1
                            break                        
                ## Update Research Area Match Stats
                if mentee_got_areamatch == True: num_mentees_got_areamatch += 1    
    
        ## Stop matching once we hit the number of commitments from mentors
        if(mentee_count >= num_mentor_commitments):
            break            
        
##############################################################

##############################################################
## Function: Random research-area based Matching with Mentor.
## Inputs: Mode (0 - Industry, 1-Academia, 2-Indifferent)
## Inputs: mentors_remaining_df -> list of unallocated mentors.
##############################################################

def match_random_area(mode):
    global num_mentees_want_affiliationtype
    global num_mentees_got_affiliationtype 
    
    ## Get remaining mentors that are not allocated yet.
    mentors_remaining_df = mentors_replicated_df[mentors_replicated_df['MenteeAllocated']!= True]    
    
    ## Filter Remaining Mentors from Industry/Academia as per mode
    if(mode == "Industry"):
        mentors_remaining_df = mentors_remaining_df[mentors_remaining_df['AffiliationType'].isin(["Industry", 'Both'])]
    elif(mode == "Academia"):
        mentors_remaining_df = mentors_remaining_df[mentors_remaining_df['AffiliationType'].isin(["Academia", 'Both'])]

    #Shuffle leftovers
    #mentors_remaining_df = mentors_remaining_df.sample(frac=1) 

    ## Get Mentee Preference for Industry/Academia
    if(mode == "Industry"):
        mentee_affiliation_type_pref = 'Yes. Would prefer a mentor from Industry if possible'
    elif (mode == "Academia"):
        mentee_affiliation_type_pref = 'Yes. Would prefer a mentor from Academia if possible'
        
    #Start Matching    
    mentee_count=0
    for mentee_index, mentee in mentees_df.iterrows():
        mentee_count=mentee_count+1    
        
        ## Check if Mentee prefers Industry or Academia as per the mode
        if(((mode == "Industry") and (mentees_df.loc[int(mentee_index),'MenteeSignup'] == mentee_affiliation_type_pref)) |
           ((mode == "Academia") and (mentees_df.loc[int(mentee_index),'MenteeSignup'] == mentee_affiliation_type_pref)) |
           ((mode in ["Industry","Academia"]) != True)):

            #If leftover mentee: Match with first leftover mentor
            if((mentees_df.loc[int(mentee_index),'MentorAllocated'] != True)  and len(mentors_remaining_df.index)):
                mentor_chosen = mentors_remaining_df.iloc[0]
                mentor_chosen_index = int(mentors_remaining_df.index[0])

                #Mark mentor as allocated in mentees_df and mentors_replicated_df
                mentees_df.loc[int(mentee_index),'MentorAllocated'] = True
                mentees_df.loc[int(mentee_index),'MentorName']      = mentor_chosen['FirstName'] + " " + mentor_chosen['LastName']
                mentees_df.loc[int(mentee_index),'MentorEmail']     = mentor_chosen['Email']       
                mentees_df.loc[int(mentee_index),'MentorAffiliation'] = mentor_chosen['Affiliation']     
                mentors_replicated_df.loc[mentor_chosen_index,'MenteeAllocated'] = True
                mentors_replicated_df.loc[mentor_chosen_index,'MenteeName']      = mentee['FirstName'] + " " + mentee['LastName']
                mentors_replicated_df.loc[mentor_chosen_index,'MenteeEmail']     = mentee['Email']       
                mentors_replicated_df.loc[mentor_chosen_index,'MenteeAffiliation']     = mentee['Affiliation']                            

                #Remove matched mentor from leftover list
                mentors_remaining_df = mentors_remaining_df.drop(index=mentor_chosen_index)

                #Remove matched mentor from all area-specific lists.
                for temp_area in research_areas:
                    if(mentor_chosen_index in mentors_by_area[temp_area].index):
                        mentors_by_area[temp_area] = mentors_by_area[temp_area].drop(index=mentor_chosen_index)
                    if(mentor_chosen_index in mentors_by_area_industry[temp_area].index):
                        mentors_by_area_industry[temp_area] = mentors_by_area_industry[temp_area].drop(index=mentor_chosen_index)
                    if(mentor_chosen_index in mentors_by_area_academia[temp_area].index):
                        mentors_by_area_academia[temp_area] = mentors_by_area_academia[temp_area].drop(index=mentor_chosen_index)

                #Update industry/academia preference match:
                if (((mentee['MenteeSignup'] == 'Yes. Would prefer a mentor from Academia if possible') and (mentor_chosen['AffiliationType'] in ['Academia','Both'])) or
                           ((mentee['MenteeSignup'] == 'Yes. Would prefer a mentor from Industry if possible') and (mentor_chosen['AffiliationType'] in ['Industry','Both']))):
                    num_mentees_got_affiliationtype += 1

        ## Stop matching once we hit the number of commitments from mentors
        if(mentee_count >= num_mentor_commitments):
            break

##############################################################

##############################################################
## MENTEES PREFRRING INDUSTRY MENTORS : Match Mentors By Reserach Area, then Random-Area
##############################################################

## Match by Research Area
print("Matching Mentees Preferring Industry-Mentor: By Research Area")
match_research_area("Industry")

## Match by Random Area    
print("Matching Mentees Preferring Industry-Mentor: By Random Area")
match_random_area("Industry")
        
    
##############################################################
## MENTEES PREFRRING ACADEMIA MENTORS : Match Mentors By Reserach Area, then Random-Area
##############################################################

## Match by Research Area
print("Matching Mentees Preferring Academia-Mentor: By Research Area")
match_research_area("Academia")

## Match by Random Area    
print("Matching Mentees Preferring Academia-Mentor: By Random Area")
match_random_area("Academia")
        

##############################################################
## ALL REMAINING : Match Mentors By Reserach Area, then Random-Area
##############################################################

## Match by Research Area
print("Matching Mentees without strict-mentor preference: By Research Area")
match_research_area("ALL")

## Match by Random Area    
print("Matching Mentees without strict-mentor Preference: By Random Area")
match_random_area("ALL")
        

##############################################################
## SANITY CHECKS
##############################################################

## Check Each Mentor's NumMentees <= Number they Asserted in Form Response
for mentor_index,mentor in mentors_replicated_df[mentors_replicated_df['MenteeAllocated'] == True].iterrows():
    num_mentees_allotted = ((mentors_replicated_df['MenteeAllocated'] == True) &
                           (mentors_replicated_df['Email'] == mentor['Email'])).sum()
    num_mentees_asserted_str = mentors_df[mentors_df['Email'] == mentor['Email']]['NumMentees'].values[0]
    # Transform num_mentees_asserted_str to int:
    if(num_mentees_asserted_str == "One") :
        num_mentees_asserted = 1
    elif (num_mentees_asserted_str == "Two") :
        num_mentees_asserted = 2
    elif (num_mentees_asserted_str == "Three") :
        num_mentees_asserted = 3
    elif num_mentees_asserted_str.find("two - but note I am early in my career") != -1:
        num_mentees_asserted = 2
    elif num_mentees_asserted_str.find("to the extent this is compatible with being a co-program chair") != -1:
        num_mentees_asserted = 1   
    else :
        print(mentor['Email']+": " + num_mentees_asserted_str)
        assert(0)
    assert(num_mentees_allotted <= num_mentees_asserted)
    
## Check each mentor's assigned mentee, and make sure they are assigned the same mentor. 
for mentor_index,mentor in mentors_replicated_df[mentors_replicated_df['MenteeAllocated'] == True].iterrows():
    #Get Assigned Mentee
    mentee = mentees_df[mentees_df['Email'] == mentor["MenteeEmail"]]
    #Ensure Mentee is assigned Same Mentor.
    assert(mentee['MentorEmail'].values[0] == mentor['Email'])    
    #print(mentee['MentorEmail'].values[0] +" == " + mentor['Email'])


##############################################################
## CONCLUSION
##############################################################

## Dump csv files for mentors_replicated_df and mentees_df 
mentors_replicated_df.to_csv('mentors_final.csv', index=False)
mentees_df.to_csv('mentees_final.csv', index=False)        

## Get Stats
num_mentees_want_areamatch = (mentees_df['ResearchArea'].str.contains("|".join(research_areas)) &
                                    (mentees_df['MentorAllocated'] == True)).sum()
num_mentees_want_affiliationtype = (mentees_df['MenteeSignup'].isin(('Yes. Would prefer a mentor from Academia if possible',
                                                                    'Yes. Would prefer a mentor from Industry if possible')) &
                                    (mentees_df['MentorAllocated'] == True)).sum()

## Print Stats 
print("")
print("Total Mentees Matched: "+str(num_mentor_commitments))
print("Mentees Wanting Mentor in Matching Research Area: "+str(num_mentees_want_areamatch))
print("Mentees Provided Mentor in Matching Research Area: "+str(num_mentees_got_areamatch))
if num_mentees_got_areamatch > 0 : 
    print("Research Area Matching Success Rate: "+str(int(num_mentees_got_areamatch/num_mentees_want_areamatch*100))+"%")

print("")
print("Mentees Wanting Mentor Specifically in Industry/Academia: "+str(num_mentees_want_affiliationtype))
print("Mentees Provided Mentor Specifically in Industry/Academia: "+str(num_mentees_got_affiliationtype))
if num_mentees_got_affiliationtype > 0 : 
    print("Research Area Matching Success Rate: "+str(int(num_mentees_got_affiliationtype/num_mentees_want_affiliationtype*100))+"%")    


## Display Overall Statistics for Mentor/Mentee Matching
print("Number of Mentors: " + str(len(mentors_df['Email'].index)))
print("Number of Mentees: " + str(len(mentees_df['Email'].index)))
print("Number of Mentees Allocated: " + str(len(mentees_df[mentees_df['MentorAllocated'] == True].index)))
print("Number of Mentees Remaining: " + str(len(mentees_df[mentees_df['MentorAllocated'] != True].index)))

