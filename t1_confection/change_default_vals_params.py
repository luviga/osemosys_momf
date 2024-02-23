# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 10:52:32 2024

@author: andreysava19
"""

import yaml
import os
from copy import deepcopy
import shutil

# Read yaml file with parameterization
with open('MOMF_T1_B1.yaml', 'r') as file:
    # Load content file
    params = yaml.safe_load(file)
# Select dict with default values parameters
default_val_params = params['default_val_params']

# Create defaul yaml file by otoole
file_path = './config/conversion_format.yaml'
directory = os.path.dirname(file_path)
if not os.path.exists(directory):
    os.makedirs(directory)
    
os.system(f'otoole setup --overwrite config {file_path}')

# Create folder with csv templates
os.system('otoole setup --overwrite csv ./config/templates')

# Read yaml file with parameterization to conversion format by otoole
with open(file_path, 'r') as file:
    # Load content file
    default_format = yaml.safe_load(file)

# Create temporal variable to delete some parameter from 'default_format'
temp_defaut_params = deepcopy(default_format)

# Delete parameters that are not in 'MOMF_T1_B1.yaml'
for old_key, attributes in temp_defaut_params.items():
    if attributes['type'] == 'param' and not old_key in default_val_params:
        default_format.pop(old_key)
        shutil.os.remove('./config/templates/' + old_key + '.csv')
        
# Change default value
for old_key, attributes in default_format.items():
    if attributes['type'] == 'param' and 'default' in attributes:
        default_val_params = params['default_val_params']
        default_format[old_key]['default'] = default_val_params[old_key]
        
# Save changes of default values in the yaml file
with open(file_path, 'w') as file:
    yaml.dump(default_format, file, sort_keys=False)