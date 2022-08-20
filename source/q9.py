# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 18:57:18 2021

@author: manjy
"""


import pandas as pd
import csv
from datetime import datetime, timedelta
import math
cowin_file = "cowin_vaccine_data_districtwise.csv"
census_file = "DDW_PCA0000_2011_Indiastatedist.xlsx"


def get_dataframe_from_csv(filename, drop_first_row=False):
    """Gets dataframe from csv

    Args:
        filename (str): Name of the csv file
        drop_first_row (bool, optional): Parameter on whether to drop the first row. Defaults to False.

    Returns:
        DataFrame: Returns the dataframe of csv
    """

    # Adding skiprow here instead of dropping later
    # because this will automatically read data as int then.
    # Otherwise data below dates is matched as float.
    if drop_first_row:
        return pd.read_csv(filename, skiprows=[1], low_memory=False)

    else:
        return pd.read_csv(filename, low_memory=False)


def get_dataframe_from_excel(filename):
    """get dataframe from excel file

    Args:
        filename (str): filename with .xlsx extension

    Returns:
        dataframe: returns corresponding dataframe
    """
    df = pd.read_excel(filename, engine="openpyxl")
    return df


def write_to_csv(rows, filename, header_row):
    """Write list to csv

    Args:
        rows (list): Target list to be outputted
        filename (str): Output file name with extension
        header_row (list): Header of the csv
    """
    with open(filename, "w", newline="") as f:
        write = csv.writer(f)
        write.writerow(header_row)
        for row in rows:
            write.writerow(row)


def clean_and_get_state_population(census_df):
    """Cleaning of the census df

    Args:
        census_df (DataFrame): Target Dataframe

    Returns:
        DataFrame: Returns cleaned dataframe
    """
    # Filtering only total population
    df = census_df[census_df['TRU'] == 'Total']
    # Filtering states
    df = df.loc[df['Level'] == 'STATE']

    # Extracting columns
    columns = ['Name', 'TRU', 'No_HH', 'TOT_P', 'TOT_M', 'TOT_F']
    df = df[columns]

    # string Lowering all the state names
    df["Name"] = df["Name"].str.lower()

    # Renaming weirdly named states
    df.loc[df.Name == "andaman & nicobar islands",
           "Name"] = "andaman and nicobar islands"
    df.loc[df.Name == "jammu & kashmir", "Name"] = "jammu and kashmir"
    df.loc[df.Name == "nct of delhi", "Name"] = "delhi"
    # merging daman and dui with dadra .
    df.loc[df.Name == "dadra & nagar haveli",
           "Name"] = "dadra and nagar haveli and daman and diu"
    df.loc[df.Name == "daman & diu",
           "Name"] = "dadra and nagar haveli and daman and diu"

    df = df.groupby("Name").sum().reset_index()

    return df


def clean_and_get_state_vaccine_data(cowin_df):
    """Cleaning of the vaccination dataframe

    Args:
        cowin_df (DataFrame): Target DataFrame

    Returns:
        DataFrame: cleaned dataframe
    """
    # Removing redundant columns
    df = cowin_df.drop(
        ["S No", "District_Key", "Cowin Key", "District"], axis=1)
    df = df.groupby(["State_Code", "State"]).sum().reset_index()
    df["State"] = df["State"].str.lower()

    # removing Telangana and Ladakh from cowin data
    df = df.loc[df['State'] != 'ladakh']
    df = df.loc[df['State'] != 'telangana']

    return df


def get_last_week_vacc_rate(cowin_row):
    """Gets vaccine rates for last week of a cowin district row

    Args:
        cowin_row (DataFrame): Dataframe row of Length 1 containing target district 

    Returns:
        int: Returns the amount of people vaccinated in last week
    """
    start_day_min_one = "07/08/2021.3"
    end_day = "14/08/2021.3"

    return int(cowin_row[end_day]) - int(cowin_row[start_day_min_one])


def get_vaccinated_population(cowin_row):
    """Given a state row of vaccination data, get total number of first dose vaccinated

    Args:
        cowin_row ([type]): [description]

    Returns:
        [type]: [description]
    """
    last_day_at_least_one_vacc = "14/08/2021.3"
    return int(cowin_row[last_day_at_least_one_vacc])


def get_total_population(cowin_row, census_df):
    """Getting the total population of a state using census df

    Args:
        cowin_row (DataFrame): A single row of dataframe containing target state
        census_df (DataFrame): DataFrame of State population data

    Returns:
        int: population of the state
    """
    census_row = census_df[census_df.Name == cowin_row.State]

    return int(census_row["TOT_P"])


def get_final_vacc_date(remaining_population, last_week_vacc_rate, from_date):
    # program to get final vaccination data given remaining population and vaccination rate

    day_rate = last_week_vacc_rate / 7
    num_of_days = math.ceil(remaining_population / day_rate)

    from_date = datetime.strptime(from_date, "%d/%m/%Y")
    final_date = from_date + timedelta(days=num_of_days)
    str_final_date = final_date.strftime("%d/%m/%Y")

    return str_final_date


def get_final_list(cowin_df, census_df):
    """Driver program to get the final list containing last vaccination date prediction

    Args:
        cowin_df (DataFrame): 
        census_df (DataFrame): 

    Returns:
        list: List containing states and their vaccination date prediction
    """

    li = []
    for i in range(len(cowin_df)):
        cowin_row = cowin_df.iloc[i]
        state_code = cowin_row["State_Code"]
        last_week_vacc_rate = get_last_week_vacc_rate(cowin_row)

        vaccinated_population = get_vaccinated_population(cowin_row)

        total_population = get_total_population(cowin_row, census_df)
        remaining_population = total_population - vaccinated_population

        vacc_date = get_final_vacc_date(
            remaining_population, last_week_vacc_rate, from_date="14/08/2021")

        li.append([state_code, remaining_population,
                  last_week_vacc_rate, vacc_date])

    return li


def main():
    cowin_df = get_dataframe_from_csv(cowin_file, drop_first_row=True)

    census_df = get_dataframe_from_excel(census_file)

    # Extract
    census_df = clean_and_get_state_population(census_df)
    cowin_df = clean_and_get_state_vaccine_data(cowin_df)

    final_list = get_final_list(cowin_df, census_df)
    header_row = ["stateid", "populationleft", "rateofvaccination", "date"]
    write_to_csv(final_list, "output/complete-vaccination.csv", header_row)


if __name__ == "__main__":
    main()
