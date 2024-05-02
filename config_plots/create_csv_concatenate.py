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

if __name__ == '__main__':
    # Read yaml file with parameterization
    file_config_address = get_config_main_path(os.path.abspath(''), 'config_main_files')
    with open(file_config_address + '\\' + 'MOMF_B1_exp_manager.yaml', 'r') as file:
        # Load content file
        params = yaml.safe_load(file)
        
    # # Read yaml file with parameterization
    # file_config_address = get_config_main_path(os.path.abspath(''), 'config_main_files')
    # with open( file_config_address + '\\' + '/MOMF_B1_exp_manager.yaml', 'r') as file:
    #     # Load content file
    #     params_tiers = yaml.safe_load(file)
        
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
                
                # The 'outer' join ensures that all combinations of dimension values are included, filling missing values with NaN
                df_all_3.to_csv(f'{file_df_dir}/Data_Output_{case[-1]}.csv')