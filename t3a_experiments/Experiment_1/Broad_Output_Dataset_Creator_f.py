from datetime import date
import sys
import pandas as pd
import os
import re
import yaml
import numpy as np


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

sys.path.insert(0, params['Executables_3'])
import local_dataset_creator_0

sys.path.insert(0, params['Futures_4'])
import local_dataset_creator_f

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


# In case if you use solver='glpk' and glpk='old' uncomment this section
#----------------------------------------------------------------------------------------------------------#
# # Use this space to edit the column names of future zero resuls:
# df_0_output = df_0_output.rename(columns=params['columns'])

# df_0_output['Strategy'] = df_0_output['Strategy'].replace('DDP50', 'DDP')

# # df_0_output.insert(1, 'Future.ID', [0]*len(df_0_output.index.tolist()))
# #df_0_output['Capex2023'] = df_0_output['DiscountedCapitalInvestment']
# #df_0_output['FixedOpex2023'] = #df_0_output['DiscountedOperatingCost']
# #df_0_output['VarOpex2023'] = #df_0_output['DiscountedOperatingCost']
# #df_0_output['Opex2023'] = df_0_output['DiscountedOperatingCost']
# #df_0_output['Externalities2023'] = df_0_output['DiscountedTechnologyEmissionsPenalty']
# #df_0_output['Capex_GDP'] = [0]*len(df_0_output.index.tolist())
# #df_0_output['FixedOpex_GDP'] = [0]*len(df_0_output.index.tolist())
# #df_0_output['VarOpex_GDP'] = [0]*len(df_0_output.index.tolist())
# #df_0_output['Opex_GDP'] = [0]*len(df_0_output.index.tolist())
# #df_0_output['Externalities_GDP'] = [0]*len(df_0_output.index.tolist())
# df_0_output['Scen_fut'] = df_0_output['Strategy'].astype(str) + "_" + df_0_output['Future.ID'].astype(str)

# valid_column_names = params['valid_column_names']

# df_0_output = df_0_output[valid_column_names]
#----------------------------------------------------------------------------------------------------------#


df_f_output = pd.read_csv( '.' + params['Futures_3'] + params['Out_dat_f'], index_col=None, header=0, low_memory=False)


# In case if you use solver='glpk' and glpk='old' uncomment this section
#----------------------------------------------------------------------------------------------------------#
# null_columns_f, valid_columns_f = [], []
# for acol in df_f_output.columns.tolist():
#     # Check if all values in the column are null
#     if df_f_output[acol].isnull().all():
#         null_columns_f.append(acol)
#     else:
#         valid_columns_f.append(acol)

# #df_f_output = df_f_output[valid_columns_f]
# df_f_output = df_f_output[valid_column_names]

# if df_0_output.columns.tolist() != df_f_output.columns.tolist():
#     print('Error')
#     sys.exit()
# else:
#     print('Success')

# df_0_output["Year"]=df_0_output["Year"].fillna(0).astype(int)
#----------------------------------------------------------------------------------------------------------#

li_output = [df_0_output, df_f_output]
#
df_output = pd.concat(li_output, axis=0, ignore_index=True)
df_output.sort_values(by=params['by_1'], inplace=True)
############################################################################################################
df_0_input = pd.read_csv(params['Executables_2'] + params['In_dat_0'], index_col=None, header=0)

# In case if you use solver='glpk' and glpk='old' uncomment this section
#----------------------------------------------------------------------------------------------------------#
# df_0_input['Strategy'] = df_0_input['Strategy'].replace('DDP50', 'DDP')
#----------------------------------------------------------------------------------------------------------#

df_f_input = pd.read_csv('.' + params['Futures_3'] + params['In_dat_f'], index_col=None, header=0, low_memory=False)
li_intput = [df_0_input, df_f_input]
#
df_input = pd.concat(li_intput, axis=0, ignore_index=True)
df_input.sort_values(by=params['by_2'], inplace=True)

#############################
#############################
libro = pd.ExcelFile('./0_From_Confection/B1_Model_Structure.xlsx')
hoja=libro.parse( 'sector' , skiprows = 0 )
encabezados=list(hoja)

col_t=list(hoja[encabezados[0]])
col_s=list(hoja[encabezados[1]])
col_d=list(hoja[encabezados[2]])
dicSector=dict(zip(col_t,col_s))
dicDescription=dict(zip(col_t,col_d))


df_output=df_output.assign(Sector=np.NaN)
df_output=df_output.assign(Description=np.NaN)

df_input=df_input.assign(Sector=np.NaN)
df_input=df_input.assign(Description=np.NaN)


llaves=list(dicSector.keys())
col_sector=np.array(list(df_output['Sector']))

for i in range(len(llaves)):
    df_output.loc[df_output['Technology'] == llaves[i], 'Sector'] =  dicSector[llaves[i]]
    df_output.loc[df_output['Technology'] == llaves[i], 'Description'] =  dicDescription[llaves[i]]
    df_input.loc[df_input['Technology'] == llaves[i], 'Sector'] =  dicSector[llaves[i]]
    df_input.loc[df_input['Technology'] == llaves[i], 'Description'] =  dicDescription[llaves[i]]

#############################
#############################

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
