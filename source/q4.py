"""
- Finding Wave 1 and wave 2 peaks
- 
- Considering Date Range from 15th March 2020 to 14th August 2021
- Output file names: district-peaks.csv, state-peaks.csv, india-peaks.csv
- Assumption:   1) Since we are smoothening the data, we can find the peak in a given duration by simply
                    querying the max of the duration. We will find wave 1 peak as max of 2020, and wave 2
                    peak as max of 2021.

                2) Since we don't have access to district keys and I wanted to use as much data as possible
                I made generated District Key at run time. I cross checked that for every district, given
                state code and district name, its district key = <State_Code>_<District_Name>. So we need 
                not have district key avaiable. It can be generated at runtime and it will match with official
                naming schemes. 
"""

import pandas as pd
import csv
import time
start = time.time()


def get_covid_excel_dataframe():
    """Get covid excel file as dataframe

    Returns:
        DataFrame: Covid dataframe
    """
    col_list = ["Date", "State", "District", "Confirmed"]
    df = pd.read_csv("districts.csv", usecols=col_list)

    return df


def get_cowin_excel_dataframe():
    """Get vaccine excel file as dataframe

    Returns:
        DataFrame: Vaccine DataFrame
    """
    col_list = ["State_Code", "State"]

    df = pd.read_csv("cowin_vaccine_data_districtwise.csv",
                     skiprows=[1], usecols=col_list)

    return df


def get_cases(district, date_range, df):
    """Given a district name, and a dataframe and a date range, find number of new cases in this district

    Args:
        district (str): Name of district
        date_range (list): This is list of dates, \
        usually we will be only interested in first and last date because its cumulitive
        df (DataFrame): This is the target dataframe

    Returns:
        int: Returns the count of cases.
    """
    minusOneofStartDate = date_range[0]
    lastDate = date_range[-1]

    minusOneofStartDateRow = df[(df["District"] == district) & (
        df["Date"] == minusOneofStartDate)]
    lastDateRow = df[(df["Date"] == lastDate) & (df["District"] == district)]
    try:
        minusOneofStartDateCumCases = minusOneofStartDateRow["Confirmed"].iloc[0]
        lastDateCumCases = lastDateRow["Confirmed"].iloc[0]

        return lastDateCumCases - minusOneofStartDateCumCases

    except:
        # This is case when we have NA value for first date in data frame.
        if len(lastDateRow["Confirmed"].values) > 0:
            # Simply return the cumulitive value, this is case of first occurance.
            return lastDateRow["Confirmed"].iloc[0]

        else:
            return 0


def week_range_generator(length):
    """Generates range of week indices

    Args:
        length (int): Number of weeks

    Returns:
        list: List of week indices
    """
    thurs_list = []
    sun_list = []
    combine_list = []
    week_one = [0, 6]
    sun_list.append(week_one)
    combine_list.append(week_one)
    for i in range(length+1):
        thurs = [(7*(i+1) - 4), (7*(i+1) + 3)]
        sundays = [(7*(i+1) - 1), (7*(i+1))+6]
        thurs_list.append(thurs)
        sun_list.append(sundays)

        combine_list.append(thurs)
        combine_list.append(sundays)
    return thurs_list, sun_list, combine_list


def get_weekly_district_cases(week_combined, state_district_list, date_ranges, state_to_state_code, df):
    """This is top level function which iterates through districts to get district cases for the date ranges

    Args:
        week_combined (list): This is list containing indices for the week start and week ends.
        state_district_list (list): List of districts
        date_ranges (list): List of all dates
        state_to_state_code (dict): This is a lookup dictionary to get state code
        df (DataFrame): This is the target dataframe with all data

    Returns:
        list: Returns list of districts with weekly covid case counts.
    """
    x = []
    for state_district in state_district_list:
        timeid = 1

        state = state_district[0]
        district = state_district[1]

        extract_df = df[df["State"] == state]
        extract_df = df[df["District"] == district]
        # print(district)
        state_code = state_to_state_code[state]
        district_code = f"{state_code}_{district}"

        for week in week_combined:
            cases = get_cases(
                district, date_ranges[week[0]:week[1]+1], extract_df)

            temp = [state_code, district_code, timeid, cases]
            x.append(temp)
            timeid += 1

        # not considering last week, because only one day
    return x


