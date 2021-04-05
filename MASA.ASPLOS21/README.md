Mentor/Mentee Matching Scripts
==============================

Script to match mentees to mentors first based on research area preference, and then any leftovers are matched randomly.

Inputs:

- ASPLOS21.cvent.csv           - responses from the ASPLOS cvent registration form (with the required MASA question headers), that contains both mentor and mentee signups (and also info on those who did not sign up).
- ASPLOS21.googleform.MASA.csv - responses from the Google Form for MASA for ASPLOS'21 (ones who had already registered before the questions got added to the ASPLOS registration form). This includes both mentor and mentee signups.


Outputs:

- mentor_pref.csv  - list of mentors (and their mentee name/email) after matching happens by research area (mentor entries replicated for multiple mentees)
- mentee_pref.csv  - list of mentees (and their mentor name/email) after matching happens by research area

- mentor_final.csv - final list of mentors (and their mentee name/email). After matching by reserach area, remainder matched randomly (mentor entries replicated for multiple mentees).
- mentee_final.csv - final list of mentees (and their mentor name/email). After matching by reserach area, remainder matched randomly. 


Process:

1. Cleans up data from Cvent Form (ASPLOS Registration Form) & Google Form, making fields consistent across both.
2. Merges Cvent and Google Form responses, Filters Mentor & Mentee Data-frames and Removes duplicates (some attendees filled questions in both forms)
3. Creates multiple entries for mentors who committed to mentor >1 mentee.
4. Separates out mentors into research-area specific lists and matches mentees one-by-one with mentors in one of their research areas. Outputs mentor_pref.csv,mentee_pref.csv. 
5. Finally, randomly allots remaining mentees to mentors.
6. Stops allocation when num-mentees-allotted is equal to number-of-commitments by mentors. 


TODO:

- Add matching based on Industry/Academia preference (basically need to perform multiple iterations of Research-Area based matching)
- Port MASA scripts to MASS.