# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 15:52:15 2021

@author: manjy
"""
import pandas as pd
import csv
cowin_file = "cowin_vaccine_data_districtwise.csv"
census_file = "DDW_PCA0000_2011_Indiastatedist.xlsx"


def get_dataframe_from_csv(filename, drop_first_row=False):

    # Adding skiprow here instead of dropping later
    # because this will automatically read data as int then.
    # Otherwise data below dates is matched as float.
    if drop_first_row:
        return pd.read_csv(filename, skiprows=[1], low_memory=False)

    else:
        return pd.read_csv(filename, low_memory=False)


def get_dataframe_from_excel(filename):

    df = pd.read_excel(filename, engine="openpyxl")
    return df


def clean_and_get_district_census_df(census_df):
    df = census_df[census_df['TRU'] == 'Total']

    df = df.loc[df['Level'] == 'DISTRICT']

    columns = ["State", 'Name', 'TRU', 'TOT_P', 'TOT_M', 'TOT_F']
    df = df[columns]


    # This is merging of dadra nagar haveli and daman and dui part
    index = df[df.State == 26].index
    df.at[index, "State"] = 25

    df["Name"] = df["Name"].str.strip()
    return df


def clean_and_get_state_census_df(census_df):

    df = census_df[census_df['TRU'] == 'Total']

    df = df.loc[df['Level'] == 'STATE']

    columns = ["State", 'Name', 'TRU', 'TOT_P', 'TOT_M', 'TOT_F']
    df = df[columns]

    df.Name = df.Name.str.lower()

    # removing Telangana and Ladakh from cowin data
    df = df.loc[df['State'] != 'ladakh']
    df = df.loc[df['State'] != 'telangana']

    # renaming nct of delhi to delhi in census data
    # renaming jammu & kashmir to jammu and kashmir in census data
    # renaming andaman & nicobar islands to andaman and nicobar islands
    df.loc[df.Name == "nct of delhi", "Name"] = "delhi"
    df.loc[df.Name == "andaman & nicobar islands",
           "Name"] = "andaman and nicobar islands"
    df.loc[df.Name == "jammu & kashmir", "Name"] = "jammu and kashmir"
    df.loc[df.Name == "dadra & nagar haveli",
           "Name"] = "dadra and nagar haveli and daman and diu"
    df.loc[df.Name == "daman & diu",
           "Name"] = "dadra and nagar haveli and daman and diu"

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
    df = df.drop_duplicates()
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

    df = cowin_df.drop(["S No", "Cowin Key"], axis=1)
    df["State"] = df["State"].str.lower()

    # removing Telangana and Ladakh from cowin data
    df = df.loc[df['State'] != 'ladakh']
    df = df.loc[df['State'] != 'telangana']
    df = df.groupby(["State_Code", "State", "District_Key",
                    "District"]).sum().reset_index()
    return df


def clean_and_get_state_vaccine_df(district_cowin_df):
    df = district_cowin_df.groupby(["State_Code", "State"]).sum().reset_index()
    return df


def get_district_output(district_cowin_df, district_census_df, state_name_to_state_num, rename_cowin_to_census):
    district_keys = district_cowin_df.District_Key.to_list()
    census_districts = district_census_df.Name.to_list()
    li = []
    for district_key in district_keys:
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

        male_date = "14/08/2021.5"
        female_date = "14/08/2021.6"

        males_vaccinated = district_cowin_row[male_date].values[0]
        females_vaccinated = district_cowin_row[female_date].values[0]
        ratio_vac = females_vaccinated/males_vaccinated

        total_male = district_row_census["TOT_M"].values[0]
        total_female = district_row_census["TOT_F"].values[0]
        ratio_pop = total_female/total_male

        ratio_of_ratio = ratio_vac/ratio_pop

        li.append([district_key, ratio_vac, ratio_pop, ratio_of_ratio])

    return li


def get_state_and_overall_output(state_cowin_df, state_census_df):
    li = []

    overall_total_male = 0
    overall_total_female = 0
    overall_males_vaccinated = 0
    overall_females_vaccinated = 0
    states = state_cowin_df.State.values.tolist()
    for state in states:
        cowin_row = state_cowin_df[state_cowin_df.State == state]
        census_row = state_census_df[state_census_df.Name == state]
        male_date = "14/08/2021.5"
        female_date = "14/08/2021.6"
        state_code = cowin_row["State"].values[0]
        males_vaccinated = cowin_row[male_date].values[0]
        overall_males_vaccinated += males_vaccinated
        females_vaccinated = cowin_row[female_date].values[0]
        overall_females_vaccinated += females_vaccinated
        ratio_vac = females_vaccinated/males_vaccinated

        total_male = census_row["TOT_M"].values[0]
        overall_total_male += total_male
        total_female = census_row["TOT_F"].values[0]
        overall_total_female += total_female
        ratio_pop = total_female/total_male
        ratio_of_ratio = ratio_vac/ratio_pop
        li.append([state_code, ratio_vac, ratio_pop, ratio_of_ratio])

    overall_ratio_vac = overall_females_vaccinated/overall_males_vaccinated
    overall_ratio_pop = overall_total_female/overall_total_male
    overall_ratio_of_ratio = overall_ratio_vac/overall_ratio_pop

    overall_li = [["India", overall_ratio_vac,
                   overall_ratio_pop, overall_ratio_of_ratio]]

    return li, overall_li


def get_rename_cowin_to_census():
    rename_df = get_dataframe_from_csv("replaceCensusName.csv")
    cowin_col = rename_df.cowin.to_list()
    census_col = rename_df.census.to_list()

    return dict(zip(cowin_col, census_col))


def write_to_csv(rows, filename, header_row):
    with open(filename, "w", newline="") as f:
        write = csv.writer(f)
        write.writerow(header_row)
        for row in rows:
            write.writerow(row)


# MAIN
cowin_df = get_dataframe_from_csv(cowin_file, drop_first_row=True)
census_df = get_dataframe_from_excel(census_file)

district_census_df = clean_and_get_district_census_df(census_df)
district_cowin_df = clean_and_get_district_vaccine_df(cowin_df)

state_cowin_df = clean_and_get_state_vaccine_df(district_cowin_df)
state_census_df = clean_and_get_state_census_df(census_df)
state_to_state_code = get_state_to_state_code()
state_name_to_state_num = get_state_name_to_state_num(state_census_df)

rename_cowin_to_census = get_rename_cowin_to_census()
district_output = get_district_output(
    district_cowin_df, district_census_df, state_name_to_state_num, rename_cowin_to_census)
district_output.sort(key=lambda x: x[3])
header = ["districtid", "vaccinationratio", "populationratio", "ratioofratios"]
write_to_csv(district_output,
             "output/district-vaccination-population-ratio.csv", header_row=header)

state_output, overall_output = get_state_and_overall_output(
    state_cowin_df, state_census_df)
state_output.sort(key=lambda x: x[3])
header = ["stateid", "vaccinationratio", "populationratio", "ratioofratios"]
write_to_csv(state_output,
             "output/state-vaccination-population-ratio.csv", header_row=header)

header = ["country", "vaccinationratio", "populationratio", "ratioofratios"]
write_to_csv(overall_output,
             "output/india-vaccination-population-ratio.csv", header_row=header)
##
