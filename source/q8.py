# -*- coding: utf-8 -*-
"""
Created on Thu Sep 16 17:03:03 2021

@author: manjy
"""

import csv
import pandas as pd
cowin_file = "cowin_vaccine_data_districtwise.csv"
census_file = "DDW_PCA0000_2011_Indiastatedist.xlsx"

def get_dataframe_from_csv(filename,drop_first_row=False):
    
    
    # Adding skiprow here instead of dropping later
    # because this will automatically read data as int then.
    # Otherwise data below dates is matched as float.    
    if drop_first_row:    
        return pd.read_csv(filename, skiprows=[1],low_memory=False)

    else:
        return pd.read_csv(filename, low_memory=False)

def get_dataframe_from_excel(filename):
    
    df = pd.read_excel(filename, engine="openpyxl")
    return df

def clean_and_get_district_census_df(census_df):
    df = census_df[census_df['TRU']=='Total']  

    df = df.loc[df['Level']=='DISTRICT']
    
    columns=["State", 'Name','TRU','TOT_P','TOT_M','TOT_F']
    df = df[columns]
    index = df[df.State == 26].index
    df.at[index, "State"] = 25
    
    df["Name"] = df["Name"].str.strip()
    return df

def clean_and_get_state_census_df(census_df):
    
    df = census_df[census_df['TRU']=='Total']  

    df = df.loc[df['Level']=='STATE']
    
    columns=["State", 'Name', 'TRU', 'TOT_P', 'TOT_M', 'TOT_F']
    df = df[columns]
    
    df.Name = df.Name.str.lower()
    
    #removing Telangana and Ladakh from cowin data
    df = df.loc[df['State']!='ladakh']
    df = df.loc[df['State']!='telangana']
    
    #renaming nct of delhi to delhi in census data
    #renaming jammu & kashmir to jammu and kashmir in census data
    #renaming andaman & nicobar islands to andaman and nicobar islands
    df.loc[df.Name == "nct of delhi" , "Name"] = "delhi"
    df.loc[df.Name == "andaman & nicobar islands" , "Name"] = "andaman and nicobar islands"
    df.loc[df.Name == "jammu & kashmir" , "Name"] = "jammu and kashmir"
    df.loc[df.Name == "dadra & nagar haveli" , "Name"] = "dadra and nagar haveli and daman and diu"
    df.loc[df.Name == "daman & diu" , "Name"] = "dadra and nagar haveli and daman and diu"
    
    daman_row1 = df.iloc[24]
    daman_row2 = df.iloc[25]
    
    daman_row1.TOT_M = daman_row1.TOT_M + daman_row2.TOT_M
    daman_row1.TOT_F = daman_row1.TOT_F + daman_row2.TOT_F
    df = df.drop([df.index[25]])
    df.iloc[24] = daman_row1
    
    return df

def get_state_to_state_code():
    df = get_dataframe_from_csv(cowin_file, drop_first_row=True)
    col_list = ["State_Code", "State"]
    df = df[col_list]
    df= df.drop_duplicates()
    df.State = df.State.str.lower()
    state_codes = df.State_Code.to_list()
    states = df.State.to_list()
    
    
    state_to_state_code = dict(
            zip(states, state_codes))
    return state_to_state_code

def get_state_name_to_state_num(state_census_df):
    
    state_num = state_census_df.State.to_list()
    state_name = state_census_df.Name.to_list()
    

    
    state_name_to_state_num = dict(
        zip(state_name, state_num))
    return state_name_to_state_num    

def clean_and_get_district_vaccine_df(cowin_df):
    
    df = cowin_df.drop(["S No","Cowin Key"], axis=1)
    df["State"] = df["State"].str.lower()
    
    #removing Telangana and Ladakh from cowin data
    df = df.loc[df['State']!='ladakh']
    df = df.loc[df['State']!='telangana']
    df = df.groupby(["State_Code","State","District_Key","District"]).sum().reset_index()
    return df

def clean_and_get_state_vaccine_df(district_cowin_df):
    df = district_cowin_df.groupby(["State_Code","State"]).sum().reset_index()
    return df

def get_district_output(district_cowin_df, district_census_df, state_name_to_state_num, rename_cowin_to_census):
    district_keys = district_cowin_df.District_Key.to_list()
    census_districts = district_census_df.Name.to_list()
    li = []
    for district_key in district_keys:
        if district_key == "KA_Bengaluru Rural":
            pass
        district_cowin_row = district_cowin_df[
            district_cowin_df.District_Key == district_key]
        
        cowin_district_name = district_cowin_row.District.values[0]
        if cowin_district_name in census_districts:
            district_name = cowin_district_name
        
        elif cowin_district_name in rename_cowin_to_census:
            district_name = rename_cowin_to_census[cowin_district_name]
            
        else:
            #print("Skipping district",cowin_district_name)
            continue
        
        
        state_name = district_cowin_row["State"].values[0]
        state_num = state_name_to_state_num[state_name.lower()]

        extract_census_df = district_census_df[district_census_df["State"] == state_num]
        
        district_row_census = extract_census_df[extract_census_df.Name == district_name]
        
        if len(district_row_census) == 0:
            # This case only happens for Balrampur.
            # no need to handle
            #print(district_name, state_num, state_name)
            continue
        
        vacc1_date = "14/08/2021.3"
        vacc2_date = "14/08/2021.4"
        
        vaccine1complete = district_cowin_row[vacc1_date].values[0]
        vaccine2complete = district_cowin_row[vacc2_date].values[0]
        
        
        total_population = district_row_census["TOT_P"].values[0]
        
        vaccine1ratio = vaccine1complete/total_population
        vaccine2ratio = vaccine2complete/total_population
        
        
        
        li.append([district_key, vaccine1ratio, vaccine2ratio])
        
    return li
        
 

def get_state_and_overall_output(state_cowin_df, state_census_df):
    li = []
    
    overall_vaccine1 = 0
    overall_vaccine2 = 0
    overall_total_population = 0
    
    states = state_cowin_df.State.values.tolist()
    for state in states:
        cowin_row = state_cowin_df[state_cowin_df.State == state]
        census_row = state_census_df[state_census_df.Name == state]
        vacc1_date = "14/08/2021.3"
        vacc2_date = "14/08/2021.4"
        state_code = cowin_row["State_Code"].values[0]
        vaccine1complete = cowin_row[vacc1_date].values[0]
        overall_vaccine1 += vaccine1complete
        vaccine2complete = cowin_row[vacc2_date].values[0]
        overall_vaccine2 += vaccine2complete
        
        total_population = census_row["TOT_P"].values[0]
        overall_total_population += total_population
        vaccine1ratio = vaccine1complete/total_population
        vaccine2ratio = vaccine2complete/total_population
        

        li.append([state_code, vaccine1ratio, vaccine2ratio])
    
    overall_vac1 = overall_vaccine1/overall_total_population
    overall_vac2 = overall_vaccine2/overall_total_population
    
    overall_li = [["India", overall_vac1, overall_vac2]]
    
    return li, overall_li


        
def get_rename_cowin_to_census():
    rename_df = get_dataframe_from_csv("replaceCensusName.csv")
    cowin_col = rename_df.cowin.to_list()
    census_col = rename_df.census.to_list()
    
    return dict(zip(cowin_col, census_col))
 

def write_to_csv(rows, filename, header_row):
    with open(filename,"w",newline="") as f:
        write = csv.writer(f)
        write.writerow(header_row)
        for row in rows:
            write.writerow(row)   
    
## MAIN
cowin_df = get_dataframe_from_csv(cowin_file, drop_first_row=True)
census_df = get_dataframe_from_excel(census_file)

district_census_df = clean_and_get_district_census_df(census_df)
district_cowin_df = clean_and_get_district_vaccine_df(cowin_df)

state_cowin_df = clean_and_get_state_vaccine_df(district_cowin_df)
state_census_df = clean_and_get_state_census_df(census_df)
state_to_state_code = get_state_to_state_code()
state_name_to_state_num = get_state_name_to_state_num(state_census_df)

rename_cowin_to_census = get_rename_cowin_to_census()
district_output = get_district_output(district_cowin_df, district_census_df, state_name_to_state_num, rename_cowin_to_census)
#write_to_csv(district_output, "")
district_output.sort(key=lambda x:x[1])

state_output, overall_output = get_state_and_overall_output(state_cowin_df, state_census_df)
state_output.sort(key=lambda x:x[1])
header = ["districtid","vaccinateddose1ratio", "vaccinateddose2ratio"]
write_to_csv(district_output, "output/district-vaccinated-dose-ratio.csv",header_row=header )
header = ["stateid","vaccinateddose1ratio", "vaccinateddose2ratio"]
write_to_csv(state_output, "output/state-vaccinated-dose-ratio.csv",header_row=header )
header = ["country","vaccinateddose1ratio", "vaccinateddose2ratio"]
write_to_csv(overall_output, "output/india-vaccinated-dose-ratio.csv",header_row=header )

##
