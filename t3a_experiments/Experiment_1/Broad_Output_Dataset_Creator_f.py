from datetime import date
import sys
import pandas as pd
import os
import re
import yaml

sys.path.insert(0, 'Executables')
import local_dataset_creator_0

sys.path.insert(0, 'Futures')
import local_dataset_creator_f

def get_config_main_path(full_path):
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
    appended_path = os.path.join(base_path, 'config_main_files') + os.sep
    
    return appended_path

# Read yaml file with parameterization
file_config_address = get_config_main_path(os.path.abspath(''))
with open(file_config_address + '\\' + 'MOMF_B1_exp_manager.yaml', 'r') as file:
    # Load content file
    params = yaml.safe_load(file)

'Define control parameters:'
file_aboslute_address = os.path.abspath(params['Bro_out_dat_cre'])
file_adress = re.escape( file_aboslute_address.replace( params['Bro_out_dat_cre'], '' ) ).replace( '\:', ':' )

run_for_first_time = True

if run_for_first_time == True:
    local_dataset_creator_0.execute_local_dataset_creator_0_outputs()
    local_dataset_creator_f.execute_local_dataset_creator_f_outputs()
    local_dataset_creator_0.execute_local_dataset_creator_0_inputs()
    local_dataset_creator_f.execute_local_dataset_creator_f_inputs()

############################################################################################################
df_0_output = pd.read_csv(params['Executables_2'] + params['Out_dat_0'], index_col=None, header=0)
df_f_output = pd.read_csv( file_adress + params['Futures_3'] + params['Out_dat_f'], index_col=None, header=0)
li_output = [df_0_output, df_f_output]
#
df_output = pd.concat(li_output, axis=0, ignore_index=True)
df_output.sort_values(by=params['by_1'], inplace=True)
############################################################################################################
df_0_input = pd.read_csv(params['Executables_2'] + params['In_dat_0'], index_col=None, header=0)

df_f_input = pd.read_csv('.' + params['Futures_3'] + params['In_dat_f'], index_col=None, header=0)
li_intput = [df_0_input, df_f_input]
#
df_input = pd.concat(li_intput, axis=0, ignore_index=True)
df_input.sort_values(by=params['by_2'], inplace=True)

dfa_list = [ df_output, df_input ]

today = date.today()
#
df_output = dfa_list[0]
df_output.to_csv ( params['ose_cou_out'] + '.csv', index = None, header=True)
df_output.to_csv ( params['ose_cou_out'] + '_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
#
df_input = dfa_list[1]
df_input.to_csv ( params['ose_cou_in'] + '.csv', index = None, header=True)
df_input.to_csv ( params['ose_cou_in'] + '_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
