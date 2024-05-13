# -*- coding: utf-8 -*-
"""
Created on Mon May 13 09:57:06 2024

@author: andreysava19
"""

# Code to verify missing technologies in various Excel files across different scenarios

import pandas as pd
import pickle
import os
import re


###############################################  Functions  ################################################################
# Function to load data and check for missing technologies
def find_missing_technologies(scenario, file_name):
    file_path = os.path.join(base_path, scenario, file_name)
    data = pd.read_csv(file_path)
    existing_technologies = set(data['TECHNOLOGY'].unique())
    missing_technologies = all_technologies - existing_technologies
    return missing_technologies

def check_tech_presence(missing_info, fleet_groups):
    for scenario, files in missing_info.items():
        for file_name, missing_techs in files.items():
            for tech_mother, tech_children in fleet_groups.items():
                if tech_mother not in missing_techs:  # Check if the mother technology is present
                    missing_children = [child for child in tech_children if child in missing_techs]
                    if missing_children:  # If there are missing child technologies, print information
                        print(f"Scenario: {scenario} \nParameter: {file_name}")
                        print(f"Mother technology present: {tech_mother}")
                        print(f"Missing child technologies: {missing_children}")
                        print("-------------------------------------------------")
                        
def check_mother_absence(missing_info, fleet_groups):
    for scenario, files in missing_info.items():
        for file_name, missing_techs in files.items():
            for tech_mother, tech_children in fleet_groups.items():
                present_children = [child for child in tech_children if child not in missing_techs]
                if present_children and tech_mother in missing_techs:  # If the mother is absent but children are not
                    print(f"Scenario: {scenario} \nParameter: {file_name}")
                    print(f"Child technologies present: {present_children}")
                    print(f"Mother technology absent: {tech_mother}")
                    print("-------------------------------------------------")


def read_parameters(file_path, parameter_name):
    data = {}  # This dictionary will store the extracted data
    years = []  # This list will store the years

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Search for the parameter definition
    start_index = -1
    for i, line in enumerate(lines):
        if f"param {parameter_name} default" in line:
            # Find the line containing the years, assumed to be two lines after the definition
            years_line = lines[i + 2]
            # Clean the years line and convert to a list of integers
            years = [int(year) for year in re.findall(r'\d{4}', years_line)]
            start_index = i + 3
            break
    
    if start_index == -1:
        print("The restriction was not found.")
        return pd.DataFrame()

    # Search and capture values for technologies until a ';' is found
    for line in lines[start_index:]:
        if line.strip() == ';':
            break
        elements = line.split()
        technology = elements[0]
        values = list(map(float, elements[1:]))  # Convert the values to float
        data[technology] = values

    # Convert the dictionary to a pandas DataFrame for easier manipulation
    return pd.DataFrame(data, index=years).T  # Transpose so that technologies are rows and years are columns

def compare_mother_children(parameter, results, fleet_groups, output_filename, i):
    comparison_results = {}  # This dictionary will store the comparison results

    if i == 0 :
        option = 'w'
    else:
        option = 'a'
    # Open the file to write the results
    with open(output_filename, option) as file:
        # Iterate over each mother technology in the group dictionary
        file.write(f"Results for {parameter}:\n")
        for tech_mother, children in fleet_groups.items():
            if tech_mother in results.index:
                comparison_results[tech_mother] = {}
                children_sum = pd.Series([0.0] * len(results.columns), index=results.columns)
                children_without_values = []

                for child in children:
                    if child in results.index:
                        # Check if the child technology has all values as zero
                        if results.loc[child].sum() == 0:
                            children_without_values.append(child)
                        children_sum += results.loc[child]
                    else:
                        # If the child technology is not in the index, it is considered to have no values
                        children_without_values.append(child)

                mother_values = results.loc[tech_mother]
                for year in results.columns:
                    if children_sum[year] > mother_values[year]:
                        comparison = "greater"
                    elif children_sum[year] < mother_values[year]:
                        comparison = "less"
                    else:
                        comparison = "equal"

                    comparison_results[tech_mother][year] = comparison

                # Write the results for the mother technology to the file
                file.write(f"   Results for {tech_mother}:\n")
                if children_without_values:
                    file.write(f"     Children without values: {children_without_values}\n")
                for year, result in comparison_results[tech_mother].items():
                    file.write(f"     {year}: {result}\n")
                file.write("-------------------------------------------------\n")

    return comparison_results

############################################################################################################################

if __name__ == '__main__':
    # Load mother and child technologies from the .pickle file
    with open('0_From_Confection/A-O_Fleet_Groups.pickle', 'rb') as file:
        fleet_groups = pickle.load(file)
    
    # List of all technology names (mother and children)
    all_technologies = set(fleet_groups.keys())  # Include mother technologies
    for techs in fleet_groups.values():
        all_technologies.update(techs)  # Include child technologies
    
    # Definition of scenarios and files to check
    scenarios = ['BAU', 'LTS']
    file_names = ['TotalTechnologyAnnualActivityUpperLimit', 'TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityLowerLimit']
    base_path = '1_Baseline_Modelling/'
      
    # Iteration over each scenario and file to find missing technologies
    missing_info = {}
    for scenario in scenarios:
        missing_info[scenario] = {}
        for file_name in file_names:
            missing = find_missing_technologies(scenario, file_name+'.csv')
            missing_info[scenario][file_name] = missing
    
    missing_info
  
    # If i want to know about what mothers o children techs are not there      
    # # Calling the function with the provided data
    # check_tech_presence(missing_info, fleet_groups)
    # # Calling the function with the provided data
    # check_mother_absence(missing_info, fleet_groups)


    # Define the path to the text file
    file_path = 'Futures\BAU\BAU_1\BAU_1.txt'
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
 
    # Define the path to the output file
    output_filename = 'comparison_results.txt'
    
    
    for i in range(len(file_names)):
        # # Take techs defined for the parameter
        result = read_parameters(file_path, file_names[i])  # Make sure parameter is defined
        if result is not None:
            comparison_results = compare_mother_children(file_names[i], result, fleet_groups, output_filename, i)
        else:
            print("No results available to compare.")
    
    

