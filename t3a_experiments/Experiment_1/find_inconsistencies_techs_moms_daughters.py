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
import sys


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
        print(f"The restriction {parameter_name} was not found.")
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

def read_parameters_variant(file_path, parameter_name):
    data = {}  # Dictionary to store extracted data
    years = []  # List to store the years

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Search for the parameter definition
    start_index = -1
    for i, line in enumerate(lines):
        if f"param {parameter_name} default" in line:
            start_index = i + 1
            break
    
    if start_index == -1:
        print(f"The parameter {parameter_name} definition was not found.")
        return pd.DataFrame()

    # Read blocks of data
    i = start_index
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('['):
            # Extract technologies and other identifiers
            identifiers = line.strip('[]').split(',')
            tech_identifier = f"{identifiers[1]}" # / {identifiers[-3]}"
            
            # Extract years from the next line
            years_line = lines[i + 1].strip().split()
            # Remove ':=', if present
            if ':=' in years_line:
                years_line.remove(':=')
            years = [int(year) for year in years_line if year.isdigit()]
            
            # Extract values from the line after the years
            values_line = lines[i + 2].strip().split()
            # Stop processing if ';' is found
            # if ';' in values_line:
            #     values_line.remove(';')
            
            # Ignore the first value (always 1) and convert the rest to float
            values = [float(value) for value in values_line[1:] if re.match(r'^-?\d+(?:\.\d+)?$', value)]
            
            # Ensure the lengths match before storing
            if len(values) == len(years):
                data[tech_identifier] = values
            else:
                print(f"Mismatch in lengths for {tech_identifier}: {len(values)} values, {len(years)} years")
            
        # Stop processing if ';' is found
        if ';' in line:
            break

            # Move to the next block
            i += 3
        else:
            i += 1

    # Convert the dictionary to a pandas DataFrame
    return pd.DataFrame(data, index=years).T  # Transpose so that technologies are rows and years are columns

def compare_mother_children(parameter, results, fleet_groups, output_filename, i):
    comparison_results = {}  # This dictionary will store the comparison results

    if i == 0 :
        option = 'w'
    else:
        option = 'a'
    # Open the file to write the results
    with open(output_filename, option) as file:
        if option == 'w':
            file.write("Check if children technologies are greater than mother technologies\n")
        # Iterate over each mother technology in the group dictionary
        if parameter != 'ResidualCapacity':
            file.write(f"\n\n\nResults for {parameter}:\n")
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
                    
                    if comparison == "greater":
                        comparison_results[tech_mother][year] = comparison + '      mother value: ' + str(mother_values[year]) + ',   children value: ' + str(children_sum[year])

                # Write the results for the mother technology to the file
                file.write(f"   Results for {tech_mother}:\n")
                file.write("     Children are _______ than mother tech\n")
                if children_without_values:
                    file.write(f"     Children without values: {children_without_values}\n") 
                for year, result in comparison_results[tech_mother].items():
                    file.write(f"     {year}: {result}\n")
                file.write("-------------------------------------------------\n")

    return comparison_results


def check_decreasing_values(data_frame, parameter_name, output_filename):
    """ Check if the values for each technology are strictly decreasing over the years. """
    # Dictionary to store technologies with non-decreasing issues
    non_decreasing_issues = {}

    # Iterate through each technology
    for tech, values in data_frame.iterrows():
        # Use pd.to_numeric to convert values to float and handle non-numeric data gracefully
        numeric_values = pd.to_numeric(values, errors='coerce')
        # Drop NaN values which might occur due to conversion or invalid data
        numeric_values = numeric_values.dropna()
        # Check if the series is strictly decreasing
        if not all(numeric_values.iloc[i] > numeric_values.iloc[i + 1] for i in range(len(numeric_values) - 1)):
            non_decreasing_issues[tech] = numeric_values.tolist()

    # Open output file for appending results
    with open(output_filename, 'a') as file:
        file.write("\n\n\n\n\n\n############################################################################################################################\n")
        file.write(f"Check if technologies have strictly decreasing values for {parameter_name}\n")
        # Print warning messages if any non-decreasing issues are found
        if non_decreasing_issues:
            file.write("Warning: The following technologies do not have strictly decreasing values:\n")
            for tech, vals in non_decreasing_issues.items():
                file.write(f"{tech}: {vals}\n")
        else:
            file.write("All values are strictly decreasing for all technologies.\n")

