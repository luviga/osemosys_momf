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
from copy import deepcopy

if __name__ == '__main__':
    # Read yaml file with parameterization
    with open('plots_config.yaml', 'r') as file:
        # Load content file
        params = yaml.safe_load(file)
        
    # Read yaml file with parameterization
    with open( params['dir_main_script_yaml'] + '/MOMF_B1_exp_manager.yaml', 'r') as file:
        # Load content file
        params_tiers = yaml.safe_load(file)
        
    sets_corrects = deepcopy(params_tiers['sets_otoole'])
    sets_corrects.insert(0,'Parameter')
    sets_corrects.append('VALUE')
    

    sets_csv = ['YEAR', 'TECHNOLOGY', 'FUEL', 'EMISSION']
    sets_csv_temp = deepcopy(sets_csv)
    sets_csv_temp.insert(0,'Parameter')
    sets_csv_temp.append('VALUE')
    set_no_needed = [item for item in params_tiers['sets_otoole'] if item not in sets_csv]
    
    if params['model']=='MOMF':
        dict_scen_folder_unique = {}
        for scen in params['scens']:
            if params['tier']=='1':
                all_files_internal = os.listdir(params['tier1_dir'])
                dict_scen_folder_unique[f'{scen}'] = [i for i in all_files_internal if scen in i]
            elif params['tier']=='3a':
                all_files_internal = os.listdir(params['tier3a_dir'] + '/' + scen)
                dict_scen_folder_unique[f'{scen}'] = [i for i in all_files_internal if scen in i]
        count = 0
        for scen in dict_scen_folder_unique:
            for case in dict_scen_folder_unique[f'{scen}']:
                # Select folder path
                if params['tier']=='1':
                    tier_dir = params['tier1_dir'] + '/' + case + params['out_dir']
                elif params['tier']=='3a':
                    tier_dir = params['tier3a_dir'] + '/' + scen + '/' + case + params['out_dir']
    
                # 1st try
                csv_file_list = os.listdir(tier_dir)
                
                df_list = []
                
                parameter_list = []
                parameter_dict = {}
                
                if params['vis_dir'] in csv_file_list:
                    csv_file_list.remove(f'{params["vis_dir"]}')
                
                # Read dataframe with csv concatenates in the script create_csv_concatenate.py
                df_all = pd.read_csv(f'{params["excel_data_file_dir"]}{scen}/{case}/Data_plots_{case[-1]}.csv')
                df_all.drop('Unnamed: 0', axis=1, inplace=True, errors='ignore')

                # Assuming df is your pandas DataFrame with the relevant data
                parameters = df_all['Parameter'].unique()  # Replace with your actual parameters column
                
                
                # Years availables
                years = df_all['YEAR'].unique()
                years.sort()
                
                # Print info about years, only in the base case
                if params['info']: # and int(case[-1])==0:
                    print(f'Data information of this scenario: {case[0:3]}')
                    print(f'These are the years availables:\n{years}')
                
                # Plot attempts:
                techs_desired = {}
                for parameter in parameters:
                    # Print info about technologies, only in the base case
                    if params['info']: # and int(case[-1])==0:
                        df_tech_filtered = df_all[df_all['Parameter'] == parameter]
                        technologies =  df_tech_filtered['TECHNOLOGY'].unique()
                        print(f'For {parameter}, these are the technologies availables:\n{technologies}')
                        continue
                    if not params['info']:
                        try:
                            if params[f'techs_{parameter}'] != []:
                                techs_desired[f'{parameter}'] = params[f'techs_{parameter}']
                        except Exception:
                            print(f'{parameter} do not has any technology select.')
                        
                    if parameter in techs_desired:
                        
                        
                        # Info about ticks years 
                        start_pos_year = params['start_year'] - int(years[0]) #Initial year for ticks of x label
                        
                        
                        # Filter the DataFrame for the current parameter
                        parameter_df = df_all[df_all['Parameter'] == parameter]
                        # Filter the DataFrame for the techcologies selected
                        
                        parameter_df = parameter_df[parameter_df['TECHNOLOGY'].isin(techs_desired[parameter])]
                        # sys.exit()
                        
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
                                
                                if parameter=='TotalTechnologyAnnualActivity':
                                    sys.exit()
                        
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