# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 09:48:37 2021

@author: manjy
"""
import pandas as pd
import csv

cowin_excel_file_name = "cowin_vaccine_data_districtwise.csv"


def get_dataframe_from_excel(filename):
    """Reading CSV file

    Args:
        filename (str): name of the file

    Returns:
        DataFrame: Dataframe of the csv file
    """
    df = pd.read_csv(filename, low_memory=False)
    df = df.drop(0)  # Deleting the first useless row
    return df


def get_district_count(df, districtKey, date, dose):
    """Given District key, a date, and a dose, find the number of doses for that district on the day. 
       Sometimes a district might have 2 rows, this is handled

    Args:
        df (DataFrame): DataFrame row/rows for the district. 
        districtKey (str): Target District Key 
        date (DateTime): Target date
        dose (int): Dose can be either 1 or 2 depending on dose 1 or dose 2

    Returns:
        int: Returns the number of doses on that day for the district.
    """
    # This is how pandas is reading columns
    if dose == 1:
        date = f"{date}.3"
    elif dose == 2:
        date = f"{date}.4"

    df_dist_row = df[df["District_Key"] == districtKey]
    # Len(df_dist_row) is used to handle cases when there are more than one district key with same name
    # At most there can only be 2, so we are adding those 2.
    # EG) there are 2 entries for jaipur, so we are adding both entries.
    if len(df_dist_row) > 1:
        try:
            final_date_count = int(
                df_dist_row[date].iloc[0]) + int(df_dist_row[date].iloc[1])
        except:
            final_date_count = 0

    else:
        try:
            final_date_count = int(df_dist_row[date].iloc[0])
        except:
            final_date_count = 0

    return final_date_count


def get_district_range_count(df, districtKey, date_list, week_id, first_calc=False):
    """Given District key and range of dates, we find number of doses in this range, for both first and
    second dose

    Args:
        df (DataFrame): Target Dataframe
        districtKey (str): District key from the cowin dataframe
        date_list (list): List of datetime objects
        week_id (int): Week id
        first_calc (bool, optional): This will be true incase this is our first calculation, for handling cumulative data. Defaults to False.

    Returns:
        list: List of district key, its weekid and number of dose1 and dose 2.
    """
    start_date = date_list[0]
    end_date = date_list[-1]

    if first_calc == False:
        # Dose one calculation
        start_date_d1_count = get_district_count(
            df, districtKey, start_date, dose=1)
        end_date_d1_count = get_district_count(
            df, districtKey, end_date, dose=1)
        dose1_count = end_date_d1_count - start_date_d1_count
        # Dose two calculation
        start_date_d2_count = get_district_count(
            df, districtKey, start_date, dose=2)
        end_date_d2_count = get_district_count(
            df, districtKey, end_date, dose=2)
        # Subracting, because data is cumulitive.
        dose2_count = end_date_d2_count - start_date_d2_count

    else:
        # This is case for first calculation, since data is cumulative,
        # For first calculation, we don't need any subractions.
        dose1_count = get_district_count(df, districtKey, end_date, dose=1)
        dose2_count = get_district_count(df, districtKey, end_date, dose=2)

    return [districtKey, week_id, dose1_count, dose2_count]


def get_overall_weekly_district(df, districtList, date_list):
    """Driver code to get list of districts with their weekly dose counts

    Args:
        df (dataframe): Target dataframe containing all the data
        districtList (list): List of all the districts to be iterated
        date_list (list): List of all the dates, this will assist to get the date ranges.

    Returns:
        list: List in which each row contains district key, weekid and dose counts.
    """
    overall_week_district = []
    for districtKey in districtList:
        week_id = 1

        extract_df = df[df["District_Key"] == districtKey]

        week1flag = True
        for i in range(1, len(date_list), 7):
            week_dates = date_list[i-1:i+7]

            if week1flag == True:
                week1flag = False
                temp = get_district_range_count(
                    extract_df, districtKey, week_dates, week_id, first_calc=True)
            else:
                temp = get_district_range_count(
                    extract_df, districtKey, week_dates, week_id)

            overall_week_district.append(temp)
            week_id += 1

    return overall_week_district


def get_month_indices_from_date(date_list):
    """Generating start date and end dates for month

    Args:
        date_list (list): This is list of dates

    Returns:
        list: List of list, inner list contains two elements, start date and end date.
    """
    retList = []

    retList.append([0, date_list.index('14/02/2021')])

    month_num = 8  # 8 = august

    # Start from february
    for i in range(2, month_num):
        sDate = date_list.index(f"15/0{i}/2021")
        endDate = date_list.index(f"14/0{i+1}/2021")
        retList.append([sDate, endDate])

    return retList


def get_overall_month_district(df, districtList, date_list):
    """Driver code to get districts with their monthly dose count

    Args:
        df (dataframe): Target dataframe
        districtList (list): list of districts
        date_list (list): List of dates

    Returns:
        list: Final list containing monthly district dose counts.
    """
    overall_monthly_district = []
    month_dates_indices = get_month_indices_from_date(date_list)

    for districtKey in districtList:
        month_id = 1

        extract_df = df[df["District_Key"] == districtKey]
        month1flag = True
        for date_range in month_dates_indices:
            startIndex = date_range[0]
            endIndex = date_range[1]
            date_range = date_list[startIndex:endIndex+1]

            if month1flag == True:
                month1flag = False
                temp = get_district_range_count(
                    extract_df, districtKey, date_range, month_id, first_calc=True)
            else:
                temp = get_district_range_count(
                    extract_df, districtKey, date_range, month_id)

            overall_monthly_district.append(temp)
            month_id += 1
    return overall_monthly_district


def get_overall_complete_district(df, districtList, date_list):
    """Get dose 1 and dose 2 count till 15th aug for districts

    Args:
        df (dataframe): Target dataframe
        districtList (list): list of districts to be iterated
        date_list (list): List of date, we will be only interested in last date, because data is cumulitive

    Returns:
        list: List of districts and their dose counts overall.
    """
    overall_complete_district = []

    for districtKey in districtList:
        overall_id = 1

        extract_df = df[df["District_Key"] == districtKey]
        temp = get_district_range_count(
            extract_df, districtKey, date_list, overall_id, first_calc=True)

        overall_complete_district.append(temp)

    return overall_complete_district


def get_date_list(start_date, end_date):
    """Simply generates list of dates

    Args:
        start_date (str): Start date in str format yyyy-mm-dd
        end_date (str): end date in format yyyy-mm-dd

    Returns:
        list: List of datetime object
    """
    date_list = pd.date_range(start=start_date, end=end_date)

    date_list = [y.strftime("%d/%m/%Y") for y in date_list]
    return date_list


def write_to_csv(rows, filename, header_row):
    """Writes list to csv file

    Args:
        rows (list): Target list
        filename (str): Name of output file
        header_row (list): Header row.
    """
    with open(filename, "w", newline="") as f:
        write = csv.writer(f)
        write.writerow(header_row)
        for row in rows:
            write.writerow(row)


def get_state_weekly(overall_weekly_list):
    """Given districts weekly list, we combine it depending on state to get state weekly list

    Args:
        overall_weekly_list (list): output list from the get_overall_weekly_district() code

    Returns:
        dataframe: This returns dataframe instead of list, same format as district weekly list
    """
    for row in overall_weekly_list:
        state_code = row[0][0:2]
        row.insert(0, state_code)

    state_df = pd.DataFrame(overall_weekly_list, columns=[
                            "statecode", "district_key", "weekid", "dose1", "dose2"])

    state_df = state_df.groupby(["statecode", "weekid"]).sum().reset_index()

    return state_df


def get_state_monthly(overall_monthly_list):
    """Given Districts monthly list, we combine it depending on states to get state weekly list

    Args:
        overall_monthly_list (list): output list from the get_overall_month_district() function

    Returns:
        dataframe: same format as district monthly list, but merged for states.
    """
    for row in overall_monthly_list:
        state_code = row[0][0:2]
        row.insert(0, state_code)

    state_df = pd.DataFrame(overall_monthly_list, columns=[
                            "statecode", "district_key", "monthid", "dose1", "dose2"])

    state_df = state_df.groupby(["statecode", "monthid"]).sum().reset_index()

    return state_df


def get_state_overall(overall_complete_list):
    """given district overall list, we combine it depending on states to get state overall list

    Args:
        overall_complete_list (list): output list from the get_overall_complete_district() code

    Returns:
        dataframe: same format as district overall list, but merged for states.
    """
    for row in overall_complete_list:
        state_code = row[0][0:2]
        row.insert(0, state_code)

    state_df = pd.DataFrame(overall_complete_list, columns=[
                            "statecode", "district_key", "overallid", "dose1", "dose2"])

    state_df = state_df.groupby(["statecode", "overallid"]).sum().reset_index()

    return state_df


df = get_dataframe_from_excel(cowin_excel_file_name)

# Getting the district list
districtList = df["District_Key"]
districtListValCount = districtList.value_counts()
# Finding district whose district key repeat, example jaipur
repeatingDistrictCodeList = districtListValCount[districtListValCount > 1].index
districtList = districtList.unique()

date_list = get_date_list("2021-01-16", "2021-08-14")
# Driver codes, just invoking function calls and outputting it.
overall_weekly_list = get_overall_weekly_district(df, districtList, date_list)
write_to_csv(overall_weekly_list, "output/district-vaccinated-count-week.csv",
             ["districtid", "weekid", "dose1", "dose2"])

overall_monthly_list = get_overall_month_district(df, districtList, date_list)
write_to_csv(overall_monthly_list, "output/district-vaccinated-count-month.csv",
             ["districtid", "monthid", "dose1", "dose2"])

overall_complete_list = get_overall_complete_district(
    df, districtList, date_list)
write_to_csv(overall_complete_list, "output/district-vaccinated-count-overall.csv",
             ["districtid", "overallid", "dose1", "dose2"])
# Driver codes, just calling functions and outputting them
weekly_state_df = get_state_weekly(overall_weekly_list)
weekly_state_df = weekly_state_df.values.tolist()
monthly_state_df = get_state_monthly(overall_monthly_list)
monthly_state_df = monthly_state_df.values.tolist()
overall_state_df = get_state_overall(overall_complete_list)
overall_state_df = overall_state_df.values.tolist()

write_to_csv(weekly_state_df, "output/state-vaccinated-count-week.csv",
             ["stateid", "weekid", "dose1", "dose2"])
write_to_csv(monthly_state_df, "output/state-vaccinated-count-month.csv",
             ["stateid", "monthid", "dose1", "dose2"])
write_to_csv(overall_state_df, "output/state-vaccinated-count-overall.csv",
             ["stateid", "overallid", "dose1", "dose2"])