def check_any_decreasing_values(data_frame, parameter_name, output_filename):
    """ Check if there are any decreasing values from one year to the next across each technology. """
    # Dictionary to store technologies with any decreasing values found
    decreases_found = {}

    # Iterate through each technology
    for tech, values in data_frame.iterrows():
        # Convert values to numeric, handling non-numeric data gracefully
        numeric_values = pd.to_numeric(values, errors='coerce')
        # Drop NaN values which might occur due to conversion or invalid data
        numeric_values = numeric_values.dropna()
        # Initialize list to store decreases
        decreases = []
        # Iterate through each pair of consecutive years
        years = numeric_values.index
        for i in range(len(years) - 1):
            if numeric_values[years[i]] > numeric_values[years[i+1]]:
                decreases.append((years[i], numeric_values[years[i]], years[i+1], numeric_values[years[i+1]]))

        if decreases:
            decreases_found[tech] = decreases

    # Open output file for appending results
    with open(output_filename, 'a') as file:
        file.write("\n\n\n\n\n\n############################################################################################################################\n")
        file.write(f"Check for any decreasing values across technologies for {parameter_name}:\n")
        # Print results if any decreases are found
        if decreases_found:
            for tech, dec in decreases_found.items():
                file.write(f"{tech} has decreases at the following points:\n")
                for decrease in dec:
                    file.write(f"  From Year {decrease[0]}: {decrease[1]} to Year {decrease[2]}: {decrease[3]}\n")
                file.write("\n-------------------------------------------------\n")
        else:
            file.write("No decreases found across any technology.\n")
            file.write("\n-------------------------------------------------\n")


def compare_techs(upper_techs, lower_techs, output_filename, param_names):
    # Intersection of indices to ensure operations only on common rows
    common_indices = upper_techs.index.intersection(lower_techs.index)

    # Filter DataFrames to only include common rows
    filtered_upper = upper_techs.loc[common_indices]
    filtered_lower = lower_techs.loc[common_indices]

    # Perform the subtraction
    diff_df = filtered_upper - filtered_lower
    
    # Open output file for appending results
    with open(output_filename, 'a') as file:
        file.write("\n\n\n\n\n\n\n###########################################################################################################################")
        file.write(f"\nCheck if values of {param_names[0]} is greater than {param_names[1]}\n")
        # Iterate over each row to print the results
        for index, row in diff_df.iterrows():
            file.write(f"\nCheck technology: {index}")  # Initial index print
            negative_diff_exists = False  # Flag to check for negative differences
            for year, value in row.items():
                if value < 0:  # Only print if the difference is negative
                    file.write(f"\n  Negative difference in the year {year}: {value}")
                    negative_diff_exists = True
            if not negative_diff_exists:
                file.write("\n  All in order")  # Print if there are no negative differences
            file.write("\n-------------------------------------------------\n")

