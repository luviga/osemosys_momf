# -*- coding: utf-8 -*-
# Suggested Citation:
# Victor-Gallardo, L. (2022). Robust Energy System Planning for Decarbonization under Technological Uncertainty.
# Retrieved from https://www.kerwa.ucr.ac.cr/handle/10669/87273

"""
This code is based on the methodologies and findings discussed in the work of Luis Victor-Gallardo, specifically focusing on robust energy system planning for decarbonization under technological uncertainty. The document provides a comprehensive analysis relevant to the code's development and application. For in-depth understanding and further details, please refer to the original document linked below.

Suggested Citation:
Victor-Gallardo, L. (2022). Robust Energy System Planning for Decarbonization under Technological Uncertainty.
University of Costa Rica. Retrieved from https://www.kerwa.ucr.ac.cr/handle/10669/87273
"""

from datetime import date
import sys
import pandas as pd
import os
from copy import deepcopy
import csv
import numpy as np

sys.path.insert(0, 'Executables')
import local_dataset_creator_0

# Assuming `df` is your DataFrame after loading the Excel file
df_structure = pd.read_excel('B1_Model_Structure.xlsx')

# Now let's find the last non-empty value in the 'REGION' column
region_str = df_structure['REGION'].dropna().iloc[-1]

file_name_suffix = 'f0_OSMOSYS_' + region_str + '_'

run_for_first_time = True

if run_for_first_time == True:
    local_dataset_creator_0.execute_local_dataset_creator_0_outputs()
    local_dataset_creator_0.execute_local_dataset_creator_0_inputs()
############################################################################################################
df_0_output = pd.read_csv('.\Executables\output_dataset_0.csv', index_col=None, header=0)
#
li_output = [df_0_output]
#
df_output = pd.concat(li_output, axis=0, ignore_index=True)
df_output.sort_values(by=['Future.ID','Fuel','Technology','Emission','Year'], inplace=True)

df_output=df_output.assign(Sector=np.NaN)
df_output=df_output.assign(Description=np.NaN)
df_output=df_output.assign(SpecificSector=np.NaN)


libro = pd.ExcelFile('B1_Model_Structure.xlsx')
hoja=libro.parse( 'sector' , skiprows = 0 )
encabezados=list(hoja)

col_t=list(hoja[encabezados[0]])
col_s=list(hoja[encabezados[1]])
col_d=list(hoja[encabezados[2]])
col_ss=list(hoja[encabezados[3]])
dicSector=dict(zip(col_t,col_s))
dicDescription=dict(zip(col_t,col_d))
dicSpecificSector=dict(zip(col_t,col_ss))

llaves=list(dicSector.keys())
col_sector=np.array(list(df_output['Sector']))

for i in range(len(llaves)):
    df_output.loc[df_output['Technology'] == llaves[i], 'Sector'] =  dicSector[llaves[i]]
    df_output.loc[df_output['Technology'] == llaves[i], 'Description'] =  dicDescription[llaves[i]]
    df_output.loc[df_output['Technology'] == llaves[i], 'SpecificSector'] =  dicSpecificSector[llaves[i]]
    

############################################################################################################
df_0_input = pd.read_csv('.\Executables\input_dataset_0.csv', index_col=None, header=0)
#
li_intput = [df_0_input]
#
df_input = pd.concat(li_intput, axis=0, ignore_index=True)
df_input.sort_values(by=['Future.ID','Strategy.ID','Strategy','Fuel','Technology','Emission','Season','Year'], inplace=True)
############################################################################################################
#
dfa_list = [df_output, df_input]
#
today = date.today()
#
df_output = dfa_list[0]
df_output.to_csv (region_str + 'Output.csv', index = None, header=True)
df_output.to_csv (region_str + 'Output_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
#
df_input = dfa_list[1]
df_input.to_csv (region_str + 'Input.csv', index = None, header=True)
df_input.to_csv (region_str + 'Input_' + str( today ).replace( '-', '_' ) + '.csv', index = None, header=True)
#