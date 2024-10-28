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
import sys

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

def read_parameters_variant_simple(file_path, parameters_name):
    data = {}  # This dictionary will store the extracted data

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Search for the parameter definition
    for parameter_name in parameters_name:
        for i, line in enumerate(lines):
            if f"param {parameter_name} default" in line:
                data[f'{parameter_name}'] = [line]
    return data#pd.DataFrame.from_dict(data, orient='index', columns=['Definition'])

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

def read_parameters_variant(file_path, parameter_name, number):
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
            if number == 5 and parameter_name == 'EmissionActivityRatio':
                tech_identifier = f"{identifiers[1]}/{identifiers[2]}"
            else:
                tech_identifier = f"{identifiers[1]}"
            
            # Extract years from the next line
            years_line = lines[i + 1].strip().split()
            # Remove ':=', if present
            if ':=' in years_line:
                years_line.remove(':=')
            years = [int(year) for year in years_line if year.isdigit()]
            
            # Extract values from the line after the years
            values_line = lines[i + 2].strip().split()
            
            # Ignore the first value (always 1) and convert the rest to float
            values = [float(value) for value in values_line[1:] if re.match(r'^-?\d+(?:\.\d+)?$', value)]
            
            # Ensure the lengths match before storing
            if len(values) == len(years):
                data[tech_identifier] = values
            else:
                print(f"Mismatch in lengths for {tech_identifier} in this {parameter_name}: {len(values)} values, {len(years)} years")
            
        # Stop processing if ';' is found
        if ';' in line:
            break

            # Move to the next block
            i += 3
        else:
            i += 1

    # Convert the dictionary to a pandas DataFrame
    return pd.DataFrame(data, index=years).T  # Transpose so that technologies are rows and years are columns

def read_parameters_variant_shorts(file_path, params_exeption):
    # Leer el archivo de texto
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Diccionario para almacenar los DataFrames
    data_dict = {}

    for param in params_exeption:
        # Buscar la definición del parámetro
        for i, line in enumerate(lines):
            if f"param {param} default" in line:
                # Extraer las columnas y valores
                columns_line = lines[i + 1].strip().split()
                values_line = lines[i + 2].strip().split()
                
                # Remover ':=' si está presente
                if ':=' in columns_line:
                    columns_line.remove(':=')
                if ':=' in values_line:
                    values_line.remove(':=')
                
                # Primer dato de la tercera fila es el identificador
                identifier = values_line[0]
                values = list(map(float, values_line[1:]))  # Convertir los valores a float
                
                # Crear el DataFrame
                df = pd.DataFrame([values], columns=columns_line, index=[identifier])
                
                # Agregar el DataFrame al diccionario
                data_dict[param] = df
                
                # Saltar al siguiente parámetro
                break

    return data_dict

def compare_parameters_without_data(list1, list2, list1_name, list2_name):
    differences = {}
    
    if list1 != list2:
        
        value_diffs = pd.DataFrame({
            'Index': 'list1_name',
            f'Value_in_{list1_name}': list1,
            f'Value_in_{list2_name}': list2
            })
        
        print(value_diffs)
        differences['value_difference'] = value_diffs
        
    
    
    return differences

def compare_dicts(main_dict, tolerance=0.01):
    # Get the keys of the inner dictionaries
    dict_keys = list(main_dict.keys())
    dict1_name, dict2_name = dict_keys[0], dict_keys[1]
    dict1, dict2 = main_dict[dict1_name], main_dict[dict2_name]
    differences = {}

    # Get all keys from both dictionaries
    all_keys = set(dict1.keys()).union(set(dict2.keys()))

    for key in all_keys:
        if isinstance(dict1.get(key), list) and isinstance(dict2.get(key), list):
            # Handle 'Parameters without data' comparison separately
            if key in dict1 and key in dict2:
                # print(dict1[key], dict2[key], dict1_name, dict2_name)
                # sys.exit(1)
                diff = compare_parameters_without_data(dict1[key], dict2[key], dict1_name, dict2_name)
                if diff:
                    differences[key] = diff
            continue  # Skip further processing for 'Parameters without data'

        differences[key] = {}

        if key not in dict1:
            differences[key]['missing_in_dict1'] = dict2[key]
        elif key not in dict2:
            differences[key]['missing_in_dict2'] = dict1[key]
        else:
            df1 = dict1[key]
            df2 = dict2[key]

            # Check if indices are the same
            index_diff_df1 = df1.index.difference(df2.index).tolist()
            index_diff_df2 = df2.index.difference(df1.index).tolist()
            if index_diff_df1 or index_diff_df2:
                index_diff = {}
                if index_diff_df1:
                    index_diff[f'In this file {dict1_name} not in this {dict2_name}'] = index_diff_df1
                if index_diff_df2:
                    index_diff[f'In this file {dict2_name} not in this {dict1_name}'] = index_diff_df2
                differences[key]['index_difference'] = index_diff

            # Check if columns are the same
            if not df1.columns.equals(df2.columns):
                differences[key]['column_difference'] = f'Column mismatch in {key} between {dict1_name} and {dict2_name}'

            # Compare values with tolerance
            diff_mask = (df1 - df2).abs() > tolerance
            if diff_mask.any().any():
                value_diffs = df1[diff_mask].stack().reset_index()
                value_diffs.columns = ['Index', 'Column', f'Value_in_{dict1_name}']
                value_diffs[f'Value_in_{dict2_name}'] = df2[diff_mask].stack().values

                differences[key]['value_difference'] = value_diffs

        # Remove empty difference entries
        if not differences[key]:
            del differences[key]

    return differences

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
    file_config_address = file_config_address = get_config_main_path(os.path.abspath(''))
    params = load_and_process_yaml(file_config_address + '\\' + 'MOMF_B1_exp_manager.yaml')
    
    
    
    # Variables
    file_config_address_t1_confection = file_config_address = get_config_main_path(os.path.abspath(''),'t1_confection')
    name_file = 'B1_Model_Structure.xlsx'  # Name of the Excel file
    name_sheet = 'parameters'  # Name of the sheet to read
    value_A_1 = 'parameter'  # First value in column A to read
    value_A_2 = 'number'  # Second value in column A to read
    
    # Read the Excel file
    df = pd.read_excel(file_config_address_t1_confection+name_file, sheet_name=name_sheet)
    
    # Parameters without data it write in the final of the txt file
    without_values_params = params['params_inputs_data']
    
    # Parameters have a write diferent write structure
    params_exeption = [
        "CapacityToActivityUnit",
        "OperationalLife",
        "YearSplit"
    ]

    # Generate Excel-style column names
    num_columns = df.shape[1]
    excel_column_names = generate_excel_column_names(num_columns)
    
    # Rename the columns of the DataFrame
    df.columns = excel_column_names
    
    # Filter data based on the values in column A
    sets_number_by_param = df[df['A'].isin([value_A_1, value_A_2])]

    # Search files to compare
    directory_path = 'Inputs_files'
    all_files = os.listdir(directory_path)
    txt_files = [file for file in all_files if file.endswith('.txt')]


    dict_files_data = {}
    for fil in txt_files:
        file_path = './' + directory_path + '/' + fil
        dict_params_data = {}
        
        # For parameters with data and whith this structure ([Region,*,*,*])
        for col in sets_number_by_param.columns:
            parameter = df[col][0]
            number = df[col][1]
            
            if number == 3:
                temp_param_data = read_parameters(file_path, parameter)
                temp_param_data = temp_param_data.sort_index()
                dict_params_data[parameter] = temp_param_data
            elif number == 4 or number ==5:
                temp_param_data = read_parameters_variant(file_path, parameter, number)
                temp_param_data = temp_param_data.sort_index()
                dict_params_data[parameter] = temp_param_data
    
        # For parameters without data
        without_values_params_data = read_parameters_variant_simple(file_path, without_values_params)
        
        # For parameters to have diferent wirte structure
        shorts_values_params_data = read_parameters_variant_shorts(file_path, params_exeption)
        
        # Add "shorts_values_params_data" into "dict_params_data" 
        # dict_params_data['Parameters without data'] = without_values_params_data
        dict_params_data.update(shorts_values_params_data) 
        # Delete inputs with size (0, 0) or (0, 1)
        keys_to_delete = [key for key, df in dict_params_data.items() if df.shape == (0, 0) or df.shape == (0, 1)]
        for key in keys_to_delete:
            del dict_params_data[key]
           
        # Add "without_values_params_data" into "dict_params_data"
        dict_params_data.update(without_values_params_data)
        
        # Update dict with data of the two files
        dict_files_data[fil.replace('.txt', '')] = dict_params_data

             
    # Compare data of both dictionaries with a tolerance of 0.01
    differences = compare_dicts(dict_files_data, tolerance=0.01)
    
    # Print final messages
    if differences == {}:
        print('The files are the same.')
    else:
        print('The files have differences, check variable "differences"')
        
    print('\nThe test process ran successful')
    
    
     
    
