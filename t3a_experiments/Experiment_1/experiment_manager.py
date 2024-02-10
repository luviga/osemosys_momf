# -*- coding: utf-8 -*-
"""
@author: luisf
"""
# SOURCE: https://pypi.org/project/lhsmdu/
import os, os.path
import multiprocessing as mp
import errno
import scipy
from scipy import stats
import pandas as pd
import numpy as np
import xlrd
import csv
import os, os.path
import sys
import math
from copy import deepcopy
import time
import re
import linecache
import gc
import shutil
import pickle
# https://pythonhosted.org/pyDOE/randomized.html#latin-hypercube
from pyDOE import *

'''
We implement OSEMOSYS-CR in a procedimental code
The main features are:
inherited_scenarios : implemented in procedimental code
function_C_mathprog_parallel : we will insert it all in a function to run in parallel
interpolation : implemented in a function for linear of non-linear time-series
'''
#
def set_first_list( Executed_Scenario ):
    #
    first_list_raw = os.listdir( './Experimental_Platform/Futures/' + str( Executed_Scenario ) )
    #
    global first_list
    first_list = [e for e in first_list_raw if ( '.csv' not in e ) and ( 'Table' not in e ) and ( '.py' not in e ) and ( '__pycache__' not in e ) ]

############################################################################################################################################################################################################

def data_processor( case, Executed_Scenario, unpackaged_useful_elements ):
    #
    Reference_driven_distance =     unpackaged_useful_elements[0]
    Reference_occupancy_rate =      unpackaged_useful_elements[1]
    Fleet_Groups_inv =              unpackaged_useful_elements[2]
    time_range_vector =             unpackaged_useful_elements[3]
    dict_gdp_ref      =             unpackaged_useful_elements[4]
    #
    # Briefly open up the system coding to use when processing for visualization:
    df_fuel_to_code = pd.read_excel( './0_From_Confection/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Fuel_to_Code' )
    df_fuel_2_code_fuel_list        = df_fuel_to_code['Code'].tolist()
    df_fuel_2_code_plain_english    = df_fuel_to_code['Plain_English'].tolist()
    df_tech_to_code = pd.read_excel( './0_From_Confection/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Tech_to_Code' )
    df_tech_2_code_fuel_list        = df_tech_to_code['Techs'].tolist()
    df_tech_2_code_plain_english    = df_tech_to_code['Plain_English'].tolist()
    #
    # 1 - Always call the structure for the model:
    #-------------------------------------------#
    structure_filename = "./0_From_Confection/B1_Model_Structure.xlsx"
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
    output_header = [ 'Strategy', 'Future.ID','Fuel','Technology','Emission','Year']
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
    list_gdp_ref = dict_gdp_ref[int(this_future)]
    #-------------------------------------------------------#
    #
    vars_as_appear = []
    data_name = str( './Experimental_Platform/Futures/' + str( Executed_Scenario ) + '/' + first_list[case] ) + '/' + str(first_list[case]) + '_output.txt'
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
    output_adress = './Experimental_Platform/Futures/' + str( Executed_Scenario ) + '/' + str( first_list[case] )
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
            if this_variable == 'TotalTechnologyAnnualActivity' or this_variable == 'NewCapacity':
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
                    if 'Trains' not in group_tech:
                        ''' Debug section start
                        '''
                        try:
                            driven_distance = float( Reference_driven_distance[ this_strategy ][int(this_future)][ group_tech ][ this_year_index ] )
                        except Exception:
                            print(this_strategy)
                            print(this_future)
                            print(group_tech)
                            print(this_year_index)
                            print('error here')
                        #
                        if 'Motos' in group_tech or 'Freight' in group_tech:
                            passenger_per_vehicle = 1
                        else:
                            try:
                                passenger_per_vehicle = float( Reference_occupancy_rate[ this_strategy ][int(this_future)][ group_tech ][ this_year_index ]  )
                            except Exception:
                                print(list(Reference_occupancy_rate[ this_strategy ][int(this_future)].keys()))
                                print('check alert')
                                sys.exit()
                        ''' Debug section end
                        '''
                        #
                        if this_variable == 'NewCapacity':
                            var_position_index = output_header.index( 'NewFleet' )
                            this_data_row[ var_position_index ] =  round( (10**9)*float( this_data_row[ ref_var_position_index ] )/driven_distance, 4)
                        #
                        if this_variable == 'TotalTechnologyAnnualActivity':
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
            output_csv_r = 0.05*100
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
                this_cap_inv = float(this_data_row[ ref_var_position_index ])
                this_data_row[ref_var_position_index] = \
                    str(this_cap_inv)  # Here we re-write the new capacity to adjust the system
                #
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
            this_existing_combination.append( '' )
            this_existing_combination.append( non_year_combination_list_years[n][0] )
            ref_index = combination_list.index( this_existing_combination )
            this_existing_data_row = deepcopy( data_row_list[ ref_index ] )
            #
            for n2 in range( len(time_range_vector) ):
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
                        #
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
    shutil.os.remove(data_name)
    #-----------------------------------------------------------------------------------------------------------%
    gc.collect(generation=2)
    time.sleep(0.05)
    #-----------------------------------------------------------------------------------------------------------%
    print(  'We finished with printing the outputs.', case)

############################################################################################################################################################################################################
def main_executer(n1, Executed_Scenario, packaged_useful_elements):
    print('# ' + str(n1+1) + ' of ' + Executed_Scenario )
    set_first_list( Executed_Scenario )
    file_aboslute_address = os.path.abspath("experiment_manager.py")
    file_adress = re.escape( file_aboslute_address.replace( 'experiment_manager.py', '' ) ).replace( '\:', ':' )
    #
    case_address = file_adress + r'Experimental_Platform\\Futures\\' + Executed_Scenario + '\\' + str( first_list[n1] )
    #
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
    data_processor(n1,Executed_Scenario,packaged_useful_elements)
