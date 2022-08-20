# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 16:35:02 2021

@author: manjy
"""
import pandas as pd
import csv
import math
cowin_excel_file_name = "cowin_vaccine_data_districtwise.csv"


def get_dataframe_from_excel(filename):
    df = pd.read_csv(filename, skiprows=[1], low_memory=False)
    return df


def get_district_count(df, districtKey, date, vaccine):
    if vaccine == "covaxin":
        date = f"{date}.8"
    elif vaccine == "covishield":
        date = f"{date}.9"

    df_dist_row = df[df["District_Key"] == districtKey]
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


def get_district_range_count(df, districtKey, date_list):

    covaxin_count, covishield_count = 0, 0

    covaxin_count = get_district_count(
        df, districtKey, date_list[-1], vaccine="covaxin")
    covishield_count = get_district_count(
        df, districtKey, date_list[-1], vaccine="covishield")

    try:
        ratio = covishield_count / covaxin_count
    except:
        ratio = math.inf

    return [districtKey, covishield_count, covaxin_count, ratio]


def get_overall_district(df, districtList, date_list):
    overall_district = []
    for districtKey in districtList:

        extract_df = df[df["District_Key"] == districtKey]
        temp = get_district_range_count(extract_df, districtKey, date_list)

        overall_district.append(temp)

    return overall_district


def get_state_count(state_row, date, vaccine):
    if vaccine == "covaxin":
        date = f"{date}.8"
    elif vaccine == "covishield":
        date = f"{date}.9"

    try:
        final_count = int(state_row[date])
    except:
        final_count = 0

    return final_count


def get_overall_state(df, date_list):
    overall_state = []

    state_df = df.groupby(by=["State_Code"]).sum()

    state_codes_list = state_df.index
    for state in state_codes_list:
        covishield_count, covaxin_count = 0, 0
        state_row = state_df.loc[state]

        covishield_count = get_state_count(
            state_row, date_list[-1], vaccine="covishield")
        covaxin_count = get_state_count(
            state_row, date_list[-1], vaccine="covaxin")

        if covaxin_count == 0:
            ratio = math.inf
        else:
            ratio = covishield_count/covaxin_count
        temp = [state, covishield_count, covaxin_count, ratio]
        overall_state.append(temp)
    return overall_state


def get_overall_country(state_list):

    covishield_count, covaxin_count = 0, 0
    for row in state_list:

        covishield_count += row[1]
        covaxin_count += row[2]

    ratio = covishield_count/covaxin_count
    return ["INDIA", covaxin_count, covishield_count, ratio]


def get_date_list(start_date, end_date):
    date_list = pd.date_range(start=start_date, end=end_date)

    date_list = [y.strftime("%d/%m/%Y") for y in date_list]
    return date_list


def write_to_csv(rows, filename, header_row):
    with open(filename, "w", newline="") as f:
        write = csv.writer(f)
        write.writerow(header_row)
        for row in rows:
            # this is specific to this code
            # We are ignoring covaxin and covishield count
            # only output id and ratio
            new_row = [row[0], row[-1]]
            write.writerow(new_row)


df = get_dataframe_from_excel(cowin_excel_file_name)

districtList = df["District_Key"]
districtListValCount = districtList.value_counts()
repeatingDistrictCodeList = districtListValCount[districtListValCount > 1].index
districtList = districtList.unique()

date_list = get_date_list("2021-01-16", "2021-08-14")

overall_district_list = get_overall_district(df, districtList, date_list)
#write_to_csv(overall_district_list, "vaccinated-type-ratio.csv")

overall_state_list = get_overall_state(df, date_list)
#write_to_csv(overall_state_list, "vaccine-type-ratio.csv")

overall_country_list = get_overall_country(overall_state_list)
final_list = [overall_country_list] + \
    overall_state_list + overall_district_list

# overall_monthly_list = get_overall_month_district(df, districtList, date_list)
overall_district_list.sort(key= lambda x:x[3])
header_rows = ["districtid", "vaccineratio"]
write_to_csv(overall_district_list,
             "output/district-vaccine-type-ratio.csv", header_rows)
header_rows = ["stateid", "vaccineratio"]
overall_state_list.sort(key= lambda x:x[3])
write_to_csv(overall_state_list,
             "output/state-vaccine-type-ratio.csv", header_rows)
header_rows = ["country", "vaccineratio"]
write_to_csv([overall_country_list],
             "output/india-vaccine-type-ratio.csv", header_rows)
# overall_complete_list = get_overall_complete_district(df, districtList, date_list)
# write_to_csv(overall_complete_list, "vaccinated-count-overall2.csv")
