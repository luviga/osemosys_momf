# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 17:18:23 2024

@author: luisf
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import sys
import numpy as np
from copy import deepcopy

def filter_and_select_columns(df, initial_column, additional_columns):
    # Filter rows where the initial column does not have NaN values
    filtered_df = df[df[initial_column].notna()]
    
    # Select the additional columns first and then the initial column
    columns_to_select = additional_columns + [initial_column]
    new_df = filtered_df[columns_to_select].copy()
    
    # Add the 'Parameter' column with the name of the initial column
    new_df['Parameter'] = initial_column
    
    # Rename the initial column to 'values'
    new_df.rename(columns={initial_column: 'VALUE'}, inplace=True)
    
    # Reorder columns to place 'Parameter' as the first column
    columns_order = ['Parameter'] + additional_columns + ['VALUE']
    new_df = new_df[columns_order]
    
    return new_df


def find_first_difference(df1, df2, columns_to_remove):
    # Remove specified columns from both DataFrames
    df1 = df1.drop(columns=columns_to_remove, errors='ignore')
    df2 = df2.drop(columns=columns_to_remove, errors='ignore')
    
    # Determine the minimum number of rows and columns to compare
    min_rows = min(len(df1), len(df2))
    min_cols = min(len(df1.columns), len(df2.columns))
    
    # Iterate over the rows and columns to find the first difference
    for i in range(min_rows):
        for col in df1.columns[:min_cols]:
            if df1.iloc[i][col] != df2.iloc[i][col]:
                return i, col
    
    # Check if the number of rows or columns is different
    if len(df1) != len(df2):
        return "Different number of rows"
    if len(df1.columns) != len(df2.columns):
        return "Different number of columns"
    
    # If no difference is found
    return None, None

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
            updated_dict = {}
            for k, v in obj.items():
                updated_key = update_strings(k)
                updated_value = update_strings(v)
                updated_dict[updated_key] = updated_value
            return updated_dict
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
    file_config_address = get_config_main_path(os.path.abspath(''), 'config_plots')
    params = load_and_process_yaml(file_config_address + '\\' + 'plots_config.yaml')
        
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
                all_files_internal = os.listdir(params['tier1_dir'])
                dict_scen_folder_unique[f'{scen}_0'] = [i for i in all_files_internal if scen in i]
                info_filename = params['tier1_dir'] + '/' + params['info_filename']
            elif params['tier']=='3a':
                all_files_internal = os.listdir(params['tier3a_dir'] + '/' + scen)
                dict_scen_folder_unique[f'{scen}'] = [i for i in all_files_internal if scen in i]
                info_filename = params['tier3a_dir'] + '/' + params['info_filename']
        count = 0
        for scen in dict_scen_folder_unique:
            
            for case in dict_scen_folder_unique[f'{scen}']:
                scen = scen.replace('_0', '')
                # Select folder path
                if params['tier']=='1':
                    tier_dir = params['tier1_dir'] + '/' + case
                    tier = params['tier1_dir']
                elif params['tier']=='3a':
                    tier_dir = params['tier3a_dir'] + '/' + scen + '/' + case 
                    tier = params['tier3a_dir']
    
                # 1st try
                csv_file_list = os.listdir(tier_dir)
                
                df_list = []
                
                parameter_list = []
                parameter_dict = {}
                
                if params['vis_dir'] in csv_file_list:
                    csv_file_list.remove(f'{params["vis_dir"]}')

                
                if params['tier']=='3a':
                    # Read dataframe with csv concatenates in the script create_csv_concatenate.py
                    df_outputs = pd.read_csv(f'{tier}/{scen}/{case}/{case}_output.csv', low_memory=False)
                    parameters = df_outputs.columns.values
                    columns_names_delete = [
                        'Unnamed: 0', 'YEAR', 'TECHNOLOGY', 'FUEL', 'EMISSION'
                        ]
                elif params['tier']=='1':
                    # Read dataframe with csv concatenates in the script create_csv_concatenate.py
                    df_outputs = pd.read_csv(f'{tier}/{case}/{case}_output.csv', low_memory=False)
                    parameters = df_outputs.columns.values
                    columns_names_delete = [
                                            "Strategy",
                                            "Future.ID",
                                            "Fuel",
                                            "Technology",
                                            "Emission",
                                            "Year",
                                            "DistanceDriven",
                                            "Fleet",
                                            "NewFleet",
                                            "ProducedMobility",
                                            "FilterFuelType",
                                            "FilterVehicleType",
                                            "Capex_GDP",
                                            "FixedOpex_GDP",
                                            "VarOpex_GDP",
                                            "Opex_GDP",
                                            "Externalities_GDP"
                                        ]
                    # Name of the sets
                    sets_csv_old = ['Year', 'Technology', 'Fuel', 'Emission']
                    sets_csv_new = ['YEAR', 'TECHNOLOGY', 'FUEL', 'EMISSION']
                    
                    # Create a dictionary to map old names to new ones
                    rename_dict = dict(zip(sets_csv_old, sets_csv_new))
                    
                    # Use the rename method to change the column names
                    df_outputs.rename(columns=rename_dict, inplace=True)

                parameters = np.array([col for col in parameters if col not in columns_names_delete])
                
                # Years availables
                years = df_outputs['YEAR'].unique()
                years.sort()
                
                # Print info about years, only in the base case
                if case == 'BAU_0':
                    option = 'w'
                else:
                    option = 'a'

                    
                if params['info']: # and int(case[-1])==0:
                    with open(info_filename, option) as file_info:
                        file_info.write('\n###################################################################################')
                        file_info.write(f'\n\nData information of this scenario: {case[0:3]}')
                        file_info.write(f'\n\nThese are the years availables:\n{years}')
                        file_info.write('\n-----------------------------------------------------------------------------------\n')

                        option = 'a'
                        file_info.close()
                
                # Plot attempts:
                techs_desired = {}
                for parameter in parameters:
                    # Print info about technologies, only in the base case
                    if params['info']:
                        
                        
                        df_tech_filtered = filter_and_select_columns(df_outputs, parameter, ['YEAR', 'TECHNOLOGY', 'FUEL', 'EMISSION'])
                        technologies =  df_tech_filtered['TECHNOLOGY'].unique()
                        with open(info_filename, option) as file_info:
                            file_info.write(f'\nFor {parameter}, these are the technologies availables:\n{technologies}')
                            file_info.write('\n-----------------------------------------------------------------------------------\n')
                            file_info.close()

                        continue
                    if not params['info']:
                        year_apply_discount_rate = params['year_apply_discount_rate']
                        
                        try:
                            if params[f'techs_{scen}_{parameter}'] != []:
                                techs_desired[f'{parameter}'] = params[f'techs_{scen}_{parameter}']
                            elif parameter.endswith(str(year_apply_discount_rate)) and params[f'techs_{scen}_{parameter}'] != []:
                                techs_desired[f'{parameter}'] = params[f'techs_{scen}_{parameter}']
                            else:
                                print(f'For this scenario {scen}, this {parameter} do not has any technology select.')
                        except Exception:
                            continue
                            
                            
                    
                    if parameter in techs_desired:
                        
                        
                        # Info about ticks years 
                        start_pos_year = params['start_year'] - int(years[0]) #Initial year for ticks of x label           
                        
                        # Filter the DataFrame for the current parameter
                        parameter_df = filter_and_select_columns(df_outputs, parameter, ['YEAR', 'TECHNOLOGY', 'FUEL', 'EMISSION'])

                        # Filter the DataFrame for the techcologies selected
                        parameter_df = parameter_df[parameter_df['TECHNOLOGY'].isin(techs_desired[parameter])]
                        
                        # If the filtered DataFrame is empty, skip this parameter
                        if parameter_df.empty:
                            print(f"No data for parameter {parameter}. Skipping plot.")
                            continue
                    
                        # Check if there are multiple values for the same Year and Technology/Fuel and aggregate them if necessary
                        parameter_df = parameter_df.groupby(['YEAR', 'TECHNOLOGY'], as_index=False).agg('sum')
                    
                        # Create the plot only if there are technologies/fuels for this parameter
                        if not parameter_df['TECHNOLOGY'].empty:
                            if params['plot_type']=='bar':
                                plt.figure(figsize=(10, 6))  # Adjust the size as needed
                                # Plot the DataFrame as a bar chart
                                sns.barplot(data=parameter_df, x='YEAR', y='VALUE', hue='TECHNOLOGY')
                        
                            if params['plot_type']=='stacked_bar':
                                # Pivot the DataFrame to have technologies as columns and years as rows
                                pivot_df = parameter_df.pivot(index='YEAR', columns='TECHNOLOGY', values='VALUE').fillna(0)
                                # Plot the pivoted DataFrame as a stacked bar chart
                                pivot_df.plot(kind='bar', stacked=True, figsize=(10, 6))
                                

                        
                            # Adjust the X-axis ticks if necessary
                            xticks = plt.xticks()[0]  # Gets the current locations of the ticks
                            xticklabels = [label+int(years[0]) if (int(label-start_pos_year)%params['separation_years'] == 0) else '' for i, label in enumerate(xticks)]
                            plt.xticks(rotation=0, ticks=xticks, labels=xticklabels)
                            
                            # Labels and title
                            plt.title(f'{parameter} Investment by Technology {case}')
                            plt.ylabel('Million $')
                            plt.xlabel('Year')
                            
                            # Display the legend and the chart
                            plt.legend(title='Technology').set_visible(params['visible_legend'])
                            
                            # Show/save the plot
                            if params['show_fig']:
                                plt.show()
                            # To save the plot, uncomment the following line
                            if params['save_fig']:
                                file_path = f'{tier_dir}/{params["vis_dir"]}/{parameter}_investment_by_technology.png'
                                directory = os.path.dirname(file_path)
                                if not os.path.exists(directory):
                                    os.makedirs(directory)
                                plt.savefig(file_path)
                            plt.close()
                        else:
                            print(f"No technologies associated with parameter {parameter} {case}.")
                            