def check_demand_vs_capacity(df_mode_broad, parameter, spec_an_dem_techs, oar_techs, output_filename, param_names):
    """
    Function to check if param_names[0] is less than param_names[1] x param_names[2]
    for each grandmother technology.
    """
    # Open output file for appending results
    with open(output_filename, 'a') as file:
        file.write("\n\n\n\n\n\n\n###########################################################################################################################")
        file.write(f"\nCheck if values of {param_names[0]} are less than {param_names[1]} x {param_names[2]}\n")
        
        # Calculate the equation for each grandmother technology
        for grandmother in df_mode_broad.columns[1:]:
            mother_techs = df_mode_broad[df_mode_broad[grandmother] == 'x']['Techs/Demand']
            sum_products = 0
        
            for year in parameter.columns:
                for mother in mother_techs:
                    if mother in parameter.index and mother in oar_techs.index:
                        max_cap = parameter.loc[mother, year]
                        output_ratio = oar_techs.loc[mother, year]
                        sum_products += max_cap * output_ratio
        
                specified_demand = spec_an_dem_techs.loc[grandmother, year]
                # Check if the sum of products is greater than or equal to the specified demand
                if not sum_products >= specified_demand:
                    file.write(f"For {grandmother} in year {year}, the condition is NOT satisfied.\n")

