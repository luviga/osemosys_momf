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

import errno
import scipy
import pandas as pd
import numpy as np
import xlrd
import re
import csv
import os, os.path
import sys
import math
import linecache
from copy import deepcopy
import time
import gc
import shutil
import pickle
import multiprocessing as mp

from setup_utils import install_requirements

'''
Some variables need to be defined at the beginning of the code
(eventually .yaml file) to make the model nomenclature compatible
with the script.
'''

IGNORE_TECHS = ['TRANRAILFREINF',  'TRANOMOTWalk', 'TRANOMOTBike',
                'TRXTRAIELE', 'TRXTRAIFREELE', 'TRANRAILINF', 'TRANPUB',
                'TRANRAILCAR', 'LATR', 'PROD_CLK_TRAD', 'NO_CONTR_OD',
                'AG_TRVEG']
"""
IGNORE_TECHS:
is defined to control "rewrite_techs_maxcap". It updates capacities of
transport that belong to the Fleet_Groups dictionary.
Other implementations may also be effected by .
"""


REGION_STR = 'RD'
"""
IGNORE_TECHS: avoids ad-hoc region definition
"""


BAU_STR = 'BAU'
"""
IGNORE_TECHS: makes the BAU string explicit from the top
"""


SET_LIST_GROUP_DICT = {'Passenger':['DEMTRNPASPRI', 'DEMTRNPASPUB', 'DEMTRN_NOMOT'],
                       'Freight':['DEMTRNFREHEA', 'DEMTRNFREMED', 'DEMTRNFRELIG']}
"""
SET_LIST_GROUP_DICT: controls the sets of passenger and transport demand
"""


BY_INT = 2018
"""
BY_INT: introduce the base yaer
"""


START_VAR_YR_INT = 2024
"""
START_VAR_YR_INT: introduce the year where variations start
"""


EY_INT = 2050
"""
EY_INT: introduce the end year
"""


PRIVATE_TRANSPORT_DEMAND_STR = 'E6TDPASPRI'
"""
PRIVATE_TRANSPORT_DEMAND_STR: introduce the string calling private passenger trn.
"""


PUBLIC_TRANSPORT_DEMAND_STR = 'E6TDPASPUB'
"""
PUBLIC_TRANSPORT_DEMAND_STR: introduce the string calling public passenger trn.
"""


HEAVY_FREIGHT_TRANSPORT_DEMAND_STR = 'E6TDFREHEA'
"""
HEAVY_FREIGHT_TRANSPORT_DEMAND_STR: introduce the string calling heavy freight
"""


LIGHT_FREIGHT_TRANSPORT_DEMAND_STR = 'E6TDFRELIG'
"""
LIGHT_FREIGHT_TRANSPORT_DEMAND_STR: introduce the string calling light freight
Note: some countries have "medium freight". In this case, it is necessary to
create a new instance of light or heavy freight demand conditions troughout the
 code, but refering to medium freight transport.
"""


'''
We implement OSEMOSYS-CR in a csv based system for semi-automatic manipulation of parameters.
'''
def intersection_2(lst1, lst2): 
    return list(set(lst1) & set(lst2))
#
def interp_max_cap( x ):
    x_change_known = []
    x_unknown = []
    last_big_known = 0
    x_pick = [ x[0] ]
    for n in range( 1, len( x ) ):
        if x[n] > x[n-1] and x[n-1] >= last_big_known:
            last_big_known = x[n-1]
            appender = x[n]
            x_change_known.append( x[n] )
            x_unknown.append( 'none' )
            x_pick.append( x[n] )
        else:
            if x[n] >= last_big_known and x[n] > x_change_known[0]:
                x_change_known.append( x[n] )
                x_unknown.append( 'none' )
                x_pick.append( x[n] )
            else:
                x_change_known.append( 'none' )
                x_unknown.append( x[n] )
                x_pick.append( appender )
    return x_pick
    #
#
def main_executer(n1, packaged_useful_elements, scenario_list_print):
    set_first_list(scenario_list_print)
    file_aboslute_address = os.path.abspath("B1_Base_Scenarios.py")
    file_adress = re.escape( file_aboslute_address.replace( 'B1_Base_Scenarios.py', '' ) ).replace( '\:', ':' )
    #
    case_address = file_adress + r'Executables\\' + str( first_list[n1] )
    this_case = [ e for e in os.listdir( case_address ) if '.txt' in e ]
    #
    str1 = "start /B start cmd.exe @cmd /k cd " + file_adress
    #
    data_file = case_address.replace('./','').replace('/','\\') + '\\' + str( this_case[0] )
    output_file = case_address.replace('./','').replace('/','\\') + '\\' + str( this_case[0] ).replace('.txt','') + '_output' + '.txt'
    #
    str2 = "glpsol -m OSeMOSYS_Model.txt -d " + str( data_file )  +  " -o " + str(output_file)
    os.system( str1 and str2 )
    time.sleep(1)
    #
    data_processor(n1,packaged_useful_elements)
    #
#
def set_first_list(scenario_list_print):
    #
    first_list_raw = os.listdir( './Executables' )
    #
    global first_list
    scenario_list_print_with_fut = [ e + '_0' for e in scenario_list_print ]
    first_list = [e for e in first_list_raw if ( '.csv' not in e ) and ( 'Table' not in e ) and ( '.py' not in e ) and ( '__pycache__' not in e ) and ( e in scenario_list_print_with_fut ) ]
    #