#
def function_C_mathprog_parallel( fut_index, inherited_scenarios, unpackaged_useful_elements ):
    #
    scenario_list =                     unpackaged_useful_elements[0]
    S_DICT_sets_structure =             unpackaged_useful_elements[1]
    S_DICT_params_structure =           unpackaged_useful_elements[2]
    list_param_default_value_params =   unpackaged_useful_elements[3]
    list_param_default_value_value =    unpackaged_useful_elements[4]
    print_adress =                      unpackaged_useful_elements[5]
    all_futures =                       unpackaged_useful_elements[6]
    #
    Reference_driven_distance =         unpackaged_useful_elements[7]
    Fleet_Groups_inv =                  unpackaged_useful_elements[8]
    time_range_vector =                 unpackaged_useful_elements[9]
    Blend_Shares =                      unpackaged_useful_elements[10]
    #
    # Briefly open up the system coding to use when processing for visualization:
    df_fuel_to_code = pd.read_excel( './0_From_Confection/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Fuel_to_Code' )
    df_fuel_2_code_fuel_list        = df_fuel_to_code['Code'].tolist()
    df_fuel_2_code_plain_english    = df_fuel_to_code['Plain_English'].tolist()
    df_tech_to_code = pd.read_excel( './0_From_Confection/A-I_Classifier_Modes_Transport.xlsx', sheet_name='Tech_to_Code' )
    df_tech_2_code_fuel_list        = df_tech_to_code['Techs'].tolist()
    df_tech_2_code_plain_english    = df_tech_to_code['Plain_English'].tolist()
    #
    if fut_index < len( all_futures ):
        fut = all_futures[fut_index]
        scen = 0
    if fut_index >= len( all_futures ) and fut_index < 2*len( all_futures ):
        fut = all_futures[fut_index - len( all_futures ) ]
        scen = 1
    if fut_index >= 2*len( all_futures ) and fut_index < 3*len( all_futures ):
        fut = all_futures[fut_index - 2*len( all_futures ) ]
        scen = 2
    if fut_index >= 3*len( all_futures ) and fut_index < 4*len( all_futures ):
        fut = all_futures[fut_index - 3*len( all_futures ) ]
        scen = 3
    if fut_index >= 4*len( all_futures ) and fut_index < 5*len( all_futures ):
        fut = all_futures[fut_index - 4*len( all_futures ) ]
        scen = 4
    if fut_index >= 5*len( all_futures ) and fut_index < 6*len( all_futures ):
        fut = all_futures[fut_index - 5*len( all_futures ) ]
        scen = 5
    if fut_index >= 6*len( all_futures ):
        fut = all_futures[fut_index - 6*len( all_futures ) ]
        scen = 6
    #
    # header = ['Scenario','Parameter','REGION','TECHNOLOGY','FUEL','EMISSION','MODE_OF_OPERATION','TIMESLICE','YEAR','SEASON','DAYTYPE','DAILYTIMEBRACKET','STORAGE','Value']
    header_indices = ['Scenario','Parameter','r','t','f','e','m','l','y','ls','ld','lh','s','value']
    #
    fut = all_futures[fut_index - scen*len( all_futures ) ]
    #
    print('# This is future:', fut, ' and scenario ', scenario_list[scen] )
    #
    try:
        scen_file_dir = print_adress + '/' + str( scenario_list[scen] ) + '/' + str( scenario_list[scen] ) + '_' + str( fut )
        os.mkdir( scen_file_dir )

    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass
    #
    this_scenario_data = inherited_scenarios[ scenario_list[scen] ][ fut ]
    #
    g= open( print_adress + '/' + str( scenario_list[scen] ) + '/' + str( scenario_list[scen] ) + '_' + str( fut ) + '/' + str( scenario_list[scen] ) + '_' + str( fut ) + '.txt',"w+")
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
                            these_values.append( this_scenario_data[ this_param ]['value'][ value_indices[val] ] )
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
            if len(this_param_keys) == 5:
                this_set_element_unique_all = []
                for pkey in range( len(this_param_keys)-2 ):
                    for i in range( 2, len(header_indices)-1 ):
                        if header_indices[i] == this_param_keys[pkey]:
                            this_set_element = this_scenario_data[ this_param ][ header_indices[i] ]
                            this_set_element_unique_all.append( list( set( this_set_element ) ) )
                #
                this_set_element_unique_1 = deepcopy( this_set_element_unique_all[0] )
                this_set_element_unique_2 = deepcopy( this_set_element_unique_all[1] )
                this_set_element_unique_3 = deepcopy( this_set_element_unique_all[2] )
                #
                for n1 in range( len( this_set_element_unique_1 ) ):
                    for n2 in range( len( this_set_element_unique_2 ) ):
                        for n3 in range( len( this_set_element_unique_3 ) ): #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                            # MOVE AFTER len() conditional // g.write( '[' + str( this_set_element_unique_1[n1] ) + ',' + str( this_set_element_unique_2[n2] ) + ',' + str( this_set_element_unique_3[n3] ) + ',*,*]:\n' )
                            # get the last and second last parameters of the list:
                            last_set_element = this_scenario_data[ this_param ][ this_param_keys[-1] ]
                            last_set_element_unique = [] # list( set( last_set_element ) )
                            for u in range( len( last_set_element ) ):
                                if last_set_element[u] not in last_set_element_unique:
                                    last_set_element_unique.append( last_set_element[u] )
                            #
                            second_last_set_element = this_scenario_data[ this_param ][ this_param_keys[-2] ]
                            second_last_set_element_unique = [] # list( set( second_last_set_element ) )
                            for u in range( len( second_last_set_element ) ):
                                if second_last_set_element[u] not in second_last_set_element_unique:
                                    second_last_set_element_unique.append( second_last_set_element[u] )
                            #
                            for s in range( len( second_last_set_element_unique ) ):
                                #  MOVE AFTER len() conditional // g.write( second_last_set_element_unique[s] + ' ' )
                                value_indices_s = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[-2] ] ) if x == str( second_last_set_element_unique[s] ) ]
                                value_indices_n1 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[0] ] ) if x == str( this_set_element_unique_1[n1] ) ]
                                value_indices_n2 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[1] ] ) if x == str( this_set_element_unique_2[n2] ) ]
                                value_indices_n3 = [ i for i, x in enumerate( this_scenario_data[ this_param ][ this_param_keys[2] ] ) if x == str( this_set_element_unique_3[n3] ) ]
                                #
                                r_index = set(value_indices_s) & set(value_indices_n1) & set(value_indices_n2) & set(value_indices_n3)
                                value_indices = list( r_index )
                                value_indices.sort()
                                #
                                if len( value_indices ) != 0:
                                    g.write( '[' + str( this_set_element_unique_1[n1] ) + ',' + str( this_set_element_unique_2[n2] ) + ',' + str( this_set_element_unique_3[n3] ) + ',*,*]:\n' )
                                    #
                                    for y in range( len( last_set_element_unique ) ):
                                        g.write( str( last_set_element_unique[y] ) + ' ')
                                    g.write(':=\n')
                                    #
                                    g.write( second_last_set_element_unique[s] + ' ' )
                                    #
                                    # these_values = this_scenario_data[ this_param ]['value'][ value_indices[0]:value_indices[-1]+1 ]
                                    these_values = []
                                    for val in range( len( value_indices ) ):
                                        these_values.append( this_scenario_data[ this_param ]['value'][ value_indices[val] ] )
                                    for val in range( len( these_values ) ):
                                        g.write( str( these_values[val] ) + ' ' )
                                    g.write('\n') #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
            #
            #g.write('\n') 
            #-----------------------------------------#
            g.write( ';\n\n' )
    #
    # remember the default values for printing:
    g.write('param AccumulatedAnnualDemand default 0 :=\n;\n')
    # if scenario_list[scen] == 'BAU':
    #     g.write('param AnnualEmissionLimit default 99999 :=\n;\n')
    g.write('param AnnualEmissionLimit default 99999 :=\n;\n') # here we are using no Emission Limit
    g.write('param AnnualExogenousEmission default 0 :=\n;\n')
    g.write('param CapacityOfOneTechnologyUnit default 0 :=\n;\n')
    g.write('param CapitalCostStorage default 0 :=\n;\n')
    g.write('param Conversionld default 0 :=\n;\n')
    g.write('param Conversionlh default 0 :=\n;\n')
    g.write('param Conversionls default 0 :=\n;\n')
    g.write('param DaySplit default 0.00137 :=\n;\n')
    g.write('param DaysInDayType default 7 :=\n;\n')
    g.write('param DepreciationMethod default 1 :=\n;\n')
    g.write('param DiscountRate default 0.05 :=\n;\n')
    # g.write('param EmissionsPenalty default 0 :=\n;\n')
    g.write('param MinStorageCharge default 0 :=\n;\n')
    g.write('param ModelPeriodEmissionLimit default 99999 :=\n;\n')
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
    # g.write('param TotalAnnualMaxCapacityInvestment default 99999 :=\n;\n')
    if scenario_list[scen] == 'BAU':
        g.write('param TotalAnnualMinCapacity default 0 :=\n;\n')
    # g.write('param TotalTechnologyAnnualActivityUpperLimit default 99999 :=\n;\n')
    g.write('param TotalTechnologyModelPeriodActivityLowerLimit default 0 :=\n;\n')
    g.write('param TotalTechnologyModelPeriodActivityUpperLimit default 99999 :=\n;\n')
    g.write('param TradeRoute default 0 :=\n;\n')
    #
    g.write('#\n' + 'end;\n')
    #
    g.close()
    #
    ###########################################################################################################################
    # Furthermore, we must print the inputs separately for fast deployment of the input matrix:
    #
    if scenario_list[scen] != 'BAU':
        this_Blend_Shares_data = Blend_Shares[ scenario_list[scen] ][ fut ]
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
                            'TotalTechnologyAnnualActivityLowerLimit']
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
            single_data_row.append( fut )
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
                strcode += '000' # this is done to avoid repeated characters
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
                if scenario_list[scen] != 'BAU':
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
                    if 'Trains' not in group_tech:
                        driven_distance = Reference_driven_distance[ scenario_list[scen] ][int(fut)][ group_tech ][ this_year_index ]
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
                    if 'TR' in this_tech:
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
    file_aboslute_address = os.path.abspath("experiment_manager.py")
    file_adress = re.escape( file_aboslute_address.replace( 'experiment_manager.py', '' ) ).replace( '\:', ':' )
    with open( file_adress + '\\Experimental_Platform\\Futures\\' + str( scenario_list[scen] ) + '\\' + str( scenario_list[scen] ) + '_' + str( fut ) + '\\' + str( scenario_list[scen] ) + '_' + str( fut ) + '_Input.csv', 'w', newline = '') as param_csv:
        csvwriter = csv.writer(param_csv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # Print the header:
        csvwriter.writerow( input_params_table_headers )
        # Print all else:
        for n in range( len( synthesized_all_data_row ) ):
            csvwriter.writerow( synthesized_all_data_row[n] )
    #
    
#
'''
Function 1: Notes
a) This function interpolates the time series with the most similar  rate of change (linear to non-linear).
b) This approach only affects the final value of the time series.
c) The result depends on the initial year of uncertainty which is a global parameter and is specified in experiment setup.
'''

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

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
    if int(m_original) == 0:
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

'''
Function 2: Notes
a) This function changes the initial value of the time series.
'''
def interpolation_non_linear_initial( time_list, value_list, new_relative_initial_value ):
    # Rememeber that the 'old_relative_final_value' is 1
    old_relative_final_value = 1
    new_value_list = []
    # We do the interpolation across all years
    xdata = [ time_list[i] - time_list[0] for i in range( len( time_list ) ) ]
    ydata = value_list
    delta_ydata = [ ydata[i]-ydata[i-1] for i in range( 1,len( ydata ) ) ]
    #
    m_original = ( ydata[-1]-ydata[0] ) / ( xdata[-1]-xdata[0] )
    m_new = ( ydata[-1] - ydata[0]*(new_relative_initial_value/old_relative_final_value) ) / ( xdata[-1]-xdata[0] )
    #
    if float(m_original) == 0.0:
        delta_ydata_new = [m_new for i in range( 1,len( ydata ) ) ]
    else:
        delta_ydata_new = [ (m_new/m_original)*(ydata[i]-ydata[i-1]) for i in range( 1,len( ydata ) ) ]
    #
    ydata_new = [ 0 for i in range( len( ydata ) ) ]
    ydata_new[0] = ydata[0]*new_relative_initial_value
    for i in range( 0, len( delta_ydata ) ):
        ydata_new[i+1] = ydata_new[i] + delta_ydata_new[i]
    # we assign the returnable
    new_value_list = ydata_new
    #
    # We return the list:
    return new_value_list

'''
Function 3: Notes
a) There is a shift of the time series for some uncertainties, reflecting uncertainty in the initial value. For this reason, we provide al alternative function to adjust the curve.
b) There is a dc shift that changes all values in a percent. This is useful for discrete investments, where there are zeros along the time series.
'''
def time_series_shift( time_list, value_list, new_relative_initial_value ):
    new_value_list = []
    # We multiply the initial value of value_list times the new_relative_value
    new_initial_value = value_list[0]*new_relative_initial_value
    shift_value = new_initial_value - value_list[0]
    #
    for n in range(len( time_list ) ):
        new_value_list.append( value_list[n] + shift_value )
    #
    # We return the list:
    return new_value_list
#
def dc_shift( time_list, value_list, new_relative_initial_value ):
    new_value_list = []
    #
    for t in range( len( time_list ) ):
        if float( value_list[t] ) == 0.0:
            new_value_list.append( 0.0 )
        else:
            new_value_list.append( round( value_list[t]*new_relative_initial_value , 4 ) )
        #
    #
    return new_value_list
    #
#
'''
Function 4: Notes
a) For old technologies, the values must go to zero at a desired year
'''
def year_when_reaches_zero( time_list, value_list, ywrz ):
    new_value_list = []
    # We interpolate the value list defining when the value reaches 0. The values go from 100% in the base year to 0% in year_when_reaches_zero
    # We will create an interpoaltion function for the percentages:
    x_coord_tofill = [] # these are indices that are NOT known - to interpolate
    xp_coord_known = [] # these are known indices - use for interpolation
    fp_coord_known = []# [100,0] # these are the values known to interpolate the whole series
    #
    original_shares = [ 100*value_list[n]/value_list[0] for n in range(len(value_list)) ]
    original_shares_add = []
    for n in range( len(original_shares) ):
        if time_list[n] <= Initial_Year_of_Uncertainty:
            fp_coord_known.append( original_shares[n] )
            original_shares_add.append( original_shares[n] )
    fp_coord_known.append( 0 )
    #
    years_with_value_different_from_zero = [ n for n in range( time_list[0],int(ywrz)+1 ) ]
    for n in range( len( years_with_value_different_from_zero ) ):
        if years_with_value_different_from_zero[n] <= Initial_Year_of_Uncertainty or years_with_value_different_from_zero[n]==ywrz:
            xp_coord_known.append( n )
        else:
            x_coord_tofill.append( n )
    #
    y_coord_filled = list( np.interp( x_coord_tofill, xp_coord_known, fp_coord_known ) )
    percentage_list = original_shares_add + y_coord_filled + [0]
    #
    for n in range( len( time_list ) ):
        if time_list[n] <= ywrz:
            new_value_list.append( (percentage_list[n]/100)*value_list[0] )
        else:
            new_value_list.append( 0.0 )
    #
    # We return the list:
    return new_value_list

'''
Function 5: Notes
a) We apply the logistic curve varying years in x
'''
def generalized_logistic_curve(x, L, Q, k, M):
  return L/( 1 + Q*math.exp( -k*( x-M ) ) )
#
def logistic_curve_controlled(L, xM, C, xo, x):
    k = np.log( L/C - 1) / ( xo-xM )
    return L/( 1 + math.exp( -k*( x-xo ) ) )
#
'''
Function 6: Notes
a) We apply the blend interpolation
'''
def interpolation_blend( start_blend_point, final_blend_point, value_list, time_range_vector ):
    #
    start_blend_year, start_blend_value = start_blend_point[0], start_blend_point[1]/100
    final_blend_year, final_blend_value = final_blend_point[0], final_blend_point[1]/100
    #
    # Now we need to interpolate:
    x_coord_tofill = [] # these are indices that are NOT known - to interpolate
    xp_coord_known = [] # these are known indices - use for interpolation
    fp_coord_known = [] # these are the values known to interpolate the whole series
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
    new_value_list = []
    for n in range( len( value_list ) ):
        new_value_list.append( value_list[n]*( 1-interpolated_values[n] ) )
    new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
    biofuel_shares = [ round(elem, 4) for elem in interpolated_values ]
    #
    return new_value_list_rounded, biofuel_shares
    #
#
if __name__ == '__main__':
    #
    '''
    Let us define some control inputs internally:
    '''
    # generator_or_executor = 'None'
    generator_or_executor = 'Both'
    # generator_or_executor = 'Generator'
    # generator_or_executor = 'Executor'
    inputs_txt_csv = 'Both'
    # inputs_txt_csv = 'csv'
    parallel_or_linear = 'Parallel'
    # parallel_or_linear = 'Linear'
    #
    #############################################################################################################################
    '''
    # 1.A) We extract the strucute setup of the model based on 'Structure.xlsx'
    '''
    structure_filename = "./0_From_Confection/B1_Model_Structure.xlsx"
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
    for col in range(1,11+1):
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
    for col in range(1,30+1):
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
    for col in range(1,43+1):
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
    #############################################################################################################################
    '''
    Structural dictionary 1: Notes
    a) We use this dictionary relating a specific technology and a group technology and associate the prefix list
    '''

    Fleet_Groups = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups.pickle', "rb" ))
    Fleet_Techs_Distance = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups_Distance.pickle', "rb" ))
    Fleet_Techs_OR = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups_OR.pickle', "rb" ))
    Fleet_Groups_techs_2_dem = pickle.load( open( './0_From_Confection/A-O_Fleet_Groups_T2D.pickle', "rb" ))

    Fleet_Groups_inv = {}
    for k in range( len( list( Fleet_Groups.keys() ) ) ):
        this_fleet_group_key = list( Fleet_Groups.keys() )[k]
        for e in range( len( Fleet_Groups[ this_fleet_group_key ] ) ):
            this_fleet_group_tech = Fleet_Groups[ this_fleet_group_key ][ e ]
            Fleet_Groups_inv.update( { this_fleet_group_tech:this_fleet_group_key } )
    
    Fleet_Groups_list = [] # list( Fleet_Groups.keys() )
    Fleet_Groups_Distance = {}
    Fleet_Techs_with_Distance = list( Fleet_Techs_Distance.keys() )
    for u in range( len( Fleet_Techs_with_Distance ) ):
        if Fleet_Groups_inv[ Fleet_Techs_with_Distance[u] ] not in Fleet_Groups_list:
            Fleet_Groups_list.append( Fleet_Groups_inv[ Fleet_Techs_with_Distance[u] ] )
            Fleet_Groups_Distance.update( { Fleet_Groups_list[-1]:Fleet_Techs_Distance[ Fleet_Techs_with_Distance[u] ] } )
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
        if 'PUB' in this_fuel:
            group_tech_PUBLIC.append( tech_key )
        if 'FREHEA' in this_fuel:
            group_tech_FREIGHT_HEA.append( tech_key )
        if 'FRELIG' in this_fuel:
            group_tech_FREIGHT_LIG.append( tech_key )
    #
    group_tech_PASSENGER = group_tech_PUBLIC + group_tech_PRIVATE
    group_tech_FREIGHT = group_tech_FREIGHT_HEA + group_tech_FREIGHT_LIG
    #
    global time_range_vector # This is the variable that manages time throughout the experiment
    time_range_vector = [ int(i) for i in S_DICT_sets_structure[ 'elements_list' ][0] ]
    #
    global final_year
    final_year = time_range_vector[-1]
    global initial_year
    initial_year = time_range_vector[0]

    # We must open useful GDP data for demand projection
    df_gdp_ref = pd.read_excel('_GDP_Ref.xlsx', 'GDP')
    list_gdp_growth_ref = df_gdp_ref['GDP_Growth'].tolist()
    list_gdp_ref = df_gdp_ref['GDP'].tolist()
    df_elasticities = pd.read_excel('_GDP_Ref.xlsx', 'Elasticities')
    df_intensities = pd.read_excel('_GDP_Ref.xlsx', 'Intensities')
    #
    #############################################################################################################################
    #
    '''
    For all effects, read all the user-defined scenarios in future 0, created by hand in Base_Runs_Generator.py ;
    These data parameters serve as the basis to implement the experiment.
    '''
    #
    '''
    Part 1: the experiment data generator for N samplles that are DEFINED BY USER
    Part 2: read all relevant inputs based on the SPD heritage
    Part 3: the manipulation of the base data where applicable and generation of new data
        (read the column 'Explored_Parameter_is_Relative_to_Baseline' of Uncertainty_Table)
        NOTE: part 3 has a strict manipulation procedure
        NOTE: part 3 must execute the experiment entirely
    CONTROL ACTION 1: Select the scenario that you want to generate (USER INPUT).
    CONTROL ACTION 2: select all the futures that you want to process in this run, from beginning to end
    Part 4: print the new .txt files
    '''
    setup_table = pd.read_excel('_Experiment_Setup.xlsx' )
    scenarios_to_reproduce = str( setup_table.loc[ 0 ,'Scenario_to_Reproduce'] )
    experiment_ID = str( setup_table.loc[ 0 ,'Experiment_ID'] )
    #
    global Initial_Year_of_Uncertainty
    Initial_Year_of_Uncertainty = int( setup_table.loc[ 0 ,'Initial_Year_of_Uncertainty'] )
    '''''
    ################################# PART 1 #################################
    '''''
    print('1: I start by reading the Uncertainty Table and systematically perturbing the paramaters.')
    uncertainty_table = pd.read_excel( 'Uncertainty_Table.xlsx' )
    # use .loc to access [row, column name]
    experiment_variables = list( uncertainty_table.columns )
    #
    np.random.seed( 555 )
    P = len( uncertainty_table.index ) # variables to vary
    N = int( setup_table.loc[ 0 ,'Number_of_Runs'] )  # number of samples

    # Here we need to define the number of elements that need to be included in the hypercube
    list_xlrm_IDs = uncertainty_table['XLRM_ID']
    ignore_indices = [p for p in range(len(list_xlrm_IDs)) if list_xlrm_IDs[p] == 'none']  # these are positions where we should not ask for a lhs sample
    subtracter = 0
    col_idx = {}
    for p in range( P ):
        if p in ignore_indices:
            subtracter += 1
            col_idx.update({p:'none'})
        else:
            col_idx.update({p:p-subtracter})    

    # sys.exit()

    hypercube = lhs( P , samples = N )
    # hypercube[p] gives vector with values of variable p across the N futures, hence len( hypercube[p] ) = N
    #
    experiment_dictionary = {}
    all_dataset_address = './1_Baseline_Modelling/'

    for n in range( N ):
        this_future_X_change_direction = [] # up or down
        this_future_X_change = [] # this is relative to baseline
        this_future_X_param = [] # this is NOT relative to baseline
        #
        X_Num_unique = []
        X_Num = []
        X_Cat = []
        Exact_Param_Num = []
        #
        for p in range( P ):
            #
            # Here we extract crucial infromation for each row:
            #
            math_type = str( uncertainty_table.loc[ p ,'X_Mathematical_Type'] )
            Explored_Parameter_of_X = str( uncertainty_table.loc[ p ,'Explored_Parameter_of_X'] )
            #
            Involved_Scenarios = str( uncertainty_table.loc[ p ,'Involved_Scenarios'] ).replace(' ','').split(';')
            Involved_Sets_in_Osemosys = str( uncertainty_table.loc[ p ,'Involved_Sets_in_Osemosys'] ).replace(' ','').split(';')
            Exact_Parameters_Involved_in_Osemosys = str( uncertainty_table.loc[ p ,'Exact_Parameters_Involved_in_Osemosys'] ).replace(' ','').split(';')
            Exact_X = str( uncertainty_table.loc[ p ,'X_Plain_English_Description'] )
            #
            #######################################################################
            X_Num.append( int( uncertainty_table.loc[ p ,'X_Num'] ) )
            X_Cat.append( str( uncertainty_table.loc[ p ,'X_Category'] ) )
            Exact_Param_Num.append( int( uncertainty_table.loc[ p ,'Explored_Parameter_Number'] ) )
            #
            this_min = uncertainty_table.loc[ p , 'Min_Value' ]
            this_max = uncertainty_table.loc[ p , 'Max_Value' ]
            #
            this_loc = this_min
            this_loc_scale = this_max - this_min
            #
            hyper_col_idx = col_idx[p]
            if hyper_col_idx != 'none':
                evaluation_value_preliminary = hypercube[n].item(hyper_col_idx)
                # if n == 0:
                #     print(evaluation_value_preliminary, hyper_col_idx, p)
            else:
                evaluation_value_preliminary = 1
            #
            # evaluation_value_preliminary = hypercube[n].item(p)
            #
            evaluation_value = scipy.stats.uniform.ppf(evaluation_value_preliminary, this_loc, this_loc_scale)
            #
            #######################################################################
            # here, we program the conditions of a useful adoption S-curve if parameters depend on others defined previosly:
            if ( p > 1 ) and ( str( uncertainty_table.loc[ p ,'Dependency_on_Previous_Explored_Parameter'] ) != 'n.a.' ):
                #
                independent_Param_pointer = int( uncertainty_table.loc[ p ,'Dependency_on_Previous_Explored_Parameter'] )
                #
                independent_Param_index = Exact_Param_Num.index( independent_Param_pointer )
                #
                # What parameters are constrained to have a coherent experiment?
                depending_Param = str( uncertainty_table.loc[ p ,'Explored_Parameter_of_X'] ) # actually the current parameter
                independent_Param = str( uncertainty_table.loc[ independent_Param_index ,'Explored_Parameter_of_X'] )
                ##################################################################################
                independent_Param_value = this_future_X_param[ independent_Param_index ]
                ##################################################################################
                #if 'L (' in independent_Param and evaluation_value > independent_Param_value*0.5: # means we are in C
                if 'L (' in independent_Param and evaluation_value > independent_Param_value: # means we are in C
                    this_max = independent_Param_value
                    #
                #
                elif 'M (' in independent_Param: # means we are ready to estimate all the parameters
                    # we must calculate the upper limit as a function of the other parametrs for a coherent outcome
                    r2021max = 1/0.05 # 1/this_future_X_param[ independent_Param_index-2 ]
                    r2050 = 1/0.999 # 1/this_future_X_param[ independent_Param_index-1 ]
                    #
                    M = this_future_X_param[ independent_Param_index ]
                    #
                    this_C = evaluation_value
                    this_L = this_future_X_param[ independent_Param_index-1 ]
                    #
                    log_Qmax_wo_elevate = (r2021max-1)/( (r2050-1)**( (M-2021)/(M-2050) ) )
                    Q_elevation_factor = 1 - (M-2021)/(M-2050)
                    log_Qmax = np.log(log_Qmax_wo_elevate)/Q_elevation_factor
                    Qmax = np.exp( log_Qmax )
                    Cmax = this_L/( Qmax+1 )
                    #                   
                    if this_C > Cmax:
                        this_max = Cmax
                    #
                this_loc_scale = this_max - this_min
                evaluation_value = scipy.stats.uniform.ppf(evaluation_value_preliminary, this_loc, this_loc_scale)
                #
                # print( independent_Param )
                if 'M (' in independent_Param:
                    this_C = evaluation_value
                    Q = this_L/this_C - 1
                    k = np.log( (r2050-1)/Q )/(M-2050)

            #######################################################################
            # here, we program the direction dependencies:
            this_depending_on_X_list = str( uncertainty_table.loc[ p ,'Sign_Dependency_on_Specified_Xs'] ).replace(' ','').split(';')
            if ( p > 1 ) and ( str( uncertainty_table.loc[ p ,'Sign_Dependency_on_Specified_Xs'] ) != 'n.a.' ) and ( len(this_depending_on_X_list) == 1 ):
                #
                depending_on_X = int( uncertainty_table.loc[ p ,'Sign_Dependency_on_Specified_Xs'] )
                #
                depending_on_X_index = X_Num.index( depending_on_X )
                # we modify the direction by changing this_loc and this_loc_scale:
                # we apply the correction only if the original probability is incompatible
                # if str(this_future_X_change_direction[depending_on_X_index]) == 'down' and evaluation_value > 0.5*(this_max + this_min): # this approach serves for symmentrical experiments only
                if str(this_future_X_change_direction[depending_on_X_index]) == 'down' and evaluation_value > 1: # this approach serves for symmentrical or assymetrical experiments
                    this_loc_scale = 0.5*(this_max - this_min)
                # elif str(this_future_X_change_direction[depending_on_X_index]) == 'up' and evaluation_value < 0.5*(this_max + this_min): # this approach serves for symmentrical experiments only
                elif str(this_future_X_change_direction[depending_on_X_index]) == 'up' and evaluation_value < 1: # this approach serves for symmentrical or assymetrical experiments
                    this_loc = this_min + 0.5*(this_max - this_min)
                #
                evaluation_value = scipy.stats.uniform.ppf(evaluation_value_preliminary, this_loc, this_loc_scale)
            #
            #######################################################################
            #
            if str( uncertainty_table.loc[ p , 'Explored_Parameter_is_Relative_to_Baseline' ] ) == 'YES':
                if evaluation_value > 1:
                    this_future_X_change_direction.append('up')
                else:
                    this_future_X_change_direction.append('down')
                #
                this_future_X_change.append( evaluation_value )
                #
                this_future_X_param.append('n.a.')
            #
            elif str( uncertainty_table.loc[ p , 'Explored_Parameter_is_Relative_to_Baseline' ] ) == 'NO':
                this_future_X_change_direction.append('n.a.')
                this_future_X_change.append( 'n.a.' )
                #
                if 'C (' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                    this_future_X_param.append( [ Q, k, M ] )
                #
                else:
                    if 'Year_when_reaches_zero' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                        this_future_X_param.append( int( evaluation_value ) )
                    #
                    elif ( 'C (' not in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ) ) or ( 'Blend_Time_Series' in str( uncertainty_table.loc[ p , 'X_Mathematical_Type' ] ) ):
                        this_future_X_param.append( evaluation_value )
                    #
                    elif str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ) == 'Constant':
                        this_future_X_param.append( evaluation_value )
                        #
                #
            #
            #######################################################################
            #
            # We can now store all the information for each future in a dictionary:
            #
            if n == 0: # the dictionary is created only when the first future appears
                if int( uncertainty_table.loc[ p ,'X_Num'] ) in X_Num_unique: # by design, this means the math_type is an Adoption_Curve or Blend_Time_Series math type
                    if 'L (' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Explored_Parameter_of_X' ].append( Explored_Parameter_of_X )
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][0].append( this_future_X_param[-1] )
                    elif 'C (' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Explored_Parameter_of_X' ].append('Q')
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Explored_Parameter_of_X' ].append('k')
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Explored_Parameter_of_X' ].append('M')
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n] += this_future_X_param[-1]
                    elif 'Blend_Time_Series' in str( uncertainty_table.loc[ p , 'X_Mathematical_Type' ] ):
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Explored_Parameter_of_X' ].append( Explored_Parameter_of_X )
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][0].append( this_future_X_param[-1] )
                    #
                #
                ###################################################################################################################################
                #
                elif int( uncertainty_table.loc[ p ,'X_Num'] ) not in X_Num_unique:
                    #
                    X_Num_unique.append( int( uncertainty_table.loc[ p ,'X_Num'] ) )
                    #
                    Relative_to_Baseline = str( uncertainty_table.loc[ p ,'Explored_Parameter_is_Relative_to_Baseline'] )
                    #
                    experiment_dictionary.update( { X_Num_unique[-1]:{ 'Category':X_Cat[-1], 'Math_Type':math_type, 'Relative_to_Baseline':Relative_to_Baseline, 'Exact_X':Exact_X } } )
                    experiment_dictionary[ X_Num_unique[-1] ].update({ 'Involved_Scenarios':Involved_Scenarios })
                    experiment_dictionary[ X_Num_unique[-1] ].update({ 'Involved_Sets_in_Osemosys':Involved_Sets_in_Osemosys })
                    experiment_dictionary[ X_Num_unique[-1] ].update({ 'Exact_Parameters_Involved_in_Osemosys':Exact_Parameters_Involved_in_Osemosys })
                    experiment_dictionary[ X_Num_unique[-1] ].update({ 'Futures':[x for x in range( 1, N+1 ) ] })
                    #
                    if math_type == 'Time_Series' or math_type == 'Discrete_Investments':
                        experiment_dictionary[ X_Num_unique[-1] ].update({ 'Explored_Parameter_of_X':Explored_Parameter_of_X } )
                        experiment_dictionary[ X_Num_unique[-1] ].update({ 'Values':[0.0 for x in range( 1, N+1 ) ] })
                        # We fill the data for future n=1 // it is important to note that the future n=0 can have completely different parameters when values are not relative to baseline
                        if str( uncertainty_table.loc[ p , 'Explored_Parameter_is_Relative_to_Baseline'] ) == 'YES':
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][0] = this_future_X_change[-1] # here n=0
                        elif str( uncertainty_table.loc[ p , 'Explored_Parameter_is_Relative_to_Baseline'] ) == 'NO':
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][0] = this_future_X_param[-1] # here n=0
                    #
                    elif math_type == 'Adoption_Curve':
                        if 'L (' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                            experiment_dictionary[ X_Num_unique[-1] ].update({ 'Explored_Parameter_of_X':[ Explored_Parameter_of_X ] } )
                            experiment_dictionary[ X_Num_unique[-1] ].update({ 'Values':[[] for x in range( 1, N+1 ) ] })
                            # We fill the data for future n=1 // it is important to note that the future n=0 can have completely different parameters when values are not relative to baseline
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][0].append( this_future_X_param[-1] ) # here n=0
                            #
                        #
                    elif math_type == 'Blend_Time_Series':
                        if 'Initial_Year' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                            experiment_dictionary[ X_Num_unique[-1] ].update({ 'Explored_Parameter_of_X':[ Explored_Parameter_of_X ] } )
                            experiment_dictionary[ X_Num_unique[-1] ].update({ 'Values':[[] for x in range( 1, N+1 ) ] })
                            # We fill the data for future n=1 // it is important to note that the future n=0 can have completely different parameters when values are not relative to baseline
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][0].append( this_future_X_param[-1] ) # here n=0
                            #
                    elif math_type == 'Constant':
                        experiment_dictionary[ X_Num_unique[-1] ].update({ 'Explored_Parameter_of_X':[ Explored_Parameter_of_X ] } )
                        experiment_dictionary[ X_Num_unique[-1] ].update({ 'Values':[[] for x in range( 1, N+1 ) ] })
                        # We fill the data for future n=1 // it is important to note that the future n=0 can have completely different parameters when values are not relative to baseline
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][0] = this_future_X_param[-1] # here n=0
                        #
                    #
                #
            #
            ###################################################################################################################################
            #
            else:
                #
                if int( uncertainty_table.loc[ p ,'X_Num'] ) in X_Num_unique: # by design, this means the math_type is an Adoption_Curve or Blend_Time_Series math type
                    if 'C (' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n] += this_future_X_param[-1]
                    elif 'Initial_Year' not in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ) and math_type == 'Blend_Time_Series':
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n].append( this_future_X_param[-1] )
                #
                ###################################################################################################################################
                #
                elif int( uncertainty_table.loc[ p ,'X_Num'] ) not in X_Num_unique:
                    #
                    X_Num_unique.append( int( uncertainty_table.loc[ p ,'X_Num'] ) )
                    #
                    if math_type == 'Time_Series' or math_type == 'Discrete_Investments':
                        if str( uncertainty_table.loc[ p , 'Explored_Parameter_is_Relative_to_Baseline'] ) == 'YES':
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n] = this_future_X_change[-1]
                        elif str( uncertainty_table.loc[ p , 'Explored_Parameter_is_Relative_to_Baseline'] ) == 'NO':
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n] = this_future_X_param[-1]
                    #
                    elif math_type == 'Adoption_Curve':
                        if 'L (' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n].append( this_future_X_param[-1] )
                    #
                    elif math_type == 'Blend_Time_Series':
                        if 'Initial_Year' in str( uncertainty_table.loc[ p , 'Explored_Parameter_of_X' ] ):
                            experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n].append( this_future_X_param[-1] )
                    #
                    elif math_type == 'Constant':
                        experiment_dictionary[ int( uncertainty_table.loc[ p ,'X_Num'] ) ][ 'Values' ][n] = this_future_X_param[-1]

    '''''
    ################################# PART 2 #################################
    '''''
    print('2: That is done. Now I initialize some key structural data.')
    '''
    # 2.B) We finish this sub-part, and proceed to read all the base scenarios.
    '''
    header_row = ['PARAMETER','Scenario','REGION','TECHNOLOGY','FUEL','EMISSION','MODE_OF_OPERATION','TIMESLICE','YEAR','SEASON','DAYTYPE','DAILYTIMEBRACKET','STORAGE','Value']
    #
    scenario_list = []
    if scenarios_to_reproduce == 'All':
        stable_scenario_list_raw = os.listdir( '1_Baseline_Modelling' )
        for n in range( len( stable_scenario_list_raw ) ):
            if stable_scenario_list_raw[n] not in ['_Base_Dataset', '_BACKUP'] and '.txt' not in stable_scenario_list_raw[n]:
                scenario_list.append( stable_scenario_list_raw[n] )
    elif scenarios_to_reproduce == 'Experiment':
        scenario_list.append( 'BAU' )
        scenario_list.append( 'NDP' )
    elif scenarios_to_reproduce != 'All' and scenarios_to_reproduce != 'Experiment':
        scenario_list.append( scenarios_to_reproduce )
    #
    '''
    print('brake here to check experiment scenarios')
    sys.exit()
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
        #
        this_paramter_list_dir = '1_Baseline_Modelling/' + str( scenario_list[scen] )
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
    '''
    # 2.C) We call the default parameters for later use:
    '''
    list_param_default_value = pd.read_excel( './0_From_Confection/B1_Default_Param.xlsx' )
    list_param_default_value_params = list( list_param_default_value['Parameter'] )
    list_param_default_value_value = list( list_param_default_value['Default_Value'] )

    # We perturb the system that re-applies the uncertainty across parameters using the 'experiment_disctionary'
    '''
    # 3.A) We create a copy of all the scenarios
    '''
    all_futures = [n for n in range(1,N+1)]
    inherited_scenarios = {}
    for n1 in range( len( scenario_list ) ):
        inherited_scenarios.update( { scenario_list[n1]:{} } )
        #
        for n2 in range( len( all_futures ) ):
            copy_stable_dictionary = deepcopy( stable_scenarios[ scenario_list[n1] ] )
            inherited_scenarios[ scenario_list[n1] ].update( { all_futures[n2]:copy_stable_dictionary } )

    '''
    # 3.B) We iterate over the experiment dictionary for the 1 to N futures additional to future 0, implementing the orderly manipulation
    '''
    print('3: That is done. Now I systematically perturb the model parameters.')
    # Broadly speaking, we must perfrom the same calculation across futures, as all futres are independent.
    #
    reference_driven_distance = {}
    reference_occupancy_rate = {}
    Blend_Shares = { 'NDP':{} , 'NDPTh':{} , 'NDPWOS':{}, 'NDPWOSTh':{} }
    #
    for s in range( len( scenario_list ) ):
        this_s = s
        reference_driven_distance.update( { scenario_list[s]:{} } )
        reference_occupancy_rate.update( { scenario_list[s]:{} } )
        fut_id = 0
        #


        ### WHAT HAPPENED TO DEMAND???
        if scenario_list[s] == 'BAU':
            test_dict = {}
            test_dict_1 = {}
            test_dict_2 = {}
            test_dict_3 = {}
            test_dict_4 = {}


        for f in range( 1, len( all_futures )+1 ):
            this_f = f
            #
            reference_driven_distance[ scenario_list[s] ].update( { f:{} } )
            reference_occupancy_rate[ scenario_list[s] ].update( { f:{} } )
            if scenario_list[s] != 'BAU':
                Blend_Shares[ scenario_list[s] ].update( { f:{} } )
            #
            # NOTE 0: TotalDemand and Mode Shift must take the BAU SpeecifiedAnnualDemand for coherence.
            TotalDemand = []
            TotalDemand_BASE_BAU = []

            for u in range( 2, len(experiment_dictionary)+1 ): # u is for the uncertainty number // start at 2 because the GDP is assigned to the first row
                Exact_X = experiment_dictionary[u]['Exact_X']
                X_Cat = experiment_dictionary[u]['Category']
                # Extract crucial sets and parameters to be manipulated in the model:
                Parameters_Involved = experiment_dictionary[u]['Exact_Parameters_Involved_in_Osemosys']
                Sets_Involved = deepcopy( experiment_dictionary[u]['Involved_Sets_in_Osemosys'] )
                #
                Scenarios_Involved = experiment_dictionary[u]['Involved_Scenarios']
                # Extract crucial identifiers:
                Explored_Parameter_of_X = experiment_dictionary[u]['Explored_Parameter_of_X']
                Math_Type = experiment_dictionary[u]['Math_Type']
                Relative_to_Baseline = experiment_dictionary[u]['Relative_to_Baseline']
                # Extract the values:
                Values_per_Future =  experiment_dictionary[u]['Values']
                # For the manipulation, we deploy consecutive actions on the system depending on every X parameter:
                # NOTE 1: we will perform the changes in the consecutive order of the Uncertainty_Table, using distance as a final adjustment.
                # NOTE 2: the distance reduction of DP is relative to BAU. All other uncertainties are independent of the scenario.
                # NOTE 3: we go ahead with the manipulation of the uncertainty if it is applicable to the scenario we are interested in reproducing.
                # NOTE 4: we store the TotalDemand vector to be used in the uncertainties that require it.

                if str( scenario_list[s] ) in Scenarios_Involved:
                    # We iterate over the involved parameters of the model here:
                    #
                    for p in range( len( Parameters_Involved ) ):
                        this_parameter = Parameters_Involved[p]
                        #
                        if 'Passenger Demand' in X_Cat:
                            #
                            if scenario_list[s] == 'BAU':
                                distribution_passenger_BAU = {}
                            # This uncertainty must be dealt with by adding the specified annual demand of the involved sets. Then, the final value is changed with the experimetn value. Finally, the time series (math type) is interpolated.
                            this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('FUEL') ]
                            summed_value_list = []
                            for a_set in range( len( Sets_Involved ) ):
                                this_set = Sets_Involved[a_set]
                                this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                # for each index we extract the time and value in a list:
                                # extracting time:
                                time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                # extracting value:
                                value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                value_list = [ float(value_list[j]) for j in range( len( value_list ) ) ]
                                # performing addition of sets in the case of x = 1:
                                for element in range( len( value_list ) ):
                                    if a_set == 0:
                                        summed_value_list.append( float( value_list[element] ) )
                                    else:
                                        summed_value_list[element] += float ( value_list[element] )
                                #
                                if scenario_list[s] == 'BAU':
                                    distribution_passenger_BAU.update( { this_set:[] } )
                                    distribution_passenger_BAU[ this_set ] = deepcopy( value_list )
                                #
                            # Here we take advantage of the loop to obtain the baseline shares to apply to the BAU scenario:
                            if scenario_list[s] == 'BAU':
                                TotalDemand_BASE_BAU = deepcopy( summed_value_list )
                                for a_set_BASE in range( len( Sets_Involved ) ):
                                    this_set_distribution = [ distribution_passenger_BAU[ Sets_Involved[a_set_BASE] ][n] / TotalDemand_BASE_BAU[n] for n in range( len( TotalDemand_BASE_BAU ) ) ]
                                    distribution_passenger_BAU[ Sets_Involved[a_set_BASE] ] = deepcopy( this_set_distribution )

                            # now that the value is extracted, we must manipulate the result and store in TotalDemand
                            all_years = [ y for y in range( 2018 , 2050+1 ) ]
                            index_2024 = all_years.index( 2024 )
                            local_df_elasticities = deepcopy(df_elasticities)
                            local_df_elasticities.iloc[-1, local_df_elasticities.columns.get_loc('e_Passenger')] = float(Values_per_Future[fut_id])
                            local_df_elasticities['e_Passenger'].interpolate(method ='linear', limit_direction ='forward', inplace = True)
                            list_e_pass = local_df_elasticities['e_Passenger'].tolist()

                            new_value_list = []
                            for y in range(len(all_years)):
                                if y < index_2024:
                                    new_value_list.append(summed_value_list[y])
                                else:  # apply growth formula with demand elasticity
                                    gdp_growth_apply = experiment_dictionary[1]['Values'][fut_id]  # the first element in the uncertainty table
                                    last_value = new_value_list[-1]
                                    new_value_list.append(last_value*(1 + list_e_pass[y-1]*gdp_growth_apply/100))

                            # store the results now:
                            new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                            TotalDemand = deepcopy( new_value_list_rounded )
                            #
                            if scenario_list[s] == 'BAU':  # NDP needs mode shift
                                for a_set in range( len( Sets_Involved ) ):
                                    this_set = Sets_Involved[a_set]
                                    this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                    updated_value_list = []
                                    #
                                    for n in range( len(TotalDemand) ):
                                        updated_value_list.append( TotalDemand[n]*distribution_passenger_BAU[ this_set ][n] )
                                    updated_value_list_rounded = [ round(elem, 4) for elem in updated_value_list ]
                                    #
                                    inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy( updated_value_list_rounded )

                        #
                        elif X_Cat in [ 'Electrical Demand', 'Fuel Demand', 'Freight Demand' ]:                          
                            # Extract the total demands before any adjustment:
                            value_list_total = [0 for j in range(len(time_range_vector))]
                            for a_set_aux in range( len( Sets_Involved ) ):
                                this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('FUEL') ]
                                #
                                this_set_aux = Sets_Involved[a_set_aux]
                                this_set_range_indices_aux = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set_aux ) ]
                                value_list_aux = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices_aux[0]:this_set_range_indices_aux[-1]+1 ] )
                                for j in range( len( value_list_aux ) ):
                                    value_list_total[j] += deepcopy( float( value_list_aux[j] ) )
                            #
                            for a_set in range( len( Sets_Involved ) ):
                                this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('FUEL') ]
                                #
                                this_set = Sets_Involved[a_set]
                                this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                #
                                value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                value_list = [ float( value_list[j] ) for j in range( len( value_list ) ) ]

                                if X_Cat in 'Freight Demand':
                                    # now that the value is extracted, we must manipulate the result and store in TotalDemand
                                    all_years = [ y for y in range( 2018 , 2050+1 ) ]
                                    index_2024 = all_years.index( 2024 )
                                    local_df_elasticities = deepcopy(df_elasticities)
                                    local_df_elasticities.iloc[-1, local_df_elasticities.columns.get_loc('e_Freight')] = float(Values_per_Future[fut_id])
                                    local_df_elasticities['e_Freight'].interpolate(method ='linear', limit_direction ='forward', inplace = True)
                                    list_e_fre = local_df_elasticities['e_Freight'].tolist()

                                    new_value_list = []
                                    for y in range(len(all_years)):
                                        if y < index_2024:
                                            new_value_list.append(value_list[y])
                                        else:  # apply growth formula with demand elasticity
                                            gdp_growth_apply = experiment_dictionary[1]['Values'][fut_id]  # the first element in the uncertainty table
                                            last_value = new_value_list[-1]
                                            new_value_list.append(last_value*(1 + list_e_fre[y-1]*gdp_growth_apply/100))

                                else:  # non-transport demands
                                    value_list_ratio = [value_list[j]/value_list_total[j] for j in range( len( value_list ) )]
                                    if X_Cat in 'Electrical Demand':
                                        df_intensity_col = 'i_NT_elec'
                                    elif X_Cat in 'Fuel Demand':
                                        df_intensity_col = 'i_NT_fossil'
                                    # We must now find the elements
                                    if a_set == 0:
                                        local_df_intensities = deepcopy(df_intensities)
                                        last_value_use = local_df_intensities[df_intensity_col].tolist()[-1]
                                        local_df_intensities.iloc[-1, local_df_intensities.columns.get_loc(df_intensity_col)] = float(Values_per_Future[fut_id])*last_value_use
                                        local_df_intensities[df_intensity_col].interpolate(method ='linear', limit_direction ='forward', inplace = True)
                                        list_i = local_df_intensities[df_intensity_col].tolist()
                                        
                                        print('check intensities')
                                        sys.exit()

                                    new_value_list = []
                                    for y in range(len(all_years)):
                                        if y < index_2024:
                                            new_value_list.append(value_list_ratio[y]*list_gdp_ref[y]*list_i[y]/1e6)
                                            last_gdp = deepcopy(list_gdp_ref[y])
                                        else:  # apply growth formula with demand elasticity
                                            gdp_growth_apply = experiment_dictionary[1]['Values'][fut_id]  # the first element in the uncertainty table
                                            new_gdp = last_gdp*(1+gdp_growth_apply/100)
                                            new_value_list.append(value_list_ratio[y]*new_gdp*list_i[y]/1e6)
                                            last_gdp = deepcopy(new_gdp)

                                # Assign parameters back: for these subset of uncertainties
                                new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy( new_value_list_rounded )

                        elif Math_Type == 'Blend_Time_Series':  # we can enter this snippet at "Adjustment OAR" if we want to ignore biofuel variations
                            #
                            Techs_Emissions = {
                                'T4DSL_HEA':[ 'CO2e_Freight', 'CO2e_HeavyCargo', 'CO2e' ],
                                'T4DSL_LIG':[ 'CO2e_Freight', 'CO2e_LightCargo', 'CO2e' ],
                                'T4DSL_PRI':[ 'CO2e' ],
                                'T4DSL_PUB':[ 'CO2e' ],
                                'T4GSL_LIG':[ 'CO2e_Freight', 'CO2e_LightCargo', 'CO2e' ],
                                'T4GSL_PRI':[ 'CO2e' ],
                                'T4GSL_PUB':[ 'CO2e' ],
                                'DIST_GSL':['CO2e_sources'] }
                            #
                            for n in range( len( Sets_Involved ) ):
                                #
                                Blend_Shares[ scenario_list[s] ][f].update( { Sets_Involved[n]:{} } )
                                #
                                for n2 in range( len( Techs_Emissions[ Sets_Involved[n] ] ) ):
                                    this_tech_emission_indices_fuel = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'EmissionActivityRatio' ][ 't' ] ) if x == Sets_Involved[n] ] # it is actually a tech representing a fuel, so it is all OK
                                    this_tech_emission_indices_emission = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'EmissionActivityRatio' ][ 'e' ] ) if x == Techs_Emissions[ Sets_Involved[n] ][n2] ]
                                    #
                                    r_index = set(this_tech_emission_indices_fuel) & set(this_tech_emission_indices_emission)
                                    this_tech_emission_indices = list( r_index )
                                    this_tech_emission_indices.sort()
                                    #
                                    # NOTE: we call stable_scenarios['BAU'] to manipulate all the emission activity ratio
                                    value_list = deepcopy( stable_scenarios[ 'BAU' ][ 'EmissionActivityRatio' ]['value'][ this_tech_emission_indices[0]:this_tech_emission_indices[-1]+1 ] )
                                    value_list = [ float(value_list[j]) for j in range( len(value_list) ) ]
                                    #
                                    start_blend_point = [int(Values_per_Future[fut_id][0]), Values_per_Future[fut_id][1]]
                                    final_blend_point = [int(Values_per_Future[fut_id][2]), Values_per_Future[fut_id][3]]
                                    new_value_list_rounded, biofuel_shares = interpolation_blend( start_blend_point, final_blend_point, value_list, time_range_vector )
                                    #
                                    inherited_scenarios[ scenario_list[s] ][ f ][ 'EmissionActivityRatio' ]['value'][ this_tech_emission_indices[0]:this_tech_emission_indices[-1]+1 ] = deepcopy( new_value_list_rounded )
                                    #
                                    Blend_Shares[ scenario_list[s] ][f][ Sets_Involved[n] ].update( { Techs_Emissions[ Sets_Involved[n] ][n2]:deepcopy( biofuel_shares ) } )
                                    #
                                #
                            #
                        #------------------------------------------------------------------------------------------------------------------------------------------#
                        elif X_Cat == 'Rail Demand': # THIS SEEMS UNUSED
                            #
                            for a_set in range( len( Sets_Involved ) ):
                                #
                                this_set = Sets_Involved[ a_set ]
                                this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ 't' ] ) if x == str( this_set ) ]
                                #
                                # extracting time:
                                time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                # extracting value:
                                value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                value_list = [ float( value_list[j] ) for j in range( len( value_list ) ) ]
                                #                                
                                new_value_list = deepcopy( dc_shift( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                #
                                inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy( new_value_list_rounded )

                        #------------------------------------------------------------------------------------------------------------------------------------------#
                        # The X type below is manipulated with immediate restitution after adjustment.
                        elif Math_Type == 'Adoption_Curve' and X_Cat == 'Mode Shift':
                            for a_set in range( len( Sets_Involved ) ):
                                this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('FUEL') ]
                                #
                                this_set = Sets_Involved[a_set]
                                this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                #--------------------------------------------------------------------------#
                                # before manipulating the variables for Mode Shift, we must use use the reference ratio of the future 0 - BAU. It is crucial to conceive the change as a relative of this baseline for more critcal comparison. BAU does not change this share. Finally, we leave Non-Motorized out of this procedure because it does not affect the BAU.
                                #
                                passpub_range_indices_BAU = [ i for i, x in enumerate( stable_scenarios['BAU'][ 'SpecifiedAnnualDemand' ][ this_set_type_initial ] ) if x == str( 'E6TDPASPUB' ) ]
                                passpub_value_list_BAU_0 = deepcopy( stable_scenarios['BAU'][ 'SpecifiedAnnualDemand' ]['value'][ passpub_range_indices_BAU[0]:passpub_range_indices_BAU[-1]+1 ] )
                                passpub_value_list_BAU_0 = [ float( passpub_value_list_BAU_0[j] ) for j in range( len( passpub_value_list_BAU_0 ) ) ]
                                #
                                passpriv_range_indices_BAU = [ i for i, x in enumerate( stable_scenarios['BAU'][ 'SpecifiedAnnualDemand' ][ this_set_type_initial ] ) if x == str( 'E6TDPASPRI' ) ]
                                passpriv_value_list_BAU_0 = deepcopy( stable_scenarios['BAU'][ 'SpecifiedAnnualDemand' ]['value'][ passpriv_range_indices_BAU[0]:passpriv_range_indices_BAU[-1]+1 ] )
                                passpriv_value_list_BAU_0 = [ float( passpriv_value_list_BAU_0[j] ) for j in range( len( passpriv_value_list_BAU_0 ) ) ]
                                #
                                passpub_share_list_BAU_0 = [ passpub_value_list_BAU_0[j]/(passpub_value_list_BAU_0[j]+passpriv_value_list_BAU_0[j]) for j in range( len(passpub_value_list_BAU_0) ) ]
                                #
                                passpriv_share_list_BAU_0 = [ passpriv_value_list_BAU_0[j]/(passpub_value_list_BAU_0[j]+passpriv_value_list_BAU_0[j]) for j in range( len(passpriv_value_list_BAU_0) ) ]
                                #
                                # we are done here, no we proceed as usual...
                                #--------------------------------------------------------------------------#
                                # for each index we extract the time and value in a list:
                                # extracting time:
                                time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                #  WE DO NOT NEED TO EXTRACT THE EXACT VALUE:
                                # now that the value is extracted, we must manipulate the result and assign back
                                L_index = 0
                                Q_index = 1
                                k_index = 2
                                M_index = 3
                                #
                                L = Values_per_Future[fut_id][L_index]
                                Q = Values_per_Future[fut_id][Q_index]
                                k = Values_per_Future[fut_id][k_index]
                                M = Values_per_Future[fut_id][M_index]
                                #
                                shift_years = [ n for n in range( Initial_Year_of_Uncertainty+1,final_year+1 ) ]
                                shift_year_counter = 0
                                adoption_shift = []
                                #
                                for t in range( len( time_list ) ):
                                    if time_list[t] > Initial_Year_of_Uncertainty:
                                        x = int( shift_years[shift_year_counter] )
                                        adoption_shift.append( generalized_logistic_curve(x, L, Q, k, M))
                                        shift_year_counter += 1
                                    else:
                                        adoption_shift.append( 0.0 )
                                ######################################################################################################################################################
                                new_value_list = []
                                for n in range( len( time_list ) ):
                                    if 'E6TDPASPUB' in this_set:
                                        new_value_list.append( ( passpub_share_list_BAU_0[n] + adoption_shift[n] )*( TotalDemand[n] ) )
                                        #
                                    #
                                    elif 'E6TRNOMOT' in this_set:
                                        new_value_list.append( ( adoption_shift[n] )*( TotalDemand[n] ) )
                                # 
                                new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                #
                                # Assign parameters back: for these subset of uncertainties
                                inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy( new_value_list_rounded )
                                #
                                #-----------------------------------------------------------------------#
                                # Note that because of the Experimental Table setup, after the non-motorized assignation we can adjust the values for PRIVATE TRANSPORT.
                                if 'E6TRNOMOT' in this_set:
                                    nonmot_values = deepcopy( new_value_list_rounded )# this retrieves non-motorized
                                    # we must retrieve the value of public transport
                                    passpub_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ this_set_type_initial ] ) if x == str( 'E6TDPASPUB' ) ]
                                    passpub_values = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ passpub_range_indices[0]:passpub_range_indices[-1]+1 ] )
                                    # we estimate the new private transport demand here:
                                    passpriv_new_value_list = []
                                    for n in range( len(TotalDemand) ):
                                        passpriv_new_value_list.append( TotalDemand[n] - nonmot_values[n] - passpub_values[n] )

                                    passpriv_new_value_list_rounded = [ round(elem, 4) for elem in passpriv_new_value_list ]

                                    # Assign parameters back:
                                    this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ this_set_type_initial ] ) if x == str( 'E6TDPASPRI' ) ]
                                    inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy( passpriv_new_value_list_rounded )

                        #------------------------------------------------------------------------------------------------------------------------------------------#
                        elif Math_Type == 'Time_Series' and X_Cat == 'Mode Shift':  # this generally applies to freight rail
                            # CODE HERE THE MODIFICATION OF THE CAPACITY OF RAIL
                            this_set = Sets_Involved[0]

                            # We need to call the group capacity
                            this_set_indices = [ i for i, x in enumerate( inherited_scenarios[scenario_list[s]][f][ this_parameter ][ 't' ] ) if x == str( this_set ) ]
                            value_list = deepcopy( inherited_scenarios[scenario_list[s]][f][ this_parameter ]['value'][ this_set_indices[0]:this_set_indices[-1]+1 ] )
                            value_list = [ float(value_list[j]) for j in range( len( time_range_vector ) ) ]

                            # We also need the demand correspoding to this set before any adjustments (stable_scenarios) // demand-based adjustments occurs later
                            this_demand_set = Fleet_Groups_techs_2_dem[ this_set ]
                            this_demand_set_range_indices = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( this_demand_set ) ]
                            this_demand_set_value = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ]['value'][ this_demand_set_range_indices[0]:this_demand_set_range_indices[-1]+1 ] )
                            this_demand_set_value = [ float(this_demand_set_value[j]) for j in range( len( time_range_vector ) ) ]

                            # Linear interpolation of freight modal shift
                            v_2050 = float(Values_per_Future[fut_id] )
                            x_coord_tofill, xp_coord_known, yp_coord_known = [], [], []
                            for y in range( len( time_range_vector ) ):
                                not_known_e = True
                                if time_range_vector[y] < Initial_Year_of_Uncertainty:
                                    xp_coord_known.append( y )
                                    yp_coord_known.append( 0 )
                                    not_known_e = False
                                if time_range_vector[y] == 2050:
                                    xp_coord_known.append( y )
                                    yp_coord_known.append( v_2050 )
                                    not_known_e = False
                                if not_known_e is True:
                                    x_coord_tofill.append( y )
                            #
                            y_coord_filled = list( np.interp( x_coord_tofill, xp_coord_known, yp_coord_known ) )
                            interpolated_values = []
                            for coord in range( len( time_range_vector ) ):
                                if coord in xp_coord_known:
                                    value_index = xp_coord_known.index(coord)
                                    interpolated_values.append( float( yp_coord_known[value_index] ) )
                                elif coord in x_coord_tofill:
                                    value_index = x_coord_tofill.index(coord)
                                    interpolated_values.append( float( y_coord_filled[value_index] ) )

                            # We redifine the new capacity of trains according to demand:
                            new_value_list = [ float( interpolated_values[j]*this_demand_set_value[j] ) for j in range( len( time_range_vector ) ) ]
                            new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                            inherited_scenarios[scenario_list[s]][f][ this_parameter ]['value'][ this_set_indices[0]:this_set_indices[-1]+1 ] = deepcopy( new_value_list_rounded )

                            # We must adjust the capacity of the complementary set of *Techs_Trains_Freight*
                            this_set_complement_dict = {'Techs_Trains_Freight':'Techs_He_Freight'}
                            this_set_complement = this_set_complement_dict[this_set]
                            this_set_complement_indices = [ i for i, x in enumerate( inherited_scenarios[scenario_list[s]][f][ this_parameter ][ 't' ] ) if x == str( this_set_complement ) ]
                            value_list_complement = deepcopy( inherited_scenarios[scenario_list[s]][f][ this_parameter ]['value'][ this_set_complement_indices[0]:this_set_complement_indices[-1]+1 ] )
                            value_list_complement = [ float(value_list_complement[j]) for j in range( len( time_range_vector ) ) ]

                            # Extract OR parameters:
                            or_group_tech_indices = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( this_set_complement ) ]
                            or_group_tech_values = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                            or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]

                            # Define new heavy truck capacity
                            if this_parameter == 'TotalAnnualMaxCapacity':
                                security_multiplier_factor = 1.01
                            elif this_parameter == 'TotalTechnologyAnnualActivityLowerLimit':
                                security_multiplier_factor = 0.999

                            new_value_list_comp = []
                            for y in range(len(time_range_vector)):
                                if time_range_vector[y] < Initial_Year_of_Uncertainty:
                                    new_value_list_comp.append(value_list_complement[y])
                                else:
                                    new_value_list_comp.append( security_multiplier_factor*(this_demand_set_value[y] - new_value_list_rounded[y])/or_group_tech_values[y] )

                            new_value_list_comp_rounded = [ round(elem, 4) for elem in new_value_list_comp ]
                            inherited_scenarios[scenario_list[s]][f][ this_parameter ]['value'][ this_set_complement_indices[0]:this_set_complement_indices[-1]+1 ] = deepcopy( new_value_list_comp_rounded )

                        #------------------------------------------------------------------------------------------------------------------------------------------#
                        elif Math_Type=='Time_Series' and 'Public Transport Distribution' in X_Cat:
                            for a_set in range( len( Sets_Involved ) ):
                                this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('TECHNOLOGY') ]
                                #
                                this_set = Sets_Involved[a_set]
                                this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                #
                                time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                #
                                value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                value_list = [ float( value_list[j] ) for j in range( len( value_list ) ) ]
                                #
                                # We must call base parameters, as these have not been modified as of yet:
                                # 
                                or_indices_BASE = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( this_set ) ]
                                or_values_BASE = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'OutputActivityRatio' ]['value'][ or_indices_BASE[0]:or_indices_BASE[-1]+1 ] )
                                or_values_BASE = [ float(or_values_BASE[j]) for j in range( len(or_values_BASE) )]
                                #
                                # to call the demand we must also call the capacity of the rail, which is in 1:1 relationship for capacity and demand
                                #
                                d_indices_BASE = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( Fleet_Groups_techs_2_dem[ this_set ] ) ]
                                d_values_BASE = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ]['value'][ d_indices_BASE[0]:d_indices_BASE[-1]+1 ] )
                                d_values_BASE = [ float(d_values_BASE[j]) for j in range( len(d_values_BASE) )]
                                #
                                d_indices_FUT = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( Fleet_Groups_techs_2_dem[ this_set ] ) ]
                                d_values_FUT = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ d_indices_FUT[0]:d_indices_FUT[-1]+1 ] )
                                d_values_FUT = [ float(d_values_FUT[j]) for j in range( len(d_values_FUT) )]
                                #
                                # now, we look at the adjustment algorithm by first extracting a pkm proportion
                                this_set_pkm_proportion = []
                                for n in range( len(value_list) ):
                                    this_set_pkm_proportion.append( value_list[n]*or_values_BASE[n] / d_values_BASE[n] )
                                # we can re-use the Final_Value interpolation for Time Series. However, we first need to define the correct value
                                Existing_Final_Value_Porportion = this_set_pkm_proportion[-1]
                                New_Final_Value_Porportion = Existing_Final_Value_Porportion*Values_per_Future[fut_id]
                                # the final value of the Time_Series of the capacity set is given by:
                                Final_Value_Porportion = (New_Final_Value_Porportion*d_values_BASE[-1]/or_values_BASE[-1])/value_list[-1]
                                new_value_list_pre = deepcopy( interpolation_non_linear_final( time_list, value_list, Final_Value_Porportion ) )
                                new_value_list = [ new_value_list_pre[n]*d_values_FUT[n]/d_values_BASE[n] for n in range( len( time_list ) ) ]
                                #
                                new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy( new_value_list_rounded )
                                #
                                #-----------------------------------------------------------------------------------------#
                                if 'Techs_Taxis' == this_set:
                                    # By design from the Uncertainty_Table, we know that BUSES need to be adjusted as the subtraction of taxis and minibuses (taxis was the last).
                                    # First, call the indices of the values for the BUSES:
                                    bus_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( 'Techs_Buses' ) ]
                                    # Then call the total public passenger demand (reusing the work of this session):
                                    public_demand_value = deepcopy( d_values_FUT )
                                    #--------------------------------------------------------------------------------------------------------------------------------------------#
                                    # Then retrieve the taxi data (reusing the work of this session):
                                    taxis_or_values = deepcopy( or_values_BASE )
                                    taxis_capacity = deepcopy( new_value_list_rounded )
                                    #--------------------------------------------------------------------------------------------------------------------------------------------#
                                    # We recall what we had for minibuses:
                                    minibus_or_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ this_set_type_initial ] ) if x == str( 'Techs_Microbuses' ) ]
                                    minibus_capacity_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( 'Techs_Microbuses' ) ]
                                    #
                                    minibus_or_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ minibus_or_indices[0]:minibus_or_indices[-1]+1 ]
                                    minibus_capacity = inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ minibus_capacity_indices[0]:minibus_capacity_indices[-1]+1 ]
                                    #
                                    minibus_or_values = [ float( minibus_or_values[j] ) for j in range( len( minibus_or_values ) ) ]
                                    #--------------------------------------------------------------------------------------------------------------------------------------------#
                                    # We recall what we had for trains: // this is not experimented across
                                    train_pass_or_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ this_set_type_initial ] ) if x == str( 'Techs_Trains' ) ]
                                    train_pass_capacity_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( 'Techs_Trains' ) ]
                                    #
                                    train_pass_or_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ train_pass_or_indices[0]:train_pass_or_indices[-1]+1 ]
                                    train_pass_capacity_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ train_pass_capacity_indices[0]:train_pass_capacity_indices[-1]+1 ]
                                    #
                                    train_pass_or_values, train_pass_capacity_values = [ float( train_pass_or_values[j] ) for j in range( len( train_pass_or_values ) ) ], [ float( train_pass_capacity_values[j] ) for j in range( len( train_pass_capacity_values ) ) ]
                                    #--------------------------------------------------------------------------------------------------------------------------------------------#
                                    # Here the key is to adjust the values of CAPACITY for Buses. For this, we must first retrieve the Occupancy Rate values for Buses:
                                    bus_or_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ this_set_type_initial ] ) if x == str( 'Techs_Buses' ) ]
                                    bus_or_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ bus_or_indices[0]:bus_or_indices[-1]+1 ]
                                    bus_or_values = [ float( bus_or_values[j] ) for j in range( len( bus_or_values ) ) ]
                                    # Now we proceed:
                                    if this_parameter == 'TotalAnnualMaxCapacity':
                                        security_multiplier_factor = 1.001
                                        security_multiplier_factor_inverse = 1.01
                                    elif this_parameter == 'TotalTechnologyAnnualActivityLowerLimit':
                                        security_multiplier_factor = 0.999
                                        security_multiplier_factor_inverse = 0.99
                                    #
                                    bus_damand_values = []
                                    bus_capacity_values = []
                                    
                                    taxis_lower_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ this_set_type_initial ] ) if x == str( 'Techs_Taxis' ) ]
                                    minibus_lower_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ this_set_type_initial ] ) if x == str( 'Techs_Microbuses' ) ]
                                    taxis_lower_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ taxis_lower_indices[0]:taxis_lower_indices[-1]+1 ]
                                    minibus_lower_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ minibus_lower_indices[0]:minibus_lower_indices[-1]+1 ]
                                    
                                    for n in range( len( time_list ) ):
                                        bus_damand_values.append( public_demand_value[n] - ( taxis_lower_values[n]*taxis_or_values[n] + minibus_lower_values[n]*minibus_or_values[n] + train_pass_capacity_values[n]*train_pass_or_values[n] )/security_multiplier_factor_inverse )
                                        bus_capacity_values.append( security_multiplier_factor*bus_damand_values[n]/bus_or_values[n] )
                                    #
                                    # I have to do this because of the covid system
                                    if this_parameter == 'TotalAnnualMaxCapacity':
                                        bus_capacity_values_saturate = [ bus_capacity_values[0] ]
                                        for n in range( 1, len( bus_capacity_values ) ):
                                            if bus_capacity_values[n] < bus_capacity_values[n-1] or bus_capacity_values[n] < bus_capacity_values_saturate[-1]:
                                                bus_capacity_values_saturate.append( bus_capacity_values_saturate[-1] )
                                            else:
                                                bus_capacity_values_saturate.append( bus_capacity_values[n] )
                                        bus_capacity_values = deepcopy( bus_capacity_values_saturate )

                                    new_bus_value_list = deepcopy( bus_capacity_values )
                                    #
                                    new_bus_value_list_rounded = [ round(elem, 4) for elem in new_bus_value_list ]
                                    inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ bus_set_range_indices[0]:bus_set_range_indices[-1]+1 ] = deepcopy( new_bus_value_list_rounded )
                                    #
                                    # We must be aware that we need these results and that they will change later on. So we must sort them for the adjustment of the fuel technologies.
                                    #-----------------------------------------------------------------------------------------#
                                #-----------------------------------------------------------------------#
                            #
                        #
                        # The X type below is manipulated with immidiate restitution after adjustment.
                        elif ( Math_Type=='Time_Series' and ( Explored_Parameter_of_X=='Initial_Value' or
                                                              Explored_Parameter_of_X=='Final_Value' or
                                                              Explored_Parameter_of_X=='Shift_as_percent_of_Initial_Value'
                                                              or Explored_Parameter_of_X=='Year_when_reaches_zero' )
                                                              and ('Distance' not in X_Cat)
                                                              and ('Demand' not in X_Cat)
                                                              and ('Non-Rail' not in X_Cat)
                                                              and ('Mode Shift' not in X_Cat) ) or ( Math_Type=='Discrete_Investments' ):
                            #
                            if 'InputActivityRatio' == this_parameter: # we must carefully select the fuels for IAR!
                                #
                                for a_set in range( len( Sets_Involved ) ):
                                    #
                                    this_set = Sets_Involved[a_set]
                                    this_set_range_indices_tech = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ 't' ] ) if x == str( this_set ) ]
                                    #
                                    this_set_fuel_list = []
                                    for test_j in range( len( this_set_range_indices_tech ) ):
                                        if float( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices_tech[test_j] ] ) != 1.0:
                                            this_set_fuel_list.append( deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['f'][ this_set_range_indices_tech[test_j] ] ) )
                                        #
                                    #
                                    this_set_fuel_list_unique = list( set( this_set_fuel_list ) )
                                    #
                                    for a_fuel in range( len( this_set_fuel_list_unique ) ):
                                        this_set_fuel = this_set_fuel_list_unique[ a_fuel ]
                                        #
                                        this_set_range_indices_fuel = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ 'f' ] ) if x == str( this_set_fuel ) ]
                                        #
                                        r_index = set(this_set_range_indices_tech) & set(this_set_range_indices_fuel)
                                        this_set_range_indices = list( r_index )
                                        this_set_range_indices.sort()
                                        #
                                        # extracting time:
                                        time_list = []
                                        for i_list in this_set_range_indices:
                                            # time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                            time_list.append(deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ i_list ] ))
                                        time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                        # extracting value:
                                        value_list = []
                                        for i_list in this_set_range_indices:
                                            # value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                            value_list.append(deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ i_list ] ))
                                        value_list = [ float( value_list[j] ) for j in range( len( value_list ) ) ]
                                        #
                                        if Explored_Parameter_of_X=='Final_Value':
                                            new_value_list = deepcopy( interpolation_non_linear_final( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                        #
                                        if Explored_Parameter_of_X=='Shift_as_percent_of_Initial_Value':
                                            new_value_list = deepcopy( time_series_shift( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                        #--------------------------------------------------------------------#
                                        new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                        #
                                        for i_list_idx in range(len(this_set_range_indices)):
                                            i_list = this_set_range_indices[i_list_idx]
                                            inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ i_list ] = deepcopy( new_value_list_rounded[i_list_idx] )
                                        #
                                        '''
                                        if X_Cat == 'Unit BEV Cost':
                                            xx1 = value_list
                                            xx2 = new_value_list
                                            print('check this IAR issue internal')
                                            sys.exit()
                                        '''
                                    #
                                    '''
                                    if X_Cat == 'Unit BEV Cost':
                                        print('check this IAR issue')
                                        sys.exit()
                                    '''
                                    #
                                #
                            #
                            #
                            else:
                                for a_set in range( len( Sets_Involved ) ):
                                    this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('TECHNOLOGY') ]
                                    #
                                    this_set = Sets_Involved[a_set]
                                    this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                    #
                                    if this_parameter != 'CapacityFactor' and len(this_set_range_indices) != 0:
                                        # for each index we extract the time and value in a list:
                                        # extracting time:
                                        time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                        time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                        # extracting value:
                                        value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                        value_list = [ float( value_list[j] ) for j in range( len( value_list ) ) ]
                                        #--------------------------------------------------------------------#
                                        # now that the value is extracted, we must manipulate the result and assign back
                                        if Explored_Parameter_of_X == 'Final_Value': # we must add a component to make occupancy rate be relative to BAU for the other 3 base scenarios
                                            if this_parameter == 'OutputActivityRatio' and 'Adjustment OAR' not in X_Cat:
                                                if scenario_list[s] == 'BAU':  # bypass this
                                                    new_value_list = deepcopy( interpolation_non_linear_final( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                                    reference_occupancy_rate[ scenario_list[s] ][f].update( { this_set:new_value_list } )
                                                #
                                                else:
                                                    # Store the pre-modification values for the BAU
                                                    reference_occupancy_rate[ 'BAU' ][f].update( { this_set:value_list } )
                                                    new_value_list = deepcopy( interpolation_non_linear_final( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                                    reference_occupancy_rate[ scenario_list[s] ][f].update( { this_set:new_value_list } )
                                                    #
                                                ###############################################################################
                                                # Take advantage of this action and make adjustment to accident externalities with changed occupancy rate:
                                                oar_indices_BASE = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( this_set ) ]
                                                oar_values_BASE = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'OutputActivityRatio' ]['value'][ oar_indices_BASE[0]:oar_indices_BASE[-1]+1 ] )
                                                oar_values_BASE = [ float(oar_values_BASE[j]) for j in range( len(oar_values_BASE) )]
                                                #
                                                time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                                time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                                #
                                                # Use 'new_value_list' to adjust the system:
                                                base_set_range_indices_tech = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'EmissionActivityRatio' ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                                base_set_range_indices_emission = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'EmissionActivityRatio' ][ 'e' ] ) if x == str( 'Accidents' ) ]
                                                base_set_range_indices_adjust = list( set(base_set_range_indices_tech) & set(base_set_range_indices_emission) )
                                                base_set_range_indices_adjust.sort()
                                                #--#
                                                this_set_range_indices_tech = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'EmissionActivityRatio' ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                                this_set_range_indices_emission = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'EmissionActivityRatio' ][ 'e' ] ) if x == str( 'Accidents' ) ]
                                                this_set_range_indices_adjust = list( set(this_set_range_indices_tech) & set(this_set_range_indices_emission) )
                                                this_set_range_indices_adjust.sort()
                                                #
                                                this_tech_externality_emission = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'EmissionActivityRatio' ]['value'][ base_set_range_indices_adjust[0]:base_set_range_indices_adjust[-1]+1 ] )
                                                #
                                                new_tech_externality_emission = [ float( this_tech_externality_emission[n] )*float( new_value_list[n] )/float( oar_values_BASE[n] ) for n in range( len( this_tech_externality_emission ) ) ]
                                                new_tech_externality_emission_rounded = [ round(elem, 4) for elem in new_tech_externality_emission ]
                                                #
                                                inherited_scenarios[ scenario_list[s] ][ f ][ 'EmissionActivityRatio' ]['value'][ this_set_range_indices_adjust[0]:this_set_range_indices_adjust[-1]+1 ] = deepcopy( new_tech_externality_emission_rounded )
                                                ################################################################################
                                            #
                                            else:
                                                #
                                                new_value_list = deepcopy( interpolation_non_linear_final( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                                #
                                            #
                                        #
                                        elif Explored_Parameter_of_X=='Initial_Value':
                                            new_value_list = deepcopy( interpolation_non_linear_initial( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                        elif Explored_Parameter_of_X=='Shift_as_percent_of_Initial_Value':
                                            new_value_list = deepcopy( time_series_shift( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                        elif Explored_Parameter_of_X=='Year_when_reaches_zero':
                                            new_value_list = deepcopy( year_when_reaches_zero( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                        elif Explored_Parameter_of_X=='Overall_DC_Shift':
                                            new_value_list = deepcopy( dc_shift( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                        #
                                        new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                        #--------------------------------------------------------------------#
                                        #
                                        if this_parameter == 'OutputActivityRatio' and 'Adjustment OAR' not in X_Cat: # We must adjust the transport group capacities once we obtain new occupancy rates.

                                            # let's extract rail capacity to adjust this apropiately
                                            train_pass_capacity_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ][ 't' ] ) if x == str( 'Techs_Trains' ) ]
                                            train_pass_capacity_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ]['value'][ train_pass_capacity_indices[0]:train_pass_capacity_indices[-1]+1 ]
                                            if Fleet_Groups_techs_2_dem[ Sets_Involved[ a_set ] ] == 'E6TDPASPUB' and scenario_list[ s ] == 'NDP':
                                                subtract_list = [float(train_pass_capacity_values[j]) for j in range(len(train_pass_capacity_values))]
                                            else:
                                                subtract_list = [0 for j in range(len(train_pass_capacity_values))]

                                            # let's extract the initial demand
                                            demand_indices_BASE = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( Fleet_Groups_techs_2_dem[ this_set ] ) ]
                                            demand_values_BASE = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices_BASE[0]:demand_indices_BASE[-1]+1 ] )
                                            demand_values_BASE = [ float( demand_values_BASE[j] ) - subtract_list[j] for j in range( len( demand_values_BASE ) ) ]
                                            # let's extract the newly assigned demand
                                            demand_indices_NEW = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( Fleet_Groups_techs_2_dem[ this_set ] ) ]
                                            demand_values_NEW = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices_NEW[0]:demand_indices_NEW[-1]+1 ] )
                                            demand_values_NEW = [ float( demand_values_NEW[j] ) - subtract_list[j] for j in range( len( demand_values_NEW ) ) ]
                                            #
                                            this_set_range_indices_max_cap = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                            old_max_cap_values = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalAnnualMaxCapacity' ]['value'][ this_set_range_indices_max_cap[0]:this_set_range_indices_max_cap[-1]+1 ] )
                                            old_max_cap_values = [ float( old_max_cap_values[j] ) for j in range( len( old_max_cap_values ) ) ]
                                            #
                                            ### if (this_set in group_tech_PRIVATE and s != 0) or s==0:
                                            new_max_cap_values = [0 for n in range( len( old_max_cap_values ) )]
                                            for n in range( len( time_list ) ):
                                                if time_list[n] >= Initial_Year_of_Uncertainty:
                                                    new_max_cap_values[n] = 1.01*old_max_cap_values[n]*( ( demand_values_NEW[n] / new_value_list[n] ) / ( demand_values_BASE[n] / value_list[n] ) )
                                                else:
                                                    new_max_cap_values[n] = old_max_cap_values[n]
                                            ### elif (this_set in group_tech_PUBLIC and s != 0) or s==0: # this is done because the distribution of public transport is done earlier
                                            ###     new_max_cap_values = [ old_max_cap_values[n]*( ( demand_values_NEW[n] / new_value_list_rounded[n] ) / ( demand_values_BASE[n] / value_list[n] ) ) for n in range( len( old_max_cap_values ) ) ]
                                            ###     #
                                            #
                                            new_max_cap_values_rounded = [ round(elem, 4) for elem in new_max_cap_values ]
                                            inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalAnnualMaxCapacity' ]['value'][ this_set_range_indices_max_cap[0]:this_set_range_indices_max_cap[-1]+1 ] = deepcopy( new_max_cap_values_rounded )
                                            #
                                            this_set_range_indices_min_cap = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                            old_min_cap_values = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ this_set_range_indices_min_cap[0]:this_set_range_indices_min_cap[-1]+1 ] )
                                            old_min_cap_values = [ float( old_min_cap_values[j] ) for j in range( len( old_min_cap_values ) ) ]
                                            #
                                            ### if (this_set in group_tech_PRIVATE and s != 0) or s==0:
                                            new_min_cap_values = [0 for n in range( len( old_min_cap_values ) )]
                                            for n in range( len( time_list ) ):
                                                if time_list[n] >= Initial_Year_of_Uncertainty:
                                                    new_min_cap_values[n] = 0.99*old_min_cap_values[n]*( ( demand_values_NEW[n] / new_value_list[n] ) / ( demand_values_BASE[n] / value_list[n] ) )
                                                else:
                                                    new_min_cap_values[n] = old_min_cap_values[n]
                                            ### new_min_cap_values = [ old_min_cap_values[n]*( ( demand_values_NEW[n] / new_value_list[n] ) / ( demand_values_BASE[n] / value_list[n] ) ) for n in range( len( old_min_cap_values ) ) ]
                                            ### elif this_set in group_tech_PUBLIC and s != 0:
                                            ###     new_min_cap_values = [ old_min_cap_values[n]*( ( demand_values_NEW[n] / new_value_list_rounded[n] ) / ( demand_values_BASE[n] / value_list[n] ) ) for n in range( len( old_min_cap_values ) ) ]
                                            #
                                            new_min_cap_values_rounded = [ round(elem, 4) for elem in new_min_cap_values ]
                                            inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ this_set_range_indices_min_cap[0]:this_set_range_indices_min_cap[-1]+1 ] = deepcopy( new_min_cap_values_rounded )
                                            #
                                            if this_set == 'Techs_Sedan': # we must adjust motorcycles for demand, as it is not explored for occupancy rate
                                                #
                                                motorcycle_range_indices_max_cap = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ][ this_set_type_initial ] ) if x == str( 'Techs_Motos' ) ]
                                                old_max_cap_values = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalAnnualMaxCapacity' ]['value'][ motorcycle_range_indices_max_cap[0]:motorcycle_range_indices_max_cap[-1]+1 ] )
                                                old_max_cap_values = [ float( old_max_cap_values[j] ) for j in range( len( old_max_cap_values ) ) ]
                                                #
                                                new_max_cap_values = [ old_max_cap_values[n]*( demand_values_NEW[n] / demand_values_BASE[n] ) for n in range( len( old_max_cap_values ) ) ]
                                                new_max_cap_values_rounded = [ round(elem, 4) for elem in new_max_cap_values ]
                                                inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalAnnualMaxCapacity' ]['value'][ motorcycle_range_indices_max_cap[0]:motorcycle_range_indices_max_cap[-1]+1 ] = deepcopy( new_max_cap_values_rounded )
                                                #
                                                motorcycle_range_indices_min_cap = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ this_set_type_initial ] ) if x == str( 'Techs_Motos' ) ]
                                                old_min_cap_values = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ motorcycle_range_indices_min_cap[0]:motorcycle_range_indices_min_cap[-1]+1 ] )
                                                old_min_cap_values = [ float( old_min_cap_values[j] ) for j in range( len( old_min_cap_values ) ) ]
                                                #
                                                new_min_cap_values = [ old_min_cap_values[n]*( demand_values_NEW[n] / demand_values_BASE[n] ) for n in range( len( old_min_cap_values ) ) ]
                                                new_min_cap_values_rounded = [ round(elem, 4) for elem in new_min_cap_values ]
                                                inherited_scenarios[ scenario_list[s] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ motorcycle_range_indices_min_cap[0]:motorcycle_range_indices_min_cap[-1]+1 ] = deepcopy( new_min_cap_values_rounded )

                                            # # if scenario_list[s] != 'BAU':
                                            # if 'Techs_Taxis' == this_set:  # this is the capacity check
                                            # 
                                            #     # CHECK BEFORE ANY OAR ADJUSTMENT
                                            #     # LET'S ADJUST FOR PUBLIC TRANSPORT:
                                            #     new_public_passenger_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                                            #     for n in range( len( group_tech_PUBLIC) ): # this includes rail
                                            #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_PUBLIC[n] ) ]
                                            #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                                            #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                                            #         #
                                            #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_PUBLIC[n] ) ]
                                            #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                                            #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                                            #         #
                                            #         for n2 in range( len( time_range_vector ) ):
                                            #             new_public_passenger_demand[n2] += (cap_group_tech_values[n2]*1.00)*or_group_tech_values[n2] #*applicable_distance_dictionaries[group_tech_PUBLIC[n]][n2]
                                            #     
                                            #     # LET'S ADJUST FOR PRIVATE TRANSPORT:
                                            #     new_private_passenger_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                                            #     for n in range( len( group_tech_PRIVATE) ):
                                            #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_PRIVATE[n] ) ]
                                            #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                                            #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                                            #         #
                                            #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_PRIVATE[n] ) ]
                                            #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                                            #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                                            #         #
                                            #         for n2 in range( len( time_range_vector ) ):
                                            #             new_private_passenger_demand[n2] += (cap_group_tech_values[n2]*1.00)*or_group_tech_values[n2] # *applicable_distance_dictionaries[group_tech_PRIVATE[n]][n2]
                                            #         #
                                            #     #
                                            #     new_public_passenger_demand_rounded = [ round(elem, 4) for elem in new_public_passenger_demand ]
                                            #     public_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDPASPUB' ) ]
                                            #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ public_demand_indices[0]:public_demand_indices[-1]+1 ] = deepcopy( new_public_passenger_demand_rounded )
                                            #     #
                                            #     new_private_passenger_demand_rounded = [ round(elem, 4) for elem in new_private_passenger_demand ]
                                            #     private_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDPASPRI' ) ]
                                            #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ private_demand_indices[0]:private_demand_indices[-1]+1 ] = deepcopy( new_private_passenger_demand_rounded )

                                        #--------------------------------------------------------------------#``
                                        # Assign parameters back: for these subset of uncertainties
                                        inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy(new_value_list_rounded)

                                        # if scenario_list[s] != 'BAU':
                                        # if 'Techs_Taxis' == this_set and this_parameter == 'OutputActivityRatio' and 'Adjustment OAR' not in X_Cat:  # this is the capacity check
                                        # 
                                        #     # CHECK BEFORE ANY OAR ADJUSTMENT
                                        #     # LET'S ADJUST FOR PUBLIC TRANSPORT:
                                        #     new_public_passenger_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                                        #     for n in range( len( group_tech_PUBLIC) ): # this includes rail
                                        #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_PUBLIC[n] ) ]
                                        #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                                        #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                                        #         #
                                        #         # TotalTechnologyAnnualActivityLowerLimit // TotalAnnualMaxCapacity
                                        #         #
                                        #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_PUBLIC[n] ) ]
                                        #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                                        #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                                        #         #
                                        #         for n2 in range( len( time_range_vector ) ):
                                        #             new_public_passenger_demand[n2] += (cap_group_tech_values[n2]*1.00)*or_group_tech_values[n2] #*applicable_distance_dictionaries[group_tech_PUBLIC[n]][n2]
                                        #     
                                        #     # LET'S ADJUST FOR PRIVATE TRANSPORT:
                                        #     new_private_passenger_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                                        #     for n in range( len( group_tech_PRIVATE) ):
                                        #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_PRIVATE[n] ) ]
                                        #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                                        #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                                        #         #
                                        #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_PRIVATE[n] ) ]
                                        #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                                        #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                                        #         #
                                        #         for n2 in range( len( time_range_vector ) ):
                                        #             new_private_passenger_demand[n2] += (cap_group_tech_values[n2]*1.00)*or_group_tech_values[n2] # *applicable_distance_dictionaries[group_tech_PRIVATE[n]][n2]
                                        #         #
                                        #     #
                                        #     new_public_passenger_demand_rounded = [ round(elem, 4) for elem in new_public_passenger_demand ]
                                        #     public_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDPASPUB' ) ]
                                        #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ public_demand_indices[0]:public_demand_indices[-1]+1 ] = deepcopy( new_public_passenger_demand_rounded )
                                        #     #
                                        #     new_private_passenger_demand_rounded = [ round(elem, 4) for elem in new_private_passenger_demand ]
                                        #     private_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDPASPRI' ) ]
                                        #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ private_demand_indices[0]:private_demand_indices[-1]+1 ] = deepcopy( new_private_passenger_demand_rounded )


                                        #
                                    #--------------------------------------------------------------------#
                                    elif this_parameter == 'CapacityFactor':
                                        season_list = ['All']
                                        for season in range( len( season_list ) ):
                                            this_l_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ 'l' ] ) if x == str( season_list[season] ) ]
                                            #
                                            this_set_range_indices_useful = intersection(this_set_range_indices, this_l_range_indices)
                                            #
                                            # for each index we extract the time and value in a list:
                                            # extracting time:
                                            time_list = []
                                            for useful_index in range( len( this_set_range_indices_useful ) ):
                                                time_list.append( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices_useful[ useful_index ] ] )
                                            time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                            # extracting value:
                                            value_list = []
                                            for useful_index in range( len( this_set_range_indices_useful ) ):
                                                value_list.append( deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices_useful[ useful_index ] ] ) )
                                            value_list = [ float( value_list[j] ) for j in range( len( value_list ) ) ]
                                            #--------------------------------------------------------------------#
                                            # now that the value is extracted, we must manipulate the result and assign back
                                            if Explored_Parameter_of_X=='Final_Value': # By design, this must always happen.
                                                new_value_list = deepcopy( interpolation_non_linear_final( time_list, value_list, float(Values_per_Future[fut_id] ) ) )
                                            #--------------------------------------------------------------------#``
                                            new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                            #
                                            # Assign parameters back: for these subset of uncertainties
                                            for useful_index in range( len( this_set_range_indices_useful ) ):
                                                inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices_useful[ useful_index ]  ] = new_value_list_rounded[ useful_index ]

                        elif Math_Type=='Adoption_Curve' and ('Electrification' in X_Cat or 'Penetration' in X_Cat):
                            #
                            for a_set in range( len( Sets_Involved ) ):
                                this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('TECHNOLOGY') ]
                                #
                                this_set = Sets_Involved[a_set]
                                this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                # extracting time:
                                time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
                                #  WE DO NOT NEED TO EXTRACT THE EXACT VALUE:
                                # now that the value is extracted, we must manipulate the result and assign back
                                L_index = 0
                                Q_index = 1
                                k_index = 2
                                M_index = 3
                                #
                                L = Values_per_Future[fut_id][L_index]
                                Q = Values_per_Future[fut_id][Q_index]
                                k = Values_per_Future[fut_id][k_index]
                                M = Values_per_Future[fut_id][M_index]
                                #
                                shift_years = [ n for n in range( Initial_Year_of_Uncertainty,final_year+1 ) ]
                                shift_year_counter = 0
                                adoption_share = []
                                for t in range( len( time_list ) ):
                                    if time_list[t] > Initial_Year_of_Uncertainty:
                                        x = int( shift_years[shift_year_counter] )
                                        adoption_share.append( generalized_logistic_curve(x, L, Q, k, M))
                                        shift_year_counter += 1
                                    else:
                                        adoption_share.append( 0.0 )
                                #
                                group_tech_set = Fleet_Groups_inv[ this_set ]
                                group_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( group_tech_set ) ]
                                group_value_list = inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ group_set_range_indices[0]:group_set_range_indices[-1]+1 ]
                                group_value_list = [ float( j ) for j in group_value_list ]

                                if this_parameter == 'TotalAnnualMaxCapacity':
                                    sec_multiplier = 1.001
                                elif this_parameter == 'TotalTechnologyAnnualActivityLowerLimit':
                                    sec_multiplier = 0.999
                                #
                                new_value_list = []
                                for n in range( len( time_list ) ):
                                    new_value_list.append( sec_multiplier*group_value_list[n]*adoption_share[n] )
                                #
                                # Here we must include the exceptions for hydrgoen for the NDP no to surpass the limit of the group technology:
                                if this_set in [ 'TRBUSHYD', 'TRMBUSHYD', 'TRYTKHYD' ]:
                                    # We know Hydrogen only has TotalTechnologyAnnualActivityLowerLimit. We must compare each Hydrogen technology with the corresponding electric technology (previously determined).
                                    if this_set == 'TRBUSHYD':
                                        corresponding_set = 'TRBUSELE'
                                    if this_set == 'TRMBUSHYD':
                                        corresponding_set = 'TRMBUSELE'
                                    if this_set == 'TRYTKHYD':
                                        corresponding_set = 'TRYTKELE'
                                    #
                                    the_group_value_list = deepcopy( group_value_list )
                                    #
                                    the_electric_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ 't' ] ) if x == str( corresponding_set ) ]
                                    the_electric_tech_values = inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ the_electric_tech_indices[0]:the_electric_tech_indices[-1]+1 ]
                                    the_electric_tech_values = [ float( the_electric_tech_values[j] ) for j in range( len( the_electric_tech_values ) ) ]
                                    #
                                    new_value_list_fix = [] # Note that 'new_value_list' is for Hydrogen:
                                    for n in range( len( time_list ) ):
                                        if ( new_value_list[n] > the_group_value_list[n] - the_electric_tech_values[n] ) and ( this_parameter == 'TotalTechnologyAnnualActivityLowerLimit' ): # here we must leave the max capacity untouched
                                            new_value_list_fix.append( ( the_group_value_list[n] - the_electric_tech_values[n] )*0.999 )
                                        else:
                                            new_value_list_fix.append( new_value_list[n]*0.999 )
                                    new_value_list_rounded = [ round(elem, 4) for elem in new_value_list_fix ]
                                    #
                                else:
                                    new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                #
                                inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy(new_value_list_rounded)
                                #-----------------------------------------------------------------------#
                            #
                        #
                        elif 'Distance' in X_Cat: # This is the last adjustment

                            if p == 0:
                                dem_adj_public = True
                                dem_adj_private = True
                                dem_adj_heafre = True
                                dem_adj_ligfre = True

                            for a_set in range( len( Sets_Involved ) ):
                                # Distance is a parameter that is not in Osemosys directly, but is implicit in multiple parameters.
                                # Now, we proceed to estimate the change in the curve of distance across futures. Note that this modification does not depend on the baseline values.
                                #
                                this_set_type_initial = S_DICT_sets_structure['initial'][ S_DICT_sets_structure['set'].index('TECHNOLOGY') ]
                                #
                                this_set = Sets_Involved[a_set] # these are GROUP TECHS, please do not forget
                                #
                                base_distance = Fleet_Groups_Distance[this_set]

                                new_distance = deepcopy( interpolation_non_linear_final( time_range_vector, base_distance, float(Values_per_Future[fut_id] ) ) )
                                reference_driven_distance[ scenario_list[s] ][f].update( {this_set:new_distance} )

                                this_demand_set = Fleet_Groups_techs_2_dem[ Sets_Involved[ a_set ] ]
                                if ((this_demand_set == 'E6TDPASPRI' and dem_adj_private is True) or
                                    (this_demand_set == 'E6TDPASPUB' and dem_adj_public is True) or
                                    (this_demand_set == 'E6TDFREHEA' and dem_adj_heafre is True) or
                                    (this_demand_set == 'E6TDFRELIG' and dem_adj_ligfre is True)):

                                    # let's extract rail capacity to adjust this apropiately
                                    train_pass_capacity_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ][ 't' ] ) if x == str( 'Techs_Trains' ) ]
                                    train_pass_capacity_values = inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ]['value'][ train_pass_capacity_indices[0]:train_pass_capacity_indices[-1]+1 ]
                                    if Fleet_Groups_techs_2_dem[ Sets_Involved[ a_set ] ] == 'E6TDPASPUB' and scenario_list[ s ] == 'NDP':
                                        subtract_list = [float(train_pass_capacity_values[j]) for j in range(len(train_pass_capacity_values))]
                                    else:
                                        subtract_list = [0 for j in range(len(train_pass_capacity_values))]

                                    demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( this_demand_set ) ]
                                    demand_list = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices[0]:demand_indices[-1]+1 ] )
                                    #
                                    new_value_list = []
                                    for n in range( len( value_list ) ):
                                        if n < index_2024:
                                            new_value_list.append( demand_list[n] )
                                        else:
                                            new_value_list.append( (demand_list[n]-subtract_list[n])*new_distance[n]/base_distance[n] )
                                            new_value_list[-1] += subtract_list[n]
                                    new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                    #
                                    inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices[0]:demand_indices[-1]+1 ] = deepcopy(new_value_list_rounded)
                                    #                                       
                                    if this_demand_set == 'E6TDPASPRI':
                                        demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TRNOMOT' ) ]
                                        demand_list = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices[0]:demand_indices[-1]+1 ] )
                                        #
                                        new_value_list = []
                                        for n in range( len( value_list ) ):
                                            if n < index_2024:
                                                new_value_list.append( demand_list[n] )
                                            else:
                                                new_value_list.append( demand_list[n]*new_distance[n]/base_distance[n] )
                                        new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                        #
                                        inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices[0]:demand_indices[-1]+1 ] = deepcopy(new_value_list_rounded)
                                        dem_adj_private = False
                                        #
                                    if this_demand_set == 'E6TDPASPUB':
                                        dem_adj_public = False
                                        #
                                    if this_demand_set == 'E6TDFREHEA':
                                        dem_adj_heafre = False
                                        #
                                    if this_demand_set == 'E6TDFRELIG':
                                        dem_adj_ligfre = False

                                if ('Techs_' in this_set and this_parameter in ['TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityLowerLimit'] ): # THIS CONDITION WILL ALWAYS BE TRUE
                                    #
                                    this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( this_set ) ]
                                    #
                                    if len(this_set_range_indices) != 0:
                                        # The obtained distance change is used appropiately from here on (...)
                                        # We must proceed with the group set IF the parameter is adequate:
                                        value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                        value_list = [ float(value_list[j]) for j in range( len(value_list) ) ]
                                        #
                                        new_value_list = []
                                        for n in range( len( value_list ) ):
                                            if n < index_2024:
                                                new_value_list.append( value_list[n] )
                                            else:
                                                new_value_list.append( value_list[n]*new_distance[n]/base_distance[n] )
                                        #
                                        new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                        inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy( new_value_list_rounded )

                                        if this_set == 'Techs_He_Freight' and scenario_list[s] != 'BAU':  # here we need to adjust the capacity of freight rail for consistency
                                            tsri_frerail = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ this_set_type_initial ] ) if x == str( 'Techs_Trains_Freight' ) ]
                                            value_list_frerail = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ this_parameter ]['value'][ tsri_frerail[0]:tsri_frerail[-1]+1 ] )
                                            value_list_frerail = [ float(value_list_frerail[j]) for j in range( len(value_list_frerail) ) ]
                                            #
                                            new_value_list_frerail = []
                                            for n in range( len( value_list_frerail ) ):
                                                new_value_list_frerail.append( value_list_frerail[n]*new_distance[n]/base_distance[n] )
                                            #
                                            new_value_list_frerail_rounded = [ round(elem, 4) for elem in new_value_list_frerail ]
                                            inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ tsri_frerail[0]:tsri_frerail[-1]+1 ] = deepcopy( new_value_list_frerail_rounded )

                                # Me must act upon the parameters that get affected by the distance change. We must the read the scenario and extract a list of the technologies that require the change.
                                go_to_file = all_dataset_address + scenario_list[s] + '/' + this_parameter + '.csv'
                                df_getter = pd.read_csv( go_to_file )
                                # We first need to obtain the sets that are affected, i.e. new technologies considering the shift effect of residual technologies:
                                get_tech_list_raw_raw = df_getter.loc[ df_getter['YEAR'] == initial_year ]
                                get_tech_list_raw = list( get_tech_list_raw_raw['TECHNOLOGY'] ) # this has the technologies with a given restriction
                                #
                                applicable_transport_techs = Fleet_Groups[ this_set ]
                                this_transport_techs = []
                                #
                                for n in range( len( get_tech_list_raw ) ):
                                    if get_tech_list_raw[n] in applicable_transport_techs:
                                        this_transport_techs.append( get_tech_list_raw[n] )
                                #
                                # now we must iterate and check whether the values are adjustable;
                                # adjustable means that the values are not 99999 for TotalAnnualMaxCapacity for techs
                                for n in range( len( this_transport_techs ) ):
                                    proceed_with_adjustment = True
                                    if this_parameter == 'TotalAnnualMaxCapacity':
                                        the_2050_value_raw = df_getter.loc[ ( df_getter['TECHNOLOGY'].str.contains( this_transport_techs[n] ) ) & (df_getter['YEAR'] == final_year ) ]
                                        the_2050_value = float( "{0:.3f}".format( the_2050_value_raw['Value'].iloc[0] ) )
                                        if the_2050_value >= 99:
                                            proceed_with_adjustment = False
                                    #
                                    if proceed_with_adjustment == True:
                                        #
                                        adjust_cap_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ][ 't' ] ) if x == str( this_transport_techs[n] ) ]
                                        adjustment_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ adjust_cap_indices[0]:adjust_cap_indices[-1]+1 ] )
                                        adjustment_values = [ float( adjustment_values[j] ) for j in range( len( adjustment_values ) ) ]
                                        #--#
                                        # now we perform the adjustment for 02 techs:
                                        adjustment_values_new = []
                                        for z in range( len( adjustment_values ) ):
                                            adjustment_values_new.append( adjustment_values[z]*( new_distance[z]/base_distance[z] ) )
                                        #
                                        adjustment_values_new_rounded = [ round(elem, 4) for elem in adjustment_values_new ]
                                        inherited_scenarios[ scenario_list[ s ] ][ f ][ this_parameter ]['value'][ adjust_cap_indices[0]:adjust_cap_indices[-1]+1 ] = deepcopy( adjustment_values_new_rounded )

                            

                    # Here we now perform the demand adjustment for all demand types, as we must adjust the demands:
                    # if 'Distance' in X_Cat:
                    #     #
                    #     applicable_distance_dictionaries = reference_driven_distance[ scenario_list[s] ][f]
                    #     #
                    #     # NOTE: for separate distances for passenger and freight transport, refer to the previous Future_Runs_Manager.py version
                    #     #
                    #     # LET'S ADJUST FOR PUBLIC TRANSPORT:
                    #     new_public_passenger_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                    #     for n in range( len( group_tech_PUBLIC) ): # this includes rail
                    #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_PUBLIC[n] ) ]
                    #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                    #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                    #         #
                    #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_PUBLIC[n] ) ]
                    #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                    #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                    #         #
                    #         for n2 in range( len( time_range_vector ) ):
                    #             new_public_passenger_demand[n2] += (cap_group_tech_values[n2]*1.00001)*or_group_tech_values[n2] #*applicable_distance_dictionaries[group_tech_PUBLIC[n]][n2]
                    # 
                    #     # LET'S ADJUST FOR PRIVATE TRANSPORT:
                    #     new_private_passenger_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                    #     for n in range( len( group_tech_PRIVATE) ):
                    #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_PRIVATE[n] ) ]
                    #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                    #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                    #         #
                    #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_PRIVATE[n] ) ]
                    #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                    #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                    #         #
                    #         for n2 in range( len( time_range_vector ) ):
                    #             new_private_passenger_demand[n2] += (cap_group_tech_values[n2]*1.00001)*or_group_tech_values[n2] # *applicable_distance_dictionaries[group_tech_PRIVATE[n]][n2]
                    #         #
                    #     #
                    # 
                    #     new_public_passenger_demand_rounded = [ round(elem, 4) for elem in new_public_passenger_demand ]
                    #     public_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDPASPUB' ) ]
                    #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ public_demand_indices[0]:public_demand_indices[-1]+1 ] = deepcopy( new_public_passenger_demand_rounded )
                    #     #
                    #     new_private_passenger_demand_rounded = [ round(elem, 4) for elem in new_private_passenger_demand ]
                    #     private_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDPASPRI' ) ]
                    #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ private_demand_indices[0]:private_demand_indices[-1]+1 ] = deepcopy( new_private_passenger_demand_rounded )
                    # 
                    #     if scenario_list[s] != 'BAU':
                    #         # WE ADJUST FOR NON MOTORIZED WHEN IT IS NEEDED (IF WE ARE NOT IN BAU).
                    #         non_motorized_passenger_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == 'E6TRNOMOT' ]
                    #         non_motorized_passenger_demand_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ non_motorized_passenger_demand_indices[0]:non_motorized_passenger_demand_indices[-1]+1 ] )
                    #         #
                    #         # we must pick a this_k_adjust to manipulate the non-motrized demand based on the private demand // we arbitrarily choose Techs_Sedan
                    #         base_distance = reference_driven_distance['BAU'][f][ 'Techs_Sedan' ]
                    #         base_distance = deepcopy( interpolation_non_linear_final( time_list, base_distance, 1 ) )
                    #         this_k_adjust = [ applicable_distance_dictionaries['Techs_Sedan'][n]/base_distance[n] for n in range( len( non_motorized_passenger_demand_values ) ) ]
                    #         #
                    #         new_non_motorized_passenger_demand = []
                    #         for n in range( len( non_motorized_passenger_demand_values ) ):
                    #             new_non_motorized_passenger_demand.append( this_k_adjust[n]*non_motorized_passenger_demand_values[n] )
                    #         #
                    #         new_non_motorized_passenger_demand_rounded = [ round(elem, 4) for elem in new_non_motorized_passenger_demand ]
                    #         inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ non_motorized_passenger_demand_indices[0]:non_motorized_passenger_demand_indices[-1]+1 ] = deepcopy( new_non_motorized_passenger_demand_rounded )
                    # 
                    #     # LET'S ADJUST FOR HEAVY FREIGHT:
                    #     new_heavy_freight_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                    #     for n in range( len( group_tech_FREIGHT_HEA) ): # this includes rail
                    #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_FREIGHT_HEA[n] ) ]
                    #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                    #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                    #         #
                    #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_FREIGHT_HEA[n] ) ]
                    #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                    #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                    #         #
                    #         for n2 in range( len( time_range_vector ) ):
                    #             new_heavy_freight_demand[n2] += (cap_group_tech_values[n2]*1.00001)*or_group_tech_values[n2]
                    # 
                    #     # LET'S ADJUST FOR LIGHT FREIGHT:
                    #     new_light_freight_demand = [ 0 for n in range( len( time_range_vector ) ) ]
                    #     for n in range( len( group_tech_FREIGHT_LIG) ):
                    #         or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( group_tech_FREIGHT_LIG[n] ) ]
                    #         or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
                    #         or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
                    #         #
                    #         cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ][ 't' ] ) if x == str( group_tech_FREIGHT_LIG[n] ) ]
                    #         cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalTechnologyAnnualActivityLowerLimit' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
                    #         cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
                    #         #
                    #         for n2 in range( len( time_range_vector ) ):
                    #             new_light_freight_demand[n2] += (cap_group_tech_values[n2]*1.00001)*or_group_tech_values[n2]
                    # 
                    #     new_heavy_freight_demand_rounded = [ round(elem, 4) for elem in new_heavy_freight_demand ]
                    #     heavy_freight_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDFREHEA' ) ]
                    #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ heavy_freight_demand_indices[0]:heavy_freight_demand_indices[-1]+1 ] = deepcopy( new_heavy_freight_demand_rounded )
                    #     #
                    #     new_light_freight_demand_rounded = [ round(elem, 4) for elem in new_light_freight_demand ]
                    #     light_freight_demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( 'E6TDFRELIG' ) ]
                    #     inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ light_freight_demand_indices[0]:light_freight_demand_indices[-1]+1 ] = deepcopy( new_light_freight_demand_rounded )

                if 'Adjustment OAR' in X_Cat: # right after maximum vehicle capacity, for all scenarios, to include the changes in OutputActivityRatio
                    ####### USE THIS LINE FOR AUTOMATIC ADJUSTMENT // BY DESIGN THIS CAN BE DONE AFTER MAXIMUM VEHICLE CAPACITY HAS BEEN MANIPULATED #######
                    # %% WE CAN TAKE ADVANTAGE HERE AND ADJUST ALL GROUP TECHS FOR COHERENCE %%
                    #
                    # ADD AN EXCEPTION LIST BELOW TO SHOW THE GROUPS THAT SHOULD NOT BE ADJUSTED TO AVOID DOUBLING THE WORK:
                    except_techs = ['Techs_SUVMIV', 'Techs_Sedan', 'Techs_Motos', 'Techs_Buses', 'Techs_Microbuses', 'Techs_Taxis']
                    except_scen = ['NDP']
                    #
                    params_to_adjust = [ 'TotalAnnualMaxCapacity', 'TotalTechnologyAnnualActivityLowerLimit' ]
                    for par in range( len( params_to_adjust ) ):
                        for a_set in range( len( Sets_Involved ) ):
                            #
                            if Sets_Involved[ a_set ] in except_techs and scenario_list[ s ] in except_scen:  # except, pass
                                #print(Sets_Involved[ a_set ])
                                pass
                            else:
                                this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ params_to_adjust[par] ][ 't' ] ) if x == str( Sets_Involved[ a_set ] ) ]
                                value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ params_to_adjust[par] ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
                                value_list = [ float( value_list[j] ) for j in range( len( value_list ) ) ]
                                #
                                demand_indices_BASE = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( Fleet_Groups_techs_2_dem[ Sets_Involved[ a_set ] ] ) ]
                                demand_list_BASE = deepcopy( stable_scenarios[ scenario_list[ s ] ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices_BASE[0]:demand_indices_BASE[-1]+1 ] )
                                demand_list_BASE = [ float(demand_list_BASE[j]) for j in range(len(demand_list_BASE)) ]
                                #
                                demand_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( Fleet_Groups_techs_2_dem[ Sets_Involved[ a_set ] ] ) ]
                                demand_list = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ demand_indices[0]:demand_indices[-1]+1 ] )
                                #
                                new_value_list_old_base = deepcopy( value_list )
                                new_value_list = [ new_value_list_old_base[n]*(demand_list[n]/demand_list_BASE[n]) for n in range( len( new_value_list_old_base ) )]
                                new_value_list_rounded = [ round(elem, 4) for elem in new_value_list ]
                                #
                                inherited_scenarios[ scenario_list[s] ][ f ][ params_to_adjust[par] ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] = deepcopy(new_value_list_rounded)

                    # -.-.-.-.-.-.-.-.-.--.-.-.-.-.-.-.-.-.-.--.-.-.-.-.-.-.-.-.-.-.- #
                    # Go with TotalAnnualMaxCapacity and TotalTechnologyAnnualActivityLowerLimit changes:
                    for par in range( len( params_to_adjust ) ):
                        #
                        if params_to_adjust[par] == 'TotalAnnualMaxCapacity':
                            security_multiplier_factor = 1.001
                        elif params_to_adjust[par] == 'ResidualCapacity':
                            security_multiplier_factor = 1
                        elif params_to_adjust[par] == 'TotalTechnologyAnnualActivityLowerLimit':
                            security_multiplier_factor = 0.999

                        ##############################################################################################################################
                        #
                        go_to_file = all_dataset_address + '/' + scenario_list[s] + '/' + params_to_adjust[par] + '.csv'
                        df_getter = pd.read_csv( go_to_file )
                        # We first need to obtain the sets that are affected, i.e. new technologies considering the shift effect of residual technologies:
                        get_tech_list_raw_raw = df_getter.loc[ df_getter['YEAR'] == final_year ]
                        get_tech_list_raw = list( get_tech_list_raw_raw['TECHNOLOGY'] )
                        #
                        applicable_transport_techs = list( Fleet_Groups_inv.keys() )
                        this_transport_techs = []
                        #
                        for n in range( len( get_tech_list_raw ) ):
                            if get_tech_list_raw[n] in applicable_transport_techs:
                                this_transport_techs.append( get_tech_list_raw[n] )
                        #
                        for n in range( len( this_transport_techs ) ):
                            proceed_with_adjustment = True
                            if params_to_adjust[par] == 'TotalAnnualMaxCapacity':
                                the_2050_value_raw = df_getter.loc[ ( df_getter['TECHNOLOGY'].str.contains( this_transport_techs[n] ) ) & (df_getter['YEAR'] == final_year ) ]
                                the_2050_value = float( "{0:.3f}".format( the_2050_value_raw['Value'].iloc[0] ) )
                                if the_2050_value >= 99:
                                    proceed_with_adjustment = False
                            #
                            if proceed_with_adjustment is True:
                                #
                                adjust_cap_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ params_to_adjust[par] ][ 't' ] ) if x == str( this_transport_techs[n] ) ]
                                adjust_cap_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ params_to_adjust[par] ]['value'][ adjust_cap_indices[0]:adjust_cap_indices[-1]+1 ] )
                                adjust_cap_values = [ float( adjust_cap_values[j] ) for j in range( len( adjust_cap_values ) ) ]
                                #
                                this_group_tech = Fleet_Groups_inv[ this_transport_techs[n] ]
                                # here we obtain the magnitude that must be considered for the adjustment
                                capacity_indices_BASE = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ params_to_adjust[par] ][ 't' ] ) if x == str( this_group_tech ) ]
                                capacity_values_BASE = deepcopy( stable_scenarios[ scenario_list[ s ] ][ params_to_adjust[par] ]['value'][ capacity_indices_BASE[0]:capacity_indices_BASE[-1]+1 ] )
                                capacity_values_BASE = [ float( capacity_values_BASE[j] ) for j in range( len( capacity_values_BASE ) ) ]
                                #
                                capacity_indices_NEW = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ params_to_adjust[par] ][ 't' ] ) if x == str( this_group_tech ) ]
                                capacity_values_NEW = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ params_to_adjust[par] ]['value'][ capacity_indices_NEW[0]:capacity_indices_NEW[-1]+1 ] )
                                capacity_values_NEW = [ float( capacity_values_NEW[j] ) for j in range( len( capacity_values_NEW ) ) ]
                                #
                                # we are now prepared to estimate the new values
                                adjust_cap_values_new = []
                                for z in range( len( adjust_cap_values ) ):
                                    if time_range_vector[z] > Initial_Year_of_Uncertainty:
                                        adjust_cap_values_new.append( security_multiplier_factor*adjust_cap_values[z]*( capacity_values_NEW[z]/capacity_values_BASE[z] ) )
                                    else:
                                        adjust_cap_values_new.append( adjust_cap_values[z])
                                #
                                adjust_cap_values_new_rounded = [ round(elem, 4) for elem in adjust_cap_values_new ]
                                inherited_scenarios[ scenario_list[ s ] ][ f ][ params_to_adjust[par] ]['value'][ adjust_cap_indices[0]:adjust_cap_indices[-1]+1 ] = deepcopy( adjust_cap_values_new_rounded )
                                #
                            #
                        #
                    #
                    #--------------------------------------------------------------------#
                    ignore_biofuels = True
                    if ignore_biofuels is True and scenario_list[s] != 'BAU':
                        #
                        Techs_Emissions = {
                            'T4DSL_HEA':[ 'CO2e_Freight', 'CO2e_HeavyCargo', 'CO2e' ],
                            'T4DSL_LIG':[ 'CO2e_Freight', 'CO2e_LightCargo', 'CO2e' ],
                            'T4DSL_PRI':[ 'CO2e' ],
                            'T4DSL_PUB':[ 'CO2e' ],
                            'T4GSL_LIG':[ 'CO2e_Freight', 'CO2e_LightCargo', 'CO2e' ],
                            'T4GSL_PRI':[ 'CO2e' ],
                            'T4GSL_PUB':[ 'CO2e' ],
                            'DIST_GSL':['CO2e_sources'] }
                        #
                        Sets_Involved = \
                            ['T4DSL_HEA', 'T4DSL_LIG', 'T4DSL_PRI',
                             'T4DSL_PUB', 'T4GSL_LIG',
                             'T4GSL_PRI', 'T4GSL_PUB', 'DIST_GSL']
                        #
                        for n in range( len( Sets_Involved ) ):
                            #
                            Blend_Shares[ scenario_list[s] ][f].update( { Sets_Involved[n]:{} } )
                            #
                            for n2 in range( len( Techs_Emissions[ Sets_Involved[n] ] ) ):
                                this_tech_emission_indices_fuel = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'EmissionActivityRatio' ][ 't' ] ) if x == Sets_Involved[n] ] # it is actually a tech representing a fuel, so it is all OK
                                this_tech_emission_indices_emission = [ i for i, x in enumerate( stable_scenarios[ scenario_list[ s ] ][ 'EmissionActivityRatio' ][ 'e' ] ) if x == Techs_Emissions[ Sets_Involved[n] ][n2] ]
                                #
                                r_index = set(this_tech_emission_indices_fuel) & set(this_tech_emission_indices_emission)
                                this_tech_emission_indices = list( r_index )
                                this_tech_emission_indices.sort()
                                #
                                # NOTE: we call stable_scenarios['BAU'] to manipulate all the emission activity ratio
                                value_list = deepcopy( stable_scenarios[ 'BAU' ][ 'EmissionActivityRatio' ]['value'][ this_tech_emission_indices[0]:this_tech_emission_indices[-1]+1 ] )
                                value_list = [ float(value_list[j]) for j in range( len(value_list) ) ]
                                #
                                inherited_scenarios[ scenario_list[s] ][ f ][ 'EmissionActivityRatio' ]['value'][ this_tech_emission_indices[0]:this_tech_emission_indices[-1]+1 ] = deepcopy( value_list )
                                #
                            #
                        #

#                if f == 100:
#
#                    this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == 'E6TDPASPUB' ]
#                    # extracting value:
#                    value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
#                    demand = [ float(value_list[j]) for j in range( len( value_list ) ) ]
#
#                    summed_value_list = [0 for n2 in range(len( time_range_vector ))]
#
#                    pass_dem_sets = ['Techs_Buses', 'Techs_Microbuses', 'Techs_Taxis', 'Techs_Trains']
#                    for a_set in range( len( pass_dem_sets ) ):
#                        this_set = pass_dem_sets[a_set]
#                        #
#                        or_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ][ 't' ] ) if x == str( this_set ) ]
#                        or_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'OutputActivityRatio' ]['value'][ or_group_tech_indices[0]:or_group_tech_indices[-1]+1 ] )
#                        or_group_tech_values = [ float( or_group_tech_values[j] ) for j in range( len( or_group_tech_values ) ) ]
#                        #
#                        cap_group_tech_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ][ 't' ] ) if x == str( this_set ) ]
#                        cap_group_tech_values = deepcopy( inherited_scenarios[ scenario_list[ s ] ][ f ][ 'TotalAnnualMaxCapacity' ]['value'][ cap_group_tech_indices[0]:cap_group_tech_indices[-1]+1 ] )
#                        cap_group_tech_values = [ float( cap_group_tech_values[j] ) for j in range( len( cap_group_tech_values ) ) ]
#                        #
#                        for n2 in range( len( time_range_vector ) ):
#                            summed_value_list[n2] += (cap_group_tech_values[n2])*or_group_tech_values[n2]
#                    #
#                    # Here we take advantage of the loop to obtain the baseline shares to apply to the BAU scenario:
#                    if scenario_list[s] == 'NDP':
#                        difference = [summed_value_list[j]-demand[j] for j in range(len(demand))]
#                        difference = [ round(elem, 4) for elem in difference ]
#                        print('u:', u, 'NDP', X_Cat, Exact_X)
#                        print('max production:', summed_value_list)
#                        print('demand', demand)
#                        print('dif:', difference)
#                        print('-------------------')


#                if f == 90:
#                    summed_value_list = []
#                    bau_summed_value_list = []
#                    pass_dem_sets = ['E6TDPASPUB' , 'E6TDPASPRI' , 'E6TRNOMOT']
#                    for a_set in range( len( pass_dem_sets ) ):
#                        this_set = pass_dem_sets[a_set]
#                        this_set_range_indices = [ i for i, x in enumerate( inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( this_set ) ]
#                        # for each index we extract the time and value in a list:
#                        # extracting time:
#                        time_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ]['y'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
#                        time_list = [ int( time_list[j] ) for j in range( len( time_list ) ) ]
#                        # extracting value:
#                        value_list = deepcopy( inherited_scenarios[ scenario_list[s] ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ this_set_range_indices[0]:this_set_range_indices[-1]+1 ] )
#                        value_list = [ float(value_list[j]) for j in range( len( value_list ) ) ]
#
#                        this_set_range_indices_bau = [ i for i, x in enumerate( inherited_scenarios[ 'BAU' ][ f ][ 'SpecifiedAnnualDemand' ][ 'f' ] ) if x == str( this_set ) ]
#                        # extracting value:
#                        value_list_bau = deepcopy( inherited_scenarios[ 'BAU' ][ f ][ 'SpecifiedAnnualDemand' ]['value'][ this_set_range_indices_bau[0]:this_set_range_indices_bau[-1]+1 ] )
#                        value_list_bau = [ float(value_list_bau[j]) for j in range( len( value_list ) ) ]
#
#                        # performing addition of sets in the case of x = 1:
#                        for element in range( len( value_list ) ):
#                            if a_set == 0:
#                                summed_value_list.append( float( value_list[element] ) )
#                                bau_summed_value_list.append( float( value_list_bau[element] ) )
#                            else:
#                                summed_value_list[element] += float ( value_list[element] )
#                                bau_summed_value_list[element] += float ( value_list_bau[element] )
#                    #
#                    if scenario_list[s] == 'BAU':
#                        test_dict.update( { u:deepcopy( summed_value_list ) } )
#                    #
#                    # Here we take advantage of the loop to obtain the baseline shares to apply to the BAU scenario:
#                    if scenario_list[s] == 'NDP':
#                        bau_summed_value_list_2 = test_dict[u]
#                        # difference = [summed_value_list[j]-bau_summed_value_list[j] for j in range(len(summed_value_list))]
#                        difference_2 = [summed_value_list[j]-bau_summed_value_list_2[j] for j in range(len(summed_value_list))]
#                        print('u:', u, 'NDP', X_Cat, Exact_X)
#                        # print('bau:', bau_summed_value_list)
#                        print('bau_2:', bau_summed_value_list_2)
#                        print('ndp:', summed_value_list)
#                        # print('dif:', difference)
#                        print('dif_2:', difference_2)
#                        print('-------------------')

            #
            fut_id += 1
    
    #
    print( '    We have finished the experiment and inheritance' )
    #
    time_list = []
    #
    scenario_list_print = scenario_list

    # We must export useful GDP data for denominator:
    gdp_dict = experiment_dictionary[1]
    gdp_growth_values = gdp_dict['Values'] # start to apply in 2024

    all_years = [ y for y in range( 2018 , 2050+1 ) ]
    index_2024 = all_years.index( 2024 )
    applicable_years = all_years[index_2024+1:]

    gdp_dict_export = {}
    gdp_dict_export.update( { 0:deepcopy( list_gdp_ref ) } )
    for n in range( 1, len( gdp_growth_values )+1 ):
        this_gdp_list = deepcopy( list_gdp_ref )
        this_growth = gdp_growth_values[n-1]
        for y in applicable_years:
            index_this_year = all_years.index( y )
            index_prev_year = all_years.index( y-1 )

            this_gdp_list[ index_this_year ] = this_gdp_list[ index_prev_year ] * ( 1 + this_growth / 100 )
            gdp_dict_export.update( { n:deepcopy( this_gdp_list ) } )

    with open( 'GDP_dict.pickle', 'wb') as handle:
        pickle.dump( gdp_dict_export, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()

    with open( 'reference_driven_distance.pickle', 'wb') as handle:
        pickle.dump( reference_driven_distance, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()

    with open( 'reference_occupancy_rate.pickle', 'wb') as handle:
        pickle.dump( reference_occupancy_rate, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()

    # Before printing the experiment dictionary, be sure to add future 0:
    experiment_dictionary[1]['Futures'] = [0] + experiment_dictionary[1]['Futures']
    experiment_dictionary[1]['Values'] = [3] + experiment_dictionary[1]['Values']  # 3% GDP growth is the basics

    with open('experiment_dictionary.pickle', 'wb') as handle:
        pickle.dump(experiment_dictionary, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()

    blend_shares_zero = pickle.load( open( './0_From_Confection/Blend_Shares_0.pickle', "rb" ) )
    Blend_Shares['NDP'].update({0: blend_shares_zero['NDP']})
    with open('Blend_Shares.pickle', 'wb') as handle:
        pickle.dump(Blend_Shares, handle, protocol=pickle.HIGHEST_PROTOCOL)
    handle.close()
    '''
    print('brake this already processed')
    sys.exit()
    '''
    if generator_or_executor == 'Generator' or generator_or_executor == 'Both':
        #
        print('4: We will now print the input .txt files of diverse future scenarios.')
        #
        print_adress = './Experimental_Platform/Futures/'
        packaged_useful_elements = [scenario_list_print, S_DICT_sets_structure, S_DICT_params_structure,
                                    list_param_default_value_params, list_param_default_value_value,
                                    print_adress, all_futures, reference_driven_distance,
                                    Fleet_Groups_inv, time_range_vector, Blend_Shares ]
        #
        if parallel_or_linear == 'Parallel':
            print('Entered Parallelization')
            #
            x = len(all_futures)*len(scenario_list_print)
            max_x_per_iter = int( setup_table.loc[ 0 ,'Parallel_Use'] ) # FLAG: This is an input
            y = x / max_x_per_iter
            y_ceil = math.ceil( y )

            #'''
            for n in range(0,y_ceil):
                n_ini = n*max_x_per_iter
                processes = []
                #
                start1 = time.time()
                #
                if n_ini + max_x_per_iter <= x:
                    max_iter = n_ini + max_x_per_iter
                else:
                    max_iter = x
                #    
                for n2 in range( n_ini , max_iter ):
                    p = mp.Process(target=function_C_mathprog_parallel, args=(n2,inherited_scenarios,packaged_useful_elements,) )
                    processes.append(p)
                    p.start()
            
                for process in processes:
                    process.join()
                end_1 = time.time()
                time_elapsed_1 = -start1 + end_1
                print( str( time_elapsed_1 ) + ' seconds' )
                time_list.append( time_elapsed_1 )
                #
            print('   The total time producing the input .txt files has been:' + str( sum( time_list ) ) + ' seconds')
            #'''
        '''
        ##########################################################################
        '''
        if parallel_or_linear == 'Linear':
            print('Started Linear Runs')
            #
            x = len(all_futures)*len(scenario_list_print)
            for n in range( x ):
                function_C_mathprog_parallel(n,inherited_scenarios,packaged_useful_elements)
        '''
        ##########################################################################
        '''
        #
    #
    #########################################################################################
    #
    if generator_or_executor == 'Executor' or generator_or_executor == 'Both':
        #
        print('5: We will produce the outputs and store the data.')
        #
        for a_scen in range( len( scenario_list_print ) ):
            #
            # packaged_useful_elements = [ specific_tech_to_group_tech, prefix_list, group_tech_ALL, BAU_reference_driven_distance, NDP_reference_driven_distance, NDP_A_reference_driven_distance, OP15C_reference_driven_distance, BAU_reference_occupancy_rate, NDP_reference_occupancy_rate, NDP_A_reference_occupancy_rate, OP15C_reference_occupancy_rate ]
            packaged_useful_elements = [reference_driven_distance, reference_occupancy_rate, Fleet_Groups_inv, time_range_vector, gdp_dict_export]
            #
            Executed_Scenario = scenario_list_print[ a_scen ]
            set_first_list(Executed_Scenario)
            #
            x = len(first_list)
            #
            max_x_per_iter = int( setup_table.loc[ 0 ,'Parallel_Use'] ) # FLAG: This is an input.
            #
            y = x / max_x_per_iter
            y_ceil = math.ceil( y )
            #
            # sys.exit()
            #'''
            for n in range(0,y_ceil):
                print('###')
                n_ini = n*max_x_per_iter
                processes = []
                #
                start1 = time.time()
                #
                if n_ini + max_x_per_iter <= x:
                    max_iter = n_ini + max_x_per_iter
                else:
                    max_iter = x
                #
                for n2 in range( n_ini , max_iter ):
                    print(n2)
                    p = mp.Process(target=main_executer, args=(n2,Executed_Scenario,packaged_useful_elements,) )
                    processes.append(p)
                    p.start()
                #
                for process in processes:
                    process.join()
                #
                end_1 = time.time()   
                time_elapsed_1 = -start1 + end_1
                print( str( time_elapsed_1 ) + ' seconds' )
                time_list.append( time_elapsed_1 )
                #'''
                #
            #
        #
    #
    print('   The total time producing outputs and storing data has been: ' + str( sum( time_list ) ) + ' seconds')
    '''
    ##########################################################################
    '''
    #
    #######################################################################################
    #
    print( 'For all effects, this has been the end. It all took: ' + str( sum( time_list ) ) + ' seconds')