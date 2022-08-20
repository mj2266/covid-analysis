
Make a virtual environment to run this code.(NOTE:   Creating virtual environment is optional, you can go to direct 
                                                        step 4 instead, but its recommended to use virtual environment)
    Example on how to make it on ubuntu 18.04:
        1)sudo apt-get install python3-venv
        2) inside the project folder execute following command:
            python3 -m venv venv

        3) now execute : 
            source venv/bin/activate

        4) Below command Installs all the required packages( numpy, pandas, openpyxl):
            pip install -r requirements.txt
	NOTE: Code is tested on python version 3.6 and 3.8
================================================================================================

Give execution permission to the sh files:

Type following command in the main code folder. 

find ./ -type f -iname "*.sh" -exec chmod +x {} \;

================================================================================================

assign1.sh is the top level script which executes all the programs.

There might be "SettingWithCopyWarning" in question 6 and 8. Kindly ignore those warnings.

Question 1)
- input files: neighbor-districts.json , replaceName.csv
- sh script: neighbor-districts-modified.sh
- source code: q1.py
- output path: output/neighbor-districts-modified.json

- Modifying neighbor district data from json file to match to the
  districts mentioned in vaccination data.
- Output is sorted on statecode and district code
- replaceName.csv is file is used to replace the districts name with their corrected.
  renamed names according to cowin data.
- This file was created by manual efforts.
- Handled Repeating Districts : Bilaspur, Pratapgarh, Hamirpur, Bijapur, Balrampur, Aurangabad
- Removed Noklak, Niwari, Konkan District from neighbor-districts.json
- Merged Mumbai city and Mumbai suburban into Mumbai
- Note Bijapur from Karnataka is replaced with Vijayapura, because that is what the name in Cowin csv file.
- NOTE:Question 1 and Question 2 are interdependent  

================================================================================================

Question 2)
- input files: output/neighbor-districts-modified.json
- sh script: edge-generator.sh
- source code: q2.py
- output path: output/edge-graph.csv

- Using output of Question 1 for this Question
- Generating Edge list for the given neighboring district json file.
- Outputting edge list in csv file.

================================================================================================

Question 3)
- input files:  districts.csv
                cowin_vaccine_data_districtwise.csv
- sh script: case-generator.sh
- source code: q3.py
- output path:  output/cases-week.csv
                output/cases-month.csv
                output/cases-overall.csv

- Finding Weekly, monthly and overall cases for every district
- Considering Date Range from 15th March 2020 to 14th August 2021.
- I didn't consider overlapping weeks. 
- Since we don't have access to district keys in districts.csv file and I wanted to use as much data as possible
  I made generated District Key at run time. I cross checked that for every district, given
  state code and district name, its district key = <State_Code>_<District_Name>. So we need 
  not have district key avaiable. It can be generated at runtime and it will match with official
  naming schemes. 
- I have verified my above assumptions by doing following: I picked up vaccination csv which contains district keys
  I seperated state_code from the district keys, what should be left should completely match with district name, 
  this was indeed true, so my hypothesis was correct thus.
- This is why, there was no need for me to seperately handle Delhi in this question, because of unavailbility of District key,
  Delhi's key is easy generated as DL_Delhi.
- Repeating Districts occur in data, but they are handled by considering their states too.

================================================================================================

Question 4)
- input files:  districts.csv
                cowin_vaccine_data_districtwise.csv
- sh file:  peaks-generator.sh
- source code: q4.py
- output path:  output/district-peaks.csv
                output/state-peaks.csv
                output/india-peaks.csv

- Date Range considered: 15th March 2020 to 14th August 2021
- Overlapping weeks is considered.
- Since we are smoothening data by considering overlapping weeks. And in assignment question we have 
  been given rough time estimations for 2 peaks, I considered peak of 2020 as max week occurance of that week.
  And Peak of 2021 as max week occurance.
  This almost always gave correct peak, there were no notable outliers, although we can add logic to check whether a peak is 
  not just a spike, but it is unlikely to get a weekly spike. A day spike is understandable, but a week spike is rare.
  So using these assumptions, I simply found maxes. 
- Also question 4 uses code of question 3 and makes it overlapping weeks, so assumptions from question 3 also follows.

================================================================================================

Question 5)
- input files: cowin_vaccine_data_districtwise.csv
- sh script: vaccinated-count-generator.sh
- source code: q5.py
- output path:  output/district-vaccinated-count-week.csv
                output/district-vaccinated-count-month.csv
                output/district-vaccinated-count-overall.csv
                output/state-vaccinated-count-week.csv
                output/state-vaccinated-count-month.csv
                output/state-vaccinated-count-overall.csv