def check_demand_vs_capacity_variant(parameter, spec_an_dem_techs, oar_techs, output_filename, param_names):
    """
    Function to check if param_names[0] is less than param_names[1] x param_names[2]
    for each common technology present in the indices of parameter, spec_an_dem_techs, and oar_techs.
    """
    # Find common indices (technologies)
    common_techs = parameter.index.intersection(spec_an_dem_techs.index).intersection(oar_techs.index)

    # Open output file for appending results
    with open(output_filename, 'a') as file:
        file.write("\n\n\n\n\n\n\n###########################################################################################################################")
        file.write(f"\nCheck if values of {param_names[0]} are less than {param_names[1]} x {param_names[2]}\n")

        # Calculate the equation for each common technology
        for tech in common_techs:
            for year in parameter.columns:
                max_cap = parameter.loc[tech, year]
                output_ratio = oar_techs.loc[tech, year]
                specified_demand = spec_an_dem_techs.loc[tech, year]
                product = max_cap * output_ratio * 31.56
                
                # Check if the product is greater than or equal to the specified demand
                if not product >= specified_demand:
                    file.write(f"For {tech} in year {year}, the condition is NOT satisfied.\n")


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
    file_names = ['TotalTechnologyAnnualActivityUpperLimit', 'TotalTechnologyAnnualActivityLowerLimit', 'TotalAnnualMaxCapacity','ResidualCapacity']
    base_path = '1_Baseline_Modelling/'
      
    # # Iteration over each scenario and file to find missing technologies
    # missing_info = {}
    # for scenario in scenarios:
    #     missing_info[scenario] = {}
    #     for file_name in file_names:
    #         missing = find_missing_technologies(scenario, file_name+'.csv')
    #         missing_info[scenario][file_name] = missing
    
    # missing_info
    
    # ###### TEST 1 ######
    # If i want to know about what mothers o children techs are not there      
    # # Calling the function with the provided data
    # check_tech_presence(missing_info, fleet_groups)
    # # Calling the function with the provided data
    # check_mother_absence(missing_info, fleet_groups)


    ###########################################################################################################################
    # Define the path to the text file
    for scen in scenarios:
        specified_case = False # if you want other file outside of the Executables or futures folders
        
        # Specify the directory path here
        dir_bau_files = './Futures/' + scen
    
        # List all entries in the directory
        all_entries = os.listdir(dir_bau_files)
    
        # Filter only the directories
        folders = [entry for entry in all_entries if os.path.isdir(os.path.join(dir_bau_files, entry))]
      
        
        for f in folders:
            future = f
            
            if future == 0 and not specified_case:
                file_path = f'Executables\{future}\{future}.txt'
            elif specified_case:
                file_path = f'{scen}_{future}.txt'
            else:
                file_path = f'Futures\{scen}\{future}\{future}.txt'
            
            with open(file_path, 'r') as file:
                lines = file.readlines()
         
            # Define the path to the output file
            if not os.path.exists('tests_results'):
                os.makedirs('tests_results')
            output_filename = f'tests_results/comparison_results_{scen}_{future}.txt'
            
            
            for i in range(len(file_names)):
                # Take techs defined for the parameter
                result = 0
                result = read_parameters(file_path, file_names[i])  # Make sure parameter is defined
        
                if result is not None:
                    # ###### TEST 2 ######
                    # Check mother - children diferrences
                    comparison_results = compare_mother_children(file_names[i], result, fleet_groups, output_filename, i)
                    if file_names[i] == "TotalAnnualMaxCapacity":
                        # ###### TEST 3 ######
                        # Check for decreasing values specifically for this parameter
                        check_any_decreasing_values(result, file_names[i], output_filename)
                else:
                    print("No results available to compare.")
                   
                # Only to check the technologies have this parameter
                if file_names[i] == 'TotalAnnualMaxCapacity':
                    tech_param_check = result
                    
                if file_names[i] == 'TotalTechnologyAnnualActivityUpperLimit':
                    upper_techs = result
                elif file_names[i] == 'TotalTechnologyAnnualActivityLowerLimit':
                    lower_techs = result
                
                if file_names[i] == 'TotalAnnualMaxCapacity':
                    maxcapa_techs = result
                elif file_names[i] == 'ResidualCapacity':
                    resicapa_techs = result
                
            # ###### TEST 4 ######
            # Check if values of TotalTechnologyAnnualActivityLowerLimit 
            # is greater than TotalTechnologyAnnualActivityUpperLimit
            compare_techs(upper_techs, lower_techs, output_filename, ['TotalTechnologyAnnualActivityLowerLimit', 'TotalTechnologyAnnualActivityUpperLimit'])
            
            
            # ###### TEST 5 ######
            # Check if values of ResidualCapacity 
            # is greater than TotalAnnualMaxCapacity
            compare_techs(maxcapa_techs, resicapa_techs, output_filename, ['ResidualCapacity', 'TotalAnnualMaxCapacity'])
            
            ###########################################################################################################################
            
            # Load the Excel file
            file_path_modes_transp = '0_From_Confection/A-I_Classifier_Modes_Transport.xlsx'
            
            # Load the 'Mode_Broad' sheet
            df_mode_broad = pd.read_excel(file_path_modes_transp, sheet_name='Mode_Broad')
            
            
            # Take techs defined for the parameter
            ta_maxcap_techs = read_parameters(file_path, 'TotalAnnualMaxCapacity')  # Make sure parameter is defined
            spec_an_dem_techs = read_parameters(file_path, 'SpecifiedAnnualDemand')  # Make sure parameter is defined
            oar_techs = read_parameters_variant(file_path, 'OutputActivityRatio')  # Make sure parameter is defined
            lower_limit = read_parameters(file_path, 'TotalTechnologyAnnualActivityLowerLimit')  # Make sure parameter is defined
            capfac_techs = read_parameters_variant(file_path, 'CapacityFactor')  # Make sure parameter is defined
            
            # TEST 6
            # Check if SpecifiedAnnualDemand is less than TotalAnnualMaxCapacity x OutputActivityRatio
            check_demand_vs_capacity(df_mode_broad, ta_maxcap_techs, spec_an_dem_techs, oar_techs, output_filename, ['SpecifiedAnnualDemand', 'TotalAnnualMaxCapacity', 'OutputActivityRatio'])
            
            # TEST 7
            # Check if SpecifiedAnnualDemand is less than TotalTechnologyAnnualActivityLowerLimit x OutputActivityRatio
            check_demand_vs_capacity(df_mode_broad, lower_limit, spec_an_dem_techs, oar_techs, output_filename, ['SpecifiedAnnualDemand', 'TotalTechnologyAnnualActivityLowerLimit', 'OutputActivityRatio'])
            
            # TEST 8
            # Check if TotalTechnologyAnnualActivityLowerLimit is less than TotalAnnualMaxCapacity x CapacityFactor x 31.56
            check_demand_vs_capacity_variant(ta_maxcap_techs, lower_limit, capfac_techs, output_filename, ['TotalTechnologyAnnualActivityLowerLimit', 'TotalAnnualMaxCapacity', 'CapacityFactor'])