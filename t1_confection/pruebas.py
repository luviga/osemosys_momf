# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 12:45:07 2024

@author: ClimateLeadGroup
"""

import pandas as pd
import string
import re
import yaml
import os

# Function to generate Excel-style column names
def generate_excel_column_names(num_columns):
    alphabet = string.ascii_uppercase
    column_names = []
    
    for i in range(num_columns):
        name = ''
        while i >= 0:
            name = alphabet[i % 26] + name
            i = i // 26 - 1
        column_names.append(name)
    
    return column_names

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

def get_config_main_path(full_path, base_folder='config_main_files'):
    # Split the path into parts
    parts = full_path.split(os.sep)
    
    # Find the index of the target directory 'osemosys_momf'
    target_index = parts.index('osemosys_momf') if 'osemosys_momf' in parts else None
    
    # If the directory is found, reconstruct the path up to that point
    if target_index is not None:
        base_path = os.sep.join(parts[:target_index + 1])
    else:
        base_path = full_path  # If not found, return the original path
    
    # Append the specified directory to the base path
    appended_path = os.path.join(base_path, base_folder) + os.sep
    
    return appended_path

def load_and_process_yaml(path):
    """
    Load a YAML file and replace the specific placeholder '${year_apply_discount_rate}' with the year specified in the file.
    
    Args:
    path (str): The path to the YAML file.
    
    Returns:
    dict: The updated data from the YAML file where the specific placeholder is replaced.
    """
    with open(path, 'r') as file:
        # Load the YAML content into 'params'
        params = yaml.safe_load(file)

    # Retrieve the reference year from the YAML file and convert it to string for replacement
    reference_year = str(params['year_apply_discount_rate'])

    # Function to recursively update strings containing the placeholder
    def update_strings(obj):
        if isinstance(obj, dict):
            return {k: update_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [update_strings(element) for element in obj]
        elif isinstance(obj, str):
            # Replace the specific placeholder with the reference year
            return obj.replace('${year_apply_discount_rate}', reference_year)
        else:
            return obj

    # Update all string values in the loaded YAML structure
    updated_params = update_strings(params)

    return updated_params

if __name__ == '__main__':
    # Read yaml file with parameterization
    file_config_address = get_config_main_path(os.path.abspath(os.path.join('..', '..')))
    params = load_and_process_yaml(file_config_address + '\\' + 'MOMF_B1_config.yaml')
    
    
    
    # Variables
    nombre_archivo = 'B1_Model_Structure.xlsx'  # Name of the Excel file
    nombre_hoja = 'parameters'  # Name of the sheet to read
    value_A_1 = 'parameter'  # First value in column A to read
    value_A_2 = 'number'  # Second value in column A to read
    
    # Read the Excel file
    df = pd.read_excel(nombre_archivo, sheet_name=nombre_hoja)
    
    # Generate Excel-style column names
    num_columns = df.shape[1]
    excel_column_names = generate_excel_column_names(num_columns)
    
    # Rename the columns of the DataFrame
    df.columns = excel_column_names
    
    # Filter data based on the values in column A
    sets_number_by_param = df[df['A'].isin([value_A_1, value_A_2])]
    
    
    
    file_path = 'C:\\Users\\ClimateLeadGroup\\Desktop\\CLG_repositories\\osemosys_momf\\t1_confection\\Executables\\BAU_0\\BAU_0.txt'
    parameter_name = 'TotalAnnualMaxCapacity'
    num_values = 3  # or 2, 4, 5 depending on the case
    
    TotalAnnualMaxCapacity = read_parameters(file_path, parameter_name)
    
    parameter_name = 'OutputActivityRatio'
    OutputActivityRatio = read_parameters_variant(file_path, parameter_name)
    
    parameter_name = 'SpecifiedDemandProfile'
    SpecifiedDemandProfile = read_parameters_variant(file_path, parameter_name)
    
    parameter_name = 'VariableCost'
    VariableCost = read_parameters_variant(file_path, parameter_name)