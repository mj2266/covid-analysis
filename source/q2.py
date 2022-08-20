"""
- Outputting Edge list format csv file.
- Using file output/neighbor-districts-modified.json
- Output File Name: edge-graph.csv
"""

import csv
import json

def main():
    neighbor_dict = get_neighbor_json_dict()
    
    # Using dictionary for lookup to get O(1) lookup time
    neighbor_already_covered_lookup = {}
    edge_list = []

    for key in neighbor_dict.keys():

        update_edge_list(key, neighbor_dict[key], edge_list, neighbor_already_covered_lookup)

    write_to_csv(edge_list)

def write_to_csv(edge_list):
    """Write the list to csv file

    Args:
        edge_list (list): edge list
    """
    with open("output/edge-graph.csv","w",newline="") as f:
        write = csv.writer(f)
        for edge in edge_list:
            write.writerow(edge)


def update_edge_list(start_vertex, end_vertex_list, edge_list, neighbor_already_covered_lookup):
    """We will have start vertex, and a list containing its end vertex, we check whether the edge is already covered and add it to edge list

    Args:
        start_vertex (str): Start vertex
        end_vertex_list (list): List of vertex neighbor to start vertex
        edge_list (list): This is the edge list that is maintained
        neighbor_already_covered_lookup (dict): This will help avoid duplicate entries
    """
    for end_vertex in end_vertex_list:
        check_string = f"{start_vertex}|{end_vertex}"
        update_string = f"{end_vertex}|{start_vertex}"
        if not(check_string in neighbor_already_covered_lookup):
            edge = [start_vertex, end_vertex]
            edge_list.append(edge)
            neighbor_already_covered_lookup[update_string] = True



def get_neighbor_json_dict():
    """Reads the json file to dictionary

    Returns:
        dict: json equivalent dictionary
    """
    with open("output/neighbor-districts-modified.json", "r") as f:
        neighbor_district_dict = json.load(f)
    return neighbor_district_dict


if __name__ == "__main__":
    main()