"""
- Modifying the neighbor districts data according to the districts found from the Covid19 portal
- Using File: cowin_vaccine_data_districtwise.csv
- Replaced Old Names with New Names and fixed districts that had mistakes in naming.
- Handled Repeating Districts : Bilaspur, Pratapgarh, Hamirpur, Bijapur, Balrampur, Aurangabad
- Note Bijapur from Karnataka is replaced with Vijayapura, because that is what the name in Cowin csv file.
- Removed Noklak, Niwari, Konkan District from neighbor-districts.json
- Final file generated: output/neighbor-districts-modified.json
"""

import json
import pandas as pd


def main():

    neighbor_district_dict = get_neighbor_json_dict()

    excel_df = get_vaccine_excel_list()

    final_neighbor_district_dict = update_neighbor_dict(
        neighbor_district_dict, excel_df)

    write_json_output("output/neighbor-districts-modified.json",
                      final_neighbor_district_dict)


def update_neighbor_dict(neighbor_district_dict, excel_df):
    """Modifies neighboring district dictionary

    Args:
        neighbor_district_dict (dict): neighboring district dict obtained by reading json
        excel_df (df): vaccine dataframe

    Returns:
        dict: modified neighboring district dict.
    """

    # -- getting dictionary for district to district_code
    district_code_list = excel_df["District_Key"].values.tolist()
    district_list = excel_df["District"].values.tolist()

    district_to_district_code_dict = convert_lists_to_dict(
        district_code_list, district_list)

    district_lower_to_upper = get_lower_to_upper_dict(district_list)

    # -- getting dictionary to rename names according to covid website name using excel sheet.
    replaceDistrictDf = get_replace_excel_list()
    covid_website_rename_list = replaceDistrictDf["covid-website"].values.tolist()
    neighbor_rename_list = replaceDistrictDf["neighbor"].values.tolist()
    neighbor_to_covid_rename_list = dict(
        zip(neighbor_rename_list, covid_website_rename_list))

    # self explanatory function names
    remove_instances_from_neighbor_dict(neighbor_district_dict)
    merge_instance_for_neighbor_dict(neighbor_district_dict)
    handle_repeating_districts(neighbor_district_dict)

    new_neighbor_dict = neighbor_district_dict.copy()
    ignore_list = ["konkan division", "niwari",
                   "noklak", "mumbai suburban", "mumbai city"]

    d2 = neighbor_district_dict.copy()
    # Iterating over district keys from json
    for key in d2:
        splitKey = key.split("/")
        splitKey = splitKey[0]
        if splitKey.find("_district") != -1:
            splitKey = splitKey.replace("_district", "")
            splitKey = splitKey.strip()
        splitKey = splitKey.replace("_", " ")

        if splitKey in ignore_list:
            #print("Ignoring this", splitKey)
            continue

        # If key is the one which has no need to be renamed and already matched
        # It will be present in this list
        if splitKey in district_lower_to_upper:
            finalKey = district_lower_to_upper[splitKey]
            replace_val = district_to_district_code_dict[finalKey]

            replace_instance_in_dict(replace_val, key, new_neighbor_dict)

        # Key is present in rename list
        elif splitKey in neighbor_to_covid_rename_list:
            splitKey = neighbor_to_covid_rename_list[splitKey]
            finalKey = district_lower_to_upper[splitKey]
            replace_val = district_to_district_code_dict[finalKey]

            replace_instance_in_dict(replace_val, key, new_neighbor_dict)

        # This case will only happen for repeating districts and already merged districts
        else:
            #print("SKIPPING THIS", splitKey)
            pass

    return new_neighbor_dict


def write_json_output(filename, dictionary):
    """converts the dictionary file to json file

    Args:
        filename (str): output file name. Relative path
        dictionary (dict)
    """
    with open(filename, 'w') as json_file:
        json.dump(dictionary, json_file,
                  indent=4, separators=(',', ':'), sort_keys=True)


def merge_instance_for_neighbor_dict(neighbor_district_dict):
    """Handling special case where mumbai needs to be merged

    Args:
        neighbor_district_dict (dict): Modified Neighbor dictionary
    """
    remove_instance_from_dict("mumbai_city/Q2341660", neighbor_district_dict)
    replace_instance_in_dict(
        "MH_Mumbai", "mumbai_suburban/Q2085374", neighbor_district_dict)


def handle_repeating_districts(neighbor_district_dict):
    """Handles districts with repeating names, and manually adding their district keys

    Args:
        neighbor_district_dict (dict): Modified neighbor dictionary.
    """
    replace_instance_in_dict(
        "HP_Bilaspur", "bilaspur/Q1478939", neighbor_district_dict)
    replace_instance_in_dict(
        "CT_Bilaspur", "bilaspur/Q100157", neighbor_district_dict)

    replace_instance_in_dict(
        "RJ_Pratapgarh", "pratapgarh/Q1585433", neighbor_district_dict)
    replace_instance_in_dict(
        "UP_Pratapgarh", "pratapgarh/Q1473962", neighbor_district_dict)

    replace_instance_in_dict(
        "HP_Hamirpur", "hamirpur/Q2086180", neighbor_district_dict)
    replace_instance_in_dict(
        "UP_Hamirpur", "hamirpur/Q2019757", neighbor_district_dict)

    replace_instance_in_dict(
        "KA_Vijayapura", "bijapur_district/Q1727570", neighbor_district_dict)
    replace_instance_in_dict(
        "CT_Bijapur", "bijapur/Q100164", neighbor_district_dict)

    replace_instance_in_dict(
        "UP_Balrampur", "balrampur/Q1948380", neighbor_district_dict)
    replace_instance_in_dict(
        "CT_Balrampur", "balrampur/Q16056268", neighbor_district_dict)

    replace_instance_in_dict(
        "BR_Aurangabad", "aurangabad/Q43086", neighbor_district_dict)
    replace_instance_in_dict(
        "MH_Aurangabad", "aurangabad/Q592942", neighbor_district_dict)


def remove_instances_from_neighbor_dict(neighbor_district_dict):
    """Removing unwanted entries from the dictionary

    Args:
        neighbor_district_dict (dictionary): modified dictionary after removing entries
    """
    remove_vals = ["konkan_division/Q6268840",
                   "niwari/Q63563797", "noklak/Q48731903"]
    for val in remove_vals:
        remove_instance_from_dict(val, neighbor_district_dict)


def get_neighbor_json_dict():
    with open("neighbor-districts.json", "r") as f:
        neighbor_district_dict = json.load(f)
    return neighbor_district_dict


def get_vaccine_excel_list():
    """gets the vaccine excel list and returns df

    Returns:
        dataframe: vaccine dataframe
    """
    col_list = ["District_Key", "District"]
    df = pd.read_csv("cowin_vaccine_data_districtwise.csv", usecols=col_list)

    return df


def get_replace_excel_list():
    """gets excel sheet that has renamed and corrected district names

    Returns:
        dataframe:
    """
    col_list = ["covid-website", "neighbor"]

    df = pd.read_csv("replaceName.csv", usecols=col_list)

    return df


def convert_list_to_lower_case(li):
    """converts all the elements of list with lower case

    Args:
        li (list): target List

    Returns:
        list: modified list
    """
    l2 = []
    for x in li:
        # print(x, type(x))
        if type(x) == "str":
            l2.append(x.lower())
    # li = [x.lower() for x in li]
    return li


def get_lower_to_upper_dict(li):
    """Makes a lookup dictionary which keys contains lower case values of list as key and value contains normal case values

    Args:
        li (list): target list

    Returns:
        dictionary: output dictionary
    """
    retDictionary = {}
    for key in li:
        try:
            lowerKey = key.lower()
            retDictionary[lowerKey] = key
        except:
            #print(f"bad key:{key}")
            pass

    return retDictionary


def replace_instance_in_dict(replace_val, search_val, dictionary):
    """Replaces a search string with replace string for all occurance of the search val in keys and value position

    Args:
        replace_val (str): value to be replaced with
        search_val (str): value to replace
        dictionary (dict): target dictionary
    """
    dictionary2 = dictionary.copy()
    for key in dictionary2:

        keys_neighbor = dictionary[key]

        if key == search_val:
            # replace the key
            dictionary[replace_val] = dictionary.pop(search_val)

        for i in range(len(keys_neighbor)):
            if keys_neighbor[i] == search_val:
                keys_neighbor[i] = replace_val
        # LIST IS IMMUTABLE, So it will be updated in dictionary.


def remove_instance_from_dict(remove_val, dictionary):
    """Removes all occurance of remove_val from dictionary, in both keys and values

    Args:
        remove_val (str): value to be removed
        dictionary (dict): target dictionary
    """
    dictionary2 = dictionary.copy()
    for key in dictionary2:

        keys_neighbor = dictionary[key]

        if key == remove_val:
            # replace the key
            del dictionary[key]

        li2 = keys_neighbor.copy()
        for i in range(len(li2)):
            if li2[i] == remove_val:
                keys_neighbor.remove(remove_val)
        # LIST IS IMMUTABLE, So it will be updated in dictionary.


def convert_lists_to_dict(district_code_list, district_list):
    """Converts two list into dict. First List is Key, second list is value

    Args:
        district_code_list (list): 
        district_list (list): 

    Returns:
        dictionary: returns converted dictionary
    """
    district_to_district_code_dict = dict(
        zip(district_list, district_code_list))

    return district_to_district_code_dict


if __name__ == "__main__":
    main()