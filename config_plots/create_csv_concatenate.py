# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 18:37:25 2024

@author: andreysava
"""

import os
import pandas as pd
import yaml
from copy import deepcopy
import sys
import shutil
import numpy as np

def get_config_main_path(full_path, base_folder='config_plots'):
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


def calculate_npv(dataframe, new_column_name, parametervalue_column, rod, year_column="YEAR", output_csv_r=0, output_csv_year=0):
    # Verify that the necessary columns exist in the DataFrame
    if parametervalue_column not in dataframe.columns or year_column not in dataframe.columns:
        raise ValueError("The specified columns do not exist in the DataFrame")
    
    # Verify that the value column contains numeric data
    if not np.issubdtype(dataframe[parametervalue_column].dtype, np.number):
        raise ValueError(f"The column {parametervalue_column} does not contain numeric values")

    # Calculate the NPV and add the new column to the DataFrame
    dataframe[new_column_name] = dataframe.apply(
        lambda row: round(row[parametervalue_column] / ((1 + output_csv_r / 100) ** (float(row[year_column]) - output_csv_year)), rod),
        axis=1
    )


def calculate_npv_filtered(dataframe, new_column_name, parametervalue_column, rod, year_column="YEAR", filter_dict=None, output_csv_r=0, output_csv_year=0):
    # Initialize the new column with null values
    dataframe[new_column_name] = np.nan

    # Verify that the necessary columns exist in the DataFrame
    if parametervalue_column not in dataframe.columns or year_column not in dataframe.columns:
        raise ValueError("The specified columns do not exist in the DataFrame")
    
    # Verify that the value column contains numeric data
    if not np.issubdtype(dataframe[parametervalue_column].dtype, np.number):
        raise ValueError(f"The column {parametervalue_column} does not contain numeric values")
    
    # Verify that filter_dict has only one key and get its value
    if filter_dict and len(filter_dict) == 1:
        filter_column = list(filter_dict.keys())[0]
        filter_values = filter_dict[filter_column]
        
        # Verify that the filter column exists in the DataFrame
        if filter_column not in dataframe.columns:
            raise ValueError("The specified filter column does not exist in the DataFrame")
        
        # Iterate over the rows of the DataFrame
        for index, row in dataframe.iterrows():
            # Verify if the value in the filter column is in the filter values
            if row[filter_column] in filter_values:
                # Verify if the value in parametervalue_column is numeric
                if pd.notna(row[parametervalue_column]):
                    npv = row[parametervalue_column] / ((1 + output_csv_r / 100) ** (float(row[year_column]) - output_csv_year))
                    dataframe.at[index, new_column_name] = round(npv, rod)


if __name__ == '__main__':    
    # Read yaml file with parameterization
    file_config_address = get_config_main_path(os.path.abspath(''), 'config_main_files')

    params = load_and_process_yaml(file_config_address + '\\' + 'MOMF_B1_exp_manager.yaml')
        
    sets_corrects = deepcopy(params['sets_otoole'])
    sets_corrects.insert(0,'Parameter')
    sets_corrects.append('VALUE')
    
    sets_csv = ['YEAR', 'TECHNOLOGY', 'FUEL', 'EMISSION']
    sets_csv_temp = deepcopy(sets_csv)
    sets_csv_temp.insert(0,'Parameter')
    sets_csv_temp.append('VALUE')
    set_no_needed = [item for item in params['sets_otoole'] if item not in sets_csv]
    
    if params['model']=='MOMF':
        dict_scen_folder_unique = {}
        for scen in params['scens']:
            if params['tier']=='1':
                dir_tier = params['tier1_dir'].replace('..\\','')
                dir_tier = get_config_main_path(os.path.abspath(''), dir_tier + '\\' + scen)
                dir_tier = dir_tier = dir_tier.replace('\\', '\\\\')
                dir_tier = dir_tier = dir_tier.replace('\\', '/')
                all_files_internal = os.listdir(dir_tier)
                dict_scen_folder_unique[f'{scen}'] = [i for i in all_files_internal if scen in i]
            elif params['tier']=='3a':
                dir_tier = params['tier3a_dir'].replace('..\\\\','')
                dir_tier = get_config_main_path(os.path.abspath('').replace('\\config_plots',''), dir_tier + '\\' + scen)
                dir_tier = dir_tier = dir_tier.replace('\\\\', '/')
                dir_tier = dir_tier = dir_tier.replace('\\', '/')
                all_files_internal = os.listdir(dir_tier)
                dict_scen_folder_unique[f'{scen}'] = [i for i in all_files_internal if scen in i]
        count = 0
        for scen in dict_scen_folder_unique:
            for case in dict_scen_folder_unique[f'{scen}']:
                # Select folder path
                if params['tier']=='1':
                    tier_dir = params['tier1_dir'] + '\\\\' + case + params['outputs']
                elif params['tier']=='3a':
                    tier_dir = params['tier3a_dir'] + '\\\\' + scen + '\\\\' + case + params['outputs']
    
                # 1st try
                tier_dir = tier_dir.replace('/','\\\\')
                tier_dir = tier_dir.replace('..\\\\','')
                
                tier_dir = tier_dir.replace('\\\\', '\\')
                # sys.exit()
                tier_dir = get_config_main_path(os.path.abspath(''), tier_dir)
                if os.path.exists(tier_dir):
                    csv_file_list = os.listdir(tier_dir)
                    
                    df_list = []
                    
                    parameter_list = []
                    parameter_dict = {}
                    
                    if params['vis_dir'] in csv_file_list:
                        csv_file_list.remove(f'{params["vis_dir"]}')
                    
                    for f in csv_file_list:
                        
                        local_df = pd.read_csv(tier_dir + '/' + f)
                        
                        
                        # Delete columns of sets do not use in otoole config yaml
                        columns_check = [column for column in local_df.columns if column in sets_corrects]
                        local_df = local_df[columns_check]
    
                        
                        local_df['Parameter'] = f.split('.')[0]
                        parameter_list.append(f.split('.')[0])
                        parameter_dict.update({parameter_list[-1]: local_df})
                        
                        df_list.append(local_df)
                    columns_check.insert(0,'Parameter')
                    df_all = pd.concat(df_list, ignore_index=True, sort=False)
                    df_all = df_all[ sets_csv_temp ]
                    file_df_dir = params["excel_data_file_dir"].replace('../','')
                    out_quick = params['outputs'].replace('/','')
                    file_df_dir = tier_dir.replace(f'{out_quick}\\', '')
                    df_all.to_csv(f'{file_df_dir}\\Data_plots_{case[-1]}.csv')
                    
                    # 3rd try
                    # Assuming parameter_list and parameter_dict are defined
                    # Initialize df_all_2 with the first DataFrame to ensure the dimension columns are set
                    first_param = parameter_list[0]
                    df_all_3 = pd.DataFrame()
                    df_all_3 = df_all[df_all['Parameter'] == first_param]
                    df_all_3 = df_all_3.rename(columns={'VALUE': first_param})
                    df_all_3 = df_all_3.drop('Parameter', axis=1)
                    df_all_3 = df_all_3.drop(columns=[col for col in df_all_3.columns if col in set_no_needed], errors='ignore')
                    df_all_3 = df_all_3.assign(**{col: 'nan' for col in sets_csv if col not in df_all_3.columns})
    
                    
                    
                    # Iterate over the remaining parameters and merge their respective DataFrames on the dimension columns
                    for p in parameter_list[1:]:  # Skip the first parameter since it's already added
                        local_df_3 = df_all[df_all['Parameter'] == p]
                        local_df_3 = local_df_3.rename(columns={'VALUE': p})
                        local_df_3 = local_df_3.drop('Parameter', axis=1)
                        local_df_3 = local_df_3.drop(columns=[col for col in local_df_3.columns if col in set_no_needed], errors='ignore')
                        local_df_3 = local_df_3.assign(**{col: 'nan' for col in sets_csv if col not in local_df_3.columns})
                        count+=1
    
                        df_all_3 = pd.merge(df_all_3, local_df_3, on=sets_csv, how='outer')
                    

                    # Add NPV columns
                    parameters_reference = params['parameters_reference']
                    parameters_news = params['parameters_news']
                    
                    for k in range(len(parameters_reference)):
                        if parameters_reference[k] == 'AnnualTechnologyEmissionPenaltyByEmission':
                            parameter_filter = {'EMISSION':params['this_combina']}
                            calculate_npv_filtered(df_all_3, parameters_news[k], parameters_reference[k], params['round_#'], 'YEAR', parameter_filter, output_csv_r=params['output_csv_r']*100, output_csv_year=params['output_csv_year'])
                        else:
                            calculate_npv(df_all_3, parameters_news[k], parameters_reference[k], params['round_#'], 'YEAR', output_csv_r=params['output_csv_r']*100, output_csv_year=params['output_csv_year'])
                                        
                    
                    # The 'outer' join ensures that all combinations of dimension values are included, filling missing values with NaN
                    #df_all_3.to_csv(f'{file_df_dir}/Data_Output_{case[-1]}.csv')
                    #print(case)
                    df_all_3.to_csv(f'{file_df_dir}/{case}_Output.csv')
    
                    # Delete Outputs folder with otoole csvs files
                    if params['del_files']:
                        outputs_otoole_csvs = file_df_dir + out_quick
                        if os.path.exists(outputs_otoole_csvs):
                            shutil.rmtree(outputs_otoole_csvs)
                else:
                    continue
                
                
                
                
                
'''
output_csv_r = params['output_csv_r']*100
output_csv_year = params['output_csv_year']

npv = parametervalue/((1 + output_csv_r/100)**(float(this_year) - output_csv_year))
'''