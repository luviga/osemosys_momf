from datetime import date
import sys
import pandas as pd
import os
import re

sys.path.insert(0, 'Executables')
import local_dataset_creator_0

sys.path.insert(0, 'Experimental_Platform\Futures')
import local_dataset_creator_f

'Define control parameters:'

file_aboslute_address = os.path.abspath("Broad_Output_Dataset_Creator_f.py")
file_adress = re.escape( file_aboslute_address.replace( 'Broad_Output_Dataset_Creator_f.py', '' ) ).replace( '\:', ':' )

run_for_first_time = True

if run_for_first_time == True:
    local_dataset_creator_0.execute_local_dataset_creator_0_outputs()
    local_dataset_creator_f.execute_local_dataset_creator_f_outputs()
    local_dataset_creator_0.execute_local_dataset_creator_0_inputs()
    local_dataset_creator_f.execute_local_dataset_creator_f_inputs()

############################################################################################################
df_0_output = pd.read_csv('.\Executables\output_dataset_0.csv', index_col=None, header=0)
df_f_output = pd.read_csv( file_adress + '\Futures\output_dataset_f.csv', index_col=None, header=0)
li_output = [df_0_output, df_f_output]
#
df_output = pd.concat(li_output, axis=0, ignore_index=True)
df_output.sort_values(by=['Strategy','Future.ID','Fuel','Technology','Emission','Year'], inplace=True)
############################################################################################################
df_0_input = pd.read_csv('.\Executables\input_dataset_0.csv', index_col=None, header=0)

df_f_input = pd.read_csv('.\Futures\input_dataset_f.csv', index_col=None, header=0)
li_intput = [df_0_input, df_f_input]
#
df_input = pd.concat(li_intput, axis=0, ignore_index=True)
df_input.sort_values(by=['Future.ID','Strategy.ID','Strategy','Fuel','Technology','Emission','Season','Year'], inplace=True)

dfa_list = [ df_output, df_input ]

today = date.today()
#
df_output = dfa_list[0]
df_output.to_csv ( 'OSMOSYS_CR_Output.csv', index = None, header=True)
df_output.to_csv ( 'OSMOSYS_CR_Output_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
#
df_input = dfa_list[1]
df_input.to_csv ( 'OSMOSYS_CR_Input.csv', index = None, header=True)
df_input.to_csv ( 'OSMOSYS_CR_Input_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