- Date Range considered: 16th January 2021 to 15th August 2021
- Week1 is 16-01-2021(Sat) to 23-01-2021(Sat). 
- Rest all districts are from Sunday to Saturday.
- Here we are finding number of people which have vaccinated with dose 1 and dose 2 for state, 
  district and time weekly, monthly and overall
- There are few districts in cowin dataset whose district key repeat. 
  Example: RJ_Jaipur repeats for districts: Jaipur I and Jaipur II.
- These cases have been handled in code.
- There are districts with repeating names, but no need to handle, because we have unique district keys(Eg Bilaspur).

================================================================================================

Question 6)
- input files:  cowin_vaccine_data_districtwise.csv
                DDW_PCA0000_2011_Indiastatedist.xlsx
                replaceCensusName.csv
- sh script: vaccination-population-ratio-generator.sh
- source code: q6.py
- output path:  output/district-vaccination-population-ratio.csv
                output/state-vaccination-population-ratio.csv
                output/india-vaccination-population-ratio.csv

- Finding Total number of females vaccinated to total number of males. Also finding population ratio of 
  female to male. And finding the ratio of ratio. This is done for every districts, states and country.
- Output is sorted on final ratio
- replaceCensusName.csv file is used to match district names from cowin data to census data
- This file was created by manual efforts.
- Date Range is from 16th January to 15th August.
- Dadra Nagar Haveli and Daman And Diu from census data are merged.
- Telangana and Ladakh are dropped because they are formed after the census.
- There are few districts in cowin dataset whose district key repeat. 
  Example: RJ_Jaipur repeats for districts: Jaipur I and Jaipur II.
  For these cases, data is merged and summed.
- There are districts with repeating names, this is handled by careful filtering.
  EG) We consider repeated district bilaspur Which is in Himachal Pradesh and Chattisgarh.
    When Considering Bilaspur of Himachal Pradesh from vaccination data, and we need to finding
    Bilaspur in Census data, we will first filter census by states. Then query the district. 
    So this way, repeating district names will never be a problem.
  NOTE: Similar approach is used to handle repeating cases in questions that follow.

================================================================================================

Question 7)
- input files: cowin_vaccine_data_districtwise.csv
- sh script: vaccine-type-ratio-generator.sh
- source code: q7.py
- output path: 
    output/district-vaccine-type-ratio.csv
    output/state-vaccine-type-ratio.csv
    output/india-vaccine-type-ratio.csv

- Finding out ratio of covishield to covaxin, for districts, states and overall
- Ratio where there is 0 covaxin dose is written as : "inf" in output
- Because Positivenumber/ 0 = infinity. 
- I purposely wrote infinity and not none, because Infinity will suggest that
  covaxin data was 0. It is giving information, if we write none, there will be 
  ambiguity whether what to consider it as.
- Date Range considered: 16th January to 15th August.
- There are few districts in cowin dataset whose district key repeat. 
  Example: RJ_Jaipur repeats for districts: Jaipur I and Jaipur II.
- These cases have been handled in code.
- There are districts with repeating names, but no need to handle, because we have unique district keys(Eg Bilaspur).

================================================================================================

Question 8)
- input files:  cowin_vaccine_data_districtwise.csv
                DDW_PCA0000_2011_Indiastatedist.xlsx
                replaceCensusName.csv
- sh script: vaccinated-ratio-generator.sh
- source code: q8.py
- output path:
      output/district-vaccinated-dose-ratio.csv
      output/state-vaccinated-dose-ratio.csv
      output/india-vaccinated-dose-ratio.csv

- Finding total number of people vaccinated both dose 1 and dose 2 to total population.
- replaceCensusName.csv file is used to match district names from cowin data to census data
- This file was created by manual efforts.
- Date Range is from 16th January to 15th August.
- Dadra Nagar Haveli and Daman And Diu from census data are merged.
- Telangana and Ladakh are dropped because they are formed after the census.
- Output is sorted by dose 1 ratio

================================================================================================

Question 9)
- input files: 
        cowin_vaccine_data_districtwise.csv
        DDW_PCA0000_2011_Indiastatedist.xlsx
- sh script: complete-vaccination-generator.sh
- source code: q9.py
- output path: 
      output/complete-vaccination.csv

- Finding the date on which the entire population will 
  get at least one does of vaccination for each state.
- Considering the vaccination rate same as rate of last week vaccination. 
  i.e the week ending on 14th august.

================================================================================================
Contact manjyots21@iitk.ac.in for any queries.