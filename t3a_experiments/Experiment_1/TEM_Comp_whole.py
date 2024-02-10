# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 10:00:00 2020

@author: luisf
"""
import pandas as pd
import os
import sys
from copy import deepcopy
import time
import pickle

start1 = time.time()
global time_range_vector
time_range_vector = [ n for n in range( 2018, 2050+1 ) ]

all_columns = [ 'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF',
                'Q Imports', 'U VKT', 'Q Total', 'U Property Tax', 'FV' ]

selected_columns = [    'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                        'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                        'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                        'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                        'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                        'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                        'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                        'U VKT', 'Q Total', 'U Property Tax', 'FV'] # define later


selected_fv_and_q = [   'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                        'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS', 'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                        'U VKT', 'Q Total', 'U Property Tax', 'FV'] # define later

gdp_dict = pickle.load( open( './GDP_dict.pickle', "rb" ) )

# Gathering the dtypes for the files:
temp_comp_assist = open('TEM_Comp_assist.xlsx', 'rb')
dtype_dfs = pd.read_excel(temp_comp_assist, sheet_name='dtype')

#           For inputs:
use_dtype = {}
df_dtype = dtype_dfs.loc[(dtype_dfs['File'] == 'TEM output')]
df_cols_tem = df_dtype['Column'].tolist()
df_types_tem = df_dtype['Type'].tolist()
for n in range(len(df_cols_tem)):
    use_dtype.update({df_cols_tem[n]: df_types_tem[n]})

#####################################################################################################################################################
# Open the list of files you need
address_list = [ '' ]
# address_list = [ 'Scenario_Transfers_OneTax_X_NoExo' ]
# address_list = [ 'Scenario_Transfers_E2' ]
# address_list = [ 'Scenario_Transfers_OneTax_X_NoExo_1000' ]
# address_list = [ 'Scenario_Transfers_OneTax_X' ]
#
strategy_contribution_id_unique = []
#
initial_future = 0
final_future = 2000 # 1000+1
future_list = [ n for n in range( initial_future, final_future+1 ) ]
# strategy_list = [ 0, 1, 2, 3, 4, 5, 6 ]
# strategy_list = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ]
strategy_list = [ n for n in range( 0, 1000+1 ) ]
# strategy_list = [ n for n in range( 0, 100, 4 ) ]
# strategy_list = [ 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
# future_list += [ 118, 59 ]
#
df_list_whole = []
df_list = []
generic_filename = 'TEM'
#
if 0 in future_list:
    main_folders = [ '/Executables', '/Experimental_Platform/Futures' ]
else:
    main_folders = [ '/Experimental_Platform/Futures' ]
    #
#

# sys.exit()

for n0 in range( len( address_list ) ):
    # print('happens 1')
    for n1 in range( len( main_folders ) ):
        # print('happens 2')
        first_list_raw = os.listdir( './' + address_list[n0] + main_folders[n1] )
        
        # print('happens')
        # sys.exit()
        
        first_list = [e for e in first_list_raw if ( '.csv' not in e ) and ( 'Table' not in e ) and ( '.py' not in e ) and ( '__pycache__' not in e ) ]
        if main_folders[n1] == '/Executables': # dig in directly
            for s in range( len( first_list ) ):
                file_list_raw = os.listdir( './' + address_list[n0] + main_folders[n1] + '/' + first_list[s] )
                #
                file_list_unique = [ i for i in file_list_raw if ( generic_filename in i ) and ( 'Gini' not in i ) and ( 'RegFull' not in i ) ]
                for x in range( len( file_list_unique ) ):
                
                    # sys.exit()
                
                    file_name = file_list_unique[x]
                    file_name_elements = file_name.split('_')
                    future = file_name_elements[1]
                    file_path = './' + address_list[n0] + main_folders[n1] + '/' + first_list[s] + '/' + file_name
                    this_df = pd.read_csv(file_path, dtype=use_dtype)
                    #
                    this_scen = file_name_elements[0]

                    pass_include = True
                    if len( file_name_elements ) == 5:
                        strategy_contribution_id = file_name_elements[-1].split('.')[0]
                        #
                        if int( strategy_contribution_id ) not in strategy_list:
                            pass_include = False
                        elif this_scen != 'BAU':
                            pass_include = False
                        else:
                            pass
                        #
                        if strategy_contribution_id not in strategy_contribution_id_unique:
                            strategy_contribution_id_unique.append( strategy_contribution_id )
                        #
                        this_df['Strategy'] = 'NDPUp' + str( strategy_contribution_id )
                        #
                    #
                    else:
                        pass
                        #
                    #
                    if pass_include == True:
                        
                        # print( file_name )
                        
                        # LET'S APPLY A FILTER TO EXCLUDE CENTRAL_GOVERNMENT GATHER, AS WE WILL NOT CARE TO SHOW REVENUE, BUT ONLY TAX EXPENSE // ASLO, LET'S REMOVE SOME COLUMNS WE WILL NOT USE.
                        #
                        # this_df_filter = this_df.loc[ ( ~this_df['Actor'].isna() ) & ( ~this_df['Actor'].isin( ['central_government', 'electricity_companies', 'hydrocarbon_companies', 'hydrogen_companies' ] ) ) ]
                        this_df_filter = this_df.loc[ ( ~this_df['Actor'].isna() ) ]
                        #
                        this_df_filter[[    'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                            'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                            'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                            'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                            'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                            'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc' ]].fillna( value=0, inplace = True )
                        
                        this_df_filter_sum = this_df_filter.groupby( [ 'Strategy','Future.ID','Year','Actor','Actor_Type','Owner','GorS' ], as_index=False ).sum()
                        #
                        this_df_filter_sum['Technology'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                        this_df_filter_sum['Fuel'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                        this_df_filter_sum['Fuel_Surname'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                        this_df_filter_sum['Age'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                        #
                        this_df_filter_sum = this_df_filter_sum [ [ 'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                                                                    'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                                                                    'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                                                    'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                                                    'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                                                    'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                                                    'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                                                    'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                                                                    'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                                                                    'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                                                                    'U VKT', 'Q Total', 'U Property Tax', 'FV'] ]
                        #
                        # now, let's add the detail of data not related to expenses, but prices and quantities
                        #
                        this_df_test = this_df.loc[ ( this_df['Actor'].isna() ) ]
                        #
                        this_df_pricing_vkt = this_df.loc[ ( this_df['Actor'].isna() ) & ( ~this_df['U VKT'].isna() ) ]
                        this_df_pricing_vkt_avg = this_df_pricing_vkt.groupby( [ 'Strategy','Future.ID','Year','Technology' ], as_index=False ).mean()
                        #
                        this_df_pricing_vkt_avg['Fuel'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                        this_df_pricing_vkt_avg['Fuel_Surname'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                        this_df_pricing_vkt_avg['Age'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                        this_df_pricing_vkt_avg['Actor'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                        this_df_pricing_vkt_avg['Actor_Type'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                        this_df_pricing_vkt_avg['Owner'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                        this_df_pricing_vkt_avg['GorS'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                        #
                        this_df_pricing_vkt_avg = this_df_pricing_vkt_avg [ [ 'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                                                                    'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                                                                    'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                                                    'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                                                    'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                                                    'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                                                    'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                                                    'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                                                                    'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                                                                    'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                                                                    'U VKT', 'Q Total', 'U Property Tax', 'FV'] ]
                        #
                        this_df_pricing_energy = this_df.loc[ ( this_df['Actor'].isna() ) & ( ~this_df['Energy Tax'].isna() ) & ( this_df['U VKT'].isna() ) ]
                        this_df_pricing_service = this_df.loc[ ( this_df['Actor'].isna() ) & ( ~this_df['Service Price'].isna() ) & ( this_df['U VKT'].isna() ) ]
                        #
                        this_df_pricing_fleet = deepcopy( this_df.loc[ ( this_df['Actor'].isna() ) & ( this_df['Owner'].isna() ) & ( this_df['Energy Tax'].isna() ) & ( this_df['U VKT'].isna() ) & ( this_df['Service Price'].isna() ) ] )
                        #
                        this_df_pricing_imports_cols = [ 'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF' ]
                        imports_mask = ( ~this_df_pricing_fleet['Q Imports'].isna() )
                        for k in range( len( this_df_pricing_imports_cols ) ):
                            this_col = this_df_pricing_imports_cols[k]
                            this_df_pricing_fleet.loc[imports_mask, this_col] *= this_df_pricing_fleet.loc[ imports_mask, 'Q Imports' ]
                        #
                        this_df_pricing_fleet_cols = [ 'U Property Tax', 'FV' ]
                        fleet_mask = ( ~this_df_pricing_fleet['Q Total'].isna() )
                        for k in range( len( this_df_pricing_fleet_cols ) ):
                            this_col = this_df_pricing_fleet_cols[k]
                            this_df_pricing_fleet.loc[fleet_mask, this_col] *= this_df_pricing_fleet.loc[ fleet_mask, 'Q Total' ]
                        #
                        this_df_pricing_fleet_sum = this_df_pricing_fleet.groupby( [ 'Strategy','Future.ID','Technology','Year' ], as_index=False ).sum()
                        #
                        this_df_pricing_fleet_sum['Fuel'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                        this_df_pricing_fleet_sum['Fuel_Surname'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                        this_df_pricing_fleet_sum['Age'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                        this_df_pricing_fleet_sum['Actor'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                        this_df_pricing_fleet_sum['Actor_Type'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                        this_df_pricing_fleet_sum['Owner'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                        this_df_pricing_fleet_sum['GorS'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                        #
                        this_df_pricing_fleet_sum = this_df_pricing_fleet_sum [ [ 'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                                                                    'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                                                                    'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                                                    'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                                                    'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                                                    'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                                                    'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                                                    'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                                                                    'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                                                                    'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                                                                    'U VKT', 'Q Total', 'U Property Tax', 'FV'] ]
                        #
                        this_df_pricing_imports_cols = [ 'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF' ]
                        imports_mask = ( ~this_df_pricing_fleet_sum['Q Imports'].isin( [0] ) )
                        for k in range( len( this_df_pricing_imports_cols ) ):
                            this_col = this_df_pricing_imports_cols[k]
                            this_df_pricing_fleet_sum.loc[imports_mask, this_col] /= this_df_pricing_fleet_sum.loc[ imports_mask, 'Q Imports' ]
                        #
                        this_df_pricing_fleet_cols = [ 'U Property Tax', 'FV' ]
                        fleet_mask = ( ~this_df_pricing_fleet_sum['Q Total'].isin( [0] ) )
                        for k in range( len( this_df_pricing_fleet_cols ) ):
                            this_col = this_df_pricing_fleet_cols[k]
                            this_df_pricing_fleet_sum.loc[fleet_mask, this_col] /= this_df_pricing_fleet_sum.loc[ fleet_mask, 'Q Total' ]
                        #
                        df_list_whole.append( deepcopy( this_df ) )
                        df_list_whole[-1]['GDP'] = [ 0 for n in range( len( df_list_whole[-1].index.tolist() ) ) ]
                        for y in range( len( time_range_vector ) ):
                            df_list_whole[-1].loc[ ( df_list_whole[-1]['Year'] == time_range_vector[y] ) & ( df_list_whole[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                        #
                        df_list.append( deepcopy( this_df_filter_sum ) )
                        df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                        for y in range( len( time_range_vector ) ):
                            df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                        #
                        # df_list.append( this_df_filter )
                        #
                        df_list.append( deepcopy( this_df_pricing_vkt_avg ) )
                        df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                        for y in range( len( time_range_vector ) ):
                            df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                        #
                        df_list.append( deepcopy( this_df_pricing_energy ) )
                        df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                        for y in range( len( time_range_vector ) ):
                            df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                        #
                        df_list.append( deepcopy( this_df_pricing_service ) )
                        df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                        for y in range( len( time_range_vector ) ):
                            df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                        #
                        df_list.append( deepcopy( this_df_pricing_fleet_sum ) )
                        df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                        for y in range( len( time_range_vector ) ):
                            df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                        #
                        print( 'n1', len( this_df.columns.tolist() ), n1, s, x )
                        #
                    #
                #
            #
        #
        else: # create a second list
            # sys.exit()
            for n2 in range( len( first_list ) ):
                second_list_raw = os.listdir( './' + address_list[n0] + main_folders[n1] + '/' + first_list[n2] )
                second_list = [e for e in second_list_raw if ( '.csv' not in e ) and ( 'Table' not in e ) and ( '.py' not in e ) and ( '__pycache__' not in e ) and ( int( e.split('_')[-1] ) in future_list ) ]
                for s in range( len( second_list ) ):
                    file_list_raw = os.listdir( './' + address_list[n0] + main_folders[n1] + '/' + first_list[n2] + '/' + second_list[s] )
                    #
                    file_list_unique = [ i for i in file_list_raw if ( generic_filename in i ) and ( 'Gini' not in i ) and ( 'RegFull' not in i ) ]
                    for x in range( len( file_list_unique ) ):
                        file_name = file_list_unique[x]
                        file_name_elements = file_name.split('_')
                        future = file_name_elements[1]
                        file_path = './' + address_list[n0] + main_folders[n1] + '/' + first_list[n2] + '/' + second_list[s] + '/' + file_name
                        this_df = pd.read_csv(file_path, dtype=use_dtype)
                        #
                        this_scen = file_name_elements[0]

                        pass_include = True
                        if len( file_name_elements ) == 5:
                            strategy_contribution_id = file_name_elements[-1].split('.')[0] # file_name_elements[-1][0]
                            #
                            if int( strategy_contribution_id ) not in strategy_list:
                                pass_include = False
                            elif this_scen != 'BAU':
                                pass_include = False
                            else:
                                pass
                            #
                            if strategy_contribution_id not in strategy_contribution_id_unique:
                                strategy_contribution_id_unique.append( strategy_contribution_id )
                            #
                            this_df['Strategy'] = 'NDPUp' + str( strategy_contribution_id )
                            #
                        #
                        else:
                            pass
                            #
                        #
                        if pass_include == True:
                            '''
                            if len( file_name_elements ) == 5:
                                strategy_contribution_id = file_name_elements[-1][0]
                                #
                                if strategy_contribution_id not in strategy_contribution_id_unique:
                                    strategy_contribution_id_unique.append( strategy_contribution_id )
                                #
                                this_df['Strategy'] = 'NDPUp' + str( strategy_contribution_id )
                            #
                            '''
                            # LET'S APPLY A FILTER TO EXCLUDE CENTRAL_GOVERNMENT GATHER, AS WE WILL NOT CARE TO SHOW REVENUE, BUT ONLY TAX EXPENSE // ASLO, LET'S REMOVE SOME COLUMNS WE WILL NOT USE.
                            this_df_filter = this_df.loc[ ( ~this_df['Actor'].isna() ) ]
                            #
                            this_df_filter[[    'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                                'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                                'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                                'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                                'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                                'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc' ]].fillna( value=0, inplace = True )
                            
                            this_df_filter_sum = this_df_filter.groupby( [ 'Strategy','Future.ID','Year','Actor','Actor_Type','Owner','GorS' ], as_index=False ).sum()
                            #
                            this_df_filter_sum['Technology'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                            this_df_filter_sum['Fuel'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                            this_df_filter_sum['Fuel_Surname'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                            this_df_filter_sum['Age'] = [ '' for k in range( len( this_df_filter_sum.index.tolist() ) ) ]
                            #
                            this_df_filter_sum = this_df_filter_sum [ [ 'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                                                                        'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                                                                        'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                                                        'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                                                        'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                                                        'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                                                        'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                                                        'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                                                                        'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                                                                        'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                                                                        'U VKT', 'Q Total', 'U Property Tax', 'FV'] ]
                            #
                            # now, let's add the detail of data not related to expenses, but prices and quantities
                            #
                            this_df_test = this_df.loc[ ( this_df['Actor'].isna() ) ]
                            #                 
                            this_df_pricing_vkt = this_df.loc[ ( this_df['Actor'].isna() ) & ( ~this_df['U VKT'].isna() ) ]
                            this_df_pricing_vkt_avg = this_df_pricing_vkt.groupby( [ 'Strategy','Future.ID','Year','Technology' ], as_index=False ).mean()
                            #
                            this_df_pricing_vkt_avg['Fuel'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                            this_df_pricing_vkt_avg['Fuel_Surname'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                            this_df_pricing_vkt_avg['Age'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                            this_df_pricing_vkt_avg['Actor'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                            this_df_pricing_vkt_avg['Actor_Type'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                            this_df_pricing_vkt_avg['Owner'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                            this_df_pricing_vkt_avg['GorS'] = [ '' for k in range( len( this_df_pricing_vkt_avg.index.tolist() ) ) ]
                            #
                            this_df_pricing_vkt_avg = this_df_pricing_vkt_avg [ [ 'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                                                                        'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                                                                        'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                                                        'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                                                        'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                                                        'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                                                        'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                                                        'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                                                                        'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                                                                        'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                                                                        'U VKT', 'Q Total', 'U Property Tax', 'FV'] ]
                            #
                            this_df_pricing_energy = this_df.loc[ ( this_df['Actor'].isna() ) & ( ~this_df['Energy Tax'].isna() ) & ( this_df['U VKT'].isna() ) ]
                            this_df_pricing_service = this_df.loc[ ( this_df['Actor'].isna() ) & ( ~this_df['Service Price'].isna() ) & ( this_df['U VKT'].isna() ) ]
                            #
                            this_df_pricing_fleet = deepcopy( this_df.loc[ ( this_df['Actor'].isna() ) & ( this_df['Owner'].isna() ) & ( this_df['Energy Tax'].isna() ) & ( this_df['U VKT'].isna() ) & ( this_df['Service Price'].isna() ) ] )
                            #
                            this_df_pricing_imports_cols = [ 'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF' ]
                            imports_mask = ( ~this_df_pricing_fleet['Q Imports'].isna() )
                            for k in range( len( this_df_pricing_imports_cols ) ):
                                this_col = this_df_pricing_imports_cols[k]
                                this_df_pricing_fleet.loc[imports_mask, this_col] *= this_df_pricing_fleet.loc[ imports_mask, 'Q Imports' ]
                            #
                            this_df_pricing_fleet_cols = [ 'U Property Tax', 'FV' ]
                            fleet_mask = ( ~this_df_pricing_fleet['Q Total'].isna() )
                            for k in range( len( this_df_pricing_fleet_cols ) ):
                                this_col = this_df_pricing_fleet_cols[k]
                                this_df_pricing_fleet.loc[fleet_mask, this_col] *= this_df_pricing_fleet.loc[ fleet_mask, 'Q Total' ]
                            #
                            this_df_pricing_fleet_sum = this_df_pricing_fleet.groupby( [ 'Strategy','Future.ID','Technology','Year' ], as_index=False ).sum()
                            #
                            this_df_pricing_fleet_sum['Fuel'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                            this_df_pricing_fleet_sum['Fuel_Surname'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                            this_df_pricing_fleet_sum['Age'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                            this_df_pricing_fleet_sum['Actor'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                            this_df_pricing_fleet_sum['Actor_Type'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                            this_df_pricing_fleet_sum['Owner'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                            this_df_pricing_fleet_sum['GorS'] = [ '' for k in range( len( this_df_pricing_fleet_sum.index.tolist() ) ) ]
                            #
                            this_df_pricing_fleet_sum = this_df_pricing_fleet_sum [ [ 'Strategy', 'Future.ID', 'Technology', 'Fuel', 'Fuel_Surname', 'Year',
                                                                        'Age', 'Actor', 'Actor_Type', 'Owner', 'GorS',
                                                                        'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                                                                        'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                                                                        'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                                                                        'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                                                                        'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                                                                        'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                                                                        'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                                                                        'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                                                                        'U VKT', 'Q Total', 'U Property Tax', 'FV'] ]
                            #
                            this_df_pricing_imports_cols = [ 'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF' ]
                            imports_mask = ( ~this_df_pricing_fleet_sum['Q Imports'].isin( [0] ) )
                            for k in range( len( this_df_pricing_imports_cols ) ):
                                this_col = this_df_pricing_imports_cols[k]
                                this_df_pricing_fleet_sum.loc[imports_mask, this_col] /= this_df_pricing_fleet_sum.loc[ imports_mask, 'Q Imports' ]
                            #
                            this_df_pricing_fleet_cols = [ 'U Property Tax', 'FV' ]
                            fleet_mask = ( ~this_df_pricing_fleet_sum['Q Total'].isin( [0] ) )
                            for k in range( len( this_df_pricing_fleet_cols ) ):
                                this_col = this_df_pricing_fleet_cols[k]
                                this_df_pricing_fleet_sum.loc[fleet_mask, this_col] /= this_df_pricing_fleet_sum.loc[ fleet_mask, 'Q Total' ]
                                #
                            #
                            df_list.append( deepcopy( this_df_filter_sum ) )
                            df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                            for y in range( len( time_range_vector ) ):
                                df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                            #
                            df_list_whole.append( deepcopy( this_df ) )
                            df_list_whole[-1]['GDP'] = [ 0 for n in range( len( df_list_whole[-1].index.tolist() ) ) ]
                            for y in range( len( time_range_vector ) ):
                                df_list_whole[-1].loc[ ( df_list_whole[-1]['Year'] == time_range_vector[y] ) & ( df_list_whole[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                            #
                            # df_list.append( this_df_filter )
                            #
                            df_list.append( deepcopy( this_df_pricing_vkt_avg ) )
                            df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                            for y in range( len( time_range_vector ) ):
                                df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                            #
                            df_list.append( deepcopy( this_df_pricing_energy ) )
                            df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                            for y in range( len( time_range_vector ) ):
                                df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                            #
                            df_list.append( deepcopy( this_df_pricing_service ) )
                            df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                            for y in range( len( time_range_vector ) ):
                                df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                            #
                            df_list.append( deepcopy( this_df_pricing_fleet_sum ) )
                            df_list[-1]['GDP'] = [ 0 for n in range( len( df_list[-1].index.tolist() ) ) ]
                            for y in range( len( time_range_vector ) ):
                                df_list[-1].loc[ ( df_list[-1]['Year'] == time_range_vector[y] ) & ( df_list[-1]['Future.ID'] == int( future ) ), 'GDP' ] = gdp_dict[ int( future ) ][y]
                            #
                            print( 'n2', len( this_df.columns.tolist() ), n2, s, x )
                            #
                        #
                    #
                #
            #
        #
    #
#

with open('df_list_whole.pickle', 'wb') as handle:
    pickle.dump(df_list_whole, handle, protocol=pickle.HIGHEST_PROTOCOL)

#
'''
df_gdp_ref = pd.read_excel('_TEM_GDP_Ref.xlsx' )
list_gdp_ref = df_gdp_ref['GDP (nominal)'].tolist()
'''
#
this_df_concat = pd.concat(df_list, axis=0, ignore_index=True)
#
'''
gdp_dict = pickle.load( open( './GDP_dict.pickle',            "rb" ) )
this_df_concat = pd.concat(df_list, axis=0, ignore_index=True)
this_df_concat['GDP'] = [ 0 for n in range( len( this_df_concat.index.tolist() ) ) ]
for n in future_list:
    for y in range( len( time_range_vector ) ):
        this_df_concat.loc[ ( this_df_concat['Year'] == time_range_vector[y] ) & ( this_df_concat['Future.ID'] == n ), 'GDP' ] = gdp_dict[n][y]
        #
    #
#
'''
all_cols =  [   'DAI', 'Customs', 'SC', 'VAT-Imports', 'Total Import Taxes', 'GE', 'Vehicle Purchase', 'Property Tax', 'IUC', 'VAT-Electricity',
                'H2', 'VKT', 'Energy Sales and Purchases', 'Investments and FOM', 'Variable Costs' ,
                'Service Sales', 'Service Purchases', 'Investments', 'FOM',
                'DAI Disc', 'Customs Disc', 'SC Disc', 'VAT-Imports Disc', 'Total Import Taxes Disc', 'GE Disc', 'Vehicle Purchase Disc', 'Property Tax Disc', 'IUC Disc', 'VAT-Electricity Disc',
                'H2 Disc', 'VKT Disc', 'Energy Sales and Purchases Disc', 'Investments and FOM Disc', 'Variable Costs Disc' ,
                'Service Sales Disc', 'Service Purchases Disc', 'Investments Disc', 'FOM Disc',
                'Energy Price', 'Energy Price wTax', 'Energy Tax', 'Service Price',
                'U SC', 'U Total Import Taxes', 'U Market Price', 'U CIF', 'Q Imports',
                'U VKT', 'Q Total', 'U Property Tax', 'FV']
#
#--------------------------------------------------------------------------------------------------------------------#
print_split = False
print_whole = True
if print_whole == True:
    this_df_concat_whole = pd.concat(df_list_whole, axis=0, ignore_index=True)
    #this_df_concat_whole['GDP'] = [ 0 for n in range( len( this_df_concat_whole.index.tolist() ) ) ]
    #for n in future_list:
    #    for y in range( len( time_range_vector ) ):
    #        this_df_concat.loc[ ( this_df_concat['Year'] == time_range_vector[y] ) & ( this_df_concat['Future.ID'] == n ), 'GDP' ] = gdp_dict[n][y]
            #
        #
    #
    this_df_concat_whole.to_csv ( 'Compiled_TEM_Whole' + '.csv', index = None, header=True)
    #
#--------------------------------------------------------------------------------------------------------------------#
# if print_split == False:
#     this_df_concat.to_csv ( 'TEM_Compiled' + '.csv', index = None, header=True)
# #
# else:
#     for k in range( len( strategy_contribution_id_unique ) ):
#         #
#         strategy_num = strategy_contribution_id_unique[k]
#         #
#         if int( strategy_num ) in strategy_list:
#             df_list_print = this_df_concat.loc[ this_df_concat['Strategy'].isin( [ 'BAU', 'NDP', 'NDPUp' + str( strategy_num ) ] ) ]
#             df_list_print['Strategy'].replace({'NDPUp' + str( strategy_num ): 'NDPUp'}, inplace=True)
#             #
#             for a_col in all_cols:
#                 df_list_print[ a_col ].replace({ 0:''}, inplace=True)
#                 #
#             # df_list_print.to_csv ( 'Test_Compiled_TEM_' + str( strategy_num ) + '.csv', index = None, header=True)
#             # df_list_print.to_csv ( 'Compiled_TEM_' + str( strategy_num ) + '.csv', index = None, header=True)
#             df_list_print.to_csv ( 'TEM_Compiled' + str( strategy_num ) + '_' + str(initial_future) + '_' + str(final_future) + '.csv', index = None, header=True)
#             #
#         #
#     #
# #
end_1 = time.time()
time_elapsed_1 = -start1 + end_1
print( str( time_elapsed_1 ) + ' seconds /', str( time_elapsed_1/60 ) + ' minutes' )
print('*: For all effects, we have finished the work of this script.')
#
sys.exit()