#
def data_processor( case, unpackaged_useful_elements ):
    #
    Reference_driven_distance =     unpackaged_useful_elements[0]
    Reference_occupancy_rate =      unpackaged_useful_elements[1]
    Reference_op_life =             unpackaged_useful_elements[2]
    Fleet_Groups_inv =              unpackaged_useful_elements[3]
    time_range_vector =             unpackaged_useful_elements[4]
    list_param_default_value_params = unpackaged_useful_elements[5]
    list_param_default_value_value = unpackaged_useful_elements[6]
    list_gdp_ref = unpackaged_useful_elements[7]

    # Extract the default (national) discount rate parameter
    dr_prm_idx = list_param_default_value_params.index('DiscountRate')
    dr_default = list_param_default_value_value[dr_prm_idx]

    # Briefly open up the system coding to use when processing for visualization:
    df_fuel_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Fuel_to_Code' )
    df_fuel_2_code_fuel_list        = df_fuel_to_code['Code'].tolist()
    df_fuel_2_code_plain_english    = df_fuel_to_code['Plain_English'].tolist()
    df_tech_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Tech_to_Code' )
    df_tech_2_code_fuel_list        = df_tech_to_code['Techs'].tolist()
    df_tech_2_code_plain_english    = df_tech_to_code['Plain_English'].tolist()
    #
    # 1 - Always call the structure of the model:
    #-------------------------------------------#
    structure_filename = "B1_Model_Structure.xlsx"
    structure_file = pd.ExcelFile(structure_filename)
    structure_sheetnames = structure_file.sheet_names  # see all sheet names
    sheet_sets_structure = pd.read_excel(open(structure_filename, 'rb'),
                                         header=None,
                                         sheet_name=structure_sheetnames[0])
    sheet_params_structure = pd.read_excel(open(structure_filename, 'rb'),
                                           header=None,
                                           sheet_name=structure_sheetnames[1])
    sheet_vars_structure = pd.read_excel(open(structure_filename, 'rb'),
                                         header=None,
                                         sheet_name=structure_sheetnames[2])

    S_DICT_sets_structure = {'set':[],'initial':[],'number_of_elements':[],'elements_list':[]}
    for col in range(1,11+1):  # 11 columns
        S_DICT_sets_structure['set'].append( sheet_sets_structure.iat[0, col] )
        S_DICT_sets_structure['initial'].append( sheet_sets_structure.iat[1, col] )
        S_DICT_sets_structure['number_of_elements'].append( int( sheet_sets_structure.iat[2, col] ) )
        #
        element_number = int( sheet_sets_structure.iat[2, col] )
        this_elements_list = []
        if element_number > 0:
            for n in range( 1, element_number+1 ):
                this_elements_list.append( sheet_sets_structure.iat[2+n, col] )
        S_DICT_sets_structure['elements_list'].append( this_elements_list )
    #
    S_DICT_params_structure = {'category':[],'parameter':[],'number_of_elements':[],'index_list':[]}
    param_category_list = []
    for col in range(1,30+1):  # 30 columns
        if str( sheet_params_structure.iat[0, col] ) != '':
            param_category_list.append( sheet_params_structure.iat[0, col] )
        S_DICT_params_structure['category'].append( param_category_list[-1] )
        S_DICT_params_structure['parameter'].append( sheet_params_structure.iat[1, col] )
        S_DICT_params_structure['number_of_elements'].append( int( sheet_params_structure.iat[2, col] ) )
        #
        index_number = int( sheet_params_structure.iat[2, col] )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_params_structure.iat[2+n, col] )
        S_DICT_params_structure['index_list'].append( this_index_list )
    #
    S_DICT_vars_structure = {'category':[],'variable':[],'number_of_elements':[],'index_list':[]}
    var_category_list = []
    for col in range(1,43+1):  # 43 columns
        if str( sheet_vars_structure.iat[0, col] ) != '':
            var_category_list.append( sheet_vars_structure.iat[0, col] )
        S_DICT_vars_structure['category'].append( var_category_list[-1] )
        S_DICT_vars_structure['variable'].append( sheet_vars_structure.iat[1, col] )
        S_DICT_vars_structure['number_of_elements'].append( int( sheet_vars_structure.iat[2, col] ) )
        #
        index_number = int( sheet_vars_structure.iat[2, col] )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_vars_structure.iat[2+n, col] )
        S_DICT_vars_structure['index_list'].append( this_index_list )
    #-------------------------------------------#
    all_vars = ['Demand',
                'NewCapacity',
                'AccumulatedNewCapacity',
                'TotalCapacityAnnual',
                'TotalTechnologyAnnualActivity',
                'ProductionByTechnology',
                'UseByTechnology',
                'CapitalInvestment',
                'DiscountedCapitalInvestment',
                'SalvageValue',
                'DiscountedSalvageValue',
                'OperatingCost',
                'DiscountedOperatingCost',
                'AnnualVariableOperatingCost',
                'AnnualFixedOperatingCost',
                'TotalDiscountedCostByTechnology',
                'TotalDiscountedCost',
                'AnnualTechnologyEmission',
                'AnnualTechnologyEmissionPenaltyByEmission',
                'AnnualTechnologyEmissionsPenalty',
                'DiscountedTechnologyEmissionsPenalty',
                'AnnualEmissions'
                ]
    #
    more_vars = [   'DistanceDriven',
                    'Fleet',
                    'NewFleet',
                    'ProducedMobility']
    #
    filter_vars = [ 'FilterFuelType',
                    'FilterVehicleType',
                    # 'DiscountedTechnEmissionsPen',
                    #
                    'Capex2021', # CapitalInvestment
                    'FixedOpex2021', # AnnualFixedOperatingCost
                    'VarOpex2021', # AnnualVariableOperatingCost
                    'Opex2021', # OperatingCost
                    'Externalities2021', # AnnualTechnologyEmissionPenaltyByEmission
                    #
                    'Capex_GDP', # CapitalInvestment
                    'FixedOpex_GDP', # AnnualFixedOperatingCost
                    'VarOpex_GDP', # AnnualVariableOperatingCost
                    'Opex_GDP', # OperatingCost
                    'Externalities_GDP' # AnnualTechnologyEmissionPenaltyByEmission
                    ]
    #
    all_vars_output_dict = [ {} for e in range( len( first_list ) ) ]
    #
    output_header = [ 'Strategy', 'Future.ID', 'Fuel', 'Technology', 'Emission', 'Year' ]
    #-------------------------------------------------------#
    for v in range( len( all_vars ) ):
        output_header.append( all_vars[v] )
    for v in range( len( more_vars ) ):
        output_header.append( more_vars[v] )
    for v in range( len( filter_vars ) ):
        output_header.append( filter_vars[v] )
    #-------------------------------------------------------#
    this_strategy = first_list[case].split('_')[0] 
    this_future   = first_list[case].split('_')[1]
    #-------------------------------------------------------#
    #
    vars_as_appear = []
    data_name = str( './Executables/' + first_list[case] ) + '/' + str(first_list[case]) + '_output.txt'
    #
    n = 0
    break_this_while = False
    while break_this_while == False:
        n += 1
        structure_line_raw = linecache.getline(data_name, n)
        if 'No. Column name  St   Activity     Lower bound   Upper bound    Marginal' in structure_line_raw:
            ini_line = deepcopy( n+2 )
        if 'Karush-Kuhn-Tucker' in structure_line_raw:
            end_line = deepcopy( n-1 )
            break_this_while = True
            break
    #
    for n in range(ini_line, end_line, 2 ):
        structure_line_raw = linecache.getline(data_name, n)
        structure_list_raw = structure_line_raw.split(' ')
        #
        structure_list_raw_2 = [ s_line for s_line in structure_list_raw if s_line != '' ]
        structure_line = structure_list_raw_2[1]
        structure_list = structure_line.split('[')
        the_variable = structure_list[0]
        #
        if the_variable in all_vars:
            set_list = structure_list[1].replace(']','').replace('\n','').split(',')
            #--%
            index = S_DICT_vars_structure['variable'].index( the_variable )
            this_variable_indices = S_DICT_vars_structure['index_list'][ index ]
            #
            #--%
            if 'y' in this_variable_indices:
                data_line = linecache.getline(data_name, n+1)
                data_line_list_raw = data_line.split(' ')
                data_line_list = [ data_cell for data_cell in data_line_list_raw if data_cell != '' ]
                useful_data_cell = data_line_list[1]
                #--%
                if useful_data_cell != '0':
                    #
                    if the_variable not in vars_as_appear:
                        vars_as_appear.append( the_variable )
                        all_vars_output_dict[case].update({ the_variable:{} })
                        all_vars_output_dict[case][the_variable].update({ the_variable:[] })
                        #
                        for n in range( len( this_variable_indices ) ):
                            all_vars_output_dict[case][the_variable].update( { this_variable_indices[n]:[] } )
                    #--%
                    this_variable = vars_as_appear[-1]
                    all_vars_output_dict[case][this_variable][this_variable].append( useful_data_cell )
                    for n in range( len( this_variable_indices ) ):
                        all_vars_output_dict[case][the_variable][ this_variable_indices[n] ].append( set_list[n] )
                #
            #
            elif 'y' not in this_variable_indices:
                data_line = linecache.getline(data_name, n+1)
                data_line_list_raw = data_line.split(' ')
                data_line_list = [ data_cell for data_cell in data_line_list_raw if data_cell != '' ]
                useful_data_cell = data_line_list[1]
                #--%
                if useful_data_cell != '0':
                    #
                    if the_variable not in vars_as_appear:
                        vars_as_appear.append( the_variable )
                        all_vars_output_dict[case].update({ the_variable:{} })
                        all_vars_output_dict[case][the_variable].update({ the_variable:[] })
                        #
                        for n in range( len( this_variable_indices ) ):
                            all_vars_output_dict[case][the_variable].update( { this_variable_indices[n]:[] } )
                    #--%
                    this_variable = vars_as_appear[-1]
                    all_vars_output_dict[case][this_variable][this_variable].append( useful_data_cell )
                    for n in range( len( this_variable_indices ) ):
                        all_vars_output_dict[case][the_variable][ this_variable_indices[n] ].append( set_list[n] )
        #--%
        else:
            pass
    #
    linecache.clearcache()
    #%%
    #-----------------------------------------------------------------------------------------------------------%
    # Extract *AccumulatedNewCapacity* for every vehicle technology:
    this_var_out1 = 'AccumulatedNewCapacity'
    this_var_dict_out1 = all_vars_output_dict[case]['AccumulatedNewCapacity']
    this_var_techs = this_var_dict_out1['t']
    this_var_techs_unique = list( Fleet_Groups_inv.keys() )  # transport techs only
    this_var_years = this_var_dict_out1['y']
    this_var_years_unique = list(set(this_var_dict_out1['y']))
    this_var_years_unique.sort()
    aide_dict_accumnewcap = {}
    for t_aid in this_var_techs_unique:
        aide_dict_accumnewcap.update({t_aid:[]})
        for y_aid in this_var_years_unique:
            tech_indices = \
                [i for i, x in enumerate(this_var_techs) if (t_aid in x )]
            year_indices = \
                [i for i, x in enumerate(this_var_years) if (y_aid in x )]
            position_idx_list = \
                list(set(tech_indices) & set(year_indices))
            if len(position_idx_list) != 0:
                position_idx = position_idx_list[0]
                this_value = float(this_var_dict_out1[this_var_out1][position_idx])
            elif len(position_idx_list) == 0:
                this_value = 0
            else:
                print('*This is an error (out 1)*')
                sys.exit()
            aide_dict_accumnewcap[t_aid].append(this_value)

    # Extract *CapitalInvestment* for every vehicle technology: // gotta divide by *NewCapacity* below:
    this_var_out2 = 'CapitalInvestment'
    this_var_dict_out2 = all_vars_output_dict[case]['CapitalInvestment']
    this_var_techs = this_var_dict_out2['t']
    this_var_techs_unique = list( Fleet_Groups_inv.keys() )  # transport techs only
    this_var_years = this_var_dict_out2['y']
    this_var_years_unique = list(set(this_var_dict_out2['y']))
    this_var_years_unique.sort()
    aide_dict_capitalcost = {}
    for t_aid in this_var_techs_unique:
        aide_dict_capitalcost.update({t_aid:[]})
        for y_aid in this_var_years_unique:
            tech_indices = \
                [i for i, x in enumerate(this_var_techs) if (t_aid in x )]
            year_indices = \
                [i for i, x in enumerate(this_var_years) if (y_aid in x )]
            position_idx_list = \
                list(set(tech_indices) & set(year_indices))
            if len(position_idx_list) != 0:
                position_idx = position_idx_list[0]
                this_value = float(this_var_dict_out2[this_var_out2][position_idx])
            elif len(position_idx_list) == 0:
                this_value = 0
            else:
                print('*This is an error (out 2)*')
                sys.exit()
            aide_dict_capitalcost[t_aid].append(this_value)

    # Extract *NewCapacity* for every vehicle technology:
    this_var_out3 = 'NewCapacity'
    this_var_dict_out3 = all_vars_output_dict[case]['NewCapacity']
    this_var_techs = this_var_dict_out3['t']
    this_var_techs_unique = list( Fleet_Groups_inv.keys() )  # transport techs only
    this_var_years = this_var_dict_out3['y']
    this_var_years_unique = list(set(this_var_dict_out3['y']))
    this_var_years_unique.sort()
    aide_dict_newcap = {}
    for t_aid in this_var_techs_unique:
        aide_dict_newcap.update({t_aid:[]})
        for y_aid in this_var_years_unique:
            tech_indices = \
                [i for i, x in enumerate(this_var_techs) if (t_aid in x )]
            year_indices = \
                [i for i, x in enumerate(this_var_years) if (y_aid in x )]
            position_idx_list = \
                list(set(tech_indices) & set(year_indices))
            if len(position_idx_list) != 0:
                position_idx = position_idx_list[0]
                this_value = float(this_var_dict_out3[this_var_out3][position_idx])
            elif len(position_idx_list) == 0:
                this_value = 0
            else:
                print('*This is an error (out 3)*')
                sys.exit()
            aide_dict_newcap[t_aid].append(this_value)

    # Extract *TotalCapacityAnnual* for every vehicle technology:
    this_var_out4 = 'TotalCapacityAnnual'
    this_var_dict_out4 = all_vars_output_dict[case]['TotalCapacityAnnual']
    this_var_techs = this_var_dict_out4['t']
    this_var_techs_unique = list( Fleet_Groups_inv.keys() )  # transport techs only
    this_var_years = this_var_dict_out4['y']
    this_var_years_unique = list(set(this_var_dict_out4['y']))
    this_var_years_unique.sort()
    aide_dict_totalcap = {}
    for t_aid in this_var_techs_unique:
        aide_dict_totalcap.update({t_aid:[]})
        for y_aid in this_var_years_unique:
            tech_indices = \
                [i for i, x in enumerate(this_var_techs) if (t_aid in x )]
            year_indices = \
                [i for i, x in enumerate(this_var_years) if (y_aid in x )]
            position_idx_list = \
                list(set(tech_indices) & set(year_indices))
            if len(position_idx_list) != 0:
                position_idx = position_idx_list[0]
                this_value = float(this_var_dict_out4[this_var_out4][position_idx])
            elif len(position_idx_list) == 0:
                this_value = 0
            else:
                print('*This is an error (out 4)*')
                sys.exit()
            aide_dict_totalcap[t_aid].append(this_value)

    #-----------------------------------------------------------------------------------------------------------%
    output_adress = './Executables/' + str( first_list[case] )
    combination_list = [] # [fuel, technology, emission, year]
    data_row_list = []
    for var in range( len( vars_as_appear ) ):
        this_variable = vars_as_appear[var]
        this_var_dict = all_vars_output_dict[case][this_variable]
        #--%
        index = S_DICT_vars_structure['variable'].index( this_variable )
        this_variable_indices = S_DICT_vars_structure['index_list'][ index ]
        #--------------------------------------#
        for k in range( len( this_var_dict[this_variable] ) ):
            this_combination = []
            #
            if 'f' in this_variable_indices:
                this_combination.append( this_var_dict['f'][k] )
            else:
                this_combination.append( '' )
            #
            if 't' in this_variable_indices:
                this_combination.append( this_var_dict['t'][k] )
            else:
                this_combination.append( '' )
            #
            if 'e' in this_variable_indices:
                this_combination.append( this_var_dict['e'][k] )
            else:
                this_combination.append( '' )
            #
            if 'l' in this_variable_indices:
                this_combination.append( '' )
            else:
                this_combination.append( '' )
            #
            if 'y' in this_variable_indices:
                this_combination.append( this_var_dict['y'][k] )
            else:
                this_combination.append( '' )
            #
            if this_combination not in combination_list:
                combination_list.append( this_combination )
                data_row = ['' for n in range( len( output_header ) ) ]
                # print('check', len(data_row), len(run_id) )
                data_row[0] = this_strategy
                data_row[1] = this_future
                data_row[2] = this_combination[0] # Fuel
                data_row[3] = this_combination[1] # Technology
                data_row[4] = this_combination[2] # Emission
                # data_row[7] = this_combination[3]
                data_row[5] = this_combination[4] # Year
                #
                var_position_index = output_header.index( this_variable )
                data_row[ var_position_index ] = this_var_dict[ this_variable ][ k ]
                data_row_list.append( data_row )
            else:
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] )
                #
                var_position_index = output_header.index( this_variable )
                #
                if 'l' in this_variable_indices: 
                    #
                    if str(this_data_row[ var_position_index ]) != '' and str(this_var_dict[ this_variable ][ k ]) != '' and ( 'Rate' not in this_variable ):
                        this_data_row[ var_position_index ] = str(  float( this_data_row[ var_position_index ] ) + float( this_var_dict[ this_variable ][ k ] ) )
                    elif str(this_data_row[ var_position_index ]) == '' and str(this_var_dict[ this_variable ][ k ]) != '':
                        this_data_row[ var_position_index ] = str( float( this_var_dict[ this_variable ][ k ] ) )
                    elif str(this_data_row[ var_position_index ]) != '' and str(this_var_dict[ this_variable ][ k ]) == '':
                        pass
                else:
                    this_data_row[ var_position_index ] = this_var_dict[ this_variable ][ k ]
                #
                data_row_list[ ref_index ]  = deepcopy( this_data_row )
                #
            #
            if this_variable == 'TotalCapacityAnnual' or this_variable == 'NewCapacity':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                this_tech = this_combination[1]
                if this_tech in list( Fleet_Groups_inv.keys() ):
                    group_tech = Fleet_Groups_inv[ this_tech ]
                    #
                    this_year = this_combination[4]
                    this_year_index = time_range_vector.index( int( this_year ) )
                    #
                    ref_var_position_index = output_header.index( this_variable )
                    #
                    if 'Trains' not in group_tech and 'Telef' not in group_tech:
                        driven_distance = float(Reference_driven_distance[this_strategy][group_tech][this_year_index])
                        driven_distance_START_VAR_YR = \
                            float(Reference_driven_distance[this_strategy][group_tech][time_range_vector.index(START_VAR_YR_INT)])
                        driven_distance_final = \
                            float(Reference_driven_distance[this_strategy][group_tech][time_range_vector.index(2050)])
                        passenger_per_vehicle = float(Reference_occupancy_rate[this_strategy][group_tech][this_year_index])
                        #
                        if this_variable == 'NewCapacity':
                            var_position_index = output_header.index( 'NewFleet' )
                            new_cap_calculated = \
                                float(this_data_row[ref_var_position_index])
                            new_fleet_calculated = \
                                (10**9)*new_cap_calculated/driven_distance

                            accum_new_cap_subtract = 0
                            driven_distance_prev = float(Reference_driven_distance[this_strategy][group_tech][this_year_index-1])
                            if int(this_year) >= START_VAR_YR_INT and driven_distance_START_VAR_YR != driven_distance_final:
                                # We need to select the appropiate accumulated new capacity:
                                accum_new_cap = \
                                    aide_dict_accumnewcap[this_tech][this_year_index-1]

                                if int(this_year) > BY_INT+Reference_op_life[this_strategy][this_tech]:  # works with a timeframe by 2050; longer timeframes may need more lifetime cycle adjustments
                                    subtract_index_accum_old = \
                                        int(Reference_op_life[this_strategy][this_tech])
                                    if int(this_year) - subtract_index_accum_old <= START_VAR_YR_INT:
                                        driven_distance_17 = \
                                            float(Reference_driven_distance[this_strategy][group_tech][time_range_vector.index(2019)])
                                    else:
                                        driven_distance_17 = \
                                            float(Reference_driven_distance[this_strategy][group_tech][this_year_index-subtract_index_accum_old])

                                    adjust_factor_old_cap = \
                                        (1-driven_distance/driven_distance_17)

                                    if int(this_year) - subtract_index_accum_old > START_VAR_YR_INT:  # this is an odd rule, but works empirically
                                        driven_distance_START_VAR_YR = \
                                            float(Reference_driven_distance[this_strategy][group_tech][time_range_vector.index(START_VAR_YR_INT)])
                                        driven_distance_minus3 = \
                                            float(Reference_driven_distance[this_strategy][group_tech][this_year_index-3])
                                        adjust_factor_old_cap -= \
                                            (1-driven_distance_17/driven_distance_START_VAR_YR)
                                        adjust_factor_old_cap -= \
                                            (1-driven_distance/driven_distance_minus3)

                                    accum_new_cap_subtract += \
                                        aide_dict_newcap[this_tech][this_year_index-subtract_index_accum_old]*adjust_factor_old_cap

                                new_cap_adj = \
                                    accum_new_cap*(1-driven_distance/driven_distance_prev) - accum_new_cap_subtract
                            else:
                                new_cap_adj = 0
                            new_fleet_adj = \
                                (10**9)*new_cap_adj/driven_distance
                            this_data_row[ var_position_index ] = \
                                round(new_fleet_calculated + new_fleet_adj, 4)
                        #
                        if this_variable == 'TotalCapacityAnnual':
                            #
                            var_position_index = output_header.index( 'Fleet' )
                            this_data_row[ var_position_index ] =  round( (10**9)*float( this_data_row[ ref_var_position_index ] )/driven_distance, 4)
                            #
                            var_position_index = output_header.index( 'DistanceDriven' )
                            this_data_row[ var_position_index ] = round(driven_distance, 4)
                            #
                            var_position_index = output_header.index( 'ProducedMobility' )
                            this_data_row[ var_position_index ] =  round( float( this_data_row[ ref_var_position_index ] )*passenger_per_vehicle, 4)
                        #
                        data_row_list[ ref_index ] = deepcopy( this_data_row )
                        #
                    #
                    ###################################################################################################
                    #
                #
            #
            # Creating convinience filters for the analysis of model outputs:
            this_tech = this_combination[1]
            if this_tech in list( Fleet_Groups_inv.keys() ):
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                var_position_index = output_header.index( 'FilterFuelType' )
                ############################################
                # By Fuel Type
                for r in range( len( df_fuel_2_code_fuel_list ) ):
                    if df_fuel_2_code_fuel_list[r] in this_tech:
                        this_data_row[ var_position_index ] = df_fuel_2_code_plain_english[ r ]
                        break
                ############################################
                var_position_index = output_header.index( 'FilterVehicleType' )
                # By vehicle type
                for r in range( len( df_tech_2_code_fuel_list ) ):
                    if df_tech_2_code_fuel_list[r] in this_tech:
                        this_data_row[ var_position_index ] = df_tech_2_code_plain_english[ r ]
                        break
                data_row_list[ ref_index ] = deepcopy( this_data_row )
            #
            output_csv_r = dr_default*100
            output_csv_year = 2021
            #
            if this_combination[2] in ['Accidents', 'Health', 'Congestion'] and this_variable == 'AnnualTechnologyEmissionPenaltyByEmission':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'AnnualTechnologyEmissionPenaltyByEmission' )
                new_var_position_index = output_header.index( 'Externalities2021' )
                new2_var_position_index = output_header.index( 'Externalities_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            ''' $ This is new (beginning) $ '''
            #
            if this_variable == 'CapitalInvestment':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'CapitalInvestment' )
                new_var_position_index = output_header.index( 'Capex2021' )
                new2_var_position_index = output_header.index( 'Capex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                # Here we must add an adjustment to the capital investment to make the fleet constant:
                this_base_cap_inv = \
                    float(this_data_row[ ref_var_position_index ])
                this_plus_cap_inv = 0
                '''
                > We need to add new capital costs if the technology is in transport:
                '''
                if this_tech in list(Fleet_Groups_inv.keys()):
                    group_tech = Fleet_Groups_inv[this_tech]
                    if 'Trains' not in group_tech and 'Telef' not in group_tech:
                        driven_distance = float(Reference_driven_distance[this_strategy][group_tech][this_year_index])
                        driven_distance_START_VAR_YR = \
                            float(Reference_driven_distance[this_strategy][group_tech][time_range_vector.index(START_VAR_YR_INT)])
                        driven_distance_final = \
                            float(Reference_driven_distance[this_strategy][group_tech][time_range_vector.index(2050)])

                        accum_new_cap_subtract = 0
                        driven_distance_prev = float(Reference_driven_distance[this_strategy][group_tech][this_year_index-1])
                        if int(this_year) >= START_VAR_YR_INT and driven_distance_START_VAR_YR != driven_distance_final:  # greater than the base year
                            # We need to select the appropiate accumulated new capacity:
                            accum_new_cap = \
                                aide_dict_accumnewcap[this_tech][this_year_index-1]

                            if int(this_year) > BY_INT+Reference_op_life[this_strategy][this_tech]:
                                subtract_index_accum_old = \
                                    int(Reference_op_life[this_strategy][this_tech])
                                if int(this_year) - subtract_index_accum_old <= START_VAR_YR_INT:
                                    driven_distance_17 = \
                                        float(Reference_driven_distance[this_strategy][group_tech][time_range_vector.index(2019)])
                                else:
                                    driven_distance_17 = \
                                        float(Reference_driven_distance[this_strategy][group_tech][this_year_index-subtract_index_accum_old])

                                adjust_factor_old_cap = \
                                    (1-driven_distance/driven_distance_17)

                                if int(this_year) - subtract_index_accum_old > START_VAR_YR_INT:  # this is an odd rule, but works empirically
                                    driven_distance_minus3 = \
                                        float(Reference_driven_distance[this_strategy][group_tech][this_year_index-3])
                                    adjust_factor_old_cap -= \
                                        (1-driven_distance_17/driven_distance_START_VAR_YR)
                                    adjust_factor_old_cap -= \
                                        (1-driven_distance/driven_distance_minus3)

                                accum_new_cap_subtract += \
                                    aide_dict_newcap[this_tech][this_year_index-subtract_index_accum_old]*adjust_factor_old_cap

                            new_cap_adj = \
                                accum_new_cap*(1-driven_distance/driven_distance_prev) - accum_new_cap_subtract
                            this_cap_cost = \
                                aide_dict_capitalcost[this_tech][this_year_index]
                            this_new_cap = \
                                aide_dict_newcap[this_tech][this_year_index]
                            this_plus_cap_inv += \
                                new_cap_adj*this_cap_cost/this_new_cap

                this_cap_inv = this_base_cap_inv + this_plus_cap_inv
                this_data_row[ref_var_position_index] = \
                    str(this_cap_inv)  # Here we re-write the new capacity to adjust the system
                '''
                > Below we continue as usual:
                '''
                resulting_value_raw = this_cap_inv/((1 + output_csv_r/100)**(float(this_year) - output_csv_year))
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            if this_variable == 'AnnualFixedOperatingCost':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'AnnualFixedOperatingCost' )
                new_var_position_index = output_header.index( 'FixedOpex2021' )
                new2_var_position_index = output_header.index( 'FixedOpex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            if this_variable == 'AnnualVariableOperatingCost':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'AnnualVariableOperatingCost' )
                new_var_position_index = output_header.index( 'VarOpex2021' )
                new2_var_position_index = output_header.index( 'VarOpex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            if this_variable == 'OperatingCost':
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( data_row_list[ ref_index ] ) # this must be updated in a further position of the list
                #
                ref_var_position_index = output_header.index( 'OperatingCost' )
                new_var_position_index = output_header.index( 'Opex2021' )
                new2_var_position_index = output_header.index( 'Opex_GDP' )
                #
                this_year = this_combination[4]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                resulting_value_raw = float(this_data_row[ ref_var_position_index ]) / ( ( 1 + output_csv_r/100 )**( float(this_year) - output_csv_year ) )
                resulting_value = round( resulting_value_raw, 4)
                #
                this_data_row[new_var_position_index] = str( resulting_value )
                this_data_row[new2_var_position_index] = str( float(this_data_row[ ref_var_position_index ])/list_gdp_ref[this_year_index] )
                #
                data_row_list[ ref_index ] = deepcopy( this_data_row )
                #
            #
            ''' $ (end) $ '''
            #
        #
    #
    non_year_combination_list = []
    non_year_combination_list_years = []
    for n in range( len( combination_list ) ):
        this_combination = combination_list[ n ]
        this_non_year_combination = [ this_combination[0], this_combination[1], this_combination[2] ]
        if this_combination[4] != '' and this_non_year_combination not in non_year_combination_list:
            non_year_combination_list.append( this_non_year_combination )
            non_year_combination_list_years.append( [ this_combination[4] ] )
        elif this_combination[4] != '' and this_non_year_combination in non_year_combination_list:
            non_year_combination_list_years[ non_year_combination_list.index( this_non_year_combination ) ].append( this_combination[4] )
    #
    for n in range( len( non_year_combination_list ) ):
        if len( non_year_combination_list_years[n] ) != len(time_range_vector):
            #
            this_existing_combination = non_year_combination_list[n]
            # print('flag 1', this_existing_combination )
            this_existing_combination.append( '' )
            # print('flag 2', this_existing_combination )
            this_existing_combination.append( non_year_combination_list_years[n][0] )
            # print('flag 3', this_existing_combination )
            ref_index = combination_list.index( this_existing_combination )
            this_existing_data_row = deepcopy( data_row_list[ ref_index ] )
            #
            for n2 in range( len( time_range_vector ) ):
                #
                if time_range_vector[n2] not in non_year_combination_list_years[n]:
                    #
                    data_row = ['' for n in range( len( output_header ) ) ]
                    data_row[0] = this_strategy
                    data_row[1] = this_future
                    data_row[2] = non_year_combination_list[n][0]
                    data_row[3] = non_year_combination_list[n][1]
                    data_row[4] = non_year_combination_list[n][2]
                    data_row[5] = time_range_vector[n2]
                    #
                    for n3 in range( len( vars_as_appear ) ):
                        this_variable = vars_as_appear[n3]
                        this_var_dict = all_vars_output_dict[case][this_variable]
                        index = S_DICT_vars_structure['variable'].index( this_variable )
                        this_variable_indices = S_DICT_vars_structure['index_list'][ index ]
                        #
                        var_position_index = output_header.index( this_variable )
                        #
                        print_true = False
                        if ( 'f' in this_variable_indices and str(non_year_combination_list[n][0]) != '' ): # or ( 'f' not in this_variable_indices and str(non_year_combination_list[n][0]) == '' ):
                            print_true = True
                        else:
                            pass
                        #
                        if ( 't' in this_variable_indices and str(non_year_combination_list[n][1]) != '' ): # or ( 't' not in this_variable_indices and str(non_year_combination_list[n][1]) == '' ):
                            print_true = True
                        else:
                            pass
                        #
                        if ( 'e' in this_variable_indices and str(non_year_combination_list[n][2]) != '' ): # or ( 'e' not in this_variable_indices and str(non_year_combination_list[n][2]) == '' ):
                            print_true = True
                        else:
                            pass
                        #
                        if 'y' in this_variable_indices and ( str( this_existing_data_row[ var_position_index ] ) != '' ) and print_true == True:
                            data_row[ var_position_index ] = '0'
                            #
                        else:
                            pass
                    #
                    data_row_list.append( data_row )
    #--------------------------------------#
    with open( output_adress + '/' + str( first_list[case] ) + '_Output' + '.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow( output_header )
        for n in range( len( data_row_list ) ):
            csvwriter.writerow( data_row_list[n] )
    #-----------------------------------------------------------------------------------------------------------%
    shutil.os.remove(data_name) #-----------------------------------------------------------------------------------------------------------%
    gc.collect(generation=2)
    time.sleep(0.05)
    #-----------------------------------------------------------------------------------------------------------%
    print(  'We finished with printing the outputs: ' + str( first_list[case] ) )
#
def function_C_mathprog( scen, stable_scenarios, unpackaged_useful_elements ):
    #
    scenario_list =                     unpackaged_useful_elements[0]
    S_DICT_sets_structure =             unpackaged_useful_elements[1]
    S_DICT_params_structure =           unpackaged_useful_elements[2]
    list_param_default_value_params =   unpackaged_useful_elements[3]
    list_param_default_value_value =    unpackaged_useful_elements[4]
    print_adress =                      unpackaged_useful_elements[5]

    # Extract the default (national) discount rate parameter
    dr_prm_idx = list_param_default_value_params.index('DiscountRate')
    dr_default = list_param_default_value_value[dr_prm_idx]

    Reference_driven_distance =         unpackaged_useful_elements[6]
    Fleet_Groups_inv =                  unpackaged_useful_elements[7]
    time_range_vector =                 unpackaged_useful_elements[8]
    Blend_Shares =                      unpackaged_useful_elements[9]
    #
    # Briefly open up the system coding to use when processing for visualization:
    df_fuel_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Fuel_to_Code' )
    df_fuel_2_code_fuel_list        = df_fuel_to_code['Code'].tolist()
    df_fuel_2_code_plain_english    = df_fuel_to_code['Plain_English'].tolist()
    df_tech_to_code = pd.read_excel( './A1_Inputs/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Tech_to_Code' )
    df_tech_2_code_fuel_list        = df_tech_to_code['Techs'].tolist()
    df_tech_2_code_plain_english    = df_tech_to_code['Plain_English'].tolist()
    #
    # header = ['Scenario','Parameter','REGION','TECHNOLOGY','FUEL','EMISSION','MODE_OF_OPERATION','TIMESLICE','YEAR','SEASON','DAYTYPE','DAILYTIMEBRACKET','STORAGE','Value']
    header_indices = ['Scenario','Parameter','r','t','f','e','m','l','y','ls','ld','lh','s','value']
    #
    # for scen in range( len( scenario_list ) ):
    print('# This is scenario ', scenario_list[scen] )
    #
    try:
        scen_file_dir = print_adress + '/' + str( scenario_list[scen] ) + '_0'
        os.mkdir( scen_file_dir )
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    this_scenario_data = stable_scenarios[ scenario_list[scen] ]
    #
    g= open( print_adress + '/' + str( scenario_list[scen] ) + '_0' + '/' + str( scenario_list[scen] ) + '_0' + '.txt',"w+")
    g.write( '###############\n#    Sets     #\n###############\n#\n' )
    g.write( 'set DAILYTIMEBRACKET :=  ;\n' )
    g.write( 'set DAYTYPE :=  ;\n' )
    g.write( 'set SEASON :=  ;\n' )
    g.write( 'set STORAGE :=  ;\n' )
    #
    for n1 in range( len( S_DICT_sets_structure['set'] ) ):
        if S_DICT_sets_structure['number_of_elements'][n1] != 0:
            g.write( 'set ' + S_DICT_sets_structure['set'][n1] + ' := ' )
            #
            for n2 in range( S_DICT_sets_structure['number_of_elements'][n1] ):
                if S_DICT_sets_structure['set'][n1] == 'YEAR' or S_DICT_sets_structure['set'][n1] == 'MODE_OF_OPERATION':
                    g.write( str( int( S_DICT_sets_structure['elements_list'][n1][n2] ) ) + ' ' )
                else:
                    g.write( str( S_DICT_sets_structure['elements_list'][n1][n2] ) + ' ' )
            g.write( ';\n' )
    #
    g.write( '\n' )
    g.write( '###############\n#    Parameters     #\n###############\n#\n' )
    #
    for p in range( len( list( this_scenario_data.keys() ) ) ):
        #
        this_param = list( this_scenario_data.keys() )[p]
        #
        default_value_list_params_index = list_param_default_value_params.index( this_param )
        default_value = float( list_param_default_value_value[ default_value_list_params_index ] )
        if default_value >= 0:
            default_value = int( default_value )
        else:
            pass
        #
        this_param_index = S_DICT_params_structure['parameter'].index( this_param )
        this_param_keys = S_DICT_params_structure['index_list'][this_param_index]
        #
        if len( this_scenario_data[ this_param ]['value'] ) != 0:
            #
#            f.write( 'param ' + this_param + ':=\n' )
            if len(this_param_keys) != 2:
                g.write( 'param ' + this_param + ' default ' + str( default_value ) + ' :=\n' )
            else:
                g.write( 'param ' + this_param + ' default ' + str( default_value ) + ' :\n' )
            #
            #-----------------------------------------#
            if len(this_param_keys) == 2: #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                # get the last and second last parameters of the list:
                last_set_element = this_scenario_data[ this_param ][ this_param_keys[-1] ] # header_indices.index( this_param_keys[-1] ) ]
                last_set_element_unique = [] # list( set( last_set_element ) )
                for u in range( len( last_set_element ) ):
                    if last_set_element[u] not in last_set_element_unique:
                        last_set_element_unique.append( last_set_element[u] )
                #
                for y in range( len( last_set_element_unique ) ):
                    g.write( str( last_set_element_unique[y] ) + ' ')
                g.write(':=\n')
                #
                second_last_set_element = this_scenario_data[ this_param ][ this_param_keys[-2] ] # header_indices.index( this_param_keys[-2] ) ]
                second_last_set_element_unique = [] # list( set( second_last_set_element ) )
                for u in range( len( second_last_set_element ) ):
                    if second_last_set_element[u] not in second_last_set_element_unique:
                        second_last_set_element_unique.append( second_last_set_element[u] )
                #
                for s in range( len( second_last_set_element_unique ) ):
                    g.write( second_last_set_element_unique[s] + ' ' )
                    value_indices = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[-2] ] ) if x == str( second_last_set_element_unique[s] ) ]
                    these_values = []
                    for val in range( len( value_indices ) ):
                        these_values.append( this_scenario_data[ this_param ]['value'][ value_indices[val] ] )
                    for val in range( len( these_values ) ):
                        g.write( str( these_values[val] ) + ' ' )
                    g.write('\n') #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            #%%%
            if len(this_param_keys) == 3:
                this_set_element_unique_all = []
                for pkey in range( len(this_param_keys)-2 ):
                    for i in range( 2, len(header_indices)-1 ):
                        if header_indices[i] == this_param_keys[pkey]:
                            this_set_element = this_scenario_data[ this_param ][ header_indices[i] ]
                    this_set_element_unique_all.append( list( set( this_set_element ) ) )
                #
                this_set_element_unique_1 = deepcopy( this_set_element_unique_all[0] )
                #
                for n1 in range( len( this_set_element_unique_1 ) ): #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                    g.write( '[' + str( this_set_element_unique_1[n1] ) + ',*,*]:\n' )
                    # get the last and second last parameters of the list:
                    last_set_element = this_scenario_data[ this_param ][ this_param_keys[-1] ] # header_indices.index( this_param_keys[-1] ) ]
                    last_set_element_unique = [] # list( set( last_set_element ) )
                    for u in range( len( last_set_element ) ):
                        if last_set_element[u] not in last_set_element_unique:
                            last_set_element_unique.append( last_set_element[u] )
                    #
                    for y in range( len( last_set_element_unique ) ):
                        g.write( str( last_set_element_unique[y] ) + ' ')
                    g.write(':=\n')
                    #
                    second_last_set_element = this_scenario_data[ this_param ][ this_param_keys[-2] ] #header_indices.index( this_param_keys[-2] ) ]
                    second_last_set_element_unique = [] # list( set( second_last_set_element ) )
                    for u in range( len( second_last_set_element ) ):
                        if second_last_set_element[u] not in second_last_set_element_unique:
                            second_last_set_element_unique.append( second_last_set_element[u] )
                    #
                    for s in range( len( second_last_set_element_unique ) ):
                        g.write( second_last_set_element_unique[s] + ' ' )
                        #
                        value_indices_s = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[-2] ] ) if x == str( second_last_set_element_unique[s] ) ]
                        value_indices_n1 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[0] ] ) if x == str( this_set_element_unique_1[n1] ) ]
                        #
                        r_index = set(value_indices_s) & set(value_indices_n1)
                        #
                        value_indices = list( r_index )
                        value_indices.sort()
                        #
                        these_values = []
                        for val in range( len( value_indices ) ):
                            try:
                                these_values.append( this_scenario_data[ this_param ]['value'][ value_indices[val] ] )
                            except:
                                print( this_param, val )
                        for val in range( len( these_values ) ):
                            g.write( str( these_values[val] ) + ' ' )
                        g.write('\n') #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            #%%%
            if len(this_param_keys) == 4:
                this_set_element_unique_all = []
                for pkey in range( len(this_param_keys)-2 ):
                    for i in range( 2, len(header_indices)-1 ):
                        if header_indices[i] == this_param_keys[pkey]:
                            this_set_element = this_scenario_data[ this_param ][ header_indices[i] ]
                            this_set_element_unique_all.append( list( set( this_set_element ) ) )
                #
                this_set_element_unique_1 = deepcopy( this_set_element_unique_all[0] )
                this_set_element_unique_2 = deepcopy( this_set_element_unique_all[1] )
                #
                for n1 in range( len( this_set_element_unique_1 ) ):
                    for n2 in range( len( this_set_element_unique_2 ) ): #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                        g.write( '[' + str( this_set_element_unique_1[n1] ) + ',' + str( this_set_element_unique_2[n2] ) + ',*,*]:\n' )
                        # get the last and second last parameters of the list:
                        last_set_element = this_scenario_data[ this_param ][ this_param_keys[-1] ] # header_indices.index( this_param_keys[-1] ) ]
                        last_set_element_unique = [] # list( set( last_set_element ) )
                        for u in range( len( last_set_element ) ):
                            if last_set_element[u] not in last_set_element_unique:
                                last_set_element_unique.append( last_set_element[u] )
                        #
                        for y in range( len( last_set_element_unique ) ):
                            g.write( str( last_set_element_unique[y] ) + ' ')
                        g.write(':=\n')
                        #
                        second_last_set_element = this_scenario_data[ this_param ][ this_param_keys[-2] ] # header_indices.index( this_param_keys[-2] ) ]
                        second_last_set_element_unique = [] # list( set( second_last_set_element ) )
                        for u in range( len( second_last_set_element ) ):
                            if second_last_set_element[u] not in second_last_set_element_unique:
                                second_last_set_element_unique.append( second_last_set_element[u] )
                        #
                        for s in range( len( second_last_set_element_unique ) ):
                            g.write( second_last_set_element_unique[s] + ' ' )
                            #
                            value_indices_s = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[-2] ] ) if x == str( second_last_set_element_unique[s] ) ]
                            value_indices_n1 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[0] ] ) if x == str( this_set_element_unique_1[n1] ) ]
                            value_indices_n2 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[1] ] ) if x == str( this_set_element_unique_2[n2] ) ]
                            r_index = set(value_indices_s) & set(value_indices_n1) & set(value_indices_n2)
                            value_indices = list( r_index )
                            value_indices.sort()
                            #
                            # these_values = this_scenario_data[ this_param ]['value'][ value_indices[0]:value_indices[-1]+1 ]
                            these_values = []
                            for val in range( len( value_indices ) ):
                                these_values.append( this_scenario_data[ this_param ]['value'][ value_indices[val] ] )
                            for val in range( len( these_values ) ):
                                g.write( str( these_values[val] ) + ' ' )
                            g.write('\n') #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            #%%%
            # if len(this_param_keys) == 5:
            #     this_set_element_unique_all = []
            #     for pkey in range( len(this_param_keys)-2 ):
            #         for i in range( 2, len(header_indices)-1 ):
            #             if header_indices[i] == this_param_keys[pkey]:
            #                 this_set_element = this_scenario_data[ this_param ][ header_indices[i] ]
            #                 this_set_element_unique_all.append( list( set( this_set_element ) ) )
            #     #
            #     this_set_element_unique_1 = deepcopy( this_set_element_unique_all[0] )
            #     this_set_element_unique_2 = deepcopy( this_set_element_unique_all[1] )
            #     this_set_element_unique_3 = deepcopy( this_set_element_unique_all[2] )
            #     #
            #     for n1 in range( len( this_set_element_unique_1 ) ):
            #         for n2 in range( len( this_set_element_unique_2 ) ):
            #             for n3 in range( len( this_set_element_unique_3 ) ): #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            #                 # MOVE AFTER len() conditional // g.write( '[' + str( this_set_element_unique_1[n1] ) + ',' + str( this_set_element_unique_2[n2] ) + ',' + str( this_set_element_unique_3[n3] ) + ',*,*]:\n' )
            #                 # get the last and second last parameters of the list:
            #                 last_set_element = this_scenario_data[ this_param ][ this_param_keys[-1] ]
            #                 last_set_element_unique = [] # list( set( last_set_element ) )
            #                 for u in range( len( last_set_element ) ):
            #                     if last_set_element[u] not in last_set_element_unique:
            #                         last_set_element_unique.append( last_set_element[u] )
            #                 #
            #                 #
            #                 second_last_set_element = this_scenario_data[ this_param ][ this_param_keys[-2] ]
            #                 second_last_set_element_unique = [] # list( set( second_last_set_element ) )
            #                 for u in range( len( second_last_set_element ) ):
            #                     if second_last_set_element[u] not in second_last_set_element_unique:
            #                         second_last_set_element_unique.append( second_last_set_element[u] )
            #                 #
            #                 for s in range( len( second_last_set_element_unique ) ):
            #                     #  MOVE AFTER len() conditional // g.write( second_last_set_element_unique[s] + ' ' )
            #                     value_indices_s = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[-2] ] ) if x == str( second_last_set_element_unique[s] ) ]
            #                     value_indices_n1 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[0] ] ) if x == str( this_set_element_unique_1[n1] ) ]
            #                     value_indices_n2 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[1] ] ) if x == str( this_set_element_unique_2[n2] ) ]
            #                     value_indices_n3 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[2] ] ) if x == str( this_set_element_unique_3[n3] ) ]
            #                     #
            #                     r_index = set(value_indices_s) & set(value_indices_n1) & set(value_indices_n2) & set(value_indices_n3)
            #                     value_indices = list( r_index )
            #                     value_indices.sort()
            #                     #
            #                     if len( value_indices ) != 0:
            #                         g.write( '[' + str( this_set_element_unique_1[n1] ) + ',' + str( this_set_element_unique_2[n2] ) + ',' + str( this_set_element_unique_3[n3] ) + ',*,*]:\n' )
            #                         #
            #                         for y in range( len( last_set_element_unique ) ):
            #                             g.write( str( last_set_element_unique[y] ) + ' ')
            #                         g.write(':=\n')
            #                         #
            #                         g.write( second_last_set_element_unique[s] + ' ' )
            #                         #
            #                         # these_values = this_scenario_data[ this_param ]['value'][ value_indices[0]:value_indices[-1]+1 ]
            #                         these_values = []
            #                         for val in range( len( value_indices ) ):
            #                             these_values.append( this_scenario_data[ this_param ]['value'][ value_indices[val] ] )
            #                         for val in range( len( these_values ) ):
            #                             g.write( str( these_values[val] ) + ' ' )
            #                         g.write('\n') #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            #

            if len(this_param_keys) == 5:
                print(5, p, this_param)
                this_set_element_unique_all = []
                last_set_element_unique = []
                second_last_set_element_unique = []
                for pkey in range(len(this_param_keys)-2):
                    for i in range(2, len(header_indices)-1):
                        if header_indices[i] == this_param_keys[pkey]:
                            this_set_element = this_scenario_data[this_param][header_indices[i]]
                            this_set_element_unique_all.append(list(set(this_set_element)))
                #
                this_set_element_unique_1 = deepcopy(this_set_element_unique_all[0])
                this_set_element_unique_2 = deepcopy(this_set_element_unique_all[1])
                this_set_element_unique_3 = deepcopy(this_set_element_unique_all[2])

                last_set_element = np.array(this_scenario_data[this_param][this_param_keys[-1]])
                last_set_element_unique = np.unique(last_set_element)

                second_last_set_element = np.array(this_scenario_data[this_param][this_param_keys[-2]])
                second_last_set_element_unique = np.unique(second_last_set_element)

                long_list1 = this_scenario_data[this_param][this_param_keys[1]]
                long_list2 = this_scenario_data[this_param][this_param_keys[2]]
                concat_result = list(map(lambda x, y: x + '-' + y, long_list1, long_list2))
                concat_result_set = list(set(concat_result))

                short_list1, short_list2 = \
                    zip(*(s.split('-') for s in concat_result_set))
                short_list1_set = list(set(short_list1))
                short_list2_set = list(set(short_list2))

                # print(this_param_keys[-1], this_param_keys[-2])

                # print(len(long_list1))
                # print(len(long_list2))
                # print(len(concat_result))
                # print(len(concat_result_set))
                # 
                # print(len(short_list1))
                # print(len(short_list2))
                # 
                # print(len(short_list1_set))
                # print(len(short_list2_set))
                # 
                # print('-')
                # 
                # print(len(this_set_element_unique_1))
                # print(len(this_set_element_unique_2)) # tech
                # print(len(this_set_element_unique_3))  # fuel
                # print(len(second_last_set_element_unique))
                # print(len(this_scenario_data[this_param][this_param_keys[0]]))
                # print(len(this_scenario_data[this_param][this_param_keys[1]]))
                # print(len(this_scenario_data[this_param][this_param_keys[2]]))
                # print(len(this_scenario_data[this_param][this_param_keys[-2]]))

                # print('Reviewing the slowest component')
                # sys.exit()

                for n1 in range(len(this_set_element_unique_1)):
                    # for n2 in range(len(this_set_element_unique_2)):
                    # for n3 in range(len(this_set_element_unique_3)):
                    for nx in range(len(concat_result_set)):
                        n1_faster = concat_result_set[nx].split('-')[0]
                        n2_faster = concat_result_set[nx].split('-')[1]

                        for s in range(len(second_last_set_element_unique)):
                            value_indices_s = [i for i, x in enumerate(this_scenario_data[this_param][this_param_keys[-2]]) if x == str(second_last_set_element_unique[s])]
                            value_indices_n1 = [i for i, x in enumerate(this_scenario_data[this_param][this_param_keys[0]]) if x == str(this_set_element_unique_1[n1])]
                            value_indices_n2 = [i for i, x in enumerate(this_scenario_data[this_param][this_param_keys[1]]) if x == str(n1_faster)]
                            value_indices_n3 = [i for i, x in enumerate(this_scenario_data[this_param][this_param_keys[2]]) if x == str(n2_faster)]

                            r_index = set(value_indices_s) & set(value_indices_n1) & set(value_indices_n2) & set(value_indices_n3)
                            value_indices = list(r_index)
                            value_indices.sort()

                            if len(value_indices) != 0:
                                g.write('[' + str(this_set_element_unique_1[n1]) + ',' + str(n1_faster) + ',' + str(n2_faster) + ',*,*]:\n')

                                for y in range(len(last_set_element_unique)):
                                    g.write(str(last_set_element_unique[y]) + ' ')
                                g.write(':=\n')

                                g.write(second_last_set_element_unique[s] + ' ')

                                these_values = []
                                for val in range(len(value_indices)):
                                    these_values.append(this_scenario_data[this_param]['value'][value_indices[val]])
                                for val in range(len(these_values)):
                                    g.write(str(these_values[val]) + ' ')
                                g.write('\n')

                            else:
                                print('Never happens right?')
                                sys.exit()

            #g.write('\n') 
            #-----------------------------------------#
            g.write( ';\n\n' )
    #
    # remember the default values for printing:
    g.write('param AccumulatedAnnualDemand default 0 :=\n;\n')
    # if scenario_list[scen] == BAU_STR:
    #     g.write('param AnnualEmissionLimit default 99999 :=\n;\n')
    g.write('param AnnualEmissionLimit default 999999999999999999999 :=\n;\n') # here we are using no Emission Limit
    g.write('param AnnualExogenousEmission default 0 :=\n;\n')
    g.write('param CapacityOfOneTechnologyUnit default 0 :=\n;\n')
    g.write('param CapitalCostStorage default 0 :=\n;\n')
    g.write('param Conversionld default 0 :=\n;\n')
    g.write('param Conversionlh default 0 :=\n;\n')
    g.write('param Conversionls default 0 :=\n;\n')
    g.write('param DaySplit default 0.00137 :=\n;\n')
    g.write('param DaysInDayType default 7 :=\n;\n')
    g.write('param DepreciationMethod default 1 :=\n;\n')
    g.write('param DiscountRate default ' + str(dr_default) + ' :=\n;\n') # repalced from 0.05 // 0.0831
    # g.write('param EmissionsPenalty default 0 :=\n;\n')
    g.write('param MinStorageCharge default 0 :=\n;\n')
    g.write('param ModelPeriodEmissionLimit default 999999999999999999999 :=\n;\n')
    g.write('param ModelPeriodExogenousEmission default 0 :=\n;\n')
    g.write('param OperationalLifeStorage default 1 :=\n;\n')
    g.write('param REMinProductionTarget default 0 :=\n;\n')
    g.write('param RETagFuel default 0 :=\n;\n')
    g.write('param RETagTechnology default 0 :=\n;\n')
    g.write('param ReserveMargin default 0 :=\n;\n')
    g.write('param ReserveMarginTagFuel default 0 :=\n;\n')
    g.write('param ReserveMarginTagTechnology default 0 :=\n;\n')
    g.write('param ResidualStorageCapacity default 0 :=\n;\n')
    g.write('param StorageLevelStart default 0 :=\n;\n')
    g.write('param StorageMaxChargeRate default 0 :=\n;\n')
    g.write('param StorageMaxDischargeRate default 0 :=\n;\n')
    g.write('param TechnologyFromStorage default 0 :=\n;\n')
    g.write('param TechnologyToStorage default 0 :=\n;\n')
    g.write('param TotalAnnualMaxCapacityInvestment default 999999999999999999999 :=\n;\n')
    g.write('param TotalAnnualMaxCapacityInvestment default 0 :=\n;\n')
    if scenario_list[scen] == BAU_STR:
        g.write('param TotalAnnualMinCapacity default 0 :=\n;\n')
    # g.write('param TotalTechnologyAnnualActivityUpperLimit default 99999 :=\n;\n')
    g.write('param TotalTechnologyModelPeriodActivityLowerLimit default 0 :=\n;\n')
    g.write('param TotalTechnologyModelPeriodActivityUpperLimit default 999999999999999999999 :=\n;\n')
    g.write('param TradeRoute default 0 :=\n;\n')
    #
    g.write('#\n' + 'end;\n')
    #
    g.close()
    #
    ###########################################################################################################################
    # Furthermore, we must print the inputs separately for faste deployment of the input matrix:
    #
    if scenario_list[scen] != BAU_STR:
        this_Blend_Shares_data = Blend_Shares[ scenario_list[scen] ]
    #
    basic_header_elements = [ 'Future.ID', 'Strategy.ID', 'Strategy', 'Fuel', 'Technology', 'Emission', 'Season', 'Year' ]
    #
    parameters_to_print = [ 'SpecifiedAnnualDemand',
                            'CapacityFactor',
                            'OperationalLife',
                            'ResidualCapacity',
                            'InputActivityRatio',
                            'OutputActivityRatio',
                            'EmissionActivityRatio',
                            'CapitalCost',
                            'VariableCost',
                            'FixedCost',
                            'TotalAnnualMaxCapacity',
                            'TotalAnnualMinCapacity',
                            'TotalAnnualMaxCapacityInvestment',
                            'TotalAnnualMinCapacityInvestment',
                            'TotalTechnologyAnnualActivityUpperLimit',
                            'TotalTechnologyAnnualActivityLowerLimit' ]
    #
    more_params = [   'DistanceDriven',
                    'UnitCapitalCost (USD)',
                    'UnitFixedCost (USD)',
                    'BiofuelShares']
    #
    filter_params = [   'FilterFuelType',
                    'FilterVehicleType']
    #
    input_params_table_headers = basic_header_elements + parameters_to_print + more_params + filter_params
    all_data_row = []
    all_data_row_partial = []
    #
    combination_list = []
    synthesized_all_data_row = []
    #
    # memory elements:
    f_unique_list, f_counter, f_counter_list, f_unique_counter_list = [], 1, [], []
    t_unique_list, t_counter, t_counter_list, t_unique_counter_list = [], 1, [], []
    e_unique_list, e_counter, e_counter_list, e_unique_counter_list = [], 1, [], []
    l_unique_list, l_counter, l_counter_list, l_unique_counter_list = [], 1, [], []
    y_unique_list, y_counter, y_counter_list, y_unique_counter_list = [], 1, [], []
    #
    for p in range( len( parameters_to_print ) ):
        #
        this_p_index = S_DICT_params_structure[ 'parameter' ].index( parameters_to_print[p] )
        this_p_index_list = S_DICT_params_structure[ 'index_list' ][ this_p_index ]
        #
        for n in range( 0, len( this_scenario_data[ parameters_to_print[p] ][ 'value' ] ) ):
            #
            single_data_row = []
            single_data_row_partial = []
            #
            single_data_row.append( 0 )
            single_data_row.append( scen )
            single_data_row.append( scenario_list[scen] )
            #
            strcode = ''
            #
            if 'f' in this_p_index_list:
                single_data_row.append( this_scenario_data[ parameters_to_print[p] ][ 'f' ][n] ) # Filling FUEL if necessary
                if single_data_row[-1] not in f_unique_list:
                    f_unique_list.append( single_data_row[-1] )
                    f_counter_list.append( f_counter )
                    f_unique_counter_list.append( f_counter )
                    f_counter += 1
                else:
                    f_counter_list.append( f_unique_counter_list[ f_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(f_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            if 't' in this_p_index_list:
                single_data_row.append( this_scenario_data[ parameters_to_print[p] ][ 't' ][n] ) # Filling TECHNOLOGY if necessary
                if single_data_row[-1] not in t_unique_list:
                    t_unique_list.append( single_data_row[-1] )
                    t_counter_list.append( t_counter )
                    t_unique_counter_list.append( t_counter )
                    t_counter += 1
                else:
                    t_counter_list.append( t_unique_counter_list[ t_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(t_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            if 'e' in this_p_index_list:
                single_data_row.append( this_scenario_data[ parameters_to_print[p] ][ 'e' ][n] ) # Filling EMISSION if necessary
                if single_data_row[-1] not in e_unique_list:
                    e_unique_list.append( single_data_row[-1] )
                    e_counter_list.append( e_counter )
                    e_unique_counter_list.append( e_counter )
                    e_counter += 1
                else:
                    e_counter_list.append( e_unique_counter_list[ e_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(e_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            if 'l' in this_p_index_list:
                single_data_row.append( this_scenario_data[ parameters_to_print[p] ][ 'l' ][n] ) # Filling SEASON if necessary
                if single_data_row[-1] not in l_unique_list:
                    l_unique_list.append( single_data_row[-1] )
                    l_counter_list.append( l_counter )
                    l_unique_counter_list.append( l_counter )
                    l_counter += 1
                else:
                    l_counter_list.append( l_unique_counter_list[ l_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(l_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            if 'y' in this_p_index_list:
                single_data_row.append( this_scenario_data[ parameters_to_print[p] ][ 'y' ][n] ) # Filling YEAR if necessary
                if single_data_row[-1] not in y_unique_list:
                    y_unique_list.append( single_data_row[-1] )
                    y_counter_list.append( y_counter )
                    y_unique_counter_list.append( y_counter )
                    y_counter += 1
                else:
                    y_counter_list.append( y_unique_counter_list[ y_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(y_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            this_combination_str = str(1) + strcode # deepcopy( single_data_row )
            this_combination = int( this_combination_str )
            #
            for aux_p in range( len(basic_header_elements), len(basic_header_elements) + len( parameters_to_print ) ):
                if aux_p == p + len(basic_header_elements):
                    single_data_row.append( this_scenario_data[ parameters_to_print[p] ][ 'value' ][n] ) # Filling the correct data point
                    single_data_row_partial.append( this_scenario_data[ parameters_to_print[p] ][ 'value' ][n] )
                else:
                    single_data_row.append( '' )
                    single_data_row_partial.append( '' )
            #
            #---------------------------------------------------------------------------------#
            for aide in range( len(more_params)+len(filter_params) ):
                single_data_row.append( '' )
                single_data_row_partial.append( '' )
            #---------------------------------------------------------------------------------#
            #
            all_data_row.append( single_data_row )
            all_data_row_partial.append( single_data_row_partial )
            #
            if this_combination not in combination_list:
                combination_list.append( this_combination )
                synthesized_all_data_row.append( single_data_row )
            else:
                ref_combination_index = combination_list.index( this_combination )
                ref_parameter_index = input_params_table_headers.index( parameters_to_print[p] )
                synthesized_all_data_row[ ref_combination_index ][ ref_parameter_index ] = deepcopy( single_data_row_partial[ ref_parameter_index-len( basic_header_elements ) ] )
                #
            #
            ##################################################################################################################
            #
            if parameters_to_print[p] in ['EmissionActivityRatio']:
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( synthesized_all_data_row[ ref_index ] ) # this must be updated in a further position of the list
                #
                this_tech = this_data_row[4]
                this_emission = this_data_row[5]
                this_year = this_data_row[7]
                this_year_index = time_range_vector.index( int( this_year ) )
                #
                if scenario_list[scen] != BAU_STR:
                    if this_tech in list( this_Blend_Shares_data.keys() ):
                        if this_emission in list( this_Blend_Shares_data[ this_tech ].keys() ):
                            #
                            this_Blend_Shares = this_Blend_Shares_data[ this_tech ][ this_emission ]
                            #
                            var_position_index = input_params_table_headers.index( 'BiofuelShares' )
                            this_data_row[ var_position_index ] = round(this_Blend_Shares[ this_year_index ], 4)
                            #
                        #
                    #
                #
                else:
                    var_position_index = input_params_table_headers.index( 'BiofuelShares' )
                    this_data_row[ var_position_index ] = 0.0
                #
                synthesized_all_data_row[ ref_index ] = deepcopy( this_data_row )
                #
            #
            ##################################################################################################################
            #
            if parameters_to_print[p] in [ 'TotalAnnualMaxCapacity', 'CapitalCost', 'FixedCost' ]:
                ref_index = combination_list.index( this_combination )
                this_data_row = deepcopy( synthesized_all_data_row[ ref_index ] ) # this must be updated in a further position of the list
                #
                this_tech = this_data_row[4]
                if this_tech in list( Fleet_Groups_inv.keys() ):
                    group_tech = Fleet_Groups_inv[ this_tech ]
                    #
                    this_year = this_data_row[7]
                    this_year_index = time_range_vector.index( int( this_year ) )
                    #
                    ref_var_position_index = input_params_table_headers.index( parameters_to_print[p] )
                    #
                    if 'Trains' not in group_tech and 'Telef' not in group_tech:
                        driven_distance = Reference_driven_distance[ scenario_list[scen] ][ group_tech ][ this_year_index ]
                        #
                        if parameters_to_print[p] == 'TotalAnnualMaxCapacity' or parameters_to_print[p] == 'FixedCost': # this will overwrite for zero-carbon techs, but will not fail.
                            var_position_index = input_params_table_headers.index( 'DistanceDriven' )
                            this_data_row[ var_position_index ] = round(driven_distance, 4)
                        #
                        if parameters_to_print[p] == 'CapitalCost':
                            var_position_index = input_params_table_headers.index( 'UnitCapitalCost (USD)' )
                            this_data_row[ var_position_index ] = round( (10**6)*float( this_data_row[ ref_var_position_index ] )*driven_distance/(10**9), 4)
                        #
                        if parameters_to_print[p] == 'FixedCost':
                            var_position_index = input_params_table_headers.index( 'UnitFixedCost (USD)' )
                            this_data_row[ var_position_index ] = round( (10**6)*float( this_data_row[ ref_var_position_index ] )*driven_distance/(10**9), 4)
                        #
                        synthesized_all_data_row[ ref_index ] = deepcopy( this_data_row )
                        #
                    #
                    ###################################################################################################
                    #
                #
                if parameters_to_print[p] == 'FixedCost':
                    # Creating convinience filters for the analysis of model outputs:
                    if 'TR' in this_tech[:2]:
                        #
                        ref_index = combination_list.index( this_combination )
                        this_data_row = deepcopy( synthesized_all_data_row[ ref_index ] ) # this must be updated in a further position of the list
                        #
                        var_position_index = input_params_table_headers.index( 'FilterFuelType' )
                        ############################################
                        # By Fuel Type
                        for r in range( len( df_fuel_2_code_fuel_list ) ):
                            if df_fuel_2_code_fuel_list[r] in this_tech:
                                this_data_row[ var_position_index ] = df_fuel_2_code_plain_english[ r ]
                                break
                        ############################################
                        var_position_index = input_params_table_headers.index( 'FilterVehicleType' )
                        # By vehicle type
                        for r in range( len( df_tech_2_code_fuel_list ) ):
                            if df_tech_2_code_fuel_list[r] in this_tech:
                                this_data_row[ var_position_index ] = df_tech_2_code_plain_english[ r ]
                                break
                        #
                        synthesized_all_data_row[ ref_index ] = deepcopy( this_data_row )
                        #
                    #
                #
            #
        #
    #
    ###########################################################################################################################
    #
    with open( './Executables' + '/' + str( scenario_list[scen] ) + '_0' + '/' + str( scenario_list[scen] ) + '_0' + '_Input.csv', 'w', newline = '') as param_csv:
        csvwriter = csv.writer(param_csv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # Print the header:
        csvwriter.writerow( input_params_table_headers )
        # Print all else:
        for n in range( len( synthesized_all_data_row ) ):
            csvwriter.writerow( synthesized_all_data_row[n] )
    #

def generalized_logistic_curve(x, L, Q, k, M):
  return L/( 1 + Q*math.exp( -k*( x-M ) ) )
#
def interpolation_blend( start_blend_point, mid_blend_point, final_blend_point, value_list, time_range_vector ):
    #
    start_blend_year, start_blend_value = start_blend_point[0], start_blend_point[1]/100
    final_blend_year, final_blend_value = final_blend_point[0], final_blend_point[1]/100
    #
    # Now we need to interpolate:
    x_coord_tofill = [] # these are indices that are NOT known - to interpolate
    xp_coord_known = [] # these are known indices - use for interpolation
    fp_coord_known = [] # these are the values known to interpolate the whole series
    #
    if mid_blend_point != 'None': # this means we must use a linear interpolation
        mid_blend_year, mid_blend_value = mid_blend_point[0], mid_blend_point[1]/100
        #
        for t in range( len( time_range_vector ) ):
            something_to_fill = False
            #
            if time_range_vector[t] < start_blend_year:
                fp_coord_known.append( 0.0 )
            #
            if time_range_vector[t] == start_blend_year:
                fp_coord_known.append( start_blend_value )
            #
            if ( time_range_vector[t] > start_blend_year and time_range_vector[t] < mid_blend_year ) or ( time_range_vector[t] > mid_blend_year and time_range_vector[t] < final_blend_year ):
                something_to_fill = True
            #
            if time_range_vector[t] == mid_blend_year:
                fp_coord_known.append( mid_blend_value )
            #
            if time_range_vector[t] == final_blend_year or time_range_vector[t] > final_blend_year:
                fp_coord_known.append( final_blend_value )
            #
            if something_to_fill == True:
                x_coord_tofill.append( t )
            else:
                xp_coord_known.append( t ) # means this value was stored
            #
            y_coord_filled = list( np.interp( x_coord_tofill, xp_coord_known, fp_coord_known ) )
            #
            interpolated_values = []
            for coord in range( len( time_range_vector ) ):
                if coord in xp_coord_known:
                    value_index = xp_coord_known.index(coord)
                    interpolated_values.append( float( fp_coord_known[value_index] ) )
                elif coord in x_coord_tofill:
                    value_index = x_coord_tofill.index(coord)
                    interpolated_values.append( float( y_coord_filled[value_index] ) )
            #
        #
    else:
        #
        for t in range( len( time_range_vector ) ):
            something_to_fill = False
            #
            if time_range_vector[t] < start_blend_year:
                fp_coord_known.append( 0.0 )
            #
            if time_range_vector[t] == start_blend_year:
                fp_coord_known.append( start_blend_value )
            #
            if ( time_range_vector[t] > start_blend_year and time_range_vector[t] < final_blend_year ):
                something_to_fill = True
            #
            if time_range_vector[t] == final_blend_year or time_range_vector[t] > final_blend_year:
                fp_coord_known.append( final_blend_value )
            #
            if something_to_fill == True:
                x_coord_tofill.append( t )
            else:
                xp_coord_known.append( t ) # means this value was stored
            #
            y_coord_filled = list( np.interp( x_coord_tofill, xp_coord_known, fp_coord_known ) )
            #
            interpolated_values = []
            for coord in range( len( time_range_vector ) ):
                if coord in xp_coord_known:
                    value_index = xp_coord_known.index(coord)
                    interpolated_values.append( float( fp_coord_known[value_index] ) )
                elif coord in x_coord_tofill:
                    value_index = x_coord_tofill.index(coord)
                    interpolated_values.append( float( y_coord_filled[value_index] ) )
            #
        #
    #
    new_value_list = []
    for n in range( len( value_list ) ):
        new_value_list.append( value_list[n]*( 1-interpolated_values[n] ) )
    new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
    biofuel_shares = [ round(elem, 4) for elem in interpolated_values ]
    #
    return new_value_list_rounded, biofuel_shares
    #
#
def interpolation_non_linear_final_flexible( time_list, value_list, new_relative_final_value, Flexible_Initial_Year_of_Uncertainty ):
    # Rememeber that the 'old_relative_final_value' is 1
    old_relative_final_value = 1
    new_value_list = []
    # We select a list that goes from the "Flexible_Initial_Year_of_Uncertainty" to the Final Year of the Time Series
    initial_year_index = time_list.index( Flexible_Initial_Year_of_Uncertainty )
    fraction_time_list = time_list[initial_year_index:]
    fraction_value_list = value_list[initial_year_index:]
    # We now perform the 'non-linear OR linear adjustment':
    xdata = [ fraction_time_list[i] - fraction_time_list[0] for i in range( len( fraction_time_list ) ) ]
    ydata = [ float( fraction_value_list[i] ) for i in range( len( fraction_value_list ) ) ]
    delta_ydata = [ ydata[i]-ydata[i-1] for i in range( 1,len( ydata ) ) ]
    #
    m_original = ( ydata[-1]-ydata[0] ) / ( xdata[-1]-xdata[0] )
    #
    m_new = ( ydata[-1]*(new_relative_final_value/old_relative_final_value) - ydata[0] ) / ( xdata[-1]-xdata[0] )
    #
    if float(m_original) == 0.0:
        delta_ydata_new = [m_new for i in range( 1,len( ydata ) ) ]
    else:
        delta_ydata_new = [ (m_new/m_original)*(ydata[i]-ydata[i-1]) for i in range( 1,len( ydata ) ) ]
    #
    ydata_new = [ 0 for i in range( len( ydata ) ) ]
    ydata_new[0] = ydata[0]
    for i in range( 0, len( delta_ydata ) ):
        ydata_new[i+1] = ydata_new[i] + delta_ydata_new[i]
    #
    # We now recreate the new_value_list considering the fraction before and after the Flexible_Initial_Year_of_Uncertainty
    fraction_list_counter = 0
    for n in range( len( time_list ) ):
        if time_list[n] >= Flexible_Initial_Year_of_Uncertainty:
            new_value_list.append( ydata_new[ fraction_list_counter ] )
            fraction_list_counter += 1
        else:
            new_value_list.append( float( value_list[n] ) )
    #
    # We return the list:
    return new_value_list
#
def interpolation_non_linear_final( time_list, value_list, new_relative_final_value ):
    # Rememeber that the 'old_relative_final_value' is 1
    old_relative_final_value = 1
    new_value_list = []
    # We select a list that goes from the "Initial_Year_of_Uncertainty" to the Final Year of the Time Series
    initial_year_index = time_list.index( Initial_Year_of_Uncertainty )
    fraction_time_list = time_list[initial_year_index:]
    fraction_value_list = value_list[initial_year_index:]
    # We now perform the 'non-linear OR linear adjustment':
    xdata = [ fraction_time_list[i] - fraction_time_list[0] for i in range( len( fraction_time_list ) ) ]
    ydata = [ float( fraction_value_list[i] ) for i in range( len( fraction_value_list ) ) ]
    delta_ydata = [ ydata[i]-ydata[i-1] for i in range( 1,len( ydata ) ) ]
    #
    m_original = ( ydata[-1]-ydata[0] ) / ( xdata[-1]-xdata[0] )
    #
    m_new = ( ydata[-1]*(new_relative_final_value/old_relative_final_value) - ydata[0] ) / ( xdata[-1]-xdata[0] )
    #
    if float(m_original) == 0.0:
        delta_ydata_new = [m_new for i in range( 1,len( ydata ) ) ]
    else:
        delta_ydata_new = [ (m_new/m_original)*(ydata[i]-ydata[i-1]) for i in range( 1,len( ydata ) ) ]
    #
    ydata_new = [ 0 for i in range( len( ydata ) ) ]
    ydata_new[0] = ydata[0]
    for i in range( 0, len( delta_ydata ) ):
        ydata_new[i+1] = ydata_new[i] + delta_ydata_new[i]
    #
    # We now recreate the new_value_list considering the fraction before and after the Initial_Year_of_Uncertainty
    fraction_list_counter = 0
    for n in range( len( time_list ) ):
        if time_list[n] >= Initial_Year_of_Uncertainty:
            new_value_list.append( ydata_new[ fraction_list_counter ] )
            fraction_list_counter += 1
        else:
            new_value_list.append( float( value_list[n] ) )
    #
    # We return the list:
    return new_value_list
#
def linear_interpolation_time_series( time_range, known_years, known_values ):
    # Now we need to interpolate:
    x_coord_tofill = [] # these are indices that are NOT known - to interpolate
    xp_coord_known = [] # these are known indices - use for interpolation
    fp_coord_known = [] # these are the values known to interpolate the whole series
    #
    min_t = min( known_years )
    for t in range( len( time_range ) ):
        if ( time_range[t] in known_years ) or ( time_range[t] < min_t ):
            xp_coord_known.append( t )
            #
            if time_range[t] < min_t:
                fp_coord_known.append( 0.0 )
            else:
                future_year_index = known_years.index( time_range[t] )
                fp_coord_known.append( float(known_values[ future_year_index ]) )
            #
        else:
            x_coord_tofill.append( t )
    #
    y_coord_filled = list( np.interp( x_coord_tofill, xp_coord_known, fp_coord_known ) )
    #
    interpolated_values = []
    for coord in range( len( time_range ) ):
        if coord in xp_coord_known:
            value_index = xp_coord_known.index(coord)
            interpolated_values.append( float( fp_coord_known[value_index] ) )
        elif coord in x_coord_tofill:
            value_index = x_coord_tofill.index(coord)
            interpolated_values.append( float( y_coord_filled[value_index] ) )
    #
    return interpolated_values
#
def csv_printer_parallel(s, scenario_list, stable_scenarios, basic_header_elements, parameters_to_print, S_DICT_params_structure):
    #
    input_params_table_headers = basic_header_elements + parameters_to_print
    all_data_row = []
    all_data_row_partial = []
    #
    combination_list = []
    synthesized_all_data_row = []
    #
    # memory elements:
    f_unique_list, f_counter, f_counter_list, f_unique_counter_list = [], 1, [], []
    t_unique_list, t_counter, t_counter_list, t_unique_counter_list = [], 1, [], []
    e_unique_list, e_counter, e_counter_list, e_unique_counter_list = [], 1, [], []
    l_unique_list, l_counter, l_counter_list, l_unique_counter_list = [], 1, [], []
    y_unique_list, y_counter, y_counter_list, y_unique_counter_list = [], 1, [], []
    #
    each_parameter_header = [ 'PARAMETER','Scenario','REGION','TECHNOLOGY','FUEL','EMISSION','MODE_OF_OPERATION','YEAR','TIMESLICE','SEASON','DAYTYPE','DAILYTIMEBRACKET','STORAGE','Value' ]
    each_parameter_all_data_row = {}
    #
    print( '    ', s+1, ' // Printing scenarios: ', scenario_list[s] )
    each_parameter_all_data_row.update( { scenario_list[s]:{} } )
    #
    for p in range( len( parameters_to_print ) ):
        each_parameter_all_data_row[ scenario_list[s] ].update( { parameters_to_print[p]:[] } )
        #
        this_p_index = S_DICT_params_structure[ 'parameter' ].index( parameters_to_print[p] )
        this_p_index_list = S_DICT_params_structure[ 'index_list' ][ this_p_index ]
        #
        for n in range( 0, len( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'value' ] ) ):
            #
            single_data_row = []
            single_data_row_partial = []
            #
            single_data_row.append( 0 ) # Filling Future.ID
            single_data_row.append( s ) # Filling Strategy.ID
            single_data_row.append( scenario_list[s] ) # Filling Strategy
            #
            strcode = ''
            #
            if 'f' in this_p_index_list:
                single_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'f' ][n] ) # Filling FUEL if necessary
                if single_data_row[-1] not in f_unique_list:
                    f_unique_list.append( single_data_row[-1] )
                    f_counter_list.append( f_counter )
                    f_unique_counter_list.append( f_counter )
                    f_counter += 1
                else:
                    f_counter_list.append( f_unique_counter_list[ f_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(f_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            if 't' in this_p_index_list:
                try:
                    single_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 't' ][n] ) # Filling TECHNOLOGY if necessary
                except Exception:
                    print('---------------------------')
                    print(scenario_list[s], parameters_to_print[p], n, len(stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 't' ]))
                    print('---------------------------')
                    sys.exit()

                if single_data_row[-1] not in t_unique_list:
                    t_unique_list.append( single_data_row[-1] )
                    t_counter_list.append( t_counter )
                    t_unique_counter_list.append( t_counter )
                    t_counter += 1
                else:
                    t_counter_list.append( t_unique_counter_list[ t_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(t_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            if 'e' in this_p_index_list:
                single_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'e' ][n] ) # Filling EMISSION if necessary
                if single_data_row[-1] not in e_unique_list:
                    e_unique_list.append( single_data_row[-1] )
                    e_counter_list.append( e_counter )
                    e_unique_counter_list.append( e_counter )
                    e_counter += 1
                else:
                    e_counter_list.append( e_unique_counter_list[ e_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(e_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            if 'l' in this_p_index_list:
                single_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'l' ][n] ) # Filling SEASON if necessary
                if single_data_row[-1] not in l_unique_list:
                    l_unique_list.append( single_data_row[-1] )
                    l_counter_list.append( l_counter )
                    l_unique_counter_list.append( l_counter )
                    l_counter += 1
                else:
                    l_counter_list.append( l_unique_counter_list[ l_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(l_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '000' # this is done to avoid repeated characters
            #
            if 'y' in this_p_index_list:
                single_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'y' ][n] ) # Filling YEAR if necessary
                if single_data_row[-1] not in y_unique_list:
                    y_unique_list.append( single_data_row[-1] )
                    y_counter_list.append( y_counter )
                    y_unique_counter_list.append( y_counter )
                    y_counter += 1
                else:
                    y_counter_list.append( y_unique_counter_list[ y_unique_list.index( single_data_row[-1] ) ] )
                strcode += str(y_counter_list[-1])
            else:
                single_data_row.append( '' )
                strcode += '0'
            #
            this_combination_str = str(10) + str(s) + strcode # deepcopy( single_data_row )
            #
            this_combination = int( this_combination_str )
            #
            for aux_p in range( len(basic_header_elements), len(basic_header_elements) + len( parameters_to_print ) ):
                if aux_p == p + len(basic_header_elements):
                    single_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'value' ][n] ) # Filling the correct data point
                    single_data_row_partial.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'value' ][n] )
                else:
                    single_data_row.append( '' )
                    single_data_row_partial.append( '' )
            #
            all_data_row.append( single_data_row )
            all_data_row_partial.append( single_data_row_partial )
            #
            if this_combination not in combination_list:
                combination_list.append( this_combination )
                synthesized_all_data_row.append( single_data_row )
            else:
                ref_combination_index = combination_list.index( this_combination )
                ref_parameter_index = input_params_table_headers.index( parameters_to_print[p] )
                synthesized_all_data_row[ ref_combination_index ][ ref_parameter_index ] = deepcopy( single_data_row_partial[ ref_parameter_index-len( basic_header_elements ) ] )
            #
            # Let us proceed with the list for the each_parameter list:
            this_each_parameter_all_data_row = [] # each_parameter_header = [ 'PARAMETER','Scenario','REGION','TECHNOLOGY','FUEL','EMISSION','MODE_OF_OPERATION','YEAR','TIMESLICE','SEASON','DAYTYPE','DAILYTIMEBRACKET','STORAGE','Value' ]
            #
            this_each_parameter_all_data_row.append( parameters_to_print[p] ) # Alternatively, fill PARAMETER
            this_each_parameter_all_data_row.append( scenario_list[s] ) # Alternatively, fill Scenario
            if 'r' in this_p_index_list:
                this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'r' ][n] ) # Filling REGION if necessary
            else:
                this_each_parameter_all_data_row.append( '' )
            if 't' in this_p_index_list:
                this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 't' ][n] ) # Filling TECHNOLOGY if necessary
            else:
                this_each_parameter_all_data_row.append( '' )
            if 'f' in this_p_index_list:
                this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'f' ][n] ) # Filling FUEL if necessary
            else:
                this_each_parameter_all_data_row.append( '' )
            if 'e' in this_p_index_list:
                this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'e' ][n] ) # Filling EMISSION if necessary
            else:
                this_each_parameter_all_data_row.append( '' )
            if 'm' in this_p_index_list:
                this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'm' ][n] ) # Filling MODE_OF_OPERATION if necessary
            else:
                this_each_parameter_all_data_row.append( '' )
            if 'y' in this_p_index_list:
                this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'y' ][n] ) # Filling YEAR if necessary
            else:
                this_each_parameter_all_data_row.append( '' )
            if 'l' in this_p_index_list:
                this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'l' ][n] ) # Filling TIMESLICE if necessary
            else:
                this_each_parameter_all_data_row.append( '' )
            this_each_parameter_all_data_row.append( '' )
            this_each_parameter_all_data_row.append( '' )
            this_each_parameter_all_data_row.append( '' )
            this_each_parameter_all_data_row.append( '' )
            this_each_parameter_all_data_row.append( stable_scenarios[ scenario_list[s] ][ parameters_to_print[p] ][ 'value' ][n] )
            #
            each_parameter_all_data_row[ scenario_list[s] ][ parameters_to_print[p] ].append( this_each_parameter_all_data_row )

    #########################################################################################
    print('4: We have printed the inputs. We will store the parameters that the experiment uses and be done.')
    # let us be reminded of the 'each_parameter_header'
    for p in range( len( parameters_to_print ) ):
        param_filename = './B1_Output_Params/' + str( scenario_list[s] ) + '/' + str( parameters_to_print[p] ) + '.csv'
        with open( param_filename, 'w', newline = '') as param_csv:
            csvwriter = csv.writer(param_csv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            # Print the header:
            csvwriter.writerow( each_parameter_header )
            # Let us locate the data:
            for n in range( len( each_parameter_all_data_row[ scenario_list[s] ][ parameters_to_print[p] ] ) ):
                csvwriter.writerow( each_parameter_all_data_row[ scenario_list[s] ][ parameters_to_print[p] ][n] )

if __name__ == '__main__':
    #
    all_years = [ y for y in range( BY_INT , EY_INT+1 ) ]
    index_START_VAR_YR = all_years.index( START_VAR_YR_INT )
    initial_year = all_years[0]
    final_year = all_years[-1]
    """
    *Abbreviations:*
    """
    start1 = time.time()
    #
    # We must open useful GDP data for denominator
    df_gdp_ref = pd.read_excel('_GDP_Ref.xlsx', 'GDP')
    list_gdp_growth_ref = df_gdp_ref['GDP_Growth'].tolist()
    list_gdp_ref = df_gdp_ref['GDP'].tolist()
    #
    '''''
    ################################# PART 1 #################################
    '''''
    print('1: We have defined some data. Now we will read the parameters we have as reference (or previous parameters) into a dictionary.')
    '''
    # 1.A) We extract the strucute setup of the model based on 'Structure.xlsx'
    '''
    structure_filename = "B1_Model_Structure.xlsx"
    structure_file = pd.ExcelFile(structure_filename)
    structure_sheetnames = structure_file.sheet_names  # see all sheet names
    sheet_sets_structure = pd.read_excel(open(structure_filename, 'rb'),
                                         header=None,
                                         sheet_name=structure_sheetnames[0])
    sheet_params_structure = pd.read_excel(open(structure_filename, 'rb'),
                                           header=None,
                                           sheet_name=structure_sheetnames[1])
    sheet_vars_structure = pd.read_excel(open(structure_filename, 'rb'),
                                         header=None,
                                         sheet_name=structure_sheetnames[2])

    S_DICT_sets_structure = {'set':[],'initial':[],'number_of_elements':[],'elements_list':[]}
    for col in range(1,11+1):  # 11 columns
        S_DICT_sets_structure['set'].append( sheet_sets_structure.iat[0, col] )
        S_DICT_sets_structure['initial'].append( sheet_sets_structure.iat[1, col] )
        S_DICT_sets_structure['number_of_elements'].append( int( sheet_sets_structure.iat[2, col] ) )
        #
        element_number = int( sheet_sets_structure.iat[2, col] )
        this_elements_list = []
        if element_number > 0:
            for n in range( 1, element_number+1 ):
                this_elements_list.append( sheet_sets_structure.iat[2+n, col] )
        S_DICT_sets_structure['elements_list'].append( this_elements_list )
    #
    S_DICT_params_structure = {'category':[],'parameter':[],'number_of_elements':[],'index_list':[]}
    param_category_list = []
    for col in range(1,30+1):  # 30 columns
        if str( sheet_params_structure.iat[0, col] ) != '':
            param_category_list.append( sheet_params_structure.iat[0, col] )
        S_DICT_params_structure['category'].append( param_category_list[-1] )
        S_DICT_params_structure['parameter'].append( sheet_params_structure.iat[1, col] )
        S_DICT_params_structure['number_of_elements'].append( int( sheet_params_structure.iat[2, col] ) )
        #
        index_number = int( sheet_params_structure.iat[2, col] )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_params_structure.iat[2+n, col] )
        S_DICT_params_structure['index_list'].append( this_index_list )
    #
    S_DICT_vars_structure = {'category':[],'variable':[],'number_of_elements':[],'index_list':[]}
    var_category_list = []
    for col in range(1,43+1):  # 43 columns
        if str( sheet_vars_structure.iat[0, col] ) != '':
            var_category_list.append( sheet_vars_structure.iat[0, col] )
        S_DICT_vars_structure['category'].append( var_category_list[-1] )
        S_DICT_vars_structure['variable'].append( sheet_vars_structure.iat[1, col] )
        S_DICT_vars_structure['number_of_elements'].append( int( sheet_vars_structure.iat[2, col] ) )
        #
        index_number = int( sheet_vars_structure.iat[2, col] )
        this_index_list = []
        for n in range(1, index_number+1):
            this_index_list.append( sheet_vars_structure.iat[2+n, col] )
        S_DICT_vars_structure['index_list'].append( this_index_list )
    #-------------------------------------------#
    # LET'S HAVE THE ENTIRE LIST OF TECHNOLOGIES:
    all_techs_list = S_DICT_sets_structure[ 'elements_list' ][ 1 ]
    #-------------------------------------------#
    '''
    Structural dictionary 1: Notes
    a) We use this dictionary relating a specific technology and a group technology and associate the prefix list
    '''
    Fleet_Groups =              pickle.load( open( './A1_Outputs/A-O_Fleet_Groups.pickle',            "rb" ) )
    ### Ind_Groups =                pickle.load( open( './A1_Outputs/A-O_Ind_Groups.pickle',            "rb" ) )
    ### Fleet_Groups['Techs_Microbuses'] += [ 'TRMBUSHYD' ] # this is an add on, kind of a patch
    Fleet_Groups_Distance =     pickle.load( open( './A1_Outputs/A-O_Fleet_Groups_Distance.pickle',   "rb" ) )
    Fleet_Groups_OR =           pickle.load( open( './A1_Outputs/A-O_Fleet_Groups_OR.pickle',         "rb" ) )
    Fleet_Groups_techs_2_dem =  pickle.load( open( './A1_Outputs/A-O_Fleet_Groups_T2D.pickle',        "rb" ) )
    #
    Fleet_Groups_inv = {}
    for k in range( len( list( Fleet_Groups.keys() ) ) ):
        this_fleet_group_key = list( Fleet_Groups.keys() )[k]
        for e in range( len( Fleet_Groups[ this_fleet_group_key ] ) ):
            this_fleet_group_tech = Fleet_Groups[ this_fleet_group_key ][ e ]
            Fleet_Groups_inv.update( { this_fleet_group_tech:this_fleet_group_key } )
    #
    ###Ind_Groups_inv = {}
    ### for k in range( len( list( Ind_Groups.keys() ) ) ):
    ###    this_ind_group_key = list( Ind_Groups.keys() )[k]
    ###    for e in range( len( Ind_Groups[ this_ind_group_key ] ) ):
    ###        this_ind_group_tech = Ind_Groups[ this_ind_group_key ][ e ]
    ###        Ind_Groups_inv.update( { this_ind_group_tech:this_ind_group_key } )
    #
    group_tech_PUBLIC = []
    group_tech_PRIVATE = []
    group_tech_FREIGHT_HEA = []
    group_tech_FREIGHT_LIG = []
    #
    for t in range( len( list( Fleet_Groups_techs_2_dem.keys() ) ) ):
        tech_key = list( Fleet_Groups_techs_2_dem.keys() )[t]
        this_fuel = Fleet_Groups_techs_2_dem[ tech_key ]
        if 'PRI' in this_fuel:
            group_tech_PRIVATE.append( tech_key )
        ### if 'PUB' in this_fuel:
        if 'PUB' in this_fuel and 'Telef' not in tech_key and 'Trains' not in tech_key:  # delete the trains and telef here, because we did not add them as alternatives
            group_tech_PUBLIC.append( tech_key )
        if 'FREHEA' in this_fuel:
            group_tech_FREIGHT_HEA.append( tech_key )
        if 'FRELIG' in this_fuel:
            group_tech_FREIGHT_LIG.append( tech_key )
    #
    group_tech_PASSENGER = group_tech_PUBLIC + group_tech_PRIVATE
    group_tech_FREIGHT = group_tech_FREIGHT_HEA + group_tech_FREIGHT_LIG
    #
    global time_range_vector
    time_range_vector = [ int(i) for i in S_DICT_sets_structure[ 'elements_list' ][0] ]
    '''
    ####################################################################################################################################################
    # 1.B) We finish this sub-part, and proceed to read all the base scenarios.
    '''
    header_row = ['PARAMETER','Scenario','REGION','TECHNOLOGY','FUEL','EMISSION','MODE_OF_OPERATION','TIMESLICE','YEAR','SEASON','DAYTYPE','DAILYTIMEBRACKET','STORAGE','Value']
    #
    scenario_list_sheet = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Scenarios' )
    scenario_list_all = [ scenario_list_sheet[ 'Name' ].tolist()[i] for i in range( len( scenario_list_sheet[ 'Name' ].tolist() ) ) if scenario_list_sheet[ 'Activated' ].tolist()[i] == 'YES' ]
    scenario_list_reference = [ scenario_list_sheet[ 'Reference' ].tolist()[i] for i in range( len( scenario_list_sheet[ 'Name' ].tolist() ) ) if scenario_list_sheet[ 'Activated' ].tolist()[i] == 'YES' ] # the address to the produced dataset
    scenario_list_based = [ scenario_list_sheet[ 'Based_On' ].tolist()[i] for i in range( len( scenario_list_sheet[ 'Name' ].tolist() ) ) if scenario_list_sheet[ 'Activated' ].tolist()[i] == 'YES' ]
    for i in range( len( scenario_list_sheet[ 'Base' ].tolist() ) ):
        if scenario_list_sheet[ 'Base' ].tolist()[i] == 'YES':
            ref_scenario = scenario_list_sheet[ 'Name' ].tolist()[i]
    #
    scenario_list = [ scenario_list_reference[i] for i in range( len( scenario_list_all ) ) if scenario_list_reference[i] != 'based' ]
    #sys.exit()
    #
    base_configuration_overall = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Overall_Parameters' )
    base_configuration_waste = pd.read_excel('B1_Scenario_Config.xlsx', sheet_name='Waste')
    base_configuration_transport_elasticity = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='TElasticity' )
    base_configuration_distance = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Distance_Levers' )
    base_configuration_modeshift = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Mode_Shift' )
    base_configuration_or = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Occupancy_Rate' )
    base_configuration_adoption = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Tech_Adoption' )
    base_configuration_electrical = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Electrical' )
    base_configuration_smartGrid = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='SmartGrid' )
    base_configuration_E_and_D = pd.read_excel( 'B1_Scenario_Config.xlsx', sheet_name='Efficiency' )
    #
    all_dataset_address = './A2_Output_Params/'
    '''
    # Call the default parameters for later use:
    '''
    list_param_default_value = pd.read_excel( 'B1_Default_Param.xlsx' )
    list_param_default_value_params = list( list_param_default_value['Parameter'] )
    list_param_default_value_value = list( list_param_default_value['Default_Value'] )
    #
    global Initial_Year_of_Uncertainty
    for n in range( len( base_configuration_overall.index ) ):
        if str( base_configuration_overall.loc[ n, 'Parameter' ] ) == 'Initial_Year_of_Uncertainty':
            Initial_Year_of_Uncertainty = int( base_configuration_overall.loc[ n, 'Value' ] )
    '''
    ####################################################################################################################################################
    '''
    # This section reads a reference data.csv from baseline scenarios and frames Structure-OSEMOSYS_CR.xlsx
    col_position = []
    col_corresponding_initial = []
    for n in range( len( S_DICT_sets_structure['set'] ) ):
        col_position.append( header_row.index( S_DICT_sets_structure['set'][n] ) )
        col_corresponding_initial.append( S_DICT_sets_structure['initial'][n] )
    # Define the dictionary for calibrated database:
    stable_scenarios = {}
    for scen in scenario_list:
        stable_scenarios.update( { scen:{} } )
    #
    for scen in range( len( scenario_list ) ):
        this_paramter_list_dir = 'A2_Output_Params/' + str( scenario_list[scen] )
        parameter_list = os.listdir( this_paramter_list_dir )
        #
        for p in range( len( parameter_list ) ):
            this_param = parameter_list[p].replace('.csv','')
            stable_scenarios[ scenario_list[scen] ].update( { this_param:{} } )
            # To extract the parameter input data:
            all_params_list_index = S_DICT_params_structure['parameter'].index(this_param)
            this_number_of_elements = S_DICT_params_structure['number_of_elements'][all_params_list_index]
            this_index_list = S_DICT_params_structure['index_list'][all_params_list_index]
            #
            for k in range(this_number_of_elements):
                stable_scenarios[ scenario_list[scen] ][ this_param ].update({this_index_list[k]:[]})
            stable_scenarios[ scenario_list[scen] ][ this_param ].update({'value':[]})
            # Extract data:
            with open( this_paramter_list_dir + '/' + str(parameter_list[p]), mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                #
                for row in csv_reader:
                    if row[ header_row[-1] ] != None and row[ header_row[-1] ] != '':
                        #
                        for h in range( 2, len(header_row)-1 ):
                            if row[ header_row[h] ] != None and row[ header_row[h] ] != '':
                                set_index  = S_DICT_sets_structure['set'].index( header_row[h] )
                                set_initial = S_DICT_sets_structure['initial'][ set_index ]
                                stable_scenarios[ scenario_list[scen] ][ this_param ][ set_initial ].append( row[ header_row[h] ] )
                        stable_scenarios[ scenario_list[scen] ][ this_param ][ 'value' ].append( row[ header_row[-1] ] )
                        #
    stable_scenarios_freeze = deepcopy(stable_scenarios)

    ####################################################################################################################################################
    # 1 - DISTANCE DICTIONARY:
    distance_levers = {}
    base_configuration_distance_unique_scenario_list = []
    for n in range( len( base_configuration_distance.index ) ):
        #
        if str( base_configuration_distance.loc[ n ,'Scenario'] ) not in base_configuration_distance_unique_scenario_list:
            base_configuration_distance_group_set_list = []
            base_configuration_distance_unique_scenario_list.append( str( base_configuration_distance.loc[ n ,'Scenario'] ) )
            distance_levers.update( { base_configuration_distance_unique_scenario_list[-1]:{} } )
        else:
            pass
        #
        if str( base_configuration_distance.loc[ n ,'Group_Set'] ) not in base_configuration_distance_group_set_list:
            base_configuration_distance_group_set_list.append( str( base_configuration_distance.loc[ n ,'Group_Set'] ) )
            distance_levers[ base_configuration_distance_unique_scenario_list[-1] ].update( { base_configuration_distance_group_set_list[-1]:0 } )
        else:
            pass
        #
        # Now we fill the data:
        distance_levers[ base_configuration_distance_unique_scenario_list[-1] ][ base_configuration_distance_group_set_list[-1] ] = float( base_configuration_distance.loc[ n ,'Relative reduction to BAU - distance'] )
        #
    #
    ####################################################################################################################################################
    # 3 - OCCUPANCY RATE DICTIONARY:
    or_params = {}
    base_configuration_or_unique_scenario_list = []
    for n in range( len( base_configuration_or.index ) ):
        #
        if str( base_configuration_or.loc[ n ,'Scenario'] ) not in base_configuration_or_unique_scenario_list:
            base_configuration_or_group_set_list = []
            base_configuration_or_unique_scenario_list.append( str( base_configuration_or.loc[ n ,'Scenario'] ) )
            or_params.update( { base_configuration_or_unique_scenario_list[-1]:{} } )
        else:
            pass
        #
        if str( base_configuration_or.loc[ n ,'Group_Set'] ) not in base_configuration_or_group_set_list:
            base_configuration_or_group_set_list.append( str( base_configuration_or.loc[ n ,'Group_Set'] ) )
            or_params[ base_configuration_or_unique_scenario_list[-1] ].update( { base_configuration_or_group_set_list[-1]:0 } )
        else:
            pass
        #
        # Now we fill the data:
        or_params[ base_configuration_or_unique_scenario_list[-1] ][ base_configuration_or_group_set_list[-1] ] = float( base_configuration_or.loc[ n ,'Relative increase to BAU - occupancy rate'] )
        #
    '''
    ##########################################################################
    '''
    transport_group_sets = list( Fleet_Groups.keys() )
    transport_group_sets = [ i for i in transport_group_sets if 'Train' not in i and 'Telef' not in i]
    Reference_driven_distance = {}
    Reference_occupancy_rate = {}
    Reference_op_life = {}
    #
    for s in range( len( scenario_list ) ):
        Reference_driven_distance.update( { scenario_list[s]:{} } )
        Reference_occupancy_rate.update( { scenario_list[s]:{} } )
        Reference_op_life.update( { scenario_list[s]:{} } )
        for n in range( len( transport_group_sets ) ):
            this_set = transport_group_sets[n]
            #
            if scenario_list[s] in base_configuration_distance_unique_scenario_list or scenario_list[s] == ref_scenario:
                base_distance = Fleet_Groups_Distance[ Fleet_Groups[this_set][0] ] # the [0] helps call the detail fo distance per vehicle
                if scenario_list[s] != ref_scenario:
                    new_distance = deepcopy( interpolation_non_linear_final_flexible( time_range_vector, base_distance, distance_levers[scenario_list[s]][this_set], Initial_Year_of_Uncertainty ) )
                    new_distance_rounded = [ round(elem, 4) for elem in new_distance ]
                    Reference_driven_distance[ scenario_list[s] ].update( {this_set:new_distance_rounded} )
                else:
                    Reference_driven_distance[ scenario_list[s] ].update( {this_set:base_distance} )
            #
            if scenario_list[s] in base_configuration_or_unique_scenario_list or scenario_list[s] == ref_scenario:
                these_or_indices = [ i for i, x in enumerate( stable_scenarios[ scenario_list[s] ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( this_set ) ]
                base_or = deepcopy( stable_scenarios[ scenario_list[s] ][ 'OutputActivityRatio' ]['value'][ these_or_indices[0]:these_or_indices[-1]+1 ] )
                base_or = [ float( base_or[j] ) for j in range( len( base_or ) ) ]
                if scenario_list[s] != ref_scenario:
                    new_or = deepcopy( interpolation_non_linear_final_flexible( time_range_vector, base_or, or_params[scenario_list[s]][this_set], Initial_Year_of_Uncertainty ) )
                    new_or_rounded = [ round(elem, 4) for elem in new_or ]
                    Reference_occupancy_rate[ scenario_list[s] ].update( {this_set:new_or_rounded} )
                else:
                    Reference_occupancy_rate[ scenario_list[s] ].update( {this_set:base_or} )
            #
        #
        for n in range(len(list(Fleet_Groups_inv.keys()))):
            this_set = list(Fleet_Groups_inv.keys())[n]
            if scenario_list[s] in base_configuration_distance_unique_scenario_list or scenario_list[s] == ref_scenario:  # includes distance scenarios
                these_ol_indices = [ i for i, x in enumerate( stable_scenarios[ scenario_list[s] ][ 'OperationalLife' ][ 't' ] ) if x == str( this_set ) ]
                base_ol = deepcopy( stable_scenarios[ scenario_list[s] ][ 'OperationalLife' ]['value'][ these_ol_indices[0]:these_ol_indices[-1]+1 ] )
                base_ol = [ float( base_ol[j] ) for j in range( len( base_ol ) ) ]
                Reference_op_life[ scenario_list[s] ].update( {this_set:base_ol[0]} )
    #

    global scenario_list_print
    scenario_list_print = deepcopy( scenario_list )
    scenario_list_print = ['BAU']

    print('6: We have finished printing base scenarios. We must now execute.')
    # sys.exit()
    #
    packaged_useful_elements = [Reference_driven_distance, Reference_occupancy_rate, Reference_op_life,
                                Fleet_Groups_inv, time_range_vector,
                                list_param_default_value_params, list_param_default_value_value, list_gdp_ref]
    #
    set_first_list(scenario_list_print)
    print('Entered Parallelization of model execution')
    x = len(first_list)
    max_x_per_iter = 2 # FLAG: This is an input
    y = x / max_x_per_iter
    y_ceil = math.ceil( y )
    #
    for n in range(0,y_ceil):
        n_ini = n*max_x_per_iter
        processes = []
        #
        if n_ini + max_x_per_iter <= x:
            max_iter = n_ini + max_x_per_iter
        else:
            max_iter = x
        #    
        for n2 in range( n_ini , max_iter ):
            p = mp.Process(target=main_executer, args=(n2, packaged_useful_elements, scenario_list_print) )
            processes.append(p)
            p.start()
        #
        for process in processes:
            process.join()

    end_1 = time.time()   
    time_elapsed_1 = -start1 + end_1
    print( str( time_elapsed_1 ) + ' seconds /', str( time_elapsed_1/60 ) + ' minutes' )
    print('*: For all effects, we have finished the work of this script.')
    #########################################################################################