def write_to_csv(rows, filename, header_row):
    """Writes list to csv

    Args:
        rows (list): List containing rows to output to csv
        filename (str): Name of output file
    """
    with open(filename, "w", newline="") as f:
        write = csv.writer(f)
        write.writerow(header_row)
        for row in rows:
            write.writerow(row)


def get_state_code_lookup():
    """Generates state lookup dictionary

    Returns:
        dict: state lookup
    """
    df = get_cowin_excel_dataframe()
    df = df.drop_duplicates()

    state_codes = df.State_Code.to_list()
    states = df.State.to_list()

    state_to_state_code = dict(
        zip(states, state_codes))
    return state_to_state_code


def get_clean_covid_df(covid_df):
    """Removes all the unwanted information from covid dataframe and returns data which we will be working on

    Args:
        covid_df (dataframe): Target Covid vaccine dataframe

    Returns:
        DataFrame: Cleaned and modified dataframe
    """
    unwanted_districts = [
        'Airport Quarantine', 'BSF Camp', 'Capital Complex', 'Evacuees', 'Foreign Evacuees',
        'Italians', 'Other Region', 'Other State', 'Others',
        'Railway Quarantine', 'State Pool', 'Unassigned', 'Unknown'
    ]

    for value in unwanted_districts:
        covid_df = covid_df.drop(covid_df[covid_df['District'] == value].index)

    covid_df["Date"] = pd.to_datetime(covid_df["Date"])

    covid_df = covid_df.drop(
        covid_df[covid_df["Date"] > pd.Timestamp(2021, 8, 14)].index)

    return covid_df


def get_date_range():
    """Simple Date range generater

    Returns:
        list: Returns a list of date.
    """
    start_date = pd.Timestamp(2020, 3, 15)
    end_date = pd.Timestamp(2021, 8, 14)

    return pd.date_range(start=start_date, end=end_date)


def month_range_generator():
    """Simple month start date and end date generator

    Returns:
        list: List containing rows. Row contains 2 entries, one is start date of month and one is end date
    """
    li = []

    for i in range(3, 12):
        start = pd.Timestamp(2020, i, 14)
        end = pd.Timestamp(2020, i+1, 14)
        li.append([start, end])

    start = pd.Timestamp(2020, 12, 14)
    end = pd.Timestamp(2021, 1, 14)
    li.append([start, end])

    for i in range(1, 8):
        start = pd.Timestamp(2021, i, 14)
        end = pd.Timestamp(2021, i+1, 14)
        li.append([start, end])

    return li


def get_monthly_district_cases(state_district_list, state_to_state_code, df):
    """Gets monthly case counts for every district

    Args:
        state_district_list (list): List of all districts
        state_to_state_code (dict): State code lookup given state name
        df (DataFrame): Target dataframe containing all data

    Returns:
        list: Returns list containing case counts for every district monthly.
    """
    month_range = month_range_generator()

    x = []
    for state_district in state_district_list:
        timeid = 1
        state = state_district[0]
        district = state_district[1]

        extract_df = df[df["State"] == state]
        extract_df = df[df["District"] == district]
        # print(district)
        state_code = state_to_state_code[state]
        district_code = f"{state_code}_{district}"

        for month in month_range:
            cases = get_cases(district, month, extract_df)

            temp = [state_code, district_code, timeid, cases]
            x.append(temp)
            timeid += 1

    return x


def get_overall_district_cases(state_district_list, state_to_state_code, df):
    """Driver code to get list of cases district wise

    Args:
        state_district_list (list): List of all districts
        state_to_state_code (dict): Lookup to get statecode
        df (DataFrame): DataFrame containing the data

    Returns:
        list: Output list containing districts and their number of cases
    """
    x = []

    start = pd.Timestamp(2020, 3, 14)
    end = pd.Timestamp(2021, 8, 14)
    overall_range = [start, end]
    for state_district in state_district_list:
        timeid = 1
        state = state_district[0]
        district = state_district[1]

        extract_df = df[df["State"] == state]
        extract_df = df[df["District"] == district]
        # print(district)
        state_code = state_to_state_code[state]
        district_code = f"{state_code}_{district}"

        cases = get_cases(district, overall_range, extract_df)

        temp = [district_code, timeid, cases]
        x.append(temp)
        timeid += 1

    return x


def get_district_peaks(df_weekly_district_cases, df_monthly_district_cases):
    """Peak prediction code. Returns 2 weekly and monthly peak per district. Approach is to find max weekid/monthid
        Since data is already smoothened, we are bound to get peaks by simply finding max.

    Args:
        df_weekly_district_cases (DataFrame): Contains weekly overlapped cases of districts
        df_monthly_district_cases (DataFrame): Contains monthly cases of districts.

    Returns:
        list: contains weekly and monthly peaks for district
    """

    # week index 84 is roughly around end of 2020.

    # Filtering data into wave 1 period and wave 2 period by approxing that wave 1 occurs in 2020,
    # And Wave 2 occurs in 2021.
    df_weekly_district_wave1 = df_weekly_district_cases[df_weekly_district_cases.weekid <= 84]
    df_weekly_district_wave2 = df_weekly_district_cases[df_weekly_district_cases.weekid > 84]

    # Similarly, dividing monthly dataframe too
    df_monthly_district_wave1 = df_monthly_district_cases[df_monthly_district_cases.monthid <= 9]
    df_monthly_district_wave2 = df_monthly_district_cases[df_monthly_district_cases.monthid > 9]

    # Get list of districts
    district_keys = df_weekly_district_cases.districtid.unique()

    x = []
    # Iterating over every district.
    for district_key in district_keys:
        row_weekly_district_wave1 = df_weekly_district_wave1[
            df_weekly_district_wave1.districtid == district_key]
        row_weekly_district_wave2 = df_weekly_district_wave2[
            df_weekly_district_wave2.districtid == district_key]

        index_max = row_weekly_district_wave1.cases.idxmax()
        wave1_weekid = row_weekly_district_wave1.loc[index_max].weekid

        index_max = row_weekly_district_wave2.cases.idxmax()
        wave2_weekid = row_weekly_district_wave2.loc[index_max].weekid

        row_monthly_wave1 = df_monthly_district_wave1[df_monthly_district_wave1.districtid == district_key]
        row_monthly_wave2 = df_monthly_district_wave2[df_monthly_district_wave2.districtid == district_key]

        index_max = row_monthly_wave1.cases.idxmax()
        wave1_monthid = row_monthly_wave1.loc[index_max].monthid

        index_max = row_monthly_wave2.cases.idxmax()
        wave2_monthid = row_monthly_wave2.loc[index_max].monthid

        x.append([district_key, wave1_weekid, wave2_weekid,
                 wave1_monthid, wave2_monthid])

    return x


def get_state_peaks(df_weekly_state_cases, df_monthly_state_cases):
    # Week 84 is roughly around end of 2020
    df_weekly_state_wave1 = df_weekly_state_cases[df_weekly_state_cases.weekid <= 84]
    df_weekly_state_wave2 = df_weekly_state_cases[df_weekly_state_cases.weekid > 84]

    # month id 9 is roughly around december- january month
    df_monthly_state_wave1 = df_monthly_state_cases[df_monthly_state_cases.monthid <= 9]
    df_monthly_state_wave2 = df_monthly_state_cases[df_monthly_state_cases.monthid > 9]

    stateids = df_weekly_state_cases.stateid.unique()
    x = []

    for stateid in stateids:
        row_weekly_wave1 = df_weekly_state_wave1[df_weekly_state_wave1.stateid == stateid]
        row_weekly_wave2 = df_weekly_state_wave2[df_weekly_state_wave2.stateid == stateid]

        index_max = row_weekly_wave1.cases.idxmax()
        wave1_weekid = row_weekly_wave1.loc[index_max].weekid

        index_max = row_weekly_wave2.cases.idxmax()
        wave2_weekid = row_weekly_wave2.loc[index_max].weekid

        row_monthly_wave1 = df_monthly_state_wave1[df_monthly_state_wave1.stateid == stateid]
        row_monthly_wave2 = df_monthly_state_wave2[df_monthly_state_wave2.stateid == stateid]

        index_max = row_monthly_wave1.cases.idxmax()
        wave1_monthid = row_monthly_wave1.loc[index_max].monthid

        index_max = row_monthly_wave2.cases.idxmax()
        wave2_monthid = row_monthly_wave2.loc[index_max].monthid

        x.append([stateid, wave1_weekid, wave2_weekid,
                 wave1_monthid, wave2_monthid])

    return x


def get_overall_peaks(df_weekly_overall_cases, df_monthly_overall_cases):
    # Week 84 is roughly around end of 2020
    row_weekly_wave1 = df_weekly_overall_cases[df_weekly_overall_cases.weekid <= 84]
    row_weekly_wave2 = df_weekly_overall_cases[df_weekly_overall_cases.weekid > 84]
    
    # month id 9 is roughly around december- january month
    row_monthly_wave1 = df_monthly_overall_cases[df_monthly_overall_cases.monthid <= 9]
    row_monthly_wave2 = df_monthly_overall_cases[df_monthly_overall_cases.monthid > 9]

    index_max = row_weekly_wave1.cases.idxmax()
    wave1_weekid = row_weekly_wave1.loc[index_max].weekid

    index_max = row_weekly_wave2.cases.idxmax()
    wave2_weekid = row_weekly_wave2.loc[index_max].weekid

    index_max = row_monthly_wave1.cases.idxmax()
    wave1_monthid = row_monthly_wave1.loc[index_max].monthid

    index_max = row_monthly_wave2.cases.idxmax()
    wave2_monthid = row_monthly_wave2.loc[index_max].monthid

    return [["India", wave1_weekid, wave2_weekid, wave1_monthid, wave2_monthid]]


# Initial code
covid_df = get_covid_excel_dataframe()
state_to_state_code = get_state_code_lookup()
covid_df = get_clean_covid_df(covid_df)
date_range = get_date_range()
state_dist_df = covid_df[["State", "District"]].drop_duplicates()
stateDistrictList = state_dist_df.values.tolist()


thurs_list, sun_list, week_combined = week_range_generator(
    int(len(date_range)/7))
# Dropping extra week which goes ahead of 15th august
week_combined.pop(-1)
week_combined.pop(-1)
week_combined.pop(-1)
last_week = week_combined.pop(-1)


# Getting Weekly Cases
weekly_district_cases = get_weekly_district_cases(
    week_combined, stateDistrictList, date_range, state_to_state_code, covid_df)
header_col = ["stateid", "districtid", "weekid", "cases"]
#weekly_district_cases.insert(0, header_col)
df_weekly_district_cases = pd.DataFrame(
    weekly_district_cases, columns=header_col)
df_weekly_state_cases = df_weekly_district_cases.groupby(
    ["stateid", "weekid"]).sum().reset_index()
df_weekly_overall_cases = df_weekly_state_cases.groupby(
    ["weekid"]).sum().reset_index()
# -------
# Getting monthly cases
monthly_district_cases = get_monthly_district_cases(
    stateDistrictList, state_to_state_code, covid_df)
header_col = ["stateid", "districtid", "monthid", "cases"]
df_monthly_district_cases = pd.DataFrame(
    monthly_district_cases, columns=header_col)
df_monthly_state_cases = df_monthly_district_cases.groupby(
    ["stateid", "monthid"]).sum().reset_index()
df_monthly_overall_cases = df_monthly_state_cases.groupby(
    ["monthid"]).sum().reset_index()
# -------


district_peaks = get_district_peaks(
    df_weekly_district_cases, df_monthly_district_cases)
write_to_csv(district_peaks, "output/district-peaks.csv",
             ["districtid", "wave1 weekid", "wave2 weekid", "wave1 monthid", "wave2 monthid"])
state_peaks = get_state_peaks(df_weekly_state_cases, df_monthly_state_cases)
write_to_csv(state_peaks, "output/state-peaks.csv",
             ["stateid", "wave1 weekid", "wave2 weekid", "wave1 monthid", "wave2 monthid"])
overall_peaks = get_overall_peaks(
    df_weekly_state_cases, df_monthly_overall_cases)
write_to_csv(overall_peaks, "output/india-peaks.csv",
             ["country", "wave1 weekid", "wave2 weekid", "wave1 monthid", "wave2 monthid"])
