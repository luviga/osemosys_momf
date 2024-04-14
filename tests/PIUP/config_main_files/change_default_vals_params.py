# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 10:52:32 2024

@author: andreysava19
"""

import yaml
import os
from copy import deepcopy
import shutil
import sys

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
    appended_path = os.path.join(base_path, 'tests\PIUP\config_main_files') + os.sep
    
    return appended_path

# Read yaml file with parameterization
file_config_address = get_config_main_path(os.path.abspath(''))
# sys.exit()
with open(file_config_address + '\\' + 'MOMF_B1_exp_manager.yaml', 'r') as file:
    # Load content file
    params = yaml.safe_load(file)
# Select dict with default values parameters
default_val_params = params['default_val_params']
default_val_sets = params['sets_otoole']

# Create defaul yaml file by otoole
file_path = file_config_address + 'config\\conversion_format.yaml'
directory = os.path.dirname(file_path)
if not os.path.exists(directory):
    os.makedirs(directory)
    
os.system(f'otoole setup --overwrite config {file_path}')

# Create folder with csv templates
os.system(f'otoole setup --overwrite csv ' + file_config_address + 'config\\templates')

# Read yaml file with parameterization to conversion format by otoole
with open(file_path, 'r') as file:
    # Load content file
    default_format = yaml.safe_load(file)

# Create temporal variable to delete some parameter from 'default_format'
temp_defaut_params = deepcopy(default_format)

# Delete parameters that are not in 'MOMF_T1_B1.yaml'
for old_key, attributes in temp_defaut_params.items():
    if attributes['type'] == 'param':
        for index in attributes['indices']:
            if index not in default_val_sets:
                default_format[old_key]['indices'].remove(index)
                    
        if not old_key in default_val_params:
            default_format.pop(old_key)
            shutil.os.remove(file_config_address + 'config\\templates\\' + old_key + '.csv')
        
    elif attributes['type'] == 'set' and not old_key in default_val_sets:
        a = default_format.pop(old_key)
        shutil.os.remove(file_config_address + 'config\\templates\\' + old_key + '.csv')
    
    elif attributes['type'] == 'result':
        for index in attributes['indices']:
            if index not in default_val_sets:
                default_format[old_key]['indices'].remove(index)
                # shutil.os.remove(file_config_address + 'config\\templates\\' + index + '.csv')
        
    
            
        
# Change default value
for old_key, attributes in default_format.items():
    if attributes['type'] == 'param' and 'default' in attributes:
        default_val_params = params['default_val_params']
        default_format[old_key]['default'] = default_val_params[old_key]
        
# Save changes of default values in the yaml file
with open(file_path, 'w') as file:
    yaml.dump(default_format, file, sort_keys=False)