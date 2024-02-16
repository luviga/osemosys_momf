# -*- coding: utf-8 -*-
"""
@author: Luis Victor Gallardo
"""
import multiprocessing as mp
import pandas as pd
import numpy as np
import csv
import os, os.path
import sys
import math
from copy import deepcopy
import time
import sys
from copy import deepcopy
from gekko import GEKKO
import pickle
import yaml

'''
We implement OSEMOSYS-CR-TEM to estimate transfers between agents of the transport sector.
This version implements the printing of prices, quantities and rates in a single file.
'''
class agent:  # Initializer / Instance Attributes
    def __init__( self, techs_own_i, techs_gather_i, techs_sell_i, techs_buy_i, actor_ID , r ):
        self.techs_own = techs_own_i
        self.techs_gather = techs_gather_i
        self.techs_sell = techs_sell_i
        self.techs_buy = techs_buy_i
        self.name_ID = actor_ID
        self.discount_rate = r


class o_type_1_actor( agent ): # [ central_government ]

    '''
    #------------------------------------------------------------------------------------------------------#
    '''
    # TRANSFERS TO GOVERNMENT
    def gather_derecho_arancelario( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_DerechoArancelario , m , df_new_Rates ):
        # print('Gathering Import and Sales Tax')
        df_Rates_T = df_Rates_T_DerechoArancelario # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'DAI', 'Gather', name_ID, 'Type_1', df_new_Rates, params )
        return returnable_list_of_lists
    #
    def gather_valor_aduanero( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_ValorAduanero , m , df_new_Rates ):
        # print('Gathering Import and Sales Tax')
        df_Rates_T = df_Rates_T_ValorAduanero # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Customs', 'Gather', name_ID, 'Type_1' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def gather_selectivo_al_consumo( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_SelectivoAlConsumo , m , df_new_Rates ):
        # print('Gathering Import and Sales Tax')
        df_Rates_T = df_Rates_T_SelectivoAlConsumo # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'SC', 'Gather', name_ID, 'Type_1' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def gather_import_vat( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_ImportVAT , m , df_new_Rates ):
        # print('Gathering Import and Sales Tax')
        df_Rates_T = df_Rates_T_ImportVAT # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'VAT-Imports', 'Gather', name_ID, 'Type_1' , df_new_Rates, params )
        return returnable_list_of_lists
    '''------------------------------------------
    '''
    def gather_iuc( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_IUC , m , fuel , df_new_Rates ):
        # print('Gathering fuel consumption tax')
        df_Rates_TF = df_Rates_TF_IUC # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'IUC', 'Gather', name_ID, 'Type_1', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def gather_electricity_vat( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_ElectricityVAT , m , fuel , df_new_Rates ):
        # print('Gathering fuel consumption tax')
        df_Rates_TF = df_Rates_TF_ElectricityVAT # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'VAT-Electricity', 'Gather', name_ID, 'Type_1', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def gather_h2( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_TF_H2 , m , fuel , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in fuel consumption tax')
        df_Rates_TF = df_Unit_TF_H2 # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'H2', 'Gather', name_ID, 'Type_1', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    '''------------------------------------------
    '''
    def gather_property_tax( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_PropertyTax , m , df_new_Rates ):
        # print('Gathering Property Tax')
        df_Rates_T = df_Rates_T_PropertyTax # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'TotalCapacityAnnual', m, 'Property Tax', 'Gather', name_ID, 'Type_1' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    ''' ------------------------------------------
    '''
    def gather_total_import_taxes( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_T_TotalTaxes , m , df_new_Rates ):
        # print('Gathering Property Tax')
        df_Rates_T = df_Unit_T_TotalTaxes # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Total Import Taxes', 'Gather', name_ID, 'Type_1' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    ''' ------------------------------------------
    '''
    def gather_vmt_tax( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , this_vmt_rates_per_tech , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Property Tax')
        df_Rates_T = this_vmt_rates_per_tech # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'DistanceDriven', m, 'VKT', 'Gather', name_ID, 'Type_1' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    '''
    #------------------------------------------------------------------------------------------------------#
    '''
    # PUBLIC SPENDING (MAINLY FOR PUBLIC TRANSPORT)
    def spend_investements_and_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments and FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'AnnualFixedOperatingCost', m, 'Investments and FOM', 'Spend', name_ID, 'Type_1', params )
        return returnable_list_of_lists

    def spend_investements( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'None', m, 'Investments', 'Spend', name_ID, 'Type_1', params )
        return returnable_list_of_lists
    
    def spend_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'AnnualFixedOperatingCost', 'None', m, 'FOM', 'Spend', name_ID, 'Type_1', params )
        return returnable_list_of_lists
    '''
    #------------------------------------------------------------------------------------------------------#
    '''

#####################################
class o_type_2_actor( agent ): # [ electricity_companies, hydrocarbon_companies, hydrogen_companies ]

    def gather_energy_sale( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_SalesPurchasesEnergy , m , fuel ):
        # print('Gathering energy sales')
        df_Rates_TF = df_Rates_TF_SalesPurchasesEnergy # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'Energy Sales and Purchases', 'Gather', name_ID, 'Type_2', fuel , 'NO_df_new_Rates', params )
        return returnable_list_of_lists

    def spend_investements_and_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments and FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'AnnualFixedOperatingCost', m, 'Investments and FOM', 'Spend', name_ID, 'Type_2', params )
        return returnable_list_of_lists

    def spend_investements( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'None', m, 'Investments', 'Spend', name_ID, 'Type_2', params )
        return returnable_list_of_lists
    
    def spend_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'AnnualFixedOperatingCost', 'None', m, 'FOM', 'Spend', name_ID, 'Type_2', params )
        return returnable_list_of_lists

    def spend_variable_costs( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database) // imported hydrocarbons are national costs
        # print('Spending in variable costs')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'AnnualVariableOperatingCost', 'None', m, 'Variable Costs', 'Spend', name_ID, 'Type_2', params )
        return returnable_list_of_lists

#####################################
class o_type_3_actor( agent ): # [ bus_companies , bus_special_companies , taxi_companies ]

    def gather_service_sale( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_SalesPurchasesService , m , fuel ):
        # print('Gathering service sales')
        df_Rates_TF = df_Rates_TF_SalesPurchasesService # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'ProductionByTechnology', m, 'Service Sales', 'Gather', name_ID, 'Type_3', fuel , 'NO_df_new_Rates', params )
        return returnable_list_of_lists

    def spend_investements_and_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments and FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'AnnualFixedOperatingCost', m, 'Investments and FOM', 'Spend', name_ID, 'Type_3', params )
        return returnable_list_of_lists

    def spend_investements( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'None', m, 'Investments', 'Spend', name_ID, 'Type_3', params )
        return returnable_list_of_lists
    
    def spend_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'AnnualFixedOperatingCost', 'None', m, 'FOM', 'Spend', name_ID, 'Type_3', params )
        return returnable_list_of_lists

    def spend_energy_purchase( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_SalesPurchasesEnergy , m , fuel ):
        # print('Spending in energy purchases')
        df_Rates_TF = df_Rates_TF_SalesPurchasesEnergy # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'Energy Sales and Purchases', 'Spend', name_ID, 'Type_3', fuel , 'NO_df_new_Rates', params )
        return returnable_list_of_lists

    '''
    #------------------------------------------------------------------------------------------------------#
    '''
    # TRANSFERS TO GOVERNMENT
    def spend_derecho_arancelario( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_DerechoArancelario , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_DerechoArancelario # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'DAI', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_valor_aduanero( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_ValorAduanero , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_ValorAduanero # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Customs', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_selectivo_al_consumo( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_SelectivoAlConsumo , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_SelectivoAlConsumo # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'SC', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_import_vat( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_ImportVAT , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_ImportVAT # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'VAT-Imports', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    '''------------------------------------------
    '''
    def spend_total_import_taxes( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_T_TotalTaxes , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Unit_T_TotalTaxes # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Total Import Taxes', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_estimated_earnings( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_T_GananciaEstimada , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Unit_T_GananciaEstimada # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'GE', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_vehicle_purchase( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_T_MarketPrice , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Unit_T_MarketPrice # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Vehicle Purchase', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    '''------------------------------------------
    '''
    def spend_iuc( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_IUC , m , fuel , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in fuel consumption tax')
        df_Rates_TF = df_Rates_TF_IUC # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'IUC', 'Spend', name_ID, 'Type_3', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_electricity_vat( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_ElectricityVAT , m , fuel , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in fuel consumption tax')
        df_Rates_TF = df_Rates_TF_ElectricityVAT # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'VAT-Electricity', 'Spend', name_ID, 'Type_3', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_h2( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_TF_H2 , m , fuel , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in fuel consumption tax')
        df_Rates_TF = df_Unit_TF_H2 # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'H2', 'Spend', name_ID, 'Type_3', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    ''' ------------------------------------------
    '''
    def spend_property_tax( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_PropertyTax , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Property Tax')
        df_Rates_T = df_Rates_T_PropertyTax # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'TotalCapacityAnnual', m, 'Property Tax', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    ''' ------------------------------------------
    '''
    def spend_vmt_tax( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , this_vmt_rates_per_tech , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Property Tax')
        df_Rates_T = this_vmt_rates_per_tech # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'DistanceDriven', m, 'VKT', 'Spend', name_ID, 'Type_3' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    '''
    #------------------------------------------------------------------------------------------------------#
    '''

#####################################
class o_type_4_actor( agent ): # [ light_truck_companies, heavy_freight_companies, private_transport_owners ]

    def spend_investements_and_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments and FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'AnnualFixedOperatingCost', m, 'Investments and FOM', 'Spend', name_ID, 'Type_4', params )
        return returnable_list_of_lists

    def spend_investements( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in investments')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'CapitalInvestment', 'None', m, 'Investments', 'Spend', name_ID, 'Type_4', params )
        return returnable_list_of_lists
    
    def spend_fom( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , m ): # (direct from database)
        # print('Spending in FOM')
        returnable_list_of_lists = data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate, 'AnnualFixedOperatingCost', 'None', m, 'FOM', 'Spend', name_ID, 'Type_4', params )
        return returnable_list_of_lists

    def spend_energy_purchase( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_SalesPurchasesEnergy , m , fuel ):
        # print('Spending in energy purchases')
        df_Rates_TF = df_Rates_TF_SalesPurchasesEnergy # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'Energy Sales and Purchases', 'Spend', name_ID, 'Type_4', fuel, 'NO_df_new_Rates', params )
        return returnable_list_of_lists

    '''
    #------------------------------------------------------------------------------------------------------#
    '''
    # TRANSFERS TO GOVERNMENT
    def spend_derecho_arancelario( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_DerechoArancelario , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_DerechoArancelario # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'DAI', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_valor_aduanero( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_ValorAduanero , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_ValorAduanero # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Customs', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_selectivo_al_consumo( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_SelectivoAlConsumo , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_SelectivoAlConsumo # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'SC', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_import_vat( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_ImportVAT , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Rates_T_ImportVAT # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'VAT-Imports', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    '''------------------------------------------
    '''
    def spend_total_import_taxes( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_T_TotalTaxes , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Unit_T_TotalTaxes # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Total Import Taxes', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_estimated_earnings( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_T_GananciaEstimada , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Unit_T_GananciaEstimada # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'GE', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_vehicle_purchase( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_T_MarketPrice , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Import and Sales Tax')
        df_Rates_T = df_Unit_T_MarketPrice # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'NewCapacity', m, 'Vehicle Purchase', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    '''------------------------------------------
    '''
    def spend_iuc( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_IUC , m , fuel , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in fuel consumption tax')
        df_Rates_TF = df_Rates_TF_IUC # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'IUC', 'Spend', name_ID, 'Type_4', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_electricity_vat( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_ElectricityVAT , m , fuel , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in fuel consumption tax')
        df_Rates_TF = df_Rates_TF_ElectricityVAT # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'VAT-Electricity', 'Spend', name_ID, 'Type_4', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    #
    def spend_h2( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Unit_TF_H2 , m , fuel , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in fuel consumption tax')
        df_Rates_TF = df_Unit_TF_H2 # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'UseByTechnology', m, 'H2', 'Spend', name_ID, 'Type_4', fuel , df_new_Rates, params )
        return returnable_list_of_lists
    ''' ------------------------------------------
    '''
    def spend_property_tax( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_T_PropertyTax , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in Property Tax')
        df_Rates_T = df_Rates_T_PropertyTax # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'TotalCapacityAnnual', m, 'Property Tax', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    ''' ------------------------------------------
    '''
    def spend_vmt_tax( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , this_vmt_rates_per_tech , m , df_new_Rates ): # TRANSFERED TO GOVERNMENT
        # print('Spending in VMT Tax')
        df_Rates_T = this_vmt_rates_per_tech # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_T( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_T, 'DistanceDriven', m, 'VKT', 'Spend', name_ID, 'Type_4' , df_new_Rates, params )
        return returnable_list_of_lists
    #
    '''
    #------------------------------------------------------------------------------------------------------#
    '''

#####################################
class o_type_5_actor( agent ): # [ public_transport_users ]

    def spend_service_purchase( self, discounted_or_not, assorted_data_dicts, techs , name_ID , discount_rate , df_Rates_TF_SalesPurchasesService , m , fuel ):
        # print('Spending in service purchases')
        df_Rates_TF = df_Rates_TF_SalesPurchasesService # These are actually "Unit"-type dataframes // kept rate for generality
        returnable_list_of_lists = data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, 'ProductionByTechnology', m, 'Service Purchases', 'Spend', name_ID, 'Type_5', fuel , 'NO_df_new_Rates', params )
        return returnable_list_of_lists
    #
#
#####################################
def soften_imports( x_raw ):
    x_coord_tofill = [] # these are indices that are NOT known - to interpolate
    xp_coord_known = [] # these are known indices - use for interpolation
    fp_coord_known = [] # these are the values known to interpolate the whole series
    #
    x = x_raw[1:]
    x_avg = []
    x_sum = []
    period = 3
    #
    len_x = len(x)
    #
    for i in range( 0, len_x, period ):
        sum_value = x[i]
        dividend_value = 1
        for n in range( 1,period ):
            if i+n < len_x:
                sum_value += x[i+n]
                dividend_value += 1
                #
            #
        #
        average_value = sum_value / dividend_value
        #
        for n in range( 0,period ):
            if i+n < len_x:
                x_avg.append( average_value )
        #
        x_sum.append( sum_value )
        #
        #print('--')
        #
    #
    for i in range( 0, len_x, period ):
        if i+n < len_x:
            fp_coord_known.append( x_avg[i+1] )
            xp_coord_known.append( i+1 )
            #
        #
    fp_coord_known.append( x_avg[-1] )
    xp_coord_known.append( len_x-1 )
    x_coord_tofill = []
    #
    for i in range( 0, len_x ):
        if i not in xp_coord_known:
            x_coord_tofill.append( i )
            #
        #
    #
    y_coord_filled = list( np.interp( x_coord_tofill, xp_coord_known, fp_coord_known ) )
    #
    interpolated_values = []
    for coord in range( len_x ):
        if coord in xp_coord_known:
            value_index = xp_coord_known.index(coord)
            interpolated_values.append( float( fp_coord_known[value_index] ) )
        elif coord in x_coord_tofill:
            value_index = x_coord_tofill.index(coord)
            interpolated_values.append( float( y_coord_filled[value_index] ) )
    #
    x_soft = []
    for i in range( 0, len( x_sum ) ):
        sum_value = x_sum[i]
        local_sum = 0
        for n in range( 0,period ):
            if i*period+n < len_x:
                local_sum += interpolated_values[i*period+n]
                #
            #
        #
        for n in range( 0,period ):
            if i*period+n < len_x:
                if local_sum != 0:
                    x_soft.append( sum_value*interpolated_values[i*period+n]/local_sum )
                else:
                    x_soft.append( 0 )
        #
    #
    return [ x_raw[0] ] + x_soft
    #
#
#####################################
# Data management function for technology-based parameters THAT DO NOT REQUIRE RATES:
def data_management_T_solo( discounted_or_not, assorted_data_dicts, techs , discount_rate , variable_1 , variable_2 , m , output_variable , GorS , name_ID , atype, params ):
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------#
    returnable_list_of_lists = []
    all_years = [i for i in range(2018,2050+1) ]
    #
    list_of_variables = params['list_of_variables']
    #
    fcm_table_header = params['fcm_table_header'] + list_of_variables
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------#
    #
    unique_owner = assorted_data_dicts['fleet'][2]
    #fleet_Q_per_actor_perTech_perYear_per_age = assorted_data_dicts['fleet'][3]
    #leet_Q_per_actor_perTech_perYear_per_age_share = assorted_data_dicts['fleet'][4]
    #fleet_Q_per_actor_perTech_perYear_per_age_imp = assorted_data_dicts['fleet'][5]
    #fleet_Q_per_actor_perTech_perYear_per_age_imp_share = assorted_data_dicts['fleet'][6]
    fleet_Q_per_actor_perTech_perYear_share = assorted_data_dicts['fleet'][7] # this one is actually needed
    #
    # We need to place the actors here:
    if name_ID != 'private_transport_owners' and name_ID != 'central_government':
        owner_list = ['Businesses']
    if name_ID == 'central_government':
        owner_list = ['Other']
    if name_ID == 'private_transport_owners':
        owner_list = unique_owner
    #
    for o in range( len( owner_list ) ):
        this_owner = owner_list[o]
        #
        for n in range( len( techs ) ):
            this_tech = techs[n]
            #
            for y in range( len( all_years ) ):
                value_indices_1 = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( this_tech in x ) and ( variable_1 in x ) and ( int( all_years[y] ) in x ) ]
                #%%%%%%%%%%%%%%%%%%%%%%
                if variable_2 != 'None':
                    value_indices_2 = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( this_tech in x ) and ( variable_2 in x ) and ( int( all_years[y] ) in x ) ]
                else:
                    value_indices_2 = []
                #%%%%%%%%%%%%%%%%%%%%%%
                if len(value_indices_1) != 0:
                    data_index_1 =  value_indices_1[0]
                    this_activity_value_1 = float( assorted_data_dicts['t'][ data_index_1 ][-1] )
                else:
                    this_activity_value_1 = 0
                #
                if len(value_indices_2) != 0:
                    data_index_2 =  value_indices_2[0]
                    this_activity_value_2 = float( assorted_data_dicts['t'][ data_index_2 ][-1] )
                else:
                    this_activity_value_2 = 0
                #
                #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                if name_ID != 'private_transport_owners':
                    this_share_owner_share = 1
                else:
                    if this_tech in list( fleet_Q_per_actor_perTech_perYear_share[ this_owner ].keys() ):
                        if all_years[y] in list( fleet_Q_per_actor_perTech_perYear_share[ this_owner ][ this_tech ].keys() ):
                            this_share_owner_share = fleet_Q_per_actor_perTech_perYear_share[ this_owner ][ this_tech ][ all_years[y] ]
                        else:
                            this_share_owner_share = 0
                            # print('*happens!*-1', this_tech, this_owner, all_years[y], name_ID )
                    else:
                        this_share_owner_share = 0
                        # print('*happens!*-2', this_tech, this_owner, all_years[y], name_ID )
                #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                #
                this_yearly_result = ( this_activity_value_1 + this_activity_value_2 )*this_share_owner_share
                #
                this_yearly_discounted_result = this_yearly_result / ( ( 1+discount_rate )**( all_years[y]-all_years[0] ) )
                this_yearly_undiscounted_result = this_yearly_result            
                #
                returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                returnable_list_of_lists[-1][ fcm_table_header.index( output_variable + ' Disc' ) ] = float("{0:.4f}".format( this_yearly_discounted_result ) )
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor' ) ] = name_ID
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor_Type' ) ] = atype
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                returnable_list_of_lists[-1][ fcm_table_header.index( 'GorS' ) ] = GorS
                #
                returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                returnable_list_of_lists[-1][ fcm_table_header.index( output_variable ) ] = float("{0:.4f}".format( this_yearly_undiscounted_result ) )
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor' ) ] = name_ID
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor_Type' ) ] = atype
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                returnable_list_of_lists[-1][ fcm_table_header.index( 'GorS' ) ] = GorS
                #
    #
    return returnable_list_of_lists
#
def data_management_T( discounted_or_not, assorted_data_dicts, actor_techs , discount_rate , df_Rates_T , variable , m , output_variable , GorS , name_ID , atype , df_new_Rates, params ):
    #
    if output_variable == 'Property Tax':
        if df_new_Rates == 'NO_df_new_Rates':
            dict_Rates_T_PropertyTax_query = df_Rates_T[0]
            fiscal_value_perTech_perYear_per_age = df_Rates_T[1]
            dict_Property_Tax_Applicable = df_Rates_T[2]
            dict_ER_per_year = df_Rates_T[3]
        else:
            dict_Unit_PropertyTax_new = df_Rates_T
    else:
        pass
        #
    #
    the_fleet = deepcopy( assorted_data_dicts['fleet'][0] )
    the_fleet_imported = deepcopy( assorted_data_dicts['fleet'][1] )
    unique_owner = assorted_data_dicts['fleet'][2]
    fleet_Q_per_actor_perTech_perYear_per_age = assorted_data_dicts['fleet'][3]
    # fleet_Q_per_actor_perTech_perYear_per_age_share = assorted_data_dicts['fleet'][4]
    fleet_Q_per_actor_perTech_perYear_per_age_imp = assorted_data_dicts['fleet'][5]
    # fleet_Q_per_actor_perTech_perYear_per_age_imp_share = assorted_data_dicts['fleet'][6]
    # fleet_Q_per_actor_perTech_perYear_share = assorted_data_dicts['fleet'][7]
    assorted_data_dicts_i = assorted_data_dicts['inputs']
    fleet_Q_perTech_perYear_per_nationalization = assorted_data_dicts['fleet'][-1]
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------#
    returnable_list_of_lists = []
    all_years = [i for i in range(2018,2050+1) ]
    #
    list_of_variables = params['list_of_variables']
    #
    fcm_table_header = params['fcm_table_header'] + list_of_variables
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------#
    #
    # Here the techs must be the ones that are within the tax that is being charged:
    if output_variable != 'Property Tax' and output_variable != 'VKT': # i.e. imports
        techs_within_the_rate = df_Rates_T[ all_years[0] ].keys()
    if output_variable == 'VKT': # this is the 'this_vmt_rates_per_tech'
        techs_within_the_rate = df_Rates_T[ all_years[0] ].keys()
    if output_variable == 'Property Tax': # We would be within property tax
        if df_new_Rates == 'NO_df_new_Rates':
            techs_within_the_rate = df_Rates_T[1].keys()
        else:
            # We must add something here that calls the technologies from *dict_Unit_PropertyTax_new*
            techs_within_the_rate = df_Rates_T.keys()
        #
    #
    if name_ID != 'private_transport_owners' and name_ID != 'central_government':
        owner_list = ['Businesses']
    if name_ID == 'central_government':
        owner_list = ['Other']
    if name_ID == 'private_transport_owners':
        owner_list = unique_owner
    #
    for o in range( len( owner_list ) ):
        this_owner = owner_list[o]
        #
        if name_ID == 'private_transport_owners':
            if output_variable != 'Property Tax' and output_variable != 'VKT': # i.e. imports
                owner_techs = list( set( fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_owner ].keys() ) )
            else:
                owner_techs = list( set( fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ].keys() ) )
            set_techs = set( actor_techs ) & set( techs_within_the_rate )
            list_techs = list( set_techs )
            techs = [ actor_techs[k] for k in range( len( actor_techs ) ) if ( actor_techs[k] in list_techs ) and ( actor_techs[k] in owner_techs ) ]
        else:
            set_techs = set(actor_techs) & set(techs_within_the_rate)
            list_techs = list( set_techs )
            techs = [ actor_techs[k] for k in range( len( actor_techs ) ) if actor_techs[k] in list_techs ]
        #
        for n in range( len( techs ) ):
            #
            pass_Tech = False
            #
            this_tech = techs[n]
            #
            if output_variable == 'Property Tax' or output_variable == 'VKT':
                if name_ID != 'private_transport_owners':
                    this_tech_fleet = the_fleet[ this_tech ]
                    pass_Tech = True
                else:
                    if this_tech in list( fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ].keys() ):
                        this_tech_fleet = fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ][ this_tech ]
                        pass_Tech = True
                        #
                    #
                #
                check_fleet_whole = the_fleet[ this_tech ]
                check_fleet_exo = fleet_Q_perTech_perYear_per_nationalization[ this_tech ]
                #
            #
            if output_variable != 'Property Tax' and output_variable != 'VKT':
                if name_ID != 'private_transport_owners':
                    this_tech_fleet_imp = the_fleet_imported[ this_tech ]
                    pass_Tech = True
                else:
                    if this_tech in list( fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_owner ].keys() ):
                        this_tech_fleet_imp = fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_owner ][ this_tech ]
                        pass_Tech = True
                        #
                    #
                #
            #
            if pass_Tech == True:
                for y in range( len( all_years ) ): # year at which we estimate the taxes // equivalent to 'above_y' for the fleey analysis
                    #
                    pass_Year = False
                    if ( output_variable == 'Property Tax' or output_variable == 'VKT' ):
                        if all_years[y] in list( set( this_tech_fleet.keys() ) ):
                            pass_Year =  True
                            #
                        #
                    #
                    if ( output_variable != 'Property Tax' and output_variable != 'VKT' ):
                        if all_years[y] in list( set( this_tech_fleet_imp.keys() ) ):
                            pass_Year =  True
                            #
                        #
                    #
                    if pass_Year == True: # proceed if the element exists
                        #
                        if output_variable == 'Property Tax' or output_variable == 'VKT':
                            this_tech_this_year_fleet = this_tech_fleet[ all_years[y] ]
                            check_this_tech_this_year_fleet_whole = check_fleet_whole[ all_years[y] ]
                            check_this_tech_this_year_fleet_exo = check_fleet_exo[ all_years[y] ]
                        if output_variable != 'Property Tax' and output_variable != 'VKT':
                            this_tech_this_year_fleet_imp = this_tech_fleet_imp[ all_years[y] ]
                        #
                        if output_variable == 'Property Tax': # This applies for the taxes applicable for the yearly use (or property) of vehicles.
                            #
                            # Let us extract the values for this year:
                            if df_new_Rates == 'NO_df_new_Rates':
                                applicable_dict_Rates_T_PropertyTax_query = dict_Rates_T_PropertyTax_query[ all_years[y] ]
                                the_fiscal_value_of_this_tech_of_this_year = fiscal_value_perTech_perYear_per_age[ this_tech ][ all_years[y] ]
                                #
                                # Pray proceed with the scales:
                                all_scales = list( applicable_dict_Rates_T_PropertyTax_query.keys() )
                                #
                            else:
                                this_tech_this_year_unit_pt = dict_Unit_PropertyTax_new[ this_tech ][ all_years[y] ]
                            #----------------------------------------#
                            list_ages_raw = list( this_tech_this_year_fleet.keys() )
                            list_ages = [ i for i in list_ages_raw if type(i) == int ]
                            this_yearly_result = 0
                            #
                            for a in list_ages:
                                #
                                this_q = this_tech_this_year_fleet[ a ]
                                this_q_whole = check_this_tech_this_year_fleet_whole[a]
                                if a in list( check_this_tech_this_year_fleet_exo.keys() ):
                                    this_q_exo_1 = check_this_tech_this_year_fleet_exo[a][0]
                                    this_q_exo_2 = check_this_tech_this_year_fleet_exo[a][1]
                                    this_q_exo_3 = check_this_tech_this_year_fleet_exo[a][2]
                                    this_q_exo_4 = check_this_tech_this_year_fleet_exo[a][3]
                                    this_q_exo_5 = check_this_tech_this_year_fleet_exo[a][4]
                                else:
                                    this_q_exo_1 = 0
                                    this_q_exo_2 = 0
                                    this_q_exo_3 = 0
                                    this_q_exo_4 = 0
                                    this_q_exo_5 = 0
                                    #
                                #
                                if ( ( ( 'ELE' in this_tech ) or ( 'HYD' in this_tech ) ) and this_q_whole != 0 and ( ( m['Strategy'] == 'BAU' ) or ( m['Strategy'] == 'NDP' and m['adjustment_id'] == 0 ) ) ): # and ( all_years[y] < 2035 ):
                                    exoneration_factor = ( this_q_whole - this_q_exo_1 - this_q_exo_2*0.8 - this_q_exo_3*0.6 - this_q_exo_4*0.4 - this_q_exo_5*0.2 )/this_q_whole
                                else:
                                    exoneration_factor = 1
                                #
                                '''
                                if 'TRYLF' in this_tech: # Exoneration - This defines that productive groups don't pay the import taxes
                                    exoneration_factor *= 0.25
                                else:
                                    pass
                                '''
                                #
                                if exoneration_factor < 0:
                                    print( 'WARNING' )
                                    print( m['Strategy'], m['Future.ID'], this_tech, all_years[y], a )
                                    print( this_q_whole - this_q_exo_1 - this_q_exo_2*0.8 - this_q_exo_3*0.6 - this_q_exo_4*0.4 - this_q_exo_5*0.2 )
                                    print( this_q_whole , this_q_exo_1 , this_q_exo_2*0.8 , this_q_exo_3*0.6 , this_q_exo_4*0.4 , this_q_exo_5*0.2 )
                                    print( this_q_whole , this_q_exo_1 , this_q_exo_2 , this_q_exo_3 , this_q_exo_4 , this_q_exo_5 )
                                    sys.exit()
                                #
                                if df_new_Rates == 'NO_df_new_Rates': # use "exoneration_factor" only inside this if
                                    #
                                    this_fiscal_value = the_fiscal_value_of_this_tech_of_this_year[ a ]
                                    #
                                    if dict_Property_Tax_Applicable[ this_tech ] == 'Table':
                                        for a_scale in range( len( all_scales ) ):
                                            min_threshold = dict_Rates_T_PropertyTax_query[ all_years[y] ][ all_scales[a_scale] ]['Min']
                                            max_threshold = dict_Rates_T_PropertyTax_query[ all_years[y] ][ all_scales[a_scale] ]['Max']
                                            if this_fiscal_value >= min_threshold and this_fiscal_value <= max_threshold:
                                                correct_scale = a_scale
                                        #
                                        if this_fiscal_value > max_threshold:
                                            correct_scale = len( all_scales )-1 # the last of scales
                                        #
                                        used_scales = all_scales[ :correct_scale+1 ]
                                        this_pt_amount_contribution = 0
                                        #
                                        for u_scale in range( len( used_scales ) ): # EV EXONERATIONS SHOULD BE PROGRAMMED HERE
                                            this_pt_unit = dict_Rates_T_PropertyTax_query[ all_years[y] ][ used_scales[u_scale] ]['Unit']
                                            #
                                            if this_pt_unit == 'Nominal':
                                                this_pt_amount_contribution += dict_Rates_T_PropertyTax_query[ all_years[y] ][ used_scales[u_scale] ]['Rate']/1e6 # * this_q
                                            else: # This means the rate is a percent
                                                #
                                                this_pt_rate = dict_Rates_T_PropertyTax_query[ all_years[y] ][ used_scales[u_scale] ]['Rate']
                                                min_threshold = dict_Rates_T_PropertyTax_query[ all_years[y] ][ used_scales[u_scale] ]['Min']
                                                max_threshold = dict_Rates_T_PropertyTax_query[ all_years[y] ][ used_scales[u_scale] ]['Max']
                                                #
                                                if u_scale < len( used_scales )-1 :                                       
                                                    this_pt_amount_contribution += ( max_threshold-min_threshold )/1e6 * this_pt_rate # * this_q * exoneration_factor
                                                #
                                                else: # this means *u_scale == len( used_scales )-1* and it is the correct value
                                                    this_pt_amount_contribution += ( this_fiscal_value-min_threshold )/1e6 * this_pt_rate # * this_q * exoneration_factor
                                                #
                                            #
                                        #
                                        this_yearly_result += this_pt_amount_contribution * this_q * exoneration_factor
                                        #
                                    #
                                    else: # this is a constant value
                                        this_yearly_result += exoneration_factor * this_q * ( dict_Property_Tax_Applicable[ this_tech ] / dict_ER_per_year[ all_years[y] ] )/1e6
                                    #
                                #
                                else: # gotta add the per-unit property tax
                                    this_yearly_result += ( this_tech_this_year_unit_pt[ a ]/1e6 ) * this_q * exoneration_factor
                                #
                            #
                        #
                        else: # This applies for VKT OR import taxes
                            if output_variable == 'VKT':
                                #
                                list_ages_raw = list( this_tech_this_year_fleet.keys() )
                                list_ages = [ i for i in list_ages_raw if type(i) == int ]
                                this_yearly_result = 0
                                total_fleet = 0
                                #
                                for a in list_ages:
                                    #
                                    total_fleet += this_tech_this_year_fleet[ a ]
                                    #
                                #
                                value_indices = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( this_tech in x ) and ( variable in x ) and ( int( all_years[y] ) in x ) ]
                                if len(value_indices) != 0:
                                    data_index = value_indices[0]
                                    total_km = float( assorted_data_dicts_i['t'][ data_index ][-1] )
                                else:
                                    total_km = 0
                                #
                                this_rate_value = df_Rates_T[ all_years[y] ][ this_tech ]
                                #
                                this_yearly_result = this_rate_value*total_fleet*total_km
                                #
                            #
                            else: # This applies for import taxes
                                #
                                '''
                                if 'TRYLF' in this_tech: # Exoneration - This defines that productive groups don't pay the import taxes
                                    exoneration_factor = 0.25
                                else:
                                    exoneration_factor = 1
                                '''
                                #
                                age_list = list( this_tech_this_year_fleet_imp.keys() )
                                #
                                # We compute the yearly result (nominal) per cohort.
                                this_yearly_result = 0
                                for a in age_list:
                                    #
                                    this_activity_value = deepcopy( this_tech_this_year_fleet_imp[ a ] )
                                    #
                                    this_rate_value = deepcopy( df_Rates_T[ all_years[y] ][ this_tech ][ a ] ) / 1e6 # Gives M USD per unit (unit is fleet in this case)
                                    this_yearly_result += float( this_activity_value ) * float( this_rate_value )
                                    #
                                #
                            #
                        #
                    else:
                        this_yearly_result = 0 # means it is not worth entering and calculating
                        #
                    #
                    this_yearly_discounted_result = this_yearly_result / ( ( 1+discount_rate )**( all_years[y]-all_years[0] ) )
                    this_yearly_undiscounted_result = this_yearly_result
                    #
                    returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                    returnable_list_of_lists[-1][ fcm_table_header.index( output_variable + ' Disc' ) ] = float("{0:.4f}".format( this_yearly_discounted_result ) )
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor' ) ] = name_ID
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor_Type' ) ] = atype
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'GorS' ) ] = GorS
                    #
                    returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                    returnable_list_of_lists[-1][ fcm_table_header.index( output_variable ) ] = float("{0:.4f}".format( this_yearly_undiscounted_result ) )
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor' ) ] = name_ID
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor_Type' ) ] = atype
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'GorS' ) ] = GorS
                    #
                #
            #
        #
    #
    return returnable_list_of_lists
    #
#
##########################################################################################################################################################################################
# intersection_2 for the combination of fuels and techs // lookup for TF rates table.
def intersection_2(lst1, lst2): 
    return list(set(lst1) & set(lst2))
    #
#
# Data management function for technology & fuel-based parameters:
def data_management_TF( discounted_or_not, assorted_data_dicts, techs , discount_rate, df_Rates_TF, variable , m , output_variable , GorS , name_ID , atype , fuel, df_new_Rates, params ):
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------#
    returnable_list_of_lists = []
    all_years = [i for i in range(2018,2050+1) ]
    #
    list_of_variables = params['list_of_variables']
    #
    fcm_table_header = params['fcm_table_header'] + list_of_variables
    #
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------#
    #
    global rate_row_index_tech
    global rate_row_index_fuel
    global this_tech
    global this_fuel
    this_fuel = fuel
    rate_index_list_tech = df_Rates_TF['Technology'].tolist()
    rate_index_list_fuel = df_Rates_TF['Fuel'].tolist()
    #
    # the_fleet = deepcopy( assorted_data_dicts['fleet'][0] )
    # the_fleet_imported = deepcopy( assorted_data_dicts['fleet'][1] )
    unique_owner = assorted_data_dicts['fleet'][2]
    # fleet_Q_per_actor_perTech_perYear_per_age = assorted_data_dicts['fleet'][3]
    # fleet_Q_per_actor_perTech_perYear_per_age_share = assorted_data_dicts['fleet'][4]
    # fleet_Q_per_actor_perTech_perYear_per_age_imp = assorted_data_dicts['fleet'][5]
    # fleet_Q_per_actor_perTech_perYear_per_age_imp_share = assorted_data_dicts['fleet'][6]
    fleet_Q_per_actor_perTech_perYear_share = assorted_data_dicts['fleet'][7]
    #
    share_consumption_buses = assorted_data_dicts['fleet'][-3]
    share_consumption_taxis = assorted_data_dicts['fleet'][-2]
    #
    # We need to place the actors here:
    if name_ID != 'private_transport_owners' and name_ID != 'central_government' and name_ID != 'public_transport_users':
        owner_list = ['Businesses']
    if name_ID == 'central_government':
        owner_list = ['Other']
    if name_ID == 'private_transport_owners':
        owner_list = unique_owner
    if name_ID == 'public_transport_users':
        owner_list_raw = list( share_consumption_buses[ all_years[0] ].keys() )
        owner_list = [ e for e in owner_list_raw if 'Q' in e ]
    #
    for o in range( len( owner_list ) ):
        this_owner = owner_list[o]
        #
        for n in range( len( techs ) ):
            this_tech = techs[n]
            rate_row_index_tech = [i for i, x in enumerate(rate_index_list_tech) if x == this_tech]
            #
            rate_row_index_fuel = [i for i, x in enumerate(rate_index_list_fuel) if x == this_fuel]
            #
            rate_row_index_list = intersection_2(rate_row_index_tech , rate_row_index_fuel)

            # Let's add an exception to avoid doble-counting the income of hybrids:
            pass_hybrids = True
            if name_ID == 'electricity_companies' and 'ELE' not in this_fuel:
                pass_hybrids = False
            if name_ID == 'hydrocarbon_companies' and 'ELE' in this_fuel:
                pass_hybrids = False
            # End of exception

            if len( rate_row_index_list ) != 0 and pass_hybrids is True:
                rate_row_index = rate_row_index_list[0]
                #
                for y in range( len( all_years ) ):
                    value_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( this_tech in x ) and ( this_fuel in x ) and ( int( all_years[y] ) in x ) and ( variable in x ) ]
                    #
                    if len(value_indices) != 0:
                        #
                        data_index = value_indices[0]
                        #
                        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                        if name_ID != 'private_transport_owners':
                            this_share_owner_share = 1
                        else:
                            if this_tech in list( fleet_Q_per_actor_perTech_perYear_share[ this_owner ].keys() ):
                                if all_years[y] in list( fleet_Q_per_actor_perTech_perYear_share[ this_owner ][ this_tech ].keys() ):
                                    this_share_owner_share = fleet_Q_per_actor_perTech_perYear_share[ this_owner ][ this_tech ][ all_years[y] ]
                                else:
                                    this_share_owner_share = 0
                                    # print('*happens!*-1', this_tech, this_owner, all_years[y], name_ID )
                            else:
                                this_share_owner_share = 0
                                # print('*happens!*-2', this_tech, this_owner, all_years[y], name_ID )
                        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                        #
                        if output_variable not in ['Service Sales', 'Service Purchases']: # these are energy-related transactions
                            this_activity_value = float( assorted_data_dicts['t_f'][ data_index ][-1] )*this_share_owner_share
                            this_rate_value = deepcopy( df_Rates_TF[ all_years[y] ].iloc[ rate_row_index ] )
                        else: # means we are going to calculate income from actors of transport system operators
                            if ( 'Techs_Taxis' in this_tech ) and ( GorS == 'Spend' ):
                                this_share_user = share_consumption_taxis[ all_years[y] ][ this_owner ]/100 # depricated adjustment factors: (0.1/1.1) * 
                            if ('Techs_Buses' in this_tech) and ( GorS == 'Spend' ):
                                this_share_user = share_consumption_buses[ all_years[y] ][ this_owner ]/100 # depricated adjustment factors: ( 0.5 ) * 
                            if ('Techs_Taxis' in this_tech ) and ( GorS == 'Gather' ):
                                this_share_user = 1
                            if ('Techs_Buses' in this_tech ) and ( GorS == 'Gather' ):
                                this_share_user = 1
                            this_activity_value = float( assorted_data_dicts['t_f'][ data_index ][-1] )*this_share_user*1e9
                            this_rate_value = deepcopy( df_Rates_TF[ all_years[y] ].iloc[ rate_row_index ] )
                            #
                        #
                        this_yearly_result = this_activity_value * this_rate_value
                        #
                        this_yearly_discounted_result = this_yearly_result / ( ( 1+discount_rate )**( all_years[y]-all_years[0] ) )
                        this_yearly_undiscounted_result = this_yearly_result
                        #
                        if 'E4' in fuel:
                            #
                            if 'DSL' in fuel and 'PUB' in fuel:
                                fuel_surname = 'Fuel for Public Transport'
                            elif 'DSL' in fuel and 'PRI' in fuel:
                                fuel_surname = 'Fuel for Private Transport'
                            elif 'DSL' in fuel and 'HEA' in fuel:
                                fuel_surname = 'Fuel for Heavy Freight'
                            elif 'DSL' in fuel and 'LIG' in fuel:
                                fuel_surname = 'Fuel for Light Freight'
                            #
                            elif 'GSL' in fuel and 'PUB' in fuel:
                                fuel_surname = 'Fuel for Public Transport'
                            elif 'GSL' in fuel and 'PRI' in fuel:
                                fuel_surname = 'Fuel for Private Transport'
                            elif 'GSL' in fuel and 'HEA' in fuel:
                                fuel_surname = 'Fuel for Heavy Freight'
                            elif 'GSL' in fuel and 'LIG' in fuel:
                                fuel_surname = 'Fuel for Light Freight'
                            #
                            elif 'LPG' in fuel and 'PUB' in fuel:
                                fuel_surname = 'Fuel for Public Transport'
                            elif 'LPG' in fuel and 'PRI' in fuel:
                                fuel_surname = 'Fuel for Private Transport'
                            elif 'LPG' in fuel and 'HEA' in fuel:
                                fuel_surname = 'Fuel for Heavy Freight'
                            elif 'LPG' in fuel and 'LIG' in fuel:
                                fuel_surname = 'Fuel for Light Freight'
                            #
                            elif 'ELE' in fuel and 'PUB' in fuel:
                                fuel_surname = 'Electricity for Public Transport'
                            elif 'ELE' in fuel and 'PRI' in fuel:
                                fuel_surname = 'Electricity for Private Transport'
                            elif 'ELE' in fuel and 'HEA' in fuel:
                                fuel_surname = 'Electricity for Heavy Freight'
                            elif 'ELE' in fuel and 'LIG' in fuel:
                                fuel_surname = 'Electricity for Light Freight'
                            #
                            elif 'HYD' in fuel and 'PUB' in fuel:
                                fuel_surname = 'Hydrogen for Public Transport'
                            elif 'HYD' in fuel and 'PRI' in fuel:
                                fuel_surname = 'Hydrogen for Private Transport'
                            elif 'HYD' in fuel and 'HEA' in fuel:
                                fuel_surname = 'Hydrogen for Heavy Freight'
                            elif 'HYD' in fuel and 'LIG' in fuel:
                                fuel_surname = 'Hydrogen for Light Freight'
                            else:
                                fuel_surname = ''

                        returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                        returnable_list_of_lists[-1][ fcm_table_header.index( output_variable + ' Disc' ) ] =  float("{0:.4f}".format( this_yearly_discounted_result ) )
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel' ) ] = fuel
                        if 'E4' in fuel:
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel_Surname' ) ] = fuel_surname
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor' ) ] = name_ID
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor_Type' ) ] = atype
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'GorS' ) ] =  GorS

                        returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                        returnable_list_of_lists[-1][ fcm_table_header.index( output_variable ) ] =  float("{0:.4f}".format( this_yearly_undiscounted_result ) )
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel' ) ] = fuel
                        if 'E4' in fuel:
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel_Surname' ) ] = fuel_surname
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor' ) ] = name_ID
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Actor_Type' ) ] = atype
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'GorS' ) ] =  GorS
                        # -----------------------------------------------------
                        if ( ('Techs_Taxis' in this_tech) or ('Techs_Buses' in this_tech) ) and GorS == 'Spend':
                            returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Service Price' ) ] =  float("{0:.4f}".format( this_rate_value*1e9 ) ) # $ / Gpkm

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel' ) ] = this_fuel

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]

    return returnable_list_of_lists


'''
########################################################################################################################
############    DONE EMBEDDING FCM FUNCTIONS IN BASE RUNS MANAGER - NOW TO MODEL MANIPULATION    ############
########################################################################################################################
'''


def set_first_list(params):
    # scenario_list_print = ['BAU','NDP','OP15C']
    # scenario_list_print = ['BAU','OP15C']
    # scenario_list_print = ['OP15C']
    first_list_raw = os.listdir( params['Executables'] )
    #
    global first_list
    # scenario_list_print_with_fut = [ e + '_0' for e in scenario_list_print ]
    first_list = [e for e in first_list_raw if ('.csv' not in e) and
                  ('Table' not in e) and ('.py' not in e) and
                  ('__pycache__' not in e)]
    return first_list


def set_first_list_d(Executed_Scenario):
    first_list_raw = \
        os.listdir( params['Experi_Plat'] + params['Futures'] + 
                   str(Executed_Scenario))

    global first_list_d
    first_list_d_notfiltered = [e for e in first_list_raw if ( '.csv' not in e ) and ( 'Table' not in e ) and ( '.py' not in e ) and ( '__pycache__' not in e ) ]

    # Let us filter this a moment: // will only have the future 1 at hand
    # first_list_d = [ e for e in first_list_d_notfiltered if int( e.split('_')[-1] ) in [1] ]
    # first_list_d = [ e for e in first_list_d_notfiltered if int( e.split('_')[-1] ) in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19] ]
    # first_list_d = [ e for e in first_list_d_notfiltered if int( e.split('_')[-1] ) not in [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19] ] # This should complete the reminder
    # whole_list = [ n for n in range( 1, 99+1 ) ]
    # first_list_d = [ e for e in first_list_d_notfiltered if int( e.split('_')[-1] ) in whole_list ]
    first_list_d = first_list_d_notfiltered
    return first_list_d


def calculate_transfers(    m, discounted_or_not, results_list, assorted_data_dicts, type_1_actor, type_2_actor, type_3_actor, type_4_actor, type_5_actor,
                            df_Rates_TF_SalesPurchasesEnergy, df_Unit_T_DerechoArancelario, df_Unit_T_ValorAduanero, df_Unit_T_SelectivoAlConsumo, df_Unit_T_ImportVAT,
                            df_Unit_T_TotalTaxes, df_Unit_T_GananciaEstimada, df_Unit_T_MarketPrice, df_Unit_TF_IUC, df_Unit_TF_ElectricityVAT, df_Unit_TF_H2,
                            this_vmt_rates_per_tech, df_Unit_T_PropertyTax, df_Rates_TF_SalesPurchasesService, Initial_OR_Adjustment ):

    ''' 'TYPE 1 ACTORS:' // Goverment '''
    print( Initial_OR_Adjustment + ' Part - Performing FCM_7.b.A - Calculate transfers for Government (public spending)' )
    for n in range( len( type_1_actor ) ):
        # Function 1: spend_investments_and_fom
        this_returnable = type_1_actor[n].spend_investements_and_fom( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_own , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_1_actor[n].spend_investements( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_own , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_1_actor[n].spend_fom( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_own , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

    ''' 'TYPE 2 ACTORS:' // Energy Companies '''
    print( Initial_OR_Adjustment + ' Part - Performing FCM_7.b.B - Calculate transfers for Energy Companies' )
    for n in range( len( type_2_actor ) ):
        # Function 1: gather_energy_sale
        fuels_produced_by_techs = params['fuels_produced_by_techs']
        for k in range( len( fuels_produced_by_techs ) ):
            this_returnable = type_2_actor[n].gather_energy_sale( discounted_or_not, assorted_data_dicts, type_2_actor[n].techs_sell , type_2_actor[n].name_ID , type_2_actor[n].discount_rate , df_Rates_TF_SalesPurchasesEnergy , m , fuels_produced_by_techs[k] )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
        # Function 2: spend_investments_and_fom
        this_returnable = type_2_actor[n].spend_investements_and_fom( discounted_or_not, assorted_data_dicts, type_2_actor[n].techs_own , type_2_actor[n].name_ID , type_2_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_2_actor[n].spend_investements( discounted_or_not, assorted_data_dicts, type_2_actor[n].techs_own , type_2_actor[n].name_ID , type_2_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_2_actor[n].spend_fom( discounted_or_not, assorted_data_dicts, type_2_actor[n].techs_own , type_2_actor[n].name_ID , type_2_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )
        # Function 3: spend_variable_costs
        this_returnable = type_2_actor[n].spend_variable_costs( discounted_or_not, assorted_data_dicts, type_2_actor[n].techs_own , type_2_actor[n].name_ID , type_2_actor[n].discount_rate , m ) # , fuels_produced_by_techs[k] )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

    ''' 'TYPE 3 ACTORS:' // Public Transport Operators '''
    print( Initial_OR_Adjustment + ' Part - Performing FCM_7.b.C - Calculate transfers for Public Transport Operators' )
    for n in range( len( type_3_actor ) ):
        # Define the energy commodities used by the actor type:
        fuels_used_by_techs = params['fuels_used_by_techs_2']
        # Function 1: gather_service_sale
        fuels_produced_by_techs = params['fuels_produced_by_techs'] # review the fuels produced by transport service companies // match OutputActivityRatio && Relationship_Table
        for k in range( len( fuels_produced_by_techs ) ):
            this_returnable = type_3_actor[n].gather_service_sale( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_sell , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Rates_TF_SalesPurchasesService , m , fuels_produced_by_techs[k] )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
        # Function 2: spend_investments_and_fom
        this_returnable = type_3_actor[n].spend_investements_and_fom( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_3_actor[n].spend_investements( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_3_actor[n].spend_fom( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )
        # Function 3: spend_energy_purchase (using "UseByTechnology")
        for k in range( len( fuels_used_by_techs ) ):
            this_returnable = type_3_actor[n].spend_energy_purchase( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Rates_TF_SalesPurchasesEnergy , m , fuels_used_by_techs[k] )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
    
        ''' Taxes paid to the government: '''
        # Function 4a: spend_derecho_arancelario
        this_returnable = type_3_actor[n].spend_derecho_arancelario( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_DerechoArancelario , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 4b: spend_valor_aduanero
        this_returnable = type_3_actor[n].spend_valor_aduanero( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_ValorAduanero , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 4c: spend_selectivo_al_consumo
        this_returnable = type_3_actor[n].spend_selectivo_al_consumo( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_SelectivoAlConsumo , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 4d: spend_import_vat
        this_returnable = type_3_actor[n].spend_import_vat( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_ImportVAT , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 4 PLUS-A: spend_total_import_taxes
        this_returnable = type_3_actor[n].spend_total_import_taxes( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_TotalTaxes , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 4 PLUS-B: spend_estimated_earnings
        this_returnable = type_3_actor[n].spend_estimated_earnings( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_GananciaEstimada , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 4 PLUS-C: spend_vehicle_purchase
        this_returnable = type_3_actor[n].spend_vehicle_purchase( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_MarketPrice , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 5a: spend_iuc (using "UseByTechnology")
        fuels_used_by_techs = params['fuels_used_by_techs_3']
        for k in range(len(fuels_used_by_techs)):
            this_returnable = type_3_actor[n].spend_iuc( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_TF_IUC , m , fuels_used_by_techs[k] , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

        # Function 5b: spend_electricity_vat (using "UseByTechnology")
        fuels_used_by_techs = params['fuels_used_by_techs_4']
        for k in range( len( fuels_used_by_techs ) ):
            this_returnable = type_3_actor[n].spend_electricity_vat( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_TF_ElectricityVAT , m , fuels_used_by_techs[k] , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

        # Function 5c: spend_h2 (using "UseByTechnology")
        fuels_used_by_techs = params['fuels_used_by_techs_5']
        for k in range( len( fuels_used_by_techs ) ):
            this_returnable = type_3_actor[n].spend_h2( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_TF_H2 , m , fuels_used_by_techs[k] , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 6: spend_property_tax
        if Initial_OR_Adjustment == 'Adjustment':
            this_returnable = type_3_actor[n].spend_property_tax( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_PropertyTax , m , 'df_new_Rates' )
        else:
            this_returnable = type_3_actor[n].spend_property_tax( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , df_Unit_T_PropertyTax , m , 'NO_df_new_Rates' )

        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 7: spend_vmt_tax
        if Initial_OR_Adjustment == 'Adjustment':
            this_returnable = type_3_actor[n].spend_vmt_tax( discounted_or_not, assorted_data_dicts, type_3_actor[n].techs_own , type_3_actor[n].name_ID , type_3_actor[n].discount_rate , this_vmt_rates_per_tech, m , 'df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
        else:
            pass # the tax does not exist before the adjustment

    ''' 'TYPE 4 ACTORS:' // Private Use Transport Owners '''
    print(Initial_OR_Adjustment + ' Part - Performing FCM_7.b.C - ' +
          'Calculate transfers for Private Use Transport Owners')
    for n in range(len(type_4_actor)):
        # Define the energy commodities used by the actor type:
        # review the fuels used by transport service companies //
        # match OutputActivityRatio && Relationship_Table
        fuels_used_by_techs = params['fuels_used_by_techs_6']

        # Function 1: spend_investements_and_fom
        print( '        Part - Performing FCM_7.b.D.1 - Investments and FOM for ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_investements_and_fom( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_4_actor[n].spend_investements( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        this_returnable = type_4_actor[n].spend_fom( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , m )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 2: spend_energy_purchase (using "UseByTechnology")
        print( '        Part - Performing FCM_7.b.D.2 - Energy purchase ' + str( type_4_actor[n].name_ID ) )
        for k in range( len( fuels_used_by_techs ) ):
            this_returnable = type_4_actor[n].spend_energy_purchase( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Rates_TF_SalesPurchasesEnergy , m , fuels_used_by_techs[k] )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 3a: spend_derecho_arancelario
        print( '        Part - Performing FCM_7.b.D.3 - Derecho arancelario ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_derecho_arancelario( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_DerechoArancelario , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 3b: spend_valor_aduanero
        print( '        Part - Performing FCM_7.b.D.4 - Valor aduanero ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_valor_aduanero( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_ValorAduanero , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 3c: spend_selectivo_al_consumo
        print( '        Part - Performing FCM_7.b.D.5 - Selectivo al consumo ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_selectivo_al_consumo( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_SelectivoAlConsumo , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 3d: spend_import_vat
        print( '        Part - Performing FCM_7.b.D.6 - Import VAT ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_import_vat( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_ImportVAT , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 3 PLUS-A: spend_total_import_taxes
        print( '        Part - Performing FCM_7.b.D.7 - Total Import Taxes ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_total_import_taxes( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_TotalTaxes , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 3 PLUS-B: spend_estimated_earnings
        print( '        Part - Performing FCM_7.b.D.8 - Estimated earnings ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_estimated_earnings( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_GananciaEstimada , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # Function 3 PLUS-C: spend_vehicle_purchase
        print( '        Part - Performing FCM_7.b.D.9 - Vehicle purchase ' + str( type_4_actor[n].name_ID ) )
        this_returnable = type_4_actor[n].spend_vehicle_purchase( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_MarketPrice , m , 'NO_df_new_Rates' )
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        ''' ------------------------------------------ '''
        # Function 4a: spend_iuc
        fuels_used_by_techs = params['fuels_used_by_techs_7']

        print( '        Part - Performing FCM_7.b.D.10 - Spend IUC ' + str( type_4_actor[n].name_ID ) )
        for k in range( len( fuels_used_by_techs ) ):
            this_returnable = type_4_actor[n].spend_iuc( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_TF_IUC , m , fuels_used_by_techs[k] , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

        # Function 4b: spend_electricity_vat
        fuels_used_by_techs = ['E4ELE_PRI', 'E4ELE_HEA', 'E4ELE_LIG']
        print( '        Part - Performing FCM_7.b.D.11 - Spend electricity VAT ' + str( type_4_actor[n].name_ID ) )
        for k in range( len( fuels_used_by_techs ) ):
            this_returnable = type_4_actor[n].spend_electricity_vat( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_TF_ElectricityVAT , m , fuels_used_by_techs[k] , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

        # Function 4c: spend_h2 (using "UseByTechnology")
        fuels_used_by_techs = params['fuels_used_by_techs_8']
        print( '        Part - Performing FCM_7.b.D.12 - Spend H2 ' + str( type_4_actor[n].name_ID ) )
        for k in range( len( fuels_used_by_techs ) ):
            this_returnable = type_4_actor[n].spend_h2( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_TF_H2 , m , fuels_used_by_techs[k] , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 5: spend_property_tax
        print( '        Part - Performing FCM_7.b.D.13 - Spend property tax ' + str( type_4_actor[n].name_ID ) )
        if Initial_OR_Adjustment == 'Adjustment':
            this_returnable = type_4_actor[n].spend_property_tax( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_PropertyTax , m , 'df_new_Rates' )
        else:
            this_returnable = type_4_actor[n].spend_property_tax( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , df_Unit_T_PropertyTax , m , 'NO_df_new_Rates' )

        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )
        ''' ------------------------------------------ '''
        # Function 6: spend_vmt_tax
        print( '        Part - Performing FCM_7.b.D.14 - Spend VMT ' + str( type_4_actor[n].name_ID ) )
        if Initial_OR_Adjustment == 'Adjustment':
            this_returnable = type_4_actor[n].spend_vmt_tax( discounted_or_not, assorted_data_dicts, type_4_actor[n].techs_own , type_4_actor[n].name_ID , type_4_actor[n].discount_rate , this_vmt_rates_per_tech, m , 'df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
        else:
            pass # the tax does not exist before the adjustment

    ''' 'TYPE 5 ACTORS:' // Public Transport Users '''
    print( Initial_OR_Adjustment + ' Part - Performing FCM_7.b.E - Calculate transfers for Public Transport Users' )
    for n in range( len( type_5_actor ) ):
        # Function 1: spend_service_purchase
        fuels_produced_by_techs = params['fuels_produced_by_techs'] # review the fuels produced by transport service companies // match OutputActivityRatio && Relationship_Table
        for k in range( len( fuels_produced_by_techs ) ):
            this_returnable = type_5_actor[n].spend_service_purchase( discounted_or_not, assorted_data_dicts, type_5_actor[n].techs_buy , type_5_actor[n].name_ID , type_5_actor[n].discount_rate , df_Rates_TF_SalesPurchasesService , m , fuels_produced_by_techs[k] )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

    # Let us leave here the returnables:
    return results_list


def print_transfers(m, results_list, fcm_table_header, output_adress,
                    first_list_case, phase, alternative_future):
    unique_first_seven_combination = []
    new_results_list = []

    header_size = 11
    column_var_size = 51

    for n in range( len( results_list ) ):
        this_first_seven_combination = []
        for k1 in range( 0 , header_size ):
            this_first_seven_combination.append( results_list[n][k1] )

        empty_list = []
        for k2 in range( header_size , header_size + column_var_size ):
            empty_list.append( '' )
            if results_list[n][k2] != '':
                this_variable_index = k2
                this_variable_value = results_list[n][k2]

        if this_first_seven_combination not in unique_first_seven_combination:
            unique_first_seven_combination.append( this_first_seven_combination )

            new_results_list.append( this_first_seven_combination + empty_list )

            new_results_list[-1][this_variable_index] = this_variable_value
        else:
            pass

        get_this_row_identifier_index = unique_first_seven_combination.index( this_first_seven_combination )

        new_results_list[get_this_row_identifier_index][this_variable_index] = this_variable_value

    cost_disaggregation_table = pd.DataFrame(new_results_list, columns=fcm_table_header)
    if phase != 'Upgrade':
        cost_disaggregation_table.to_csv ( output_adress + '/' + str( first_list_case ) + '_TEM' + '.csv', index = None, header=True)
    else:
        cost_disaggregation_table.to_csv ( output_adress + '/' + str( first_list_case ) + '_TEM_Upgraded_' + str(alternative_future) + '.csv', index = None, header=True)


def incorporate_qs_ps_ts( m, results_list, assorted_data_dicts, q_p_t_list, phase ):
    # NOTE: phase can be either 'Upgrade' or not.
    # If 'Update', print H2 and VKT.
    all_years = [i for i in range(2018,2050+1, 1) ]

    df_Rates_TF_SalesPurchasesEnergy    = q_p_t_list[0] # P // included
    df_Unit_TF_IUC                      = q_p_t_list[1] # T // included
    df_Unit_TF_ElectricityVAT           = q_p_t_list[2] # T // included
    df_Rates_TF_ElectricityVAT          = q_p_t_list[3] # T
    df_Unit_TF_H2                       = q_p_t_list[4] # T // included
    df_Rates_TF_SalesPurchasesService   = q_p_t_list[5] # P // included

    df_Unit_T_TotalTaxes                = q_p_t_list[6] # T
    df_Unit_T_MarketPrice               = q_p_t_list[7] # P
    df_Unit_T_SelectivoAlConsumo        = q_p_t_list[8] # T
    df_Unit_T_CIF                       = q_p_t_list[9] # P

    fleet_Q_perTech_perYear_per_age_imports = q_p_t_list[10] # Q

    this_vmt_rates_per_tech             = q_p_t_list[11] # T

    fleet_Q_perTech_perYear_per_age     = q_p_t_list[12] # Q

    fiscal_value_perTech_perYear_per_age    = q_p_t_list[13] # P
    dict_Unit_PropertyTax               = q_p_t_list[14] # T

    fleet_Q_per_actor_perTech_perYear_per_age       = q_p_t_list[15] # Q
    fleet_Q_per_actor_perTech_perYear_per_age_imp   = q_p_t_list[16] # Q
    # -------------------------------------------------------------------------
    returnable_list_of_lists = []
    all_years = [i for i in range(2018,2050+1) ]

    list_of_variables = params['list_of_variables']

    fcm_table_header = params['fcm_table_header'] + list_of_variables
    #--------------------------------------------------------------------------
    # A) Adding energy taxes:
    supplier_price_data = []
    for y in range( len( all_years ) ):
        this_y = all_years[ y ]
        supplier_price_data.append( list( df_Rates_TF_SalesPurchasesEnergy[ this_y ] ) )

    # Let's recall the taxes we have computed:
    fuels_IUC = df_Unit_TF_IUC['Fuel'].tolist()
    fuels_ElectricityVAT = df_Unit_TF_ElectricityVAT['Fuel'].tolist()
    fuels_H2 = df_Unit_TF_H2['Fuel'].tolist()

    # Now let us add the rows for energy:
    for n in range( len( df_Rates_TF_SalesPurchasesEnergy.index.tolist() ) ):
        n_index = df_Rates_TF_SalesPurchasesEnergy.index.tolist()[n]
        this_fuel = df_Rates_TF_SalesPurchasesEnergy.loc[ n_index, 'Fuel' ]
        this_tech = df_Rates_TF_SalesPurchasesEnergy.loc[ n_index, 'Technology' ]

        if this_fuel in fuels_IUC:
            df_Unit_Tax = deepcopy( df_Unit_TF_IUC )
        if this_fuel in fuels_ElectricityVAT:
            df_Unit_Tax = deepcopy( df_Unit_TF_ElectricityVAT )
        if this_fuel in fuels_H2:
            df_Unit_Tax = deepcopy( df_Unit_TF_H2 )

        tech_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Technology'].tolist() ) if element == this_tech ]

        fuel_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Fuel'].tolist() ) if element == this_fuel ]

        try:
            matching_fuel_index = list( set(tech_indices_tax) & set(fuel_indices_tax) )[0] # fuels_IUC.index( fuels_of_interest[f] )
        except Exception:
            print('debug')
            print(df_Unit_Tax['Fuel'].tolist())
            print( list( set(tech_indices_tax) ) )
            print( list( set(fuel_indices_tax) ) )
            print(this_tech, this_fuel)
            sys.exit()

        for y in range( len( all_years ) ):
            supplier_price_amount = float( df_Rates_TF_SalesPurchasesEnergy.loc[ n_index, all_years[y] ] )
            tax_amount = float( df_Unit_Tax.loc[ matching_fuel_index , all_years[y] ] )

            if 'E4' in this_fuel:
                if 'DSL' in this_fuel and 'PUB' in this_fuel:
                    fuel_surname = 'Fuel for Public Transport'
                elif 'DSL' in this_fuel and 'PRI' in this_fuel:
                    fuel_surname = 'Fuel for Private Transport'
                elif 'DSL' in this_fuel and 'HEA' in this_fuel:
                    fuel_surname = 'Fuel for Heavy Freight'
                elif 'DSL' in this_fuel and 'LIG' in this_fuel:
                    fuel_surname = 'Fuel for Light Freight'

                elif 'GSL' in this_fuel and 'PUB' in this_fuel:
                    fuel_surname = 'Fuel for Public Transport'
                elif 'GSL' in this_fuel and 'PRI' in this_fuel:
                    fuel_surname = 'Fuel for Private Transport'
                elif 'GSL' in this_fuel and 'HEA' in this_fuel:
                    fuel_surname = 'Fuel for Heavy Freight'
                elif 'GSL' in this_fuel and 'LIG' in this_fuel:
                    fuel_surname = 'Fuel for Light Freight'

                elif 'LPG' in this_fuel and 'PUB' in this_fuel:
                    fuel_surname = 'Fuel for Public Transport'
                elif 'LPG' in this_fuel and 'PRI' in this_fuel:
                    fuel_surname = 'Fuel for Private Transport'
                elif 'LPG' in this_fuel and 'HEA' in this_fuel:
                    fuel_surname = 'Fuel for Heavy Freight'
                elif 'LPG' in this_fuel and 'LIG' in this_fuel:
                    fuel_surname = 'Fuel for Light Freight'

                elif 'ELE' in this_fuel and 'PUB' in this_fuel:
                    fuel_surname = 'Electricity for Public Transport'
                elif 'ELE' in this_fuel and 'PRI' in this_fuel:
                    fuel_surname = 'Electricity for Private Transport'
                elif 'ELE' in this_fuel and 'HEA' in this_fuel:
                    fuel_surname = 'Electricity for Heavy Freight'
                elif 'ELE' in this_fuel and 'LIG' in this_fuel:
                    fuel_surname = 'Electricity for Light Freight'

                elif 'HYD' in this_fuel and 'PUB' in this_fuel:
                    fuel_surname = 'Hydrogen for Public Transport'
                elif 'HYD' in this_fuel and 'PRI' in this_fuel:
                    fuel_surname = 'Hydrogen for Private Transport'
                elif 'HYD' in this_fuel and 'HEA' in this_fuel:
                    fuel_surname = 'Hydrogen for Heavy Freight'
                elif 'HYD' in this_fuel and 'LIG' in this_fuel:
                    fuel_surname = 'Hydrogen for Light Freight'
                else:
                    fuel_surname = ''

            returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Energy Price' ) ] =  float("{0:.4f}".format( supplier_price_amount ) )
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel' ) ] = this_fuel
            if 'E4' in this_fuel:
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel_Surname' ) ] = fuel_surname
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]

            returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Energy Price wTax' ) ] =  float("{0:.4f}".format( supplier_price_amount + tax_amount ) )
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel' ) ] = this_fuel
            if 'E4' in this_fuel:
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel_Surname' ) ] = fuel_surname
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]

            returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Energy Tax' ) ] =  float("{0:.4f}".format( tax_amount ) )
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel' ) ] = this_fuel
            if 'E4' in this_fuel:
                returnable_list_of_lists[-1][ fcm_table_header.index( 'Fuel_Surname' ) ] = fuel_surname
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]
    # -------------------------------------------------------------------------
    # B) Adding Imports-related rates and units:
    dicts2check = [  df_Unit_T_SelectivoAlConsumo, df_Unit_T_TotalTaxes, df_Unit_T_MarketPrice, df_Unit_T_CIF ]
    var_names_to_check = params['var_names_to_check']

    tech_list = list( fleet_Q_perTech_perYear_per_age.keys() )
    for t in range( len( tech_list ) ):
        this_tech = tech_list[t]
        year_list = list( fleet_Q_perTech_perYear_per_age[ this_tech ].keys() )

        for y in range( len( year_list ) ):
            this_year = year_list[y]
            age_list_raw = list( fleet_Q_perTech_perYear_per_age[ this_tech ][ this_year ].keys() )
            age_list = [ e for e in age_list_raw if type(e) == int ]

            for a in range( len( age_list ) ):
                this_age = age_list[a]

                value = fleet_Q_perTech_perYear_per_age[ this_tech ][this_year][ this_age ]
                value_fv = fiscal_value_perTech_perYear_per_age[ this_tech ][this_year][ this_age ]
                value_property_unit = dict_Unit_PropertyTax[ this_tech ][this_year][ this_age ]

                value_imp = 0
                if this_tech in list( fleet_Q_perTech_perYear_per_age_imports.keys() ):
                    if this_year in list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ].keys() ):
                        if this_age in list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ this_year ].keys() ):
                            value_imp = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][this_year][ this_age ]

                if value != 0 or value_imp != 0:
                    if value != 0:
                        returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Q Total' ) ] = value
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Age' ) ] = this_age

                        returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'FV' ) ] = value_fv
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Age' ) ] = this_age

                        returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'U Property Tax' ) ] = value_property_unit
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Age' ) ] = this_age

                    if value_imp != 0:
                        returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Q Imports' ) ] = value_imp
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
                        returnable_list_of_lists[-1][ fcm_table_header.index( 'Age' ) ] = this_age
 
                        for v in range( len( var_names_to_check ) ):
                            try:
                                value_rate = dicts2check[v][this_year][ this_tech ][ this_age ]
                            except:
                                value_rate = 0
                            if value_rate != 0:
                                returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])

                                returnable_list_of_lists[-1][ fcm_table_header.index( var_names_to_check[v] ) ] = value_rate

                                returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                                returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                                returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech

                                returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
                                returnable_list_of_lists[-1][ fcm_table_header.index( 'Age' ) ] = this_age
    # -------------------------------------------------------------------------
    # C) Adding imported and present fleet
    if phase == 'Upgrade': # necessary because there are no VKT results for the system before adjustments
        year_list = list( this_vmt_rates_per_tech.keys() )
        for this_year in year_list:
            for this_tech in list( this_vmt_rates_per_tech[ this_year ].keys() ):
                value_vmt = this_vmt_rates_per_tech[ this_year ][ this_tech ]
                if value_vmt != 0:
                    returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'U VKT' ) ] = value_vmt
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech
                    returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
    # -------------------------------------------------------------------------
    # D) Adding imported and present fleet per actor
    if phase != 'Upgrade': # necessary because we don't need to print this infinite times
        owner_list = list( fleet_Q_per_actor_perTech_perYear_per_age.keys() )
        for o in range( len( owner_list ) ):
            this_owner = owner_list[o]

            tech_list = list( fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ].keys() )
            for t in range( len( tech_list ) ):
                this_tech = tech_list[t]
                year_list = list( fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ][ this_tech ].keys() )

                for y in range( len( year_list ) ):
                    this_year = year_list[y]
                    age_list_raw = list( fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ][ this_tech ][ this_year ].keys() )
                    age_list = [ e for e in age_list_raw if type(e) == int ]

                    for a in range( len( age_list ) ):
                        this_age = age_list[a]
                        value = fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ][ this_tech ][this_year][ this_age ]
                        value_imp = 0
                        if this_tech in list( fleet_Q_per_actor_perTech_perYear_per_age_imp.keys() ):
                            if this_year in list( fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_tech ].keys() ):
                                if this_age in list( fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_tech ][ this_year ].keys() ):
                                    value_imp = fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_tech ][this_year][ this_age ]

                        if value != 0:
                            returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Q Total' ) ] = value

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Age' ) ] = this_age
                        # -----------------------------------------------------
                        if value_imp != 0:
                            returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Q Imports' ) ] = value_imp

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = this_tech

                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Owner' ) ] = this_owner
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = this_year
                            returnable_list_of_lists[-1][ fcm_table_header.index( 'Age' ) ] = this_age
    # -------------------------------------------------------------------------
    for l in range( len( returnable_list_of_lists ) ):
        results_list.append( returnable_list_of_lists[l] )

    return results_list


def disag_lcoe_pp(assorted_data_dicts, time_range_vector, params):
    lcoe_per_pp = {}
    all_power_plants_techs = params['all_power_plants_techs']

    for appt in all_power_plants_techs:
        power_plants_techs = [appt]

        ElectricityPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_generated_electricity = [ 0 for y in range( len(time_range_vector) ) ]

        for y in range( len( time_range_vector ) ):

            electricity_production = 0
            for elec_techs in range( len( power_plants_techs ) ):
                elec_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( power_plants_techs[elec_techs] in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

                this_electricity_production = 0
                if len(elec_tech_indices) != 0:
                    for n in range(len(elec_tech_indices)):
                        elec_tech_index =  elec_tech_indices[n]
                        this_electricity_production += float( assorted_data_dicts['t_f'][ elec_tech_index ][-1] )  # of 'power_plants'
                else:
                    this_electricity_production += 0

                electricity_production += this_electricity_production

            new_investments = 0
            for elec_techs in range( len( power_plants_techs ) ):
                elec_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( power_plants_techs[elec_techs] in x ) and ( int( float( time_range_vector[y] ) ) in x ) and ( 'CapitalInvestment' in x ) ]

                if len(elec_tech_indices) != 0:
                    elec_tech_index =  elec_tech_indices[0]
                    this_electricity_invesmtens = float( assorted_data_dicts['t'][ elec_tech_index ][-1] ) # of 'power_plants'
                else:
                    this_electricity_invesmtens = 0
                new_investments += this_electricity_invesmtens

            new_FOM = 0
            for elec_techs in range( len( power_plants_techs ) ):
                elec_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( power_plants_techs[elec_techs] in x ) and ( int( float( time_range_vector[y] ) ) in x ) and ( 'AnnualFixedOperatingCost' in x ) ]
                #
                if len(elec_tech_indices) != 0:
                    elec_tech_index =  elec_tech_indices[0]
                    this_electricity_FOM = float( assorted_data_dicts['t'][ elec_tech_index ][-1] ) # of 'power_plants'
                else:
                    this_electricity_FOM = 0
                new_FOM += this_electricity_FOM

            annualized_new_investments = new_investments * 0.06 / ( 1 - (1+0.06)**(-25) )
            ElectricityPrice_new_investments[y] = new_investments
            for fill_y in range( y, len( time_range_vector ) ):
                ElectricityPrice_annualized_new_investments_vector[fill_y] += annualized_new_investments

            ElectricityPrice_fom_vector[y] = new_FOM
            ElectricityPrice_generated_electricity[y] = electricity_production

        # THE AVERAGE BASE PRICE IS GOING TO BE 88.9 COLONES/KWH @ 575 COLONES / USD THAT GIVES 0.1546 USD / KWH w/o TAXES
        ElectricityPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_for_new = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_for_old = [ 0 for y in range( len(time_range_vector) ) ]
        # Conversion logic: ($/kWh)*(kWh/PJ) = $/PJ, then ($/PJ)*(1 M$/ 1e6 $) = 1 M$/PJ

        for y in range( 0, len( time_range_vector ) ):
            try:
                ElectricityPrice_for_new[y] = ( ElectricityPrice_fom_vector[y] + ElectricityPrice_annualized_new_investments_vector[y] ) / ElectricityPrice_generated_electricity[y]
            except Exception:
                ElectricityPrice_for_new[y] = 0
            ElectricityPrice_for_old[y] = 0  # this is not needed for levelized cost metrics
            ElectricityPrice_vector[y] = ElectricityPrice_for_old[y] + ElectricityPrice_for_new[y]

        lcoe_per_pp.update({appt: deepcopy(ElectricityPrice_vector)})

    return lcoe_per_pp


def calc_lcot(assorted_data_dicts, time_range_vector, trn_tech, Fleet_Groups,
              fleet_Q_perTech_perYear_per_age_imports, df_Unit_T_MarketPrice,
              df_Rates_TF_SalesPurchasesEnergy,
              df_Unit_TF_IUC, df_Unit_TF_ElectricityVAT, df_Unit_TF_H2):
    fleet_techs = Fleet_Groups[trn_tech]

    trnPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
    trnPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
    trnPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
    trnPrice_variable_cost_vector = [ 0 for y in range( len(time_range_vector) ) ]
    trnPrice_produced_km = [ 0 for y in range( len(time_range_vector) ) ]

    for y in range( len( time_range_vector ) ):
        prod_pass_km = 0 # here we should select the % of trips produced by the "concesionario" fleet
        prod_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( trn_tech in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

        if len(prod_tech_indices) != 0:
            prod_tech_index =  prod_tech_indices[0]
            this_pkm_production = float( assorted_data_dicts['t_f'][ prod_tech_index ][-1] )*1e9 # of 'Techs_Buses', unit in *kilometers*
        else:
            this_pkm_production = 0

        prod_pass_km += this_pkm_production

        trnPrice_produced_km[y] = prod_pass_km
        # ---
        capital_expense = 0
        this_q_per_tech = [ 0 for t in range( len( fleet_techs ) ) ]
        # We must use the fleet here:
        for t in range( len( fleet_techs ) ):
            this_tech = fleet_techs[t]
            these_ages_raw = list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ].keys() )
            these_ages = [ i for i in these_ages_raw if type(i) == int ]
            this_inv = 0
            for a in these_ages:
                this_q_a = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ][ a ] # let's work only with the imported fleet in order to have a comparable methodology to electricity rate
                this_market_price = df_Unit_T_MarketPrice[ time_range_vector[y] ][ this_tech ][ a ]
                this_inv += this_q_a*this_market_price/1e6
                this_q_per_tech[t] += this_q_a

            capital_expense += this_inv

        annualized_new_investments = capital_expense * 0.05 / ( 1 - (1+0.05)**(-16) )  # 'WARNING THIS IS AN INPUT'
        trnPrice_new_investments[y] = capital_expense

        for fill_y in range( y, len( time_range_vector ) ):
            if fill_y <= y + 16:
                trnPrice_annualized_new_investments_vector[fill_y] += annualized_new_investments

        # ---
        technical_FOM = 0
        for t in range( len( fleet_techs ) ):
            fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'AnnualFixedOperatingCost' in x ) ]
            if len(fleet_techs_indices) != 0:
                fleet_tech_index =  fleet_techs_indices[0]
                this_fleet_tech_FOM = float( assorted_data_dicts['t'][ fleet_tech_index ][-1] ) # of 'bus technology'
            else:
                this_fleet_tech_FOM = 0
            technical_FOM += this_fleet_tech_FOM

        trnPrice_fom_vector[y] = technical_FOM

        # ---
        technical_variable_cost = 0
        for t in range( len( fleet_techs ) ):
            fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'UseByTechnology' in x ) ]
            if len(fleet_techs_indices) != 0:
                for n in range( len( fleet_techs_indices ) ):
                    fleet_tech_index =  fleet_techs_indices[n]
                    this_fleet_fuel_consumption = float( assorted_data_dicts['t_f'][ fleet_tech_index ][-1] ) # of 'bus technology' in PJ
                    this_fleet_fuel = assorted_data_dicts['t_f'][ fleet_tech_index ][1] # the fuels

                    if fleet_techs[t] in df_Unit_TF_IUC['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_IUC['Fuel'].tolist():
                        df_Unit_Tax = deepcopy( df_Unit_TF_IUC )
                    if fleet_techs[t] in df_Unit_TF_ElectricityVAT['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_ElectricityVAT['Fuel'].tolist():
                        df_Unit_Tax = deepcopy( df_Unit_TF_ElectricityVAT )
                    if fleet_techs[t] in df_Unit_TF_H2['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_H2['Fuel'].tolist():
                        df_Unit_Tax = deepcopy( df_Unit_TF_H2 )

                    tech_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Technology'].tolist() ) if element == fleet_techs[t] ]
                    fuel_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Fuel'].tolist() ) if element == this_fleet_fuel ]
                    tax_index = list( set(tech_indices_tax) & set(fuel_indices_tax) )[0]

                    df_Unit_Price = deepcopy( df_Rates_TF_SalesPurchasesEnergy )
                    tech_indices_price = [index for index, element in enumerate( df_Unit_Price['Technology'].tolist() ) if element == fleet_techs[t] ]
                    fuel_indices_price = [index for index, element in enumerate( df_Unit_Price['Fuel'].tolist() ) if element == this_fleet_fuel ]
                    price_index = list( set(tech_indices_price) & set(fuel_indices_price) )[0]

                    unit_fuel_cost = df_Unit_Tax.loc[ tax_index, time_range_vector[y] ] + df_Unit_Price.loc[ price_index, time_range_vector[y] ] # per PJ cost
                    technical_variable_cost += unit_fuel_cost * this_fleet_fuel_consumption

        trnPrice_variable_cost_vector[y] = technical_variable_cost

    trnPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]
    trnPrice_for_new = [ 0 for y in range( len(time_range_vector) ) ]
    trnPrice_for_old = [ 0 for y in range( len(time_range_vector) ) ]

    for y in range( 0, len( time_range_vector ) ):
        try:
            trnPrice_for_new[y] = ( trnPrice_variable_cost_vector[y] + trnPrice_fom_vector[y] + trnPrice_annualized_new_investments_vector[y] ) / trnPrice_produced_km[y]
        except Exception:
            trnPrice_for_new[y] = 0
        trnPrice_for_old[y] = 0  # this is not needed for levelized cost metrics
        trnPrice_vector[y] = trnPrice_for_old[y] + trnPrice_for_new[y] # USD / km

    return trnPrice_vector, trnPrice_for_new, trnPrice_produced_km, trnPrice_fom_vector, annualized_new_investments, trnPrice_variable_cost_vector


def additional_levelized_costs(m, lcot_sedan, lcoe_per_pp, all_years):
    list_of_variables = params['list_of_variables']
    fcm_table_header = params['fcm_table_header'] + list_of_variables

    returnable_list_of_lists = []

    # Adding transport levelized costs:
    for y in range(len(all_years)):
        returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])

        returnable_list_of_lists[-1][ fcm_table_header.index( 'Service Price' ) ] =  float("{0:.4f}".format( lcot_sedan[y]*1e9 ) ) # $ / Gpkm

        returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
        returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
        returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = 'Techs_Sedan'

        returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]

    # Adding power plant levelized costs
    for pp in list(lcoe_per_pp.keys()):
        for y in range(len(all_years)):
            returnable_list_of_lists.append([ '' for k in range( len( fcm_table_header ) ) ])

            returnable_list_of_lists[-1][ fcm_table_header.index( 'Energy Price' ) ] =  float("{0:.4f}".format( lcoe_per_pp[pp][y] ) ) # $ / Gpkm

            returnable_list_of_lists[-1][ fcm_table_header.index( 'Strategy' ) ] = m['Strategy']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Future.ID' ) ] = m['Future.ID']
            returnable_list_of_lists[-1][ fcm_table_header.index( 'Technology' ) ] = pp

            returnable_list_of_lists[-1][ fcm_table_header.index( 'Year' ) ] = all_years[y]

    return returnable_list_of_lists


def data_processor(case, base_or_fut, content_all):
    # The first actions is to unpack all the content sent to data_processor
    df_prm_def_content = content_all[0]
    content_df_Relations = content_all[1]
    content_TEM_rates = content_all[2]
    content_TEM_control_file = content_all[3]
    content_trn_tech_list = content_all[4]
    content_df_enigh2tem = content_all[5]
    content_fleet_groups = content_all[6]
    content_tax_rates = content_all[7]

    # Keep unpacking below (#1):
    list_param_default_value_params = df_prm_def_content[0]
    list_param_default_value_value = df_prm_def_content[1]
    global Initial_Year_of_Uncertainty
    Initial_Year_of_Uncertainty = df_prm_def_content[2]

    # Keep unpacking below (#2):
    agent_list = content_df_Relations[0]
    all_techs_list_unique = content_df_Relations[1]
    in_relationship_techs = content_df_Relations[2]
    in_relationship_ownership = content_df_Relations[3]
    in_relationship_gather = content_df_Relations[4]
    in_relationship_sell = content_df_Relations[5]
    in_relationship_buy = content_df_Relations[6]

    # Keep unpacking below (#3):
    pd_discount_rates = content_TEM_rates[0]
    dict_ER_per_year = content_TEM_rates[1]
    list_ER = content_TEM_rates[2]
    df_Rates_TF_SalesPurchasesService = content_TEM_rates[3]
    df_Rates_TF_SalesPurchasesEnergy = content_TEM_rates[4]
    df_Rates_TF_TaxEnergy = content_TEM_rates[5]

    # Keep unpacking below (#4):
    df_tax_assign = content_TEM_control_file[0]
    df_strategies = content_TEM_control_file[1]
    df_milestones = content_TEM_control_file[2]
    df_fuels_and_techs = content_TEM_control_file[3]

    # Keep unpacking below (#5):
    technology_list_cif = content_trn_tech_list[0]  # 5.1
    technology_list_transport_dict_cif = content_trn_tech_list[1]  # 5.1
    technology_list_existing = content_trn_tech_list[2]  # 5.2
    technology_list_transport_dict_existing = content_trn_tech_list[3]  # 5.2
    technology_list_transport = content_trn_tech_list[4]  # 5.3
    technology_list_transport_techs = content_trn_tech_list[5]  # 5.3
    df_Property_Tax_Ranges = content_trn_tech_list[6]  # 5.4
    df_Property_Tax_Ranges_columns_scales = content_trn_tech_list[7]  # 5.4
    dict_property_tax_fiscal_value_scales = content_trn_tech_list[8]  # 5.4
    dict_Property_Tax_Applicable = content_trn_tech_list[9]  # 5.5
    factor_Property_Growth = content_trn_tech_list[10]  # 5.6
    table_depreciation_age = content_trn_tech_list[11]  # 5.7
    table_depreciation_factor = content_trn_tech_list[12]  # 5.7
    df_bus_rates_age = content_trn_tech_list[13]  # 5.8
    df_bus_rates_dep_factor = content_trn_tech_list[14]  # 5.8
    df_bus_rates_profit_factor = content_trn_tech_list[15]  # 5.8
    df_bus_rates_profit_rate = content_trn_tech_list[16]  # 5.8
    pd_shares_fiscalvalue_per_modelyear = content_trn_tech_list[17]  # 5.9
    pd_shares_fiscalvalue_col = content_trn_tech_list[18]  # 5.9
    pd_shares_fiscalvalue_modelyears = content_trn_tech_list[19]  # 5.9
    pd_shares_fiscalvalue_projyear = content_trn_tech_list[20]  # 5.9
    pd_shares_cif_rates_per_age = content_trn_tech_list[21]  # 5.10
    pd_shares_cif_col = content_trn_tech_list[22]  # 5.10
    fixed_admin_costs_buses = content_trn_tech_list[23]  # 5.11
    fixed_admin_costs_taxis = content_trn_tech_list[24]  # 5.11

    # Keep unpacking below (#6):
    # (this is done below after opening a scenario)

    # Keep unpacking below (#7):
    Fleet_Groups = content_fleet_groups[0]
    Fleet_Groups_Distance = content_fleet_groups[1]
    Fleet_Groups_OR = content_fleet_groups[2]
    Fleet_Groups_techs_2_dem = content_fleet_groups[3]

    # Finish unpacking below (#8):
    dict_cif_distribution = content_tax_rates[0]
    dict_cif_relative_cif = content_tax_rates[1]
    dict_import_sc_rates = content_tax_rates[2]
    dict_import_dai = content_tax_rates[3]
    dict_import_6946 = content_tax_rates[4]
    dict_import_iva_relcif = content_tax_rates[5]
    dict_residual_fiscal_value_wo_depreciation = content_tax_rates[6]
    dict_residual_fiscal_value = content_tax_rates[7]
    dict_residual_fiscal_usd = content_tax_rates[8]
    dict_residual_fleet_distribution = content_tax_rates[9]

    if base_or_fut == 'base':
        first_list = set_first_list(params)
        case_element_list = first_list[case].split('_')
        scenario_string = str( first_list[case] )
        output_adress = params['Executables'] + '/' + scenario_string

        scenario_string_cif = scenario_string
        output_adress_cif = output_adress

    if base_or_fut == 'fut':
        case_element_list = case.split('_')
        scenario_string = str( case )
        output_adress = params['Experi_Plat'] + params['Futures'] + \
            scenario_string.split('_')[0] + '/' + scenario_string

        scenario_string_cif = str( case ).replace( 'BAU', 'NDP' )
        output_adress_cif = params['Experi_Plat'] + params['Futures'] + 'NDP' + \
            '/' + scenario_string_cif

    case_strategy_alphabet = case_element_list[0]
    case_future = case_element_list[-1]

    share_autos = content_df_enigh2tem[case_strategy_alphabet][0]
    share_motos = content_df_enigh2tem[case_strategy_alphabet][1]
    share_imports_autos = content_df_enigh2tem[case_strategy_alphabet][2]
    share_imports_motos = content_df_enigh2tem[case_strategy_alphabet][3]
    share_consumption_buses = content_df_enigh2tem[case_strategy_alphabet][4]
    share_consumption_taxis = content_df_enigh2tem[case_strategy_alphabet][5]

    m = {'Strategy':case_strategy_alphabet ,'Future.ID':case_future,
         'adjustment_id':-1 }

    # print( m['Strategy'], int(m['Future.ID'] ) )
    # if ( m['Strategy'] == 'BAU' and ( (int(m['Future.ID'])>800 and int(m['Future.ID'])<1000 ) or (int(m['Future.ID'])>80 and int(m['Future.ID'])<100) or (int(m['Future.ID'])==9) ) ) or ( m['Strategy'] == 'NDP' ):
    # if ( m['Strategy'] == 'BAU' or m['Strategy'] == 'NDP' ) and ( int(m['Future.ID'] ) == 999 ) :
    # if ( m['Strategy'] == 'NDP' ) and ( int(m['Future.ID'] ) == 999 ) :
    accept_all = True
    if accept_all == True:
        '''''
        EXECUTION PART (FUNCTIONS ABOVE)
        '''
        print('1: We have defined some data. ' +
              'Now we will read the parameters we have as reference ' +
              '(or previous parameters) into a dictionary.')
        ''' 1.A) We extract the strucute setup of the model
        based on 'Structure.xlsx' '''
        structure_filename = params['From_Conf'] + params['B1_Model_Struc']
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
            # ---
            ''' Structural dictionary 1: Notes
            a) We use this dictionary relating a specific technology and a group
            technology and associate the prefix list '''
            Fleet_Groups_inv = {}
            for k in range(len(list(Fleet_Groups.keys()))):
                this_fleet_group_key = list(Fleet_Groups.keys())[k]
                for e in range(len(Fleet_Groups[ this_fleet_group_key ])):
                    this_fleet_group_tech = Fleet_Groups[this_fleet_group_key][e]
                    Fleet_Groups_inv.update({this_fleet_group_tech:
                                            this_fleet_group_key})

            group_tech_PUBLIC = []
            group_tech_PRIVATE = []
            group_tech_FREIGHT_HEA = []
            group_tech_FREIGHT_LIG = []

            for t in range(len(list(Fleet_Groups_techs_2_dem.keys()))):
                tech_key = list( Fleet_Groups_techs_2_dem.keys())[t]
                this_fuel = Fleet_Groups_techs_2_dem[tech_key]
                if 'PRI' in this_fuel:
                    group_tech_PRIVATE.append(tech_key)
                if 'PUB' in this_fuel:
                    group_tech_PUBLIC.append(tech_key)
                if 'FREHEA' in this_fuel:
                    group_tech_FREIGHT_HEA.append(tech_key)
                if 'FRELIG' in this_fuel:
                    group_tech_FREIGHT_LIG.append(tech_key)

            global time_range_vector
            time_range_vector = [int(i) for i in
                                S_DICT_sets_structure[ 'elements_list'][0]]
        # -
        ''' 1.B) We finish this sub-part,
        and proceed to read all the base scenarios. '''
        header_row = params['header_row']

        scenario_list = []
        stable_scenario_list_raw = os.listdir( '1_Baseline_Modelling' )
        for n in range( len( stable_scenario_list_raw ) ):
            if (stable_scenario_list_raw[n] not in ['_Base_Dataset', '_BACKUP']
                    and '.txt' not in stable_scenario_list_raw[n]):
                scenario_list.append( stable_scenario_list_raw[n])

        # This section reads a reference data.csv from baseline scenarios and
        # frames Structure-OSEMOSYS_CR.xlsx
        col_position = []
        col_corresponding_initial = []
        for n in range(len(S_DICT_sets_structure['set'])):
            col_position\
                .append(header_row.index(S_DICT_sets_structure['set'][n]))
            col_corresponding_initial \
                .append(S_DICT_sets_structure['initial'][n])
        # Define the dictionary for calibrated database:
        stable_scenarios = {}
        for scen in scenario_list:
            stable_scenarios.update({scen:{}})

        for scen in range(len(scenario_list)):
            this_paramter_list_dir = \
                '1_Baseline_Modelling/' + str(scenario_list[scen])
            parameter_list = os.listdir(this_paramter_list_dir)

            for p in range(len(parameter_list)):
                this_param = parameter_list[p].replace('.csv','')
                stable_scenarios[ scenario_list[scen] ] \
                    .update({this_param: {}})
                # To extract the parameter input data:
                all_params_list_index = \
                    S_DICT_params_structure['parameter'].index(this_param)
                this_number_of_elements = \
                    S_DICT_params_structure['number_of_elements'
                                            ][all_params_list_index]
                this_index_list = \
                    S_DICT_params_structure['index_list'
                                            ][all_params_list_index]

                for k in range(this_number_of_elements):
                    stable_scenarios[scenario_list[scen]][this_param] \
                        .update({this_index_list[k]: []})
                stable_scenarios[scenario_list[scen]][this_param] \
                    .update({'value': []})

                # Extract data:
                with open(this_paramter_list_dir + '/' +
                          str(parameter_list[p]), mode='r') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        if (row[ header_row[-1] ] != None and
                                row[ header_row[-1] ] != ''):
                            for h in range( 2, len(header_row)-1 ):
                                if (row[header_row[h]] != None and
                                        row[header_row[h]] != ''):
                                    set_index = \
                                        S_DICT_sets_structure['set'] \
                                        .index( header_row[h] )
                                    set_initial = \
                                        S_DICT_sets_structure['initial'
                                                              ][ set_index ]
                                    stable_scenarios[scenario_list[scen]][this_param][set_initial].append(row[header_row[h]])
                            stable_scenarios[scenario_list[scen]][this_param ]['value' ].append( row[ header_row[-1] ] )

        ''' 1.C) : '''
        first_list = set_first_list(params)
        # ---
        r_government = \
            float( pd_discount_rates.loc[0 ,'Government'])
        r_energy_companies = \
            float( pd_discount_rates.loc[0 ,'Energy_Companies'])
        r_public_transport_companies = \
            float( pd_discount_rates.loc[0 ,'Public_Transport_Operator'])
        r_freight_transport_companies = \
            float( pd_discount_rates.loc[0 ,'Freight_Transport_Owner'])
        r_private_owner = \
            float( pd_discount_rates.loc[0 ,'Private_Transport_Owner'])
        r_public_user = \
            float( pd_discount_rates.loc[0 ,'Public_Transport_User'])
        # ---
        if base_or_fut == 'base':
            first_list = set_first_list(params)
            case_element_list = first_list[case].split('_')
            scenario_string = str( first_list[case] )
            output_adress = params['Executables'] + '/' + scenario_string

            scenario_string_cif = scenario_string
            output_adress_cif = output_adress

        if base_or_fut == 'fut':
            case_element_list = case.split('_')
            scenario_string = str( case )
            output_adress = \
                params['Experi_Plat'] + params['Futures'] + \
                scenario_string.split('_')[0] + '/' + scenario_string

            scenario_string_cif = str( case ).replace( 'BAU', 'NDP' )
            output_adress_cif = \
                params['Experi_Plat'] + params['Futures'] + 'NDP' + '/' + \
                scenario_string_cif

        case_strategy_alphabet = case_element_list[0]
        case_future = case_element_list[-1]

        m = {'Strategy':case_strategy_alphabet,
             'Future.ID':case_future, 'adjustment_id':0 }

        print('We already have outputs of ' + scenario_string + \
              '. The resulting csv file will now be processed in TEM')

        # FCM_1 - First, we read the inputs: 
        # ---------------------------------------------------------------------
        # Extract the OseMOSYS database:
        general_data = params['general_data']
        all_vars_of_interest = params['all_vars_of_interest']
        all_columns_of_interest = general_data + all_vars_of_interest
        with open( output_adress + '/' + scenario_string + '_Output' + '.csv' ) as csvfile:
            reader = csv.DictReader( csvfile, skipinitialspace = True )
            osemosys_database = { name: [] for name in all_columns_of_interest } # reader.fieldnames }
            for row in reader:
                for name in all_columns_of_interest:
                    if row[ 'Technology' ] in all_techs_list_unique:
                        osemosys_database[name].append( row[name] )
        # ---------------------------------------------------------------------
        # Extract the Distance Driven from the Input Parameters (to estimate the unit cost of vehicles).
        general_data_i = params['general_data_i']
        all_vars_of_interest_i = params['all_vars_of_interest_i']
        all_columns_of_interest_i = general_data_i + all_vars_of_interest_i

        with open( output_adress + '/' + scenario_string + '_Input' + '.csv' ) as csvfile:
            reader = csv.DictReader( csvfile, skipinitialspace = True )
            osemosys_database_i = { name: [] for name in all_columns_of_interest_i }
            for row in reader:
                #
                for name in all_columns_of_interest_i:
                    if row[ 'Technology' ] in all_techs_list_unique:
                        osemosys_database_i[name].append( row[name] )
        # ---------------------------------------------------------------------
        # Extract the CapitalCost from the Inputs:
        input_param_header = params['input_param_header']
        with open( output_adress_cif + '/' + scenario_string_cif + '_Input' + '.csv' ) as csvfile:
            reader = csv.DictReader( csvfile, skipinitialspace = True )
            capital_cost_database = { name: [] for name in input_param_header } # reader.fieldnames }
            for row in reader:
                for name in input_param_header:
                    if row[ 'Technology' ] in all_techs_list_unique and ( row[ 'Fuel' ] == '' and row[ 'Emission' ] == '' and row[ 'Season' ] == '' and row[ 'Year' ] != '' and row[ 'CapitalCost' ] != '' ):
                        capital_cost_database[name].append( row[name] )
                    elif row[ 'Technology' ] in all_techs_list_unique and ( row[ 'Fuel' ] == '' and row[ 'Emission' ] == '' and row[ 'Season' ] == '' and row[ 'Year' ] != '' and row[ 'CapitalCost' ] == '' ):
                        capital_cost_database[name].append( 0 )

        # Extract the VariableCost from the inputs:
        input_param_header = params['input_param_header']
        with open( output_adress + '/' + scenario_string + '_Input' + '.csv' ) as csvfile:
            reader = csv.DictReader( csvfile, skipinitialspace = True )
            variable_cost_database = { name: [] for name in input_param_header } # reader.fieldnames }
            for row in reader:
                for name in input_param_header:
                    if row[ 'Technology' ] in all_techs_list_unique and ( row[ 'Fuel' ] == '' and row[ 'Emission' ] == '' and row[ 'Season' ] == '' and row[ 'Year' ] != '' and row[ 'VariableCost' ] != '' ):
                        variable_cost_database[name].append( row[name] )
                    elif row[ 'Technology' ] in all_techs_list_unique and ( row[ 'Fuel' ] == '' and row[ 'Emission' ] == '' and row[ 'Season' ] == '' and row[ 'Year' ] != '' and row[ 'VariableCost' ] == '' ):
                        variable_cost_database[name].append( 0 )

        # Extract the OperationalLife from the inputs:
        input_param_header = params['input_param_header_2']
        with open( output_adress + '/' + scenario_string + '_Input' + '.csv' ) as csvfile: # $*$ Because of a technicality, we had not printed operational life before. Keep making reference to the future 0 for this.
        # with open( './Executables/' + scenario_string.split('_')[0] + '_0/' + scenario_string.split('_')[0] + '_0_Input' + '.csv' ) as csvfile:
            reader = csv.DictReader( csvfile, skipinitialspace = True )
            operational_life_database = { name: [] for name in input_param_header }
            for row in reader:
                for name in input_param_header:
                    if row[ 'Technology' ] in all_techs_list_unique and ( row[ 'Fuel' ] == '' and row[ 'Emission' ] == '' and row[ 'Season' ] == '' and row[ 'Year' ] == '' and row[ 'OperationalLife' ] != '' ):
                        operational_life_database[name].append( row[name] )
                    elif row[ 'Technology' ] in all_techs_list_unique and ( row[ 'Fuel' ] == '' and row[ 'Emission' ] == '' and row[ 'Season' ] == '' and row[ 'Year' ] == '' and row[ 'OperationalLife' ] == '' ):
                        operational_life_database[name].append( 0 )

        # FCM_2 - Create the "assorted" dictionaries:
        assorted_data_dicts = {}
        assorted_data_dicts_i = {}

        # Proceed for outputs:
        t_combination = []
        t_f_combination = []

        for i in range( len( osemosys_database['Strategy'] ) ):
            t = osemosys_database['Technology'][i]
            f = osemosys_database['Fuel'][i]
            y = int( osemosys_database['Year'][i] )

            for v in range( len( all_vars_of_interest ) ):
                var = osemosys_database[ all_vars_of_interest[v] ][i]
                if      t != '' and f == '' and y != '' and var != '':
                    t_combination.append( [t, y, all_vars_of_interest[v], var] )

                elif    t != '' and f != '' and y != '' and var != '':
                    t_f_combination.append( [t, f, y, all_vars_of_interest[v], var] )

        # WE WE WILL LEAVE THE FLEET INSTANCE OF THE FLEET COMPOSITION LOGIC
        assorted_data_dicts.update( { 't':t_combination, 't_f':t_f_combination, 'fleet':{}, 'inputs':assorted_data_dicts_i } )

        # Proceed for inputs:
        t_combination = []
        t_f_combination = []
        #
        for i in range( len( osemosys_database_i['Strategy'] ) ):
            t = osemosys_database_i['Technology'][i]
            f = osemosys_database_i['Fuel'][i]

            if osemosys_database_i['Year'][i] != '':
                y = int( osemosys_database_i['Year'][i] )

                for v in range( len( all_vars_of_interest_i ) ):
                    var = osemosys_database_i[ all_vars_of_interest_i[v] ][i]

                    if      t != '' and f == '' and y != '' and var != '':
                        t_combination.append( [t, y, all_vars_of_interest_i[v], var] )

                    elif    t != '' and f != '' and y != '' and var != '':
                        t_f_combination.append( [t, f, y, all_vars_of_interest_i[v], var] )

            else:
                pass

        # WE WE WILL LEAVE THE FLEET INSTANCE OF THE FLEET COMPOSITION LOGIC
        assorted_data_dicts_i.update( { 't':t_combination, 't_f':t_f_combination } )

        # ---------------------------------------------------------------------
        # WE MUST ALSO CREATE A LIST WITH ELEMENTS OF INPUT VARIABLES ASSORTED
        assorted_capital_cost = []
        for i in range( len( capital_cost_database['Technology'] ) ):
            t = capital_cost_database['Technology'][i]
            y = int( capital_cost_database['Year'][i] )
            params_of_interest = 'CapitalCost'
            param = capital_cost_database['CapitalCost'][i]

            assorted_capital_cost.append( [ t , y , params_of_interest , param ] )

        assorted_variable_cost = []
        for i in range( len( variable_cost_database['Technology'] ) ):
            t = variable_cost_database['Technology'][i]
            y = int( variable_cost_database['Year'][i] )
            params_of_interest = 'VariableCost'
            param = variable_cost_database['VariableCost'][i]

            assorted_variable_cost.append( [ t , y , params_of_interest , param ] )

        assorted_operational_life = []
        for i in range( len( operational_life_database['Technology'] ) ):
            t = operational_life_database['Technology'][i]
            params_of_interest = 'OperationalLife'
            param = operational_life_database['OperationalLife'][i]

            assorted_operational_life.append( [ t ,params_of_interest , param ] )

        # FCM_3 - Instantiate objects:
        #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
        # 1) Instantiate government objects:
        central_government  = o_type_1_actor(   in_relationship_ownership['central_government'], in_relationship_gather['central_government'],
                                                in_relationship_sell['central_government'], in_relationship_buy['central_government'], 'central_government', r_government )

        type_1_actor = [ central_government ]
        #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
        # 2) Instantiate energy company objects:
        electricity_companies   = o_type_2_actor(   in_relationship_ownership['electricity_companies'], in_relationship_gather['electricity_companies'],
                                                    in_relationship_sell['electricity_companies'], in_relationship_buy['electricity_companies'], 'electricity_companies' , r_energy_companies )
        hydrocarbon_companies   = o_type_2_actor(   in_relationship_ownership['hydrocarbon_companies'], in_relationship_gather['hydrocarbon_companies'],
                                                    in_relationship_sell['hydrocarbon_companies'], in_relationship_buy['hydrocarbon_companies'], 'hydrocarbon_companies' , r_energy_companies )
        hydrogen_companies      = o_type_2_actor(   in_relationship_ownership['hydrogen_companies'], in_relationship_gather['hydrogen_companies'],
                                                    in_relationship_sell['hydrogen_companies'], in_relationship_buy['hydrogen_companies'], 'hydrogen_companies' , r_energy_companies)

        type_2_actor = [ electricity_companies, hydrocarbon_companies, hydrogen_companies ]
        #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
        # 3) Instantiate public transport company objects:
        bus_companies               = o_type_3_actor(   in_relationship_ownership['bus_companies'], in_relationship_gather['bus_companies'],
                                                        in_relationship_sell['bus_companies'], in_relationship_buy['bus_companies'], 'bus_companies' , r_public_transport_companies )
        bus_special_companies       = o_type_3_actor(   in_relationship_ownership['special_transport_companies'], in_relationship_gather['special_transport_companies'],
                                                        in_relationship_sell['special_transport_companies'], in_relationship_buy['special_transport_companies'], 'special_transport_companies' , r_public_transport_companies )
        taxi_companies              = o_type_3_actor(   in_relationship_ownership['taxi_industry'], in_relationship_gather['taxi_industry'],
                                                        in_relationship_sell['taxi_industry'], in_relationship_buy['taxi_industry'], 'taxi_industry' , r_public_transport_companies )

        type_3_actor = [ bus_companies, bus_special_companies, taxi_companies ]
        #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
        # 4) Instantiate freight company objects :
        light_truck_companies       = o_type_4_actor(   in_relationship_ownership['light_truck_companies'], in_relationship_gather['light_truck_companies'],
                                                        in_relationship_sell['light_truck_companies'], in_relationship_buy['light_truck_companies'], 'light_truck_companies' , r_freight_transport_companies )
        heavy_freight_companies     = o_type_4_actor(   in_relationship_ownership['heavy_freight_companies'], in_relationship_gather['heavy_freight_companies'],
                                                        in_relationship_sell['heavy_freight_companies'], in_relationship_buy['heavy_freight_companies'], 'heavy_freight_companies' , r_freight_transport_companies )
        #----------------------------------------------------------------------------------------------%
        private_transport_owners = o_type_4_actor(  in_relationship_ownership['private_transport_owners'], in_relationship_gather['private_transport_owners'],
                                                    in_relationship_sell['private_transport_owners'], in_relationship_buy['private_transport_owners'], 'private_transport_owners' , r_private_owner)

        type_4_actor = [ light_truck_companies, heavy_freight_companies, private_transport_owners ]
        #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
        # 5) Instantiate user objects:
        public_transport_users = o_type_5_actor(    in_relationship_ownership['public_transport_users'], in_relationship_gather['public_transport_users'],
                                                    in_relationship_sell['public_transport_users'], in_relationship_buy['public_transport_users'], 'public_transport_users' , r_public_user)

        type_5_actor = [ public_transport_users ]

        print('Initial Part - Performing FCM_4.a - We are done initiating inputs // will define the tax structures below')
        print('     Within FCM_4 - Estimating the *Derecho Arancelario* tax structure')
        df_Rates_T_DerechoArancelario = {} # // HAS %S
        df_Unit_T_DerechoArancelario = {}
        for y in range( len( time_range_vector ) ):
            df_Unit_T_DerechoArancelario.update( { time_range_vector[y]:deepcopy( dict_import_dai ) } ) # // should HAVE VALUES BASED ON CIF
            df_Rates_T_DerechoArancelario.update( { time_range_vector[y]:deepcopy( dict_import_dai ) } )

        for t in range( len( technology_list_transport_techs ) ):
            this_tech = technology_list_transport_techs[t]
            list_ages = list( dict_import_dai[ this_tech ].keys() )
            list_ages = [ i for i in list_ages if type(i) == int ]
            list_ages.sort()

            for a in list_ages:
                import_size = dict_cif_distribution[ this_tech ][ a ]/100
                import_relative_cif = dict_cif_relative_cif[ this_tech ][ a ]
                rate = df_Rates_T_DerechoArancelario[ time_range_vector[y] ][ this_tech ][ a ]

                for y in range( len( time_range_vector ) ): # this carries the projection
                    value_indices_d = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( technology_list_transport_techs[t] in x ) and ( 'DistanceDriven' in x ) and ( int( time_range_vector[ y ] ) in x ) ]                            
                    data_index_d =  value_indices_d[0]
                    driven_distance = float( assorted_data_dicts_i['t'][ data_index_d ][-1] )

                    # NOTE: here the *capital cost* reflects the CIF
                    value_index = [i for i, x in enumerate( assorted_capital_cost ) if ( technology_list_transport_techs[t] in x ) and ( time_range_vector[y] in x ) ]
                    data_index = value_index[0]
                    cif_value = (10**6)*float( assorted_capital_cost[ data_index ][-1] )*driven_distance/(10**9) # in USD / unit, from OSEMOSYS

                    df_Unit_T_DerechoArancelario[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )
        ''' --------------------------------------------------------------- '''
        print('     Within FCM_4 - Estimating the *Valor Aduanero* tax structure')
        df_Rates_T_ValorAduanero = {} # // HAS %S
        df_Unit_T_ValorAduanero = {}
        for y in range( len( time_range_vector ) ):
            df_Unit_T_ValorAduanero.update( { time_range_vector[y]:deepcopy( dict_import_6946 ) } ) # // should HAVE VALUES BASED ON CIF
            df_Rates_T_ValorAduanero.update( { time_range_vector[y]:deepcopy( dict_import_6946 ) } )

        for t in range( len( technology_list_transport_techs ) ):
            this_tech = technology_list_transport_techs[t]
            list_ages = list( dict_import_6946[ this_tech ].keys() )
            list_ages = [ i for i in list_ages if type(i) == int ]
            list_ages.sort()

            for a in list_ages:
                import_size = dict_cif_distribution[ this_tech ][ a ]/100
                import_relative_cif = dict_cif_relative_cif[ this_tech ][ a ]

                for y in range( len( time_range_vector ) ): # this carries the projection
                    rate = df_Rates_T_ValorAduanero[ time_range_vector[y] ][ this_tech ][ a ]

                    value_indices_d = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( technology_list_transport_techs[t] in x ) and ( 'DistanceDriven' in x ) and ( int( time_range_vector[ y ] ) in x ) ]                            
                    data_index_d =  value_indices_d[0]
                    driven_distance = float( assorted_data_dicts_i['t'][ data_index_d ][-1] )

                    # NOTE: here the *capital cost* reflects the CIF
                    value_index = [i for i, x in enumerate( assorted_capital_cost ) if ( technology_list_transport_techs[t] in x ) and ( time_range_vector[y] in x ) ]
                    data_index = value_index[0]
                    cif_value = (10**6)*float( assorted_capital_cost[ data_index ][-1] )*driven_distance/(10**9) # in USD / unit, from OSEMOSYS

                    if ( time_range_vector[y] < 2023 ) and ( ( 'ELE' in this_tech ) or ( 'HYD' in this_tech ) ):
                        # SC EXONERATIONS for EVs HERE
                        if cif_value*import_relative_cif <= 30000:
                            df_Unit_T_ValorAduanero[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*0
                        if cif_value*import_relative_cif > 30000 and cif_value*import_relative_cif <= 45000:
                            df_Unit_T_ValorAduanero[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*0
                        if cif_value*import_relative_cif > 45000 and cif_value*import_relative_cif <= 60000:
                            df_Unit_T_ValorAduanero[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*0
                        if cif_value*import_relative_cif > 60000:
                            df_Unit_T_ValorAduanero[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*1
                    else:
                        df_Unit_T_ValorAduanero[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )
        ''' --------------------------------------------------------------- '''
        print('     Within FCM_4 - Estimating the *Selectivo al consumo* tax structure')
        df_Rates_T_SelectivoAlConsumo = {} # // HAS %S
        for y in range( len( time_range_vector ) ):
            # if time_range_vector[y] <= 2023:
            #     df_Rates_T_SelectivoAlConsumo.update( { time_range_vector[y]:dict_import_sc_rates_exo } )
            # else:
            #     df_Rates_T_SelectivoAlConsumo.update( { time_range_vector[y]:dict_import_sc_rates } )
            # df_Rates_T_SelectivoAlConsumo.update( { time_range_vector[y]:dict_import_sc_rates_exo } ) # let's apply exonerations all the way
            df_Rates_T_SelectivoAlConsumo.update( { time_range_vector[y]:dict_import_sc_rates } ) # let's NOT apply exonerations

        df_Unit_T_SelectivoAlConsumo = {}
        for y in range( len( time_range_vector ) ):
            df_Unit_T_SelectivoAlConsumo.update( { time_range_vector[y]:deepcopy( dict_import_sc_rates ) } ) # // should HAVE VALUES BASED ON CIF

        for t in range( len( technology_list_transport_techs ) ):
            this_tech = technology_list_transport_techs[t]
            list_ages = list( dict_import_sc_rates[ this_tech ].keys() )
            list_ages = [ i for i in list_ages if type(i) == int ]
            list_ages.sort()

            for a in list_ages:
                import_size = dict_cif_distribution[ this_tech ][ a ]/100
                import_relative_cif = dict_cif_relative_cif[ this_tech ][ a ]

                for y in range( len( time_range_vector ) ): # this carries the projection
                    rate = df_Rates_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ]

                    value_indices_d = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( technology_list_transport_techs[t] in x ) and ( 'DistanceDriven' in x ) and ( int( time_range_vector[ y ] ) in x ) ]                            
                    data_index_d =  value_indices_d[0]
                    driven_distance = float( assorted_data_dicts_i['t'][ data_index_d ][-1] )

                    # NOTE: here the *capital cost* reflects the CIF
                    value_index = [i for i, x in enumerate( assorted_capital_cost ) if ( technology_list_transport_techs[t] in x ) and ( time_range_vector[y] in x ) ]
                    data_index = value_index[0]
                    cif_value = (10**6)*float( assorted_capital_cost[ data_index ][-1] )*driven_distance/(10**9) # in USD / unit, from OSEMOSYS

                    if ( time_range_vector[y] < 2023 ) and ( ( 'ELE' in this_tech ) or ( 'HYD' in this_tech ) ):
                        # SC EXONERATIONS for EVs HERE
                        if cif_value*import_relative_cif <= 30000:
                            df_Unit_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*0
                        if cif_value*import_relative_cif > 30000 and cif_value*import_relative_cif <= 45000:
                            df_Unit_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*0.75
                        if cif_value*import_relative_cif > 45000 and cif_value*import_relative_cif <= 60000:
                            df_Unit_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*0.5
                        if cif_value*import_relative_cif > 60000:
                            df_Unit_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )*1
                    else:
                        if ( time_range_vector[y] < 2022 ) and ( 'HYB' in this_tech ):
                            df_Unit_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ] = (20/100)*( cif_value*import_relative_cif )
                        else:
                            df_Unit_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ] = (rate/100)*( cif_value*import_relative_cif )
        ''' --------------------------------------------------------------- '''
        print('     Within FCM_4 - Estimating the *Import VAT* and *Market Price* tax structure')
        df_Rates_T_ImportVAT = {} # iterates over c (cohort) and t (tehcnology)
        df_Rates_T_GananciaEstimada = {} # iterates over c (cohort) and t (tehcnology)

        df_Unit_T_ImportVAT = {} # HAS VALUES BASED ON CIF
        df_Unit_T_GananciaEstimada = {}
        df_Unit_T_TotalTaxes = {}
        df_Unit_T_MarketPrice = {} # HAS VALUES BASED ON CIF
        df_Unit_T_CIF = {}

        for y in range( len( time_range_vector ) ):
            df_Rates_T_ImportVAT.update( { time_range_vector[y]:deepcopy( dict_import_iva_relcif ) } )
            df_Rates_T_GananciaEstimada.update( { time_range_vector[y]:deepcopy( dict_import_iva_relcif ) } )

            df_Unit_T_ImportVAT.update( { time_range_vector[y]:deepcopy( dict_import_iva_relcif ) } )
            df_Unit_T_GananciaEstimada.update( { time_range_vector[y]:deepcopy( dict_import_iva_relcif ) } )    
            df_Unit_T_TotalTaxes.update( { time_range_vector[y]:deepcopy( dict_import_iva_relcif ) } )
            df_Unit_T_MarketPrice.update( { time_range_vector[y]:deepcopy( dict_import_iva_relcif ) } )
            df_Unit_T_CIF.update( { time_range_vector[y]:deepcopy( dict_import_iva_relcif ) } )   

        for t in range( len( technology_list_transport_techs ) ):
            this_tech = technology_list_transport_techs[t]
            list_ages = list( dict_import_iva_relcif[ this_tech ].keys() )
            list_ages = [ i for i in list_ages if type(i) == int ]
            list_ages.sort()

            for a in list_ages:
                import_size = dict_cif_distribution[ this_tech ][ a ]/100
                import_relative_cif = dict_cif_relative_cif[ this_tech ][ a ]

                check_rate = dict_import_iva_relcif[ this_tech ][ a ]
                if check_rate < 1:  # this is to leave low values on zero
                    rate = 0
                else:  # and this sets the VAT at 13%
                    rate = 13

                if 'BUS' in this_tech:  # this is to leave low values on zero
                    fair_rate = 0
                else:  # and this sets the VAT at 13%
                    fair_rate = 25

                for y in range(len(time_range_vector)):  # creates projection
                    df_Rates_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = rate
                    df_Rates_T_GananciaEstimada[ time_range_vector[y] ][ this_tech ][ a ] = fair_rate

                    value_indices_d = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( technology_list_transport_techs[t] in x ) and ( 'DistanceDriven' in x ) and ( int( time_range_vector[ y ] ) in x ) ]                            
                    data_index_d =  value_indices_d[0]
                    driven_distance = float( assorted_data_dicts_i['t'][ data_index_d ][-1] )

                    # NOTE: here the *capital cost* reflects the CIF
                    value_index = [i for i, x in enumerate( assorted_capital_cost ) if ( technology_list_transport_techs[t] in x ) and ( time_range_vector[y] in x ) ]
                    data_index = value_index[0]
                    cif_value = (10**6)*float( assorted_capital_cost[ data_index ][-1] )*driven_distance/(10**9) # in USD / unit, from OSEMOSYS

                    component_1 = cif_value*import_relative_cif
                    component_2 = deepcopy( df_Unit_T_DerechoArancelario[ time_range_vector[y] ][ this_tech ][ a ] )
                    component_3 = deepcopy( df_Unit_T_ValorAduanero[ time_range_vector[y] ][ this_tech ][ a ] )
                    component_4 = deepcopy( df_Unit_T_SelectivoAlConsumo[ time_range_vector[y] ][ this_tech ][ a ] )
                    component_sum = component_1+component_2+component_3+component_4
                    component_2_to_4 = component_2+component_3+component_4

                    raw_iva_unit_rate = ( rate/100 )*( ( 1+fair_rate/100 )*( component_1 ) + component_2 + component_3 + component_4 )

                    if ( time_range_vector[y] < 2023 ) and ( ( 'ELE' in this_tech ) or ( 'HYD' in this_tech ) ):
                        # VAT EXONERATIONS for EVs HERE
                        if component_1 <= 30000:
                            # df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = ( rate/100 )*( 1+fair_rate/100 )*( component_sum )*0
                            df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = raw_iva_unit_rate*0
                        if component_1 > 30000 and component_1 <= 45000:
                            # df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = ( rate/100 )*( 1+fair_rate/100 )*( component_sum )*0.5
                            df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = raw_iva_unit_rate*0.5
                        if component_1 > 45000 and component_1 <= 60000:
                            # df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = ( rate/100 )*( 1+fair_rate/100 )*( component_sum )*1
                            df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = raw_iva_unit_rate*1
                        if component_1 > 60000:
                            # df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = ( rate/100 )*( 1+fair_rate/100 )*( component_sum )*1
                            df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = raw_iva_unit_rate*1
                    else:
                        # df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = ( rate/100 )*( 1+fair_rate/100 )*( component_sum )
                        df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = raw_iva_unit_rate

                    # df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] = ( rate/100 )*( 1+fair_rate/100 )*( component_sum )
                    df_Unit_T_GananciaEstimada[ time_range_vector[y] ][ this_tech ][ a ] = ( fair_rate/100 )*( component_sum )
                    df_Unit_T_TotalTaxes[ time_range_vector[y] ][ this_tech ][ a ] = deepcopy( df_Unit_T_ImportVAT[ time_range_vector[y] ][ this_tech ][ a ] ) + component_2_to_4
                    df_Unit_T_MarketPrice[ time_range_vector[y] ][ this_tech ][ a ] = ( 1+rate/100 )*( ( 1+fair_rate/100 )*( component_1) + component_2 + component_3 + component_4 )
                    df_Unit_T_CIF[ time_range_vector[y] ][ this_tech ][ a ] = deepcopy( component_1 )

        '''
        # Action 2: Let's call the tables to consider the effects of depreciation on the property tax, as well as the scales.
        '''
        print('Initial Part - Performing FCM_4.c - Estimating Fleet per Year and Age, as well as Fiscal Value with Depreciation')
        # Call the applicable method of property tax per technology, and also the growth rate:
        # already open

        # Now, we define the 'dict_Rates_T_PropertyTax' dataframe for use in the system year by year:
        dict_Rates_T_PropertyTax_query = {} # a dictionary of dictionaries lead by the years
        for y in range( len( time_range_vector ) ):
            dict_Rates_T_PropertyTax_query.update( { time_range_vector[y]:deepcopy( dict_property_tax_fiscal_value_scales ) } )
            for a_scale in range( len( df_Property_Tax_Ranges_columns_scales ) ):
                this_scale = df_Property_Tax_Ranges_columns_scales[ a_scale ]
                if y == 0:
                    dict_Rates_T_PropertyTax_query[ time_range_vector[y] ][this_scale]['Min'] = dict_Rates_T_PropertyTax_query[ time_range_vector[y] ][this_scale]['Min']/float( list_ER[y] )
                    dict_Rates_T_PropertyTax_query[ time_range_vector[y] ][this_scale]['Max'] = dict_Rates_T_PropertyTax_query[ time_range_vector[y] ][this_scale]['Max']/float( list_ER[y] )
                else:
                    dict_Rates_T_PropertyTax_query[ time_range_vector[y] ][this_scale]['Min'] = ( 1 + ( factor_Property_Growth/100 ) )*dict_Rates_T_PropertyTax_query[ time_range_vector[y-1] ][this_scale]['Min']*float( list_ER[y-1] )/float( list_ER[y] )
                    dict_Rates_T_PropertyTax_query[ time_range_vector[y] ][this_scale]['Max'] = ( 1 + ( factor_Property_Growth/100 ) )*dict_Rates_T_PropertyTax_query[ time_range_vector[y-1] ][this_scale]['Max']*float( list_ER[y-1] )/float( list_ER[y] )

                if this_scale == 'Scale 0':
                    dict_Rates_T_PropertyTax_query[time_range_vector[y]][this_scale]['Rate'] = dict_Rates_T_PropertyTax_query[time_range_vector[y]][this_scale]['Rate']/float( list_ER[y] )

        # Fourth, we take the list of dataframes of market price and define a value for each year within the window 
        fiscal_value_perTech_perYear_per_age = {} # perTech means it is also assorted by cohort.
        fiscal_value_perTech_perYear_per_age_weights = {}
        fleet_Q_perTech_perYear_per_age = {}
        fleet_Q_perTech_perYear_per_nationalization = {}
        fleet_Q_perTech_perYear_per_age_imports = {}

        for t in range( len( technology_list_transport_techs ) ):
            this_tech = technology_list_transport_techs[t]
            fiscal_value_perTech_perYear_per_age.update( { this_tech:{} } )
            fiscal_value_perTech_perYear_per_age_weights.update( { this_tech:{} } )
            fleet_Q_perTech_perYear_per_age.update( { this_tech:{} } )
            fleet_Q_perTech_perYear_per_nationalization.update( { this_tech:{} } )
            fleet_Q_perTech_perYear_per_age_imports.update( { this_tech:{} } )

            value_index_op = [i for i, x in enumerate( assorted_operational_life ) if ( this_tech in x ) ]
            data_index_op = value_index_op[0]
            this_tech_op_life = float( assorted_operational_life[ data_index_op ][-1] )

            list_ages = list( dict_cif_distribution[ this_tech ].keys() )
            list_ages = [ i for i in list_ages if type(i) == int ]
            list_ages.sort()

            for y in range( len( time_range_vector ) ):
                fiscal_value_perTech_perYear_per_age[ this_tech ].update( { time_range_vector[y]:{} } )
                fiscal_value_perTech_perYear_per_age_weights[ this_tech ].update( { time_range_vector[y]:{} } )
                fleet_Q_perTech_perYear_per_age[ this_tech ].update( { time_range_vector[y]:{} } )
                fleet_Q_perTech_perYear_per_nationalization[ this_tech ].update( { time_range_vector[y]:{} } )
                fleet_Q_perTech_perYear_per_age_imports[ this_tech ].update( { time_range_vector[y]:{} } )
                # fill with a zero whatever should be related to imports
                for a in list_ages:
                    fiscal_value_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ].update( { a:0 } )
                    fiscal_value_perTech_perYear_per_age_weights[ this_tech ][ time_range_vector[y] ].update( { a:0 } )
                    fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ].update( { a:0 } )
                    fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ].update( { a:0 } )

                    fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y] ].update( { a:{ 0:0, 1:0, 2:0, 3:0, 4:0 } } )
                    fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y] ].update( { a+1:{ 0:0, 1:0, 2:0, 3:0, 4:0 } } )
                    fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y] ].update( { a+2:{ 0:0, 1:0, 2:0, 3:0, 4:0 } } )
                    fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y] ].update( { a+3:{ 0:0, 1:0, 2:0, 3:0, 4:0 } } )
                    fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y] ].update( { a+4:{ 0:0, 1:0, 2:0, 3:0, 4:0 } } )

            # Let's soften the imports curve, in order to make the results less bumpy:
            this_tech_new_fleet_vector = [ 0 ]
            for y in range( 1, len( time_range_vector ) ):
                value_indices_imports = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( this_tech in x ) and ( 'NewFleet' in x ) and ( int( time_range_vector[y] ) in x ) ]
                value_indices_distance = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( this_tech in x ) and ( 'DistanceDriven' in x ) and ( int( time_range_vector[y] ) in x ) ]

                if len(value_indices_imports) != 0 and len(value_indices_distance) != 0:
                    data_index_imports =  value_indices_imports[0]
                    this_model_imports_activity_value = float( assorted_data_dicts['t'][ data_index_imports ][-1] )
                    this_new_fleet_value = this_model_imports_activity_value
                else:
                    this_new_fleet_value = 0

                this_tech_new_fleet_vector.append( this_new_fleet_value )

            this_tech_new_fleet_vector_smooth = soften_imports( this_tech_new_fleet_vector )

            for y in range( len( time_range_vector ) ):
                value_indices_imports = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( this_tech in x ) and ( 'NewFleet' in x ) and ( int( time_range_vector[y] ) in x ) ]
                value_indices_capacity = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( this_tech in x ) and ( 'TotalCapacityAnnual' in x ) and ( int( time_range_vector[y] ) in x ) ]
                value_indices_residual = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( this_tech in x ) and ( 'ResidualCapacity' in x ) and ( int( time_range_vector[y] ) in x ) ]
                value_indices_distance = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( this_tech in x ) and ( 'DistanceDriven' in x ) and ( int( time_range_vector[y] ) in x ) ]

                this_new_fleet_value = this_tech_new_fleet_vector_smooth[y]

                if len(value_indices_capacity) != 0 and len(value_indices_distance) != 0:
                    data_index_total =  value_indices_capacity[0]
                    this_model_total_activity_value = float( assorted_data_dicts['t'][ data_index_total ][-1] )
                    data_index_distance = value_indices_distance[0]
                    this_model_distance_value = float( assorted_data_dicts_i['t'][ data_index_distance ][-1] )
                    this_total_fleet_value = (10**9) * this_model_total_activity_value / this_model_distance_value
                else:
                    this_total_fleet_value = 0

                if len(value_indices_residual) != 0 and len(value_indices_distance) != 0:
                    data_index_residual =  value_indices_residual[0]
                    this_model_residual_activity_value = float( assorted_data_dicts_i['t'][ data_index_residual ][-1] )
                    data_index_distance = value_indices_distance[0]
                    this_model_distance_value = float( assorted_data_dicts_i['t'][ data_index_distance ][-1] )
                    this_residual_fleet_value = (10**9) * this_model_residual_activity_value / this_model_distance_value
                else:
                    this_residual_fleet_value = 0

                if y > 0:  # extract the previous rate
                    value_indices_capacity_prev = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( this_tech in x ) and ( 'TotalCapacityAnnual' in x ) and ( int( time_range_vector[y-1] ) in x ) ]
                    value_indices_residual_prev = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( this_tech in x ) and ( 'ResidualCapacity' in x ) and ( int( time_range_vector[y-1] ) in x ) ]
                    value_indices_distance_prev = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( this_tech in x ) and ( 'DistanceDriven' in x ) and ( int( time_range_vector[y-1] ) in x ) ]

                    if len(value_indices_capacity_prev) != 0 and len(value_indices_distance_prev) != 0:
                        data_index_total =  value_indices_capacity_prev[0]
                        this_model_total_activity_value = float( assorted_data_dicts['t'][ data_index_total ][-1] )
                        data_index_distance = value_indices_distance_prev[0]
                        this_model_distance_value = float( assorted_data_dicts_i['t'][ data_index_distance ][-1] )
                        this_total_fleet_value_prev = (10**9) * this_model_total_activity_value / this_model_distance_value
                    else:
                        this_total_fleet_value_prev = 0

                    if len(value_indices_residual_prev) != 0 and len(value_indices_distance_prev) != 0:
                        data_index_residual =  value_indices_residual_prev[0]
                        this_model_residual_activity_value = float( assorted_data_dicts_i['t'][ data_index_residual ][-1] )
                        data_index_distance = value_indices_distance_prev[0]
                        this_model_distance_value = float( assorted_data_dicts_i['t'][ data_index_distance ][-1] )
                        this_residual_fleet_value_prev = (10**9) * this_model_residual_activity_value / this_model_distance_value
                    else:
                        this_residual_fleet_value_prev = 0

                if y > 0: # apply the iterations
                    imported_fleet = this_new_fleet_value

                    for a in list_ages:
                        import_size_dist = dict_cif_distribution[ this_tech ][ a ]
                        if import_size_dist != 0:
                            fiscal_value = df_Unit_T_MarketPrice[ time_range_vector[y] ][ this_tech ][ a ]
                        else:
                            fiscal_value = 0
                        import_size_q = imported_fleet*import_size_dist/100

                        fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ][a] += deepcopy( round( import_size_q, 4 ) )
                        # -----------------------------------------------------
                        # NECESSARY FOR EXONERATIONS:
                        fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y] ][a][0] += deepcopy( round( import_size_q, 4 ) )
                        if time_range_vector[y] <= 2049:
                            fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y]+1 ][a+1][1] += deepcopy( round( import_size_q, 4 ) )
                        if time_range_vector[y] <= 2048:
                            fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y]+2 ][a+2][2] += deepcopy( round( import_size_q, 4 ) )
                        if time_range_vector[y] <= 2047:
                            fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y]+3 ][a+3][3] += deepcopy( round( import_size_q, 4 ) )
                        if time_range_vector[y] <= 2046:
                            fleet_Q_perTech_perYear_per_nationalization[ this_tech ][ time_range_vector[y]+4 ][a+4][4] += deepcopy( round( import_size_q, 4 ) )
                        # -----------------------------------------------------
                        for ol in range( int( this_tech_op_life ) + 1 ): # This propagates the existance of the fleet for the rest of the years
                            if time_range_vector[y] + ol <= time_range_vector[-1]:

                                if a+ol in list( fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y]+ol ].keys() ):
                                    fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y]+ol ][a+ol] += deepcopy( round( import_size_q, 4 ) )

                                else:
                                    fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y]+ol ].update( { a+ol:deepcopy( round( import_size_q, 4 ) ) } )
                                    fiscal_value_perTech_perYear_per_age_weights[ this_tech ][ time_range_vector[y]+ol ].update( { a+ol:0 } )
                                    fiscal_value_perTech_perYear_per_age[ this_tech ][ time_range_vector[y]+ol ].update( { a+ol:0 } )

                                age = a+ol
                                if age > 0 and age <= table_depreciation_age[-1]:
                                    old_depreciation_multiplier_index = table_depreciation_age.index( age-1 )
                                    new_depreciation_multiplier_index = table_depreciation_age.index( age )
                                    old_depreciation_multiplier = table_depreciation_factor[ old_depreciation_multiplier_index ]
                                    new_depreciation_multiplier = table_depreciation_factor[ new_depreciation_multiplier_index ]
                                    depreciation_factor = new_depreciation_multiplier/old_depreciation_multiplier
                                elif ( ( age > 0 and age > table_depreciation_age[-1] ) or age <= 0 ):
                                    depreciation_factor = 1

                                #try:
                                fiscal_value_perTech_perYear_per_age_weights[ this_tech ][ time_range_vector[y]+ol ][a+ol] += round( import_size_q*fiscal_value*depreciation_factor, 4 )
                                #except Exception:
                                #    print('debug')
                                #    print(age, table_depreciation_age[-1], a, ol, this_tech_op_life, this_tech, time_range_vector[y])
                                #    print(list_ages)
                                #    sys.exit()

                # establish the base and residual fleet:
                if this_tech in list( dict_residual_fleet_distribution.keys() ):
                    if bool( dict_residual_fleet_distribution[ this_tech ][ time_range_vector[y] ] ) != False:
                        list_ages_residual = list( dict_residual_fleet_distribution[ this_tech ][ time_range_vector[y] ].keys() )
                        list_ages_residual = [ i for i in list_ages_residual if type(i) == int ]
                        list_ages_residual.sort()

                        for b in list_ages_residual:
                            existing_fleet = this_residual_fleet_value*dict_residual_fleet_distribution[ this_tech ][ time_range_vector[y] ][b]/100
                            applicable_fiscal_value = dict_residual_fiscal_usd[ this_tech ][ time_range_vector[y] ][b]
                            if b in list( fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ].keys() ):
                                fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ][b] += round( existing_fleet, 4 )
                                fiscal_value_perTech_perYear_per_age_weights[ this_tech ][ time_range_vector[y] ][b] += round( existing_fleet*applicable_fiscal_value, 4 )
                            else: # means we need to add this age, as it is unprecedented
                                fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ].update( { b:round( existing_fleet, 4 ) } )
                                fiscal_value_perTech_perYear_per_age_weights[ this_tech ][ time_range_vector[y] ].update( { b:round( existing_fleet*applicable_fiscal_value , 4 ) } )

            # now code the actual fiscal values, already depreciated, based on the weighted value of the fleet: *fiscal_value_perTech_perYear_per_age_weights*
            for y in range( len( time_range_vector ) ):
                list_ages_all = list( fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ].keys() )
                for c in list_ages_all:
                    weights = fiscal_value_perTech_perYear_per_age_weights[ this_tech ][ time_range_vector[y] ][ c ]
                    fleet_size = fleet_Q_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ][ c ]
                    if fleet_size > 0:
                        fiscal_value_perTech_perYear_per_age[ this_tech ][ time_range_vector[y] ][ c ] = round( weights/fleet_size, 4 )

        df_Unit_T_PropertyTax = [ dict_Rates_T_PropertyTax_query, fiscal_value_perTech_perYear_per_age, dict_Property_Tax_Applicable, dict_ER_per_year ]

        ''' Action 3: Let's define a distributed private fleet amongst
        companies and households. '''
        select_techs_raw = params['select_techs_raw']

        results_fleet_property = pd.DataFrame( columns = params['results_fleet_columns'] )
        results_fleet_imports = pd.DataFrame( columns = params['results_fleet_columns'] )
        import_techs_list_check = list( fleet_Q_perTech_perYear_per_age_imports.keys() )
        this_dict_4_pd_v1 = {}
        this_dict_4_pd_v2 = {}
        # Now let's iterate across the techs:
        for t in range( len( select_techs_raw ) ):
            this_group = Fleet_Groups[ select_techs_raw[t] ]
            for tg in range( len( this_group ) ):
                this_tech = this_group[tg]

                for y in range( len( time_range_vector ) ):
                    query_year = time_range_vector[y]
                    fleet_per_year = fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ]
                    age_keys = list( fleet_per_year.keys() )

                    for age in age_keys:
                        this_Q = fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ][ age ]
                        this_FV = fiscal_value_perTech_perYear_per_age[ this_tech ][ query_year ][ age ]

                        this_dict_4_pd_v1.update( {'Group':select_techs_raw[t], 'Tech':this_tech, 'Year':query_year, 'Age':age, 'Q':this_Q, 'FV':this_FV } )
                        results_fleet_property = results_fleet_property.append( this_dict_4_pd_v1 , ignore_index=True )

                    if this_tech in import_techs_list_check:
                        import_fleet_per_year = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ]
                        age_imports_keys_raw = list( import_fleet_per_year.keys() )
                        age_imports_keys = [ i for i in age_imports_keys_raw if type(i) == int ]
                        for age in age_imports_keys:
                            this_Q = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ][ age ]
                            this_FV = df_Unit_T_MarketPrice[ query_year ][ this_tech ][ age ]
                            #
                            this_dict_4_pd_v2.update( {'Group':select_techs_raw[t], 'Tech':this_tech, 'Year':query_year, 'Age':age, 'Q':this_Q, 'FV':this_FV } )
                            results_fleet_imports = results_fleet_imports.append( this_dict_4_pd_v2 , ignore_index=True )

        end_distribute_fleet_time_1 = time.time()
        print( '    Mid 1 of FCM_4.d.' )
        # With the pandas structure, it is possible to perform the sorting of the system:
        select_techs = params['select_techs']
        # Create the sorting of the fleet for property:
        results_fleet_distributed = deepcopy( results_fleet_property )
        li_results_fleet_distributed = []
        results_fleet_distributed[ 'Owner' ] = [ '' for n in range( len( results_fleet_property.index.tolist() ) ) ]
        results_fleet_distributed[ 'Q_Dist' ] = [ 0 for n in range( len( results_fleet_property.index.tolist() ) ) ]
        results_fleet_distributed[ 'Q_Acum' ] = [ 0 for n in range( len( results_fleet_property.index.tolist() ) ) ]
        results_fleet_distributed[ 'Q_Actor_Share' ] = [ 0 for n in range( len( results_fleet_property.index.tolist() ) ) ]
        results_fleet_distributed[ 'Q_Actor_Dist' ] = [ 0 for n in range( len( results_fleet_property.index.tolist() ) ) ]
        results_fleet_distributed[ 'Q_Actor_Acum' ] = [ 0 for n in range( len( results_fleet_property.index.tolist() ) ) ]

        # Create the sorting of the fleet for imports:
        results_fleet_distributed_imp = deepcopy( results_fleet_imports )
        li_results_fleet_distributed_imp = []
        results_fleet_distributed_imp[ 'Owner' ] = [ '' for n in range( len( results_fleet_imports.index.tolist() ) ) ]
        results_fleet_distributed_imp[ 'Q_Dist' ] = [ 0 for n in range( len( results_fleet_imports.index.tolist() ) ) ]
        results_fleet_distributed_imp[ 'Q_Acum' ] = [ 0 for n in range( len( results_fleet_imports.index.tolist() ) ) ]
        results_fleet_distributed_imp[ 'Q_Actor_Share' ] = [ 0 for n in range( len( results_fleet_imports.index.tolist() ) ) ]
        results_fleet_distributed_imp[ 'Q_Actor_Dist' ] = [ 0 for n in range( len( results_fleet_imports.index.tolist() ) ) ]
        results_fleet_distributed_imp[ 'Q_Actor_Acum' ] = [ 0 for n in range( len( results_fleet_imports.index.tolist() ) ) ]

        for y in range( len( time_range_vector ) ):
            query_year = time_range_vector[y]
            for t in range( len( select_techs ) ):
                if 'Techs_Motos' not in select_techs[t]:
                    sh_business = share_autos[ query_year ][ 'Businesses' ]
                    sh_quintile1 = share_autos[ query_year ][ 'Households' ]*share_autos[ query_year ][ 'Q1_Households' ]/100
                    sh_quintile2 = share_autos[ query_year ][ 'Households' ]*share_autos[ query_year ][ 'Q2_Households' ]/100
                    sh_quintile3 = share_autos[ query_year ][ 'Households' ]*share_autos[ query_year ][ 'Q3_Households' ]/100
                    sh_quintile4 = share_autos[ query_year ][ 'Households' ]*share_autos[ query_year ][ 'Q4_Households' ]/100
                    sh_quintile5 = share_autos[ query_year ][ 'Households' ]*share_autos[ query_year ][ 'Q5_Households' ]/100
                else:
                    sh_business = share_motos[ query_year ][ 'Businesses' ]
                    sh_quintile1 = share_motos[ query_year ][ 'Households' ]*share_motos[ query_year ][ 'Q1_Households' ]/100
                    sh_quintile2 = share_motos[ query_year ][ 'Households' ]*share_motos[ query_year ][ 'Q2_Households' ]/100
                    sh_quintile3 = share_motos[ query_year ][ 'Households' ]*share_motos[ query_year ][ 'Q3_Households' ]/100
                    sh_quintile4 = share_motos[ query_year ][ 'Households' ]*share_motos[ query_year ][ 'Q4_Households' ]/100
                    sh_quintile5 = share_motos[ query_year ][ 'Households' ]*share_motos[ query_year ][ 'Q5_Households' ]/100
                dict_Actors_Final = {   'Businesses':sh_business, 'Q1_Households':sh_quintile1, 'Q2_Households':sh_quintile2,
                                        'Q3_Households':sh_quintile3, 'Q4_Households':sh_quintile4, 'Q5_Households':sh_quintile5 }

                if 'Techs_Motos' not in select_techs[t]:
                    imp_sh_business = share_imports_autos[ query_year ][ 'Businesses' ]
                    imp_sh_quintile1 = share_imports_autos[ query_year ][ 'Households' ]*share_imports_autos[ query_year ][ 'Q1_Households' ]/100
                    imp_sh_quintile2 = share_imports_autos[ query_year ][ 'Households' ]*share_imports_autos[ query_year ][ 'Q2_Households' ]/100
                    imp_sh_quintile3 = share_imports_autos[ query_year ][ 'Households' ]*share_imports_autos[ query_year ][ 'Q3_Households' ]/100
                    imp_sh_quintile4 = share_imports_autos[ query_year ][ 'Households' ]*share_imports_autos[ query_year ][ 'Q4_Households' ]/100
                    imp_sh_quintile5 = share_imports_autos[ query_year ][ 'Households' ]*share_imports_autos[ query_year ][ 'Q5_Households' ]/100
                else:
                    imp_sh_business = share_imports_motos[ query_year ][ 'Businesses' ]
                    imp_sh_quintile1 = share_imports_motos[ query_year ][ 'Households' ]*share_imports_motos[ query_year ][ 'Q1_Households' ]/100
                    imp_sh_quintile2 = share_imports_motos[ query_year ][ 'Households' ]*share_imports_motos[ query_year ][ 'Q2_Households' ]/100
                    imp_sh_quintile3 = share_imports_motos[ query_year ][ 'Households' ]*share_imports_motos[ query_year ][ 'Q3_Households' ]/100
                    imp_sh_quintile4 = share_imports_motos[ query_year ][ 'Households' ]*share_imports_motos[ query_year ][ 'Q4_Households' ]/100
                    imp_sh_quintile5 = share_imports_motos[ query_year ][ 'Households' ]*share_imports_motos[ query_year ][ 'Q5_Households' ]/100
                dict_Actors_Final_2 = { 'Businesses':imp_sh_business, 'Q1_Households':imp_sh_quintile1, 'Q2_Households':imp_sh_quintile2,
                                        'Q3_Households':imp_sh_quintile3, 'Q4_Households':imp_sh_quintile4, 'Q5_Households':imp_sh_quintile5 }

                this_results_fleet_year_base = results_fleet_distributed.loc[ ( results_fleet_distributed['Year'] == query_year ) & ( results_fleet_distributed['Group'].isin( select_techs[t] ) ) ]
                sum_Q = sum( this_results_fleet_year_base['Q'].tolist() )

                if sum_Q != 0:
                    results_fleet_distributed.loc[ ( results_fleet_distributed['Year'] == query_year ) & ( results_fleet_distributed['Group'].isin( select_techs[t] ) ), 'Q_Dist' ] = this_results_fleet_year_base['Q']/sum_Q
                else:
                    results_fleet_distributed.loc[ ( results_fleet_distributed['Year'] == query_year ) & ( results_fleet_distributed['Group'].isin( select_techs[t] ) ), 'Q_Dist' ] = 0

                this_results_fleet_year = results_fleet_distributed.loc[ ( results_fleet_distributed['Year'] == query_year ) & ( results_fleet_distributed['Group'].isin( select_techs[t] ) ) ]

                this_results_fleet_year_sort = this_results_fleet_year[ ['Group', 'Tech', 'Year', 'Age', 'Q', 'FV', 'Q_Dist', 'Q_Acum', 'Owner', 'Q_Actor_Share', 'Q_Actor_Dist', 'Q_Actor_Acum' ] ]
                this_results_fleet_year_sort = this_results_fleet_year_sort.sort_values(by=['FV'], ascending=False)
                this_results_fleet_year_sort = this_results_fleet_year_sort[ this_results_fleet_year_sort['FV'] >0 ]
                indx_counter, last_n = 0, 0
                for n in this_results_fleet_year_sort.index.tolist():
                    if indx_counter == 0:
                        this_results_fleet_year_sort.loc[ n, 'Q_Acum' ] = this_results_fleet_year_sort.loc[ n, 'Q_Dist' ]
                    else:
                        this_results_fleet_year_sort.loc[ n, 'Q_Acum' ] = this_results_fleet_year_sort.loc[ n, 'Q_Dist' ] + this_results_fleet_year_sort.loc[ last_n, 'Q_Acum' ]
                    indx_counter += 1
                    last_n = n

                this_results_fleet_year_sort = this_results_fleet_year_sort[this_results_fleet_year_sort.Q != 0]
                this_results_fleet_year_sort = this_results_fleet_year_sort.reset_index(drop=True)

                # Perform the actions for the 'Businesses':
                this_actor = 'Businesses'
                acopy_this_results_fleet_year_sort = deepcopy( this_results_fleet_year_sort ) # first grab
                acopy_this_results_fleet_year_sort['Owner'] = this_actor
                acopy_this_results_fleet_year_sort['Q_Actor'] = acopy_this_results_fleet_year_sort['Q']*dict_Actors_Final[ this_actor ]/100

                if sum_Q != 0:
                    acopy_this_results_fleet_year_sort['Q_Actor_Dist'] = ( acopy_this_results_fleet_year_sort['Q']*dict_Actors_Final[ this_actor ]/100 )/sum_Q
                else:
                    acopy_this_results_fleet_year_sort['Q_Actor_Dist'] = 0

                acopy_this_results_fleet_year_sort['Q_Actor_Share'] = dict_Actors_Final[ this_actor ]/100
                li_results_fleet_distributed.append( acopy_this_results_fleet_year_sort )

                # Perform the actions for other actors different of 'Businesses':
                acopy_this_results_fleet_year_sort = pd.DataFrame( columns = this_results_fleet_year_sort.columns.tolist() + ['Q_Actor'] ) # second grab
                cumulative_ladder_households = [    sh_quintile5,
                                                    sh_quintile5+sh_quintile4,
                                                    sh_quintile5+sh_quintile4+sh_quintile3,
                                                    sh_quintile5+sh_quintile4+sh_quintile3+sh_quintile2,
                                                    sh_quintile5+sh_quintile4+sh_quintile3+sh_quintile2+sh_quintile1 ]

                car_groups_q = []
                car_groups_ass = []
                for i in this_results_fleet_year_sort.index.tolist():
                    the_fleet_assign = this_results_fleet_year_sort.loc[ i, 'Q' ]*( 1 - dict_Actors_Final[ 'Businesses' ]/100 ) # this extracts the q, but we need to figure out how to assign it
                    car_groups_q.append( the_fleet_assign )
                    the_fleet_assign_share = the_fleet_assign/sum_Q
                    car_groups_ass.append( 100*the_fleet_assign_share )
                car_groups_ass_unchanged = deepcopy( car_groups_ass )

                cumulative_assignation = params['cumulative_assignation']
                household_types = params['household_types']
                last_i = 0
                for n in range( len( household_types ) ):
                    this_household_type = household_types[n]

                    if n == 0:
                        lower_bracket = 0
                    else:
                        lower_bracket =  cumulative_ladder_households[n-1]
                    upper_bracket = cumulative_ladder_households[n]

                    cum_assigned = lower_bracket

                    for i in range( last_i, len( this_results_fleet_year_sort.index.tolist() ) ):
                        stop_car_loop = False
                        finished_car_loop = False
                        if finished_car_loop == False:
                            remain_in_this_car_group = True

                        if float(car_groups_ass[i]) == 0.0: # this means the fleet is unusable
                            break

                        while remain_in_this_car_group == True:        
                            this_assign_q = deepcopy( car_groups_q[i] )
                            this_assign = deepcopy( car_groups_ass[i] )
                            this_assign_unchanged = car_groups_ass_unchanged[i]

                            if cum_assigned >= lower_bracket and cum_assigned + this_assign <= upper_bracket:
                                cum_assigned += this_assign
                                car_groups_ass[i] -= this_assign
                                store_assign = this_assign
                                store_assign_q = ( this_assign/this_assign_unchanged )*this_assign_q

                            elif cum_assigned >= lower_bracket and cum_assigned + this_assign > upper_bracket:
                                this_assign_sat = upper_bracket - cum_assigned
                                cum_assigned += this_assign_sat
                                car_groups_ass[i] -= this_assign_sat
                                store_assign = this_assign_sat
                                store_assign_q = ( this_assign_sat/this_assign_unchanged )*this_assign_q

                            if cum_assigned > lower_bracket and cum_assigned <= upper_bracket:
                                remain_in_this_car_group = False
                                finished_car_loop = True
                                if cum_assigned == upper_bracket:
                                    stop_car_loop = True
 
                        if finished_car_loop == True:
                            acopy_this_results_fleet_year_sort = acopy_this_results_fleet_year_sort.append({
                                            'Group': this_results_fleet_year_sort.loc[ i, 'Group' ],
                                            'Tech': this_results_fleet_year_sort.loc[ i, 'Tech' ],
                                            'Year': this_results_fleet_year_sort.loc[ i, 'Year' ],
                                            'Age': this_results_fleet_year_sort.loc[ i, 'Age' ],
                                            'Q': this_results_fleet_year_sort.loc[ i, 'Q' ],
                                            'FV': this_results_fleet_year_sort.loc[ i, 'FV' ],
                                            'Q_Dist': this_results_fleet_year_sort.loc[ i, 'Q_Dist' ],
                                            'Q_Acum': this_results_fleet_year_sort.loc[ i, 'Q_Acum' ],
                                            'Owner': this_household_type,
                                            'Q_Actor_Share': 0,
                                            'Q_Actor_Dist': store_assign,
                                            'Q_Actor_Acum': cum_assigned,
                                            'Q_Actor': store_assign_q # this is the proper fleet size
                            }, ignore_index=True)
                            cumulative_assignation[ this_household_type ] += store_assign

                        if stop_car_loop == True:
                            last_i = deepcopy( i )
                            break

                for n in range( len( list( cumulative_assignation.keys() ) ) ):
                    this_actor = list( cumulative_assignation.keys() )[n]
                    this_aux_df = acopy_this_results_fleet_year_sort.loc[ acopy_this_results_fleet_year_sort['Owner'] == this_actor ]
                    for i in this_aux_df.index.tolist():
                        acopy_this_results_fleet_year_sort.loc[ i, 'Q_Actor_Share' ] = cumulative_assignation[ this_actor ]

                li_results_fleet_distributed.append( acopy_this_results_fleet_year_sort )
                #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
                #########################################################################################################################################################################################
                if y > 0: # the first year does not have imports, so exclude to avoid errors
                    this_results_fleet_imp_year_base = results_fleet_distributed_imp.loc[ ( results_fleet_distributed_imp['Year'] == query_year ) & ( results_fleet_distributed_imp['Group'].isin( select_techs[t] ) ) ]
                    sum_Q = sum( this_results_fleet_imp_year_base['Q'].tolist() )

                    if sum_Q != 0:
                        results_fleet_distributed_imp.loc[ ( results_fleet_distributed_imp['Year'] == query_year ) & ( results_fleet_distributed_imp['Group'].isin( select_techs[t] ) ), 'Q_Dist' ] = this_results_fleet_imp_year_base['Q']/sum_Q
                    else:
                        results_fleet_distributed_imp.loc[ ( results_fleet_distributed_imp['Year'] == query_year ) & ( results_fleet_distributed_imp['Group'].isin( select_techs[t] ) ), 'Q_Dist' ] = 0

                    this_results_fleet_year_imp = results_fleet_distributed_imp.loc[ ( results_fleet_distributed_imp['Year'] == query_year ) & ( results_fleet_distributed_imp['Group'].isin( select_techs[t] ) ) ]

                    this_results_fleet_year_sort_imp = this_results_fleet_year_imp[ ['Group', 'Tech', 'Year', 'Age', 'Q', 'FV', 'Q_Dist', 'Q_Acum', 'Owner', 'Q_Actor_Share', 'Q_Actor_Dist', 'Q_Actor_Acum' ] ]
                    this_results_fleet_year_sort_imp = this_results_fleet_year_sort_imp.sort_values(by=['FV'], ascending=False)
                    this_results_fleet_year_sort_imp = this_results_fleet_year_sort_imp[ this_results_fleet_year_sort_imp['FV'] >0 ]
                    indx_counter = 0
                    for n in this_results_fleet_year_sort_imp.index.tolist():
                        if indx_counter == 0:
                            this_results_fleet_year_sort_imp.loc[ n, 'Q_Acum' ] = this_results_fleet_year_sort_imp.loc[ n, 'Q_Dist' ]
                        else:
                            this_results_fleet_year_sort_imp.loc[ n, 'Q_Acum' ] = this_results_fleet_year_sort_imp.loc[ n, 'Q_Dist' ] + this_results_fleet_year_sort_imp.loc[ last_n, 'Q_Acum' ]
                        indx_counter += 1
                        last_n = n

                    this_results_fleet_year_sort_imp = this_results_fleet_year_sort_imp[this_results_fleet_year_sort_imp.Q != 0]
                    this_results_fleet_year_sort_imp = this_results_fleet_year_sort_imp.reset_index(drop=True)

                    # Perform the actions for the 'Businesses':
                    this_actor = 'Businesses'
                    acopy_this_results_fleet_year_imp_sort = deepcopy( this_results_fleet_year_sort_imp ) # first grab
                    acopy_this_results_fleet_year_imp_sort['Owner'] = this_actor
                    acopy_this_results_fleet_year_imp_sort['Q_Actor'] = acopy_this_results_fleet_year_imp_sort['Q']*dict_Actors_Final_2[ this_actor ]/100

                    if sum_Q != 0:
                        acopy_this_results_fleet_year_imp_sort['Q_Actor_Dist'] = ( acopy_this_results_fleet_year_imp_sort['Q']*dict_Actors_Final_2[ this_actor ]/100 )/sum_Q
                    else:
                        acopy_this_results_fleet_year_imp_sort['Q_Actor_Dist'] = 0

                    acopy_this_results_fleet_year_imp_sort['Q_Actor_Share'] = dict_Actors_Final_2[ this_actor ]/100
                    li_results_fleet_distributed_imp.append( acopy_this_results_fleet_year_imp_sort )

                    # Perform the actions for other actors different of 'Businesses':
                    acopy_this_results_fleet_year_imp_sort = pd.DataFrame( columns = this_results_fleet_year_sort_imp.columns.tolist() + ['Q_Actor'] ) # second grab
                    cumulative_ladder_households = [    imp_sh_quintile5,
                                                        imp_sh_quintile5 + imp_sh_quintile4,
                                                        imp_sh_quintile5 + imp_sh_quintile4 + imp_sh_quintile3,
                                                        imp_sh_quintile5 + imp_sh_quintile4 + imp_sh_quintile3 + imp_sh_quintile2,
                                                        imp_sh_quintile5 + imp_sh_quintile4 + imp_sh_quintile3 + imp_sh_quintile2 + imp_sh_quintile1 ]

                    car_groups_q = []
                    car_groups_ass = []
                    for i in this_results_fleet_year_sort_imp.index.tolist():
                        the_fleet_assign = this_results_fleet_year_sort_imp.loc[ i, 'Q' ]*( 1 - dict_Actors_Final_2[ 'Businesses' ]/100 ) # this extracts the q, but we need to figure out how to assign it
                        car_groups_q.append( the_fleet_assign )
                        the_fleet_assign_share = the_fleet_assign/sum_Q
                        car_groups_ass.append( 100*the_fleet_assign_share )
                    car_groups_ass_unchanged = deepcopy( car_groups_ass )

                    cumulative_assignation = params['cumulative_assignation']
                    household_types = params['household_types']
                    last_i = 0
                    for n in range( len( household_types ) ):
                        this_household_type = household_types[n]
                        #
                        if n == 0:
                            lower_bracket = 0
                        else:
                            lower_bracket =  cumulative_ladder_households[n-1]
                        upper_bracket = cumulative_ladder_households[n]

                        cum_assigned = lower_bracket

                        for i in range( last_i, len( this_results_fleet_year_sort_imp.index.tolist() ) ):
                            stop_car_loop = False
                            finished_car_loop = False
                            if finished_car_loop == False:
                                remain_in_this_car_group = True

                            if float(car_groups_ass[i]) == 0.0: # this means the fleet is unusable
                                break

                            while remain_in_this_car_group == True:        
                                this_assign_q = deepcopy( car_groups_q[i] )
                                this_assign = deepcopy( car_groups_ass[i] )
                                this_assign_unchanged = car_groups_ass_unchanged[i]

                                if cum_assigned >= lower_bracket and cum_assigned + this_assign <= upper_bracket:
                                    cum_assigned += this_assign
                                    car_groups_ass[i] -= this_assign
                                    store_assign = this_assign
                                    store_assign_q = ( this_assign/this_assign_unchanged )*this_assign_q

                                elif cum_assigned >= lower_bracket and cum_assigned + this_assign > upper_bracket:
                                    this_assign_sat = upper_bracket - cum_assigned
                                    cum_assigned += this_assign_sat
                                    car_groups_ass[i] -= this_assign_sat
                                    store_assign = this_assign_sat
                                    store_assign_q = ( this_assign_sat/this_assign_unchanged )*this_assign_q

                                if cum_assigned > lower_bracket and cum_assigned <= upper_bracket:
                                    remain_in_this_car_group = False
                                    finished_car_loop = True
                                    if cum_assigned == upper_bracket:
                                        stop_car_loop = True
  
                            if finished_car_loop == True:
                                acopy_this_results_fleet_year_imp_sort = acopy_this_results_fleet_year_imp_sort.append({
                                                'Group': this_results_fleet_year_sort_imp.loc[ i, 'Group' ],
                                                'Tech': this_results_fleet_year_sort_imp.loc[ i, 'Tech' ],
                                                'Year': this_results_fleet_year_sort_imp.loc[ i, 'Year' ],
                                                'Age': this_results_fleet_year_sort_imp.loc[ i, 'Age' ],
                                                'Q': this_results_fleet_year_sort_imp.loc[ i, 'Q' ],
                                                'FV': this_results_fleet_year_sort_imp.loc[ i, 'FV' ],
                                                'Q_Dist': this_results_fleet_year_sort_imp.loc[ i, 'Q_Dist' ],
                                                'Q_Acum': this_results_fleet_year_sort_imp.loc[ i, 'Q_Acum' ],
                                                'Owner': this_household_type,
                                                'Q_Actor_Share': 0,
                                                'Q_Actor_Dist': store_assign,
                                                'Q_Actor_Acum': cum_assigned,
                                                'Q_Actor': store_assign_q # this is the proper fleet size
                                }, ignore_index=True)
                                cumulative_assignation[ this_household_type ] += store_assign

                            if stop_car_loop == True:
                                last_i = deepcopy( i )
                                break

                    for n in range( len( list( cumulative_assignation.keys() ) ) ):
                        this_actor = list( cumulative_assignation.keys() )[n]
                        this_aux_df = acopy_this_results_fleet_year_imp_sort.loc[ acopy_this_results_fleet_year_imp_sort['Owner'] == this_actor ]
                        for i in this_aux_df.index.tolist():
                            acopy_this_results_fleet_year_imp_sort.loc[ i, 'Q_Actor_Share' ] = cumulative_assignation[ this_actor ]

                    li_results_fleet_distributed_imp.append( acopy_this_results_fleet_year_imp_sort )
                    # ---------------------------------------------------------

        df_results_fleet_distributed = pd.concat(li_results_fleet_distributed, axis=0, ignore_index=True)
        df_results_fleet_distributed_imp = pd.concat(li_results_fleet_distributed_imp, axis=0, ignore_index=True)

        df_distributed = df_results_fleet_distributed[ params['df_distributed'] ]
        df_distributed_imp = df_results_fleet_distributed_imp[ params['df_distributed'] ]

        tech_list_owner = list( set( df_distributed['Owner'].tolist() ) )
        tech_list_owner.sort()

        fleet_Q_per_actor_perTech_perYear_per_age = {}
        fleet_Q_per_actor_perTech_perYear_per_age_share = {}
        fleet_Q_per_actor_perTech_perYear_share = {}

        fleet_Q_per_actor_perTech_perYear_per_age_imp = {}
        fleet_Q_per_actor_perTech_perYear_per_age_imp_share = {}

        df_distributed_clean = df_distributed.loc[ ( df_distributed['Q_Actor'] != 0 ) ]
        df_distributed_clean_imp = df_distributed_imp.loc[ ( df_distributed_imp['Q_Actor'] != 0 ) ]

        for o in range( len( tech_list_owner ) ):
            this_owner = tech_list_owner[o]

            this_df_owner = df_distributed_clean.loc[ ( df_distributed_clean['Owner'] == this_owner ) ]
            fleet_Q_per_actor_perTech_perYear_per_age.update( { this_owner:{} } )
            fleet_Q_per_actor_perTech_perYear_per_age_share.update( { this_owner:{} } )
            fleet_Q_per_actor_perTech_perYear_share.update( { this_owner:{} } )

            this_tech_list = list( set( this_df_owner['Tech'].tolist() ) ) 

            for t in range( len( this_tech_list ) ):
                this_tech = this_tech_list[t]
                this_df_tech = this_df_owner.loc[ ( this_df_owner['Tech'] == this_tech ) ]
                fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ].update( { this_tech:{} } )
                fleet_Q_per_actor_perTech_perYear_per_age_share[ this_owner ].update( { this_tech:{} } )
                fleet_Q_per_actor_perTech_perYear_share[ this_owner ].update( { this_tech:{} } )

                this_year_list = list( set( this_df_tech['Year'].tolist() ) )

                for y in range( len( this_year_list ) ):
                    this_year = this_year_list[y]
                    this_df_year = this_df_tech.loc[ ( this_df_tech['Year'] == this_year ) ]
                    fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ][ this_tech ].update( { this_year:{} } )
                    fleet_Q_per_actor_perTech_perYear_per_age_share[ this_owner ][ this_tech ].update( { this_year:{} } )

                    this_age_list = list( set( this_df_year['Age'].tolist() ) )

                    this_q_actor_sum = sum( this_df_year['Q_Actor'].tolist() )
                    this_q_total_sum = sum( df_distributed.loc[ ( df_distributed['Tech']==this_tech ) & ( df_distributed['Year']==this_year ), 'Q_Actor' ].tolist() )
                    fleet_Q_per_actor_perTech_perYear_share[ this_owner ][ this_tech ].update( { this_year:this_q_actor_sum/this_q_total_sum } )

                    for a in range( len( this_age_list ) ):
                        this_age = this_age_list[a]
                        this_df_age = this_df_year.loc[ ( this_df_year['Age'] == this_age ) ]

                        this_q_actor = sum( this_df_age['Q_Actor'].tolist() )
                        this_q_total = sum( df_distributed.loc[ ( df_distributed['Tech']==this_tech ) & ( df_distributed['Year']==this_year ) & ( df_distributed['Age']==this_age ), 'Q_Actor' ].tolist() )

                        fleet_Q_per_actor_perTech_perYear_per_age[ this_owner ][ this_tech ][ this_year ].update( { this_age:this_q_actor } )
                        fleet_Q_per_actor_perTech_perYear_per_age_share[ this_owner ][ this_tech ][ this_year ].update( { this_age:this_q_actor/this_q_total } )
            #--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
            this_df_owner = df_distributed_clean_imp.loc[ ( df_distributed_clean_imp['Owner'] == this_owner ) ]
            fleet_Q_per_actor_perTech_perYear_per_age_imp.update( { this_owner:{} } )
            fleet_Q_per_actor_perTech_perYear_per_age_imp_share.update( { this_owner:{} } )

            this_tech_list = list( set( this_df_owner['Tech'].tolist() ) ) 

            for t in range( len( this_tech_list ) ):
                this_tech = this_tech_list[t]
                this_df_tech = this_df_owner.loc[ ( this_df_owner['Tech'] == this_tech ) ]
                fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_owner ].update( { this_tech:{} } )
                fleet_Q_per_actor_perTech_perYear_per_age_imp_share[ this_owner ].update( { this_tech:{} } )

                this_year_list = list( set( this_df_tech['Year'].tolist() ) )

                for y in range( len( this_year_list ) ):
                    this_year = this_year_list[y]
                    this_df_year = this_df_tech.loc[ ( this_df_tech['Year'] == this_year ) ]
                    fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_owner ][ this_tech ].update( { this_year:{} } )
                    fleet_Q_per_actor_perTech_perYear_per_age_imp_share[ this_owner ][ this_tech ].update( { this_year:{} } )

                    this_age_list = list( set( this_df_year['Age'].tolist() ) )

                    for a in range( len( this_age_list ) ):
                        this_age = this_age_list[a]
                        this_df_age = this_df_year.loc[ ( this_df_year['Age'] == this_age ) ]

                        this_q_actor = sum( this_df_age['Q_Actor'].tolist() )
                        this_q_total = sum( df_distributed_imp.loc[ ( df_distributed_imp['Tech']==this_tech ) & ( df_distributed_imp['Year']==this_year ) & ( df_distributed_imp['Age']==this_age ), 'Q_Actor' ].tolist() )

                        fleet_Q_per_actor_perTech_perYear_per_age_imp[ this_owner ][ this_tech ][ this_year ].update( { this_age:this_q_actor } )
                        fleet_Q_per_actor_perTech_perYear_per_age_imp_share[ this_owner ][ this_tech ][ this_year ].update( { this_age:this_q_actor/this_q_total } )

        end_distribute_fleet_time_2 = time.time()
        time_elapsed_distribute_fleet_2 = -end_distribute_fleet_time_1 + end_distribute_fleet_time_2

        print( '    Mid 2 of FCM_4.d - it took: ' + str( time_elapsed_distribute_fleet_2/60 ) + ' minutes to create the sorted dictionary' )
        unique_owner = tech_list_owner # already defined as *tech_list_owner*

        print( '    Ending FCM_4.d')

        print('Initial Part - Performing FCM_4.e - Storing and printing variables from middle-of-the-process')
        # This is essential for the automated calculation of expenses:
        assorted_data_dicts['fleet'] = deepcopy( [  fleet_Q_perTech_perYear_per_age, fleet_Q_perTech_perYear_per_age_imports, unique_owner, 
                                                    fleet_Q_per_actor_perTech_perYear_per_age, '',
                                                    fleet_Q_per_actor_perTech_perYear_per_age_imp, '',
                                                    fleet_Q_per_actor_perTech_perYear_share,
                                                    share_consumption_buses, share_consumption_taxis,
                                                    fleet_Q_perTech_perYear_per_nationalization ] )

        ''' ############################################################### '''
        # Procedure: we must bring the rates we know into the program.
        # The rates are in colones for fuels or in % for electricity.
        for i in range(len(time_range_vector)):
            # A change function can be added to the rates in this section
            df_Rates_TF_SalesPurchasesEnergy[time_range_vector[i]] = \
                df_Rates_TF_SalesPurchasesEnergy['Factor']

        # Store fuel prices // electricity and H2 prices are stored below
        for y in range( len( time_range_vector ) ):
            # A change function can be added to the rates in this section
            for t in range( len( df_Rates_TF_SalesPurchasesEnergy[ 'Technology' ].tolist() ) ):
                this_fuel = df_Rates_TF_SalesPurchasesEnergy[ 'Fuel' ].tolist()[t]

                if 'ELE' in this_fuel or 'HYD' in this_fuel:
                    rate = 0
                else:
                    rate = float( deepcopy( df_Rates_TF_SalesPurchasesEnergy.loc[t,time_range_vector[y]] ) )

                if rate != 0:
                    if 'DSL' in this_fuel:
                        this_tech = 'DIST_DSL'
                    elif 'GSL' in this_fuel:
                        this_tech = 'DIST_GSL'
                    elif 'LPG' in this_fuel:
                        this_tech = 'DIST_LPG'

                    if 'ELE' in this_fuel or 'HYD' in this_fuel:
                        pass
                    else:
                        value_index = [i for i, x in enumerate( assorted_variable_cost ) if ( this_tech in x ) and ( time_range_vector[y] in x ) ]
                        data_index = value_index[0]
                        df_Rates_TF_SalesPurchasesEnergy.loc[ t , time_range_vector[y] ] = (rate) * float( assorted_variable_cost[ data_index ][-1] ) # $*$ makes price for consumer be proportional to cost of imported fuel 

        for i in range(len(time_range_vector)):
            # A change function can be added to the rates in this section
            df_Rates_TF_TaxEnergy[time_range_vector[i]] = \
                df_Rates_TF_TaxEnergy['Factor']

        df_Rates_TF_IUC = deepcopy(df_Rates_TF_TaxEnergy
                                .loc[df_Rates_TF_TaxEnergy['Tax_Type'] ==
                                'Unique_Fuel_Tax'])
        df_Rates_TF_IUC.reset_index(inplace = True)
        df_Unit_TF_IUC = deepcopy(df_Rates_TF_IUC)

        grab_the_techs_IUC = df_Rates_TF_IUC['Technology'].tolist()
        _provisional_input_growth_limits_of_IUC = 0 # $*$ THIS IS AN INPUT
        for t in range( len( grab_the_techs_IUC ) ):
            # Define the conversion factor from L to PJ:
            # http://w.astro.berkeley.edu/~wright/fuel_energy.html
    
            # $*$ Here we pick automotive-type diesel
            if 'DSL' in grab_the_techs_IUC[t]:
                from_L_to_PJ = 38.6*(1e-9) # MJ/l * PJ/MJ = PJ/L
            # $*$ Here we pick automotive-type gasoline
            elif 'GSL' in grab_the_techs_IUC[t]:
                from_L_to_PJ = 34.2*(1e-9) # MJ/l * PJ/MJ = PJ/L
            # $*$ We will use a mixture of propane and butane
            elif 'LPG' in grab_the_techs_IUC[t]:
                from_L_to_PJ = 25.7*(1e-9) # MJ/l * PJ/MJ = PJ/L
    
            # this makes the system start after the initial year
            for y in range(0, len(time_range_vector)):
                if y > 0:
                    previous_value = \
                        deepcopy(df_Rates_TF_IUC
                                 .loc[t, time_range_vector[y-1]])
                    df_Rates_TF_IUC.loc[ t, time_range_vector[y] ] = \
                        previous_value \
                        * (1 + _provisional_input_growth_limits_of_IUC/100)
    
                # Conversion logic: (Colon/L)/(Colon/$) = $/l,
                # then ($/l)/(PJ/L) = $/PJ, then ($/PJ)*(1 M$/ 1e6 $) = 1 M$/PJ
                df_Unit_TF_IUC.loc[t, time_range_vector[y]] = \
                    (df_Rates_TF_IUC.loc[t, time_range_vector[y]]/ \
                    float(list_ER[y]))/( from_L_to_PJ )*(1/1e6)
    
        df_Rates_TF_IUC = deepcopy( df_Rates_TF_IUC.drop(columns=['Factor']) )
        df_Unit_TF_IUC = deepcopy( df_Unit_TF_IUC.drop(columns=['Factor']) )

        '''
        # Action 4: Let's call the TaxEnergy.csv table to differentiate the electricity VAT from the "Fuel Tax".
        # CRUCIAL NOTE: The market price of electricity must be calculated first
        '''
        # FCM_5 - Estimate electricity price:
        print('Initial Part - Performing FCM_5 - Estimating Electricity Price')
        # Electricity price analysis:
        power_plants_techs = params['power_plants_techs']
        fossil_power_plants = params['fossil_power_plants']

        electricity_related_techs = \
            power_plants_techs + params['electricity_related_techs']

        ElectricityPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_variable_cost_vector = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_generated_electricity = [ 0 for y in range( len(time_range_vector) ) ]

        for y in range( len( time_range_vector ) ):

            electricity_production = 0
            for elec_techs in range( len( power_plants_techs ) ):
                elec_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( power_plants_techs[elec_techs] in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

                this_electricity_production = 0
                if len(elec_tech_indices) != 0:
                    for n in range(len(elec_tech_indices)):
                        elec_tech_index =  elec_tech_indices[n]
                        this_electricity_production += float( assorted_data_dicts['t_f'][ elec_tech_index ][-1] )  # of 'power_plants'
                else:
                    this_electricity_production += 0

                electricity_production += this_electricity_production

            new_investments = 0
            for elec_techs in range( len( electricity_related_techs ) ):
                elec_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( electricity_related_techs[elec_techs] in x ) and ( int( float( time_range_vector[y] ) ) in x ) and ( 'CapitalInvestment' in x ) ]

                if len(elec_tech_indices) != 0:
                    elec_tech_index =  elec_tech_indices[0]
                    this_electricity_invesmtens = float( assorted_data_dicts['t'][ elec_tech_index ][-1] ) # of 'power_plants'
                else:
                    this_electricity_invesmtens = 0
                new_investments += this_electricity_invesmtens

            technical_variable_cost = 0
            for t in range( len( fossil_power_plants ) ):
                fpp_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( fossil_power_plants[t] in x ) and ( time_range_vector[y] in x ) and ( 'UseByTechnology' in x ) ]
                if len(fpp_techs_indices) != 0:
                    for n in range( len( fpp_techs_indices ) ):
                        fpp_tech_index =  fpp_techs_indices[n]
                        this_fpp_fuel_consumption = float( assorted_data_dicts['t_f'][ fpp_tech_index ][-1] ) # of 'power plant' in PJ
                        this_fpp_fuel = assorted_data_dicts['t_f'][ fpp_tech_index ][1] # the fuels

                        if fossil_power_plants[t] in df_Unit_TF_IUC['Technology'].tolist() and this_fpp_fuel in df_Unit_TF_IUC['Fuel'].tolist():
                            df_Unit_Tax = deepcopy( df_Unit_TF_IUC )

                        tech_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Technology'].tolist() ) if element == fossil_power_plants[t] ]
                        fuel_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Fuel'].tolist() ) if element == this_fpp_fuel ]
                        tax_index = list( set(tech_indices_tax) & set(fuel_indices_tax) )[0]

                        df_Unit_Price = deepcopy( df_Rates_TF_SalesPurchasesEnergy )
                        tech_indices_price = [index for index, element in enumerate( df_Unit_Price['Technology'].tolist() ) if element == fossil_power_plants[t] ]
                        fuel_indices_price = [index for index, element in enumerate( df_Unit_Price['Fuel'].tolist() ) if element == this_fpp_fuel ]
                        price_index = list( set(tech_indices_price) & set(fuel_indices_price) )[0]

                        unit_fuel_cost = df_Unit_Tax.loc[ tax_index, time_range_vector[y] ] + df_Unit_Price.loc[ price_index, time_range_vector[y] ] # per PJ cost
                        technical_variable_cost += unit_fuel_cost * this_fpp_fuel_consumption

            ElectricityPrice_variable_cost_vector[y] = technical_variable_cost

            new_FOM = 0
            for elec_techs in range( len( electricity_related_techs ) ):
                elec_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( electricity_related_techs[elec_techs] in x ) and ( int( float( time_range_vector[y] ) ) in x ) and ( 'AnnualFixedOperatingCost' in x ) ]
                #
                if len(elec_tech_indices) != 0:
                    elec_tech_index =  elec_tech_indices[0]
                    this_electricity_FOM = float( assorted_data_dicts['t'][ elec_tech_index ][-1] ) # of 'power_plants'
                else:
                    this_electricity_FOM = 0
                new_FOM += this_electricity_FOM

            # annualized_new_investments = ( new_investments / ( ( 1+0.05 )**( y ) ) )*0.05*1/( 1-(1+0.05)**(-50) # (see https://www.wallstreetmojo.com/annuity-formula/ for 50 yrs at 5%)
            # annualized_new_investments = new_investments * 0.05 / ( 1 - (1+0.05)**(-50) )

            annualized_new_investments = new_investments * 0.06 / ( 1 - (1+0.06)**(-25) )
            ElectricityPrice_new_investments[y] = new_investments
            for fill_y in range( y, len( time_range_vector ) ):
                ElectricityPrice_annualized_new_investments_vector[fill_y] += annualized_new_investments

            ElectricityPrice_fom_vector[y] = new_FOM
            ElectricityPrice_generated_electricity[y] = electricity_production

        # THE AVERAGE BASE PRICE IS GOING TO BE 88.9 COLONES/KWH @ 575 COLONES / USD THAT GIVES 0.1546 USD / KWH w/o TAXES
        ElectricityPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_for_new = [ 0 for y in range( len(time_range_vector) ) ]
        ElectricityPrice_for_old = [ 0 for y in range( len(time_range_vector) ) ]
        # Conversion logic: ($/kWh)*(kWh/PJ) = $/PJ, then ($/PJ)*(1 M$/ 1e6 $) = 1 M$/PJ
        F = ElectricityPrice_generated_electricity[0] * 0.1546 * (2.778e8/1) * (1/1e6) # factor for $/kWh to MUSD/PJ
        for y in range( 0, len( time_range_vector ) ):
            ElectricityPrice_for_new[y] = ( ElectricityPrice_variable_cost_vector[y] + ElectricityPrice_fom_vector[y] + ElectricityPrice_annualized_new_investments_vector[y] ) / ElectricityPrice_generated_electricity[y]
            ElectricityPrice_for_old[y] = ( F - ElectricityPrice_for_new[0]*ElectricityPrice_generated_electricity[0] ) / ElectricityPrice_generated_electricity[y]
            ElectricityPrice_vector[y] = ElectricityPrice_for_old[y] + ElectricityPrice_for_new[y]

        # FCM_5.b. - Estimate disaggregated power plant costs:
        lcoe_per_pp = disag_lcoe_pp(assorted_data_dicts, time_range_vector, params)

        # FCM_5.c. - Estimate hydrogen price:
        print('Initial Part - Performing FCM_5.b. - Estimating Hydrogen Price')
        # Hydrogen price analysis:
        hydrogen_input_tech = params['hydrogen_input_tech']
        hyd_2_pp_dict = params['hyd_2_pp_dict']

        hydrogen_output_tech = params['hydrogen_output_tech']

        hydrogen_cost_techs = params['hydrogen_cost_techs']

        HydrogenPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
        HydrogenPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
        HydrogenPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
        HydrogenPrice_variable_cost_vector = [ 0 for y in range( len(time_range_vector) ) ]
        HydrogenPrice_generated_H2 = [ 0 for y in range( len(time_range_vector) ) ]

        for y in range( len( time_range_vector ) ):
            hydrogen_production = 0
            for hyd_techs in range( len( hydrogen_output_tech ) ):
                hyd_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( hydrogen_output_tech[hyd_techs] in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

                if len(hyd_techs_indices) != 0:
                    hyd_tech_index = hyd_techs_indices[0]
                    this_hyd_production = float( assorted_data_dicts['t_f'][ hyd_tech_index ][-1] ) # of 'power_plants'
                else:
                    this_hyd_production = 0

                hydrogen_production += this_hyd_production

            new_investments = 0
            for hyd_techs in range( len( hydrogen_cost_techs ) ):
                hyd_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( hydrogen_cost_techs[hyd_techs] in x ) and ( int( float( time_range_vector[y] ) ) in x ) and ( 'CapitalInvestment' in x ) ]

                if len(hyd_techs_indices) != 0:
                    hyd_tech_index =  hyd_techs_indices[0]
                    this_hydrogen_invesmtens = float( assorted_data_dicts['t'][ hyd_tech_index ][-1] )
                else:
                    this_hydrogen_invesmtens = 0
                new_investments += this_hydrogen_invesmtens

            new_FOM = 0
            for hyd_techs in range( len( hydrogen_cost_techs ) ):
                hyd_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( hydrogen_cost_techs[hyd_techs] in x ) and ( int( float( time_range_vector[y] ) ) in x ) and ( 'AnnualFixedOperatingCost' in x ) ]

                if len(hyd_techs_indices) != 0:
                    hyd_tech_index =  hyd_techs_indices[0]
                    this_hydrogen_FOM = float( assorted_data_dicts['t'][ hyd_tech_index ][-1] )
                else:
                    this_hydrogen_FOM = 0
                new_FOM += this_hydrogen_FOM

            technical_variable_cost = 0
            for t in range( len( hydrogen_input_tech ) ):
                hyd_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( hydrogen_input_tech[t] in x ) and ( time_range_vector[y] in x ) and ( 'UseByTechnology' in x ) ]
                if len(hyd_techs_indices) != 0:
                    for n in range( len( hyd_techs_indices ) ):
                        hyd_tech_index =  hyd_techs_indices[n]
                        this_hyd_electricity_consumption = float( assorted_data_dicts['t_f'][ hyd_tech_index ][-1] ) # of 'bus technology' in PJ

                        hyd_2_pp = hyd_2_pp_dict[hydrogen_input_tech[t]]
                        technical_variable_cost += this_hyd_electricity_consumption * lcoe_per_pp[hyd_2_pp][y]
            HydrogenPrice_variable_cost_vector[y] = technical_variable_cost

            # annualized_new_investments = ( new_investments / ( ( 1+0.05 )**( y ) ) )*0.05*1/( 1-(1+0.05)**(-50) # (see https://www.wallstreetmojo.com/annuity-formula/ for 50 yrs at 5%)
            # annualized_new_investments = new_investments * 0.05 / ( 1 - (1+0.05)**(-50) )

            annualized_new_investments = new_investments * 0.06 / ( 1 - (1+0.06)**(-25) )
            HydrogenPrice_new_investments[y] = new_investments
            for fill_y in range( y, len( time_range_vector ) ):
                HydrogenPrice_annualized_new_investments_vector[fill_y] += annualized_new_investments

            HydrogenPrice_fom_vector[y] = new_FOM
            HydrogenPrice_generated_H2[y] = hydrogen_production

        HydrogenPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]

        for y in range( 0, len( time_range_vector ) ):
            if HydrogenPrice_generated_H2[y] != 0:
                HydrogenPrice_vector[y] = ( HydrogenPrice_fom_vector[y] + HydrogenPrice_annualized_new_investments_vector[y] + HydrogenPrice_variable_cost_vector[y] ) / HydrogenPrice_generated_H2[y]
            else:
                HydrogenPrice_vector[y] = 0

        '''
        Let's estimate the price of fossil fuels / let's provisionally include the price structure we had in November
        $*$ This is a provisional method for fossil fuel additional costs.
        '''
        print('Initial Part - Performing FCM_6 - Extracting Rates of Energy Sales/Purchases')
        # Store electricity and H2 prices // fuel prices were stored abocve
        for y in range( len( time_range_vector ) ):
            # A change function can be added to the rates in this section
            for t in range( len( df_Rates_TF_SalesPurchasesEnergy[ 'Technology' ].tolist() ) ):
                this_fuel = df_Rates_TF_SalesPurchasesEnergy[ 'Fuel' ].tolist()[t]

                if 'DSL' in this_fuel or 'GSL' in this_fuel or 'LPG' in this_fuel:
                    pass
                if 'ELE' in this_fuel:
                    df_Rates_TF_SalesPurchasesEnergy.loc[ t , time_range_vector[y] ] = ElectricityPrice_vector[y]
                if 'HYD' in this_fuel:
                    df_Rates_TF_SalesPurchasesEnergy.loc[ t , time_range_vector[y] ] = HydrogenPrice_vector[y]

        ''' ############################################################### '''
        # Procedure: we must bring the rates we know into the program. The rates are in colones for fuels or in % for electricity.
        df_Rates_TF_H2 = deepcopy(df_Rates_TF_TaxEnergy
                                .loc[df_Rates_TF_TaxEnergy['Tax_Type'] ==
                                'H2_Tax'])
        df_Rates_TF_H2.reset_index(inplace = True)
        df_Unit_TF_H2 = deepcopy(df_Rates_TF_H2)

        df_Rates_TF_ElectricityVAT = \
            deepcopy(df_Rates_TF_TaxEnergy
                     .loc[df_Rates_TF_TaxEnergy['Tax_Type']
                     == 'VAT_Electricity'])
        df_Unit_TF_ElectricityVAT = deepcopy(df_Rates_TF_ElectricityVAT)      
        df_Rates_TF_ElectricityVAT.reset_index(inplace = True)
        df_Unit_TF_ElectricityVAT.reset_index(inplace = True)

        grab_the_techs_ElectricityVAT = \
            df_Rates_TF_ElectricityVAT['Technology'].tolist()
        grab_the_fuels_ElectricityVAT = df_Rates_TF_ElectricityVAT['Fuel'].tolist()
        for t in range(len(grab_the_techs_ElectricityVAT)):
            for y in range(len(time_range_vector)):
                df_Unit_TF_ElectricityVAT.loc[t, time_range_vector[y]] = \
                    df_Rates_TF_ElectricityVAT \
                    .loc[t, time_range_vector[y]]*ElectricityPrice_vector[y]
        df_Unit_TF_ElectricityVAT = deepcopy(df_Unit_TF_ElectricityVAT
                                            .drop(columns=['Factor']))
        df_Rates_TF_ElectricityVAT = deepcopy(df_Rates_TF_ElectricityVAT
                                            .drop(columns=['Factor']))

        # We do not need to copy the H2 because it is zero;
        # just drop the factor column
        df_Unit_TF_H2 = deepcopy( df_Unit_TF_H2.drop(columns=['Factor']) )
        df_Rates_TF_H2 = deepcopy( df_Rates_TF_H2.drop(columns=['Factor']) )

        print('Initial Part - Performing FCM_6 - Extracting Rates of Services Sales/Purchases')
        for i in range( len( time_range_vector ) ):
            # A change function can be added to the rates in this section
            df_Rates_TF_SalesPurchasesService[ time_range_vector[i] ] = df_Rates_TF_SalesPurchasesService['Factor']       
        index_buses = df_Rates_TF_SalesPurchasesService['Technology'].tolist().index( 'Techs_Buses' )
        index_taxis = df_Rates_TF_SalesPurchasesService['Technology'].tolist().index( 'Techs_Taxis' )
        base_bus_rate = df_Rates_TF_SalesPurchasesService['Factor'].tolist()[ index_buses ]
        base_taxis_rate = df_Rates_TF_SalesPurchasesService['Factor'].tolist()[ index_taxis ]
        # ---------------------------------------------------------------------
        # For *Buses*:
        fleet_techs = in_relationship_ownership['bus_companies']
        production_techs = in_relationship_sell['bus_companies']

        # Depreciation factors: already open

        BusPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
        BusPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
        BusPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
        BusPrice_variable_cost_vector = [ 0 for y in range( len(time_range_vector) ) ]
        BusPrice_external_fixed_cost = [ 0 for y in range( len(time_range_vector) ) ]
        BusPrice_produced_km = [ 0 for y in range( len(time_range_vector) ) ]

        for y in range( len( time_range_vector ) ):
            prod_pass_km = 0 # here we should select the % of trips produced by the "concesionario" fleet
            for t in range( len( production_techs ) ):
                prod_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( production_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

                if len(prod_tech_indices) != 0:
                    prod_tech_index =  prod_tech_indices[0]
                    this_pkm_production = float( assorted_data_dicts['t_f'][ prod_tech_index ][-1] )*1e9 # of 'Techs_Buses', unit in *kilometers*
                else:
                    this_pkm_production = 0

                prod_pass_km += this_pkm_production

            BusPrice_produced_km[y] = prod_pass_km
            # ---
            capital_expense = 0
            this_q_per_tech = [ 0 for t in range( len( fleet_techs ) ) ]
            # We must use the fleet here:
            for t in range( len( fleet_techs ) ):
                this_tech = fleet_techs[t]
                these_ages_raw = list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ].keys() )
                these_ages = [ i for i in these_ages_raw if type(i) == int ]
                this_inv = 0
                for a in these_ages:
                    this_q_a = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ][ a ] # let's work only with the imported fleet in order to have a comparable methodology to electricity rate
                    this_market_price = df_Unit_T_MarketPrice[ time_range_vector[y] ][ this_tech ][ a ]
                    this_inv += this_q_a*this_market_price/1e6
                    this_q_per_tech[t] += this_q_a

                capital_expense += this_inv

            BusPrice_new_investments[y] = capital_expense

            fill_y_counter = 0
            for fill_y in range( y, len( time_range_vector ) ):
                if fill_y <= y + 15:  # here we will replace the annualized approach with the depreciation/proift factor approach
                    depreciation_expense = capital_expense * df_bus_rates_dep_factor[ fill_y_counter ]
                    capital_profit_amount = capital_expense * df_bus_rates_profit_factor[ fill_y_counter ] * df_bus_rates_profit_rate[ fill_y_counter ]
                    BusPrice_annualized_new_investments_vector[fill_y] += depreciation_expense + capital_profit_amount
                    fill_y_counter += 1
            # ---
            technical_FOM = 0
            for t in range( len( fleet_techs ) ):
                fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'AnnualFixedOperatingCost' in x ) ]
                if len(fleet_techs_indices) != 0:
                    fleet_tech_index =  fleet_techs_indices[0]
                    this_fleet_tech_FOM = float( assorted_data_dicts['t'][ fleet_tech_index ][-1] ) # of 'bus technology'
                else:
                    this_fleet_tech_FOM = 0
                technical_FOM += this_fleet_tech_FOM

            BusPrice_fom_vector[y] = technical_FOM
            # ---
            external_fixed_costs = 0
            external_fixed_costs_types = fixed_admin_costs_buses['Type'].tolist()
            for t in range( len( external_fixed_costs_types ) ):
                if t > 1:
                    growth_rate = fixed_admin_costs_buses['Growth'].tolist()[t]
                else:
                    growth_rate = 0
                this_cost = fixed_admin_costs_buses['Costs'].tolist()[t]
                this_frequency = fixed_admin_costs_buses['Frequency_per_year'].tolist()[t]

                this_cost_updated = ( this_cost*this_frequency*( 1+growth_rate/100 )/dict_ER_per_year[ time_range_vector[y] ] )/1e6
                external_fixed_costs += this_cost_updated

            BusPrice_external_fixed_cost[y] = external_fixed_costs * sum( this_q_per_tech )
            # ---
            technical_variable_cost = 0
            for t in range( len( fleet_techs ) ):
                fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'UseByTechnology' in x ) ]
                if len(fleet_techs_indices) != 0:
                    for n in range( len( fleet_techs_indices ) ):
                        fleet_tech_index =  fleet_techs_indices[n]
                        this_fleet_fuel_consumption = float( assorted_data_dicts['t_f'][ fleet_tech_index ][-1] ) # of 'bus technology' in PJ
                        this_fleet_fuel = assorted_data_dicts['t_f'][ fleet_tech_index ][1] # the fuels

                        if fleet_techs[t] in df_Unit_TF_IUC['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_IUC['Fuel'].tolist():
                            df_Unit_Tax = deepcopy( df_Unit_TF_IUC )
                        if fleet_techs[t] in df_Unit_TF_ElectricityVAT['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_ElectricityVAT['Fuel'].tolist():
                            df_Unit_Tax = deepcopy( df_Unit_TF_ElectricityVAT )
                        if fleet_techs[t] in df_Unit_TF_H2['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_H2['Fuel'].tolist():
                            df_Unit_Tax = deepcopy( df_Unit_TF_H2 )

                        tech_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Technology'].tolist() ) if element == fleet_techs[t] ]
                        fuel_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Fuel'].tolist() ) if element == this_fleet_fuel ]
                        tax_index = list( set(tech_indices_tax) & set(fuel_indices_tax) )[0]

                        df_Unit_Price = deepcopy( df_Rates_TF_SalesPurchasesEnergy )
                        tech_indices_price = [index for index, element in enumerate( df_Unit_Price['Technology'].tolist() ) if element == fleet_techs[t] ]
                        fuel_indices_price = [index for index, element in enumerate( df_Unit_Price['Fuel'].tolist() ) if element == this_fleet_fuel ]
                        price_index = list( set(tech_indices_price) & set(fuel_indices_price) )[0]

                        unit_fuel_cost = df_Unit_Tax.loc[ tax_index, time_range_vector[y] ] + df_Unit_Price.loc[ price_index, time_range_vector[y] ] # per PJ cost
                        technical_variable_cost += unit_fuel_cost * this_fleet_fuel_consumption

            BusPrice_variable_cost_vector[y] = technical_variable_cost

        BusPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]
        BusPrice_for_new = [ 0 for y in range( len(time_range_vector) ) ]
        BusPrice_for_old = [ 0 for y in range( len(time_range_vector) ) ]

        F = ( BusPrice_produced_km[0] * base_bus_rate / dict_ER_per_year[ time_range_vector[0] ] ) / 1e6 # this pays for the existing fleet and reflects the income of the fleet in the base year

        for y in range( 0, len( time_range_vector ) ):
            BusPrice_for_new[y] = ( BusPrice_variable_cost_vector[y] + BusPrice_fom_vector[y] + BusPrice_annualized_new_investments_vector[y] + BusPrice_external_fixed_cost[y] ) / BusPrice_produced_km[y]
            BusPrice_for_old[y] = ( F - BusPrice_for_new[0]*BusPrice_produced_km[0] ) / BusPrice_produced_km[y]
            BusPrice_vector[y] = BusPrice_for_old[y] + BusPrice_for_new[y] # USD / km

            df_Rates_TF_SalesPurchasesService.loc[ index_buses, time_range_vector[y] ] = BusPrice_vector[y]

        # For *Taxis*:
        fleet_techs = in_relationship_ownership['taxi_industry']
        production_techs = in_relationship_sell['taxi_industry']

        TaxiPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
        TaxiPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
        TaxiPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
        TaxiPrice_variable_cost_vector = [ 0 for y in range( len(time_range_vector) ) ]
        TaxiPrice_external_fixed_cost = [ 0 for y in range( len(time_range_vector) ) ]
        TaxiPrice_produced_km = [ 0 for y in range( len(time_range_vector) ) ]

        for y in range( len( time_range_vector ) ):
            prod_pass_km = 0 # here we should select the % of trips produced by the "concesionario" fleet
            for t in range( len( production_techs ) ):
                prod_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( production_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

                if len(prod_tech_indices) != 0:
                    prod_tech_index =  prod_tech_indices[0]
                    this_pkm_production = float( assorted_data_dicts['t_f'][ prod_tech_index ][-1] )*1e9 # of 'Techs_Taxis', unit in *kilometers*
                else:
                    this_pkm_production = 0
                prod_pass_km += this_pkm_production

            TaxiPrice_produced_km[y] = prod_pass_km
            # ---
            capital_expense = 0
            this_q_per_tech = [ 0 for t in range( len( fleet_techs ) ) ]
            # We must use the fleet here:
            for t in range( len( fleet_techs ) ):
                this_tech = fleet_techs[t]
                these_ages_raw = list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ].keys() )
                these_ages = [ i for i in these_ages_raw if type(i) == int ]
                this_inv = 0
                for a in these_ages:
                    this_q_a = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ][ a ] # let's work only with the imported fleet in order to have a comparable methodology to electricity rate
                    this_market_price = df_Unit_T_MarketPrice[ time_range_vector[y] ][ this_tech ][ a ]
                    this_inv += this_q_a*this_market_price/1e6
                    this_q_per_tech[t] += this_q_a

                capital_expense += this_inv

            TaxiPrice_new_investments[y] = capital_expense

            fill_y_counter = 0
            for fill_y in range( y, len( time_range_vector ) ): # here we will replace the annualized approach with the depreciation/proift factor approach // we take the same data as buses, for now
                if fill_y <= y+15:
                    depreciation_expense = capital_expense * df_bus_rates_dep_factor[ fill_y_counter ]
                    capital_profit_amount = capital_expense * df_bus_rates_profit_factor[ fill_y_counter ] * df_bus_rates_profit_rate[ fill_y_counter ]
                    TaxiPrice_annualized_new_investments_vector[fill_y] += depreciation_expense + capital_profit_amount
                    fill_y_counter += 1
            # ---
            technical_FOM = 0
            for t in range( len( fleet_techs ) ):
                fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'AnnualFixedOperatingCost' in x ) ]

                if len(fleet_techs_indices) != 0:
                    fleet_tech_index =  fleet_techs_indices[0]
                    this_fleet_tech_FOM = float( assorted_data_dicts['t'][ fleet_tech_index ][-1] ) # of 'taxi technology'
                else:
                    this_fleet_tech_FOM = 0
                technical_FOM += this_fleet_tech_FOM

            TaxiPrice_fom_vector[y] = technical_FOM
            # ---
            external_fixed_costs = 0
            external_fixed_costs_types = fixed_admin_costs_taxis['Type'].tolist()
            for t in range( len( external_fixed_costs_types ) ):
                if t > 1:
                    growth_rate = fixed_admin_costs_taxis['Growth'].tolist()[t]
                else:
                    growth_rate = 0
                this_cost = fixed_admin_costs_taxis['Costs'].tolist()[t]
                this_frequency = fixed_admin_costs_taxis['Frequency_per_year'].tolist()[t]

                this_cost_updated = ( this_cost*this_frequency*( 1+growth_rate/100 )/dict_ER_per_year[ time_range_vector[y] ] )/1e6
                external_fixed_costs += this_cost_updated

            TaxiPrice_external_fixed_cost[y] = external_fixed_costs * sum( this_q_per_tech )
            # ---
            technical_variable_cost = 0
            for t in range( len( fleet_techs ) ):
                fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'UseByTechnology' in x ) ]

                if len(fleet_techs_indices) != 0:
                    for n in range( len( fleet_techs_indices ) ):
                        fleet_tech_index =  fleet_techs_indices[n]
                        this_fleet_fuel_consumption = float( assorted_data_dicts['t_f'][ fleet_tech_index ][-1] ) # of 'taxi technology' in PJ
                        this_fleet_fuel = assorted_data_dicts['t_f'][ fleet_tech_index ][1] # the fuels

                        if fleet_techs[t] in df_Unit_TF_IUC['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_IUC['Fuel'].tolist():
                            df_Unit_Tax = deepcopy( df_Unit_TF_IUC )
                        if fleet_techs[t] in df_Unit_TF_ElectricityVAT['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_ElectricityVAT['Fuel'].tolist():
                            df_Unit_Tax = deepcopy( df_Unit_TF_ElectricityVAT )

                        tech_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Technology'].tolist() ) if element == fleet_techs[t] ]
                        fuel_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Fuel'].tolist() ) if element == this_fleet_fuel ]
                        tax_index = list( set(tech_indices_tax) & set(fuel_indices_tax) )[0]

                        df_Unit_Price = deepcopy( df_Rates_TF_SalesPurchasesEnergy )
                        tech_indices_price = [index for index, element in enumerate( df_Unit_Price['Technology'].tolist() ) if element == fleet_techs[t] ]
                        fuel_indices_price = [index for index, element in enumerate( df_Unit_Price['Fuel'].tolist() ) if element == this_fleet_fuel ]
                        price_index = list( set(tech_indices_price) & set(fuel_indices_price) )[0]

                        unit_fuel_cost = df_Unit_Tax.loc[ tax_index, time_range_vector[y] ] + df_Unit_Price.loc[ price_index, time_range_vector[y] ] # per PJ cost
                        technical_variable_cost += unit_fuel_cost * this_fleet_fuel_consumption

            TaxiPrice_variable_cost_vector[y] = technical_variable_cost

        TaxiPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]
        TaxiPrice_for_new = [ 0 for y in range( len(time_range_vector) ) ]
        TaxiPrice_for_old = [ 0 for y in range( len(time_range_vector) ) ]

        F = ( TaxiPrice_produced_km[0] * base_taxis_rate / dict_ER_per_year[ time_range_vector[0] ] ) / 1e6 # this pays for the existing fleet and reflects the income of the fleet in the base year

        for y in range( 0, len( time_range_vector ) ):
            TaxiPrice_for_new[y] = ( TaxiPrice_variable_cost_vector[y] + TaxiPrice_fom_vector[y] + TaxiPrice_annualized_new_investments_vector[y] + TaxiPrice_external_fixed_cost[y] ) / TaxiPrice_produced_km[y]
            TaxiPrice_for_old[y] = ( F - TaxiPrice_for_new[0]*TaxiPrice_produced_km[0] ) / TaxiPrice_produced_km[y]
            TaxiPrice_vector[y] = TaxiPrice_for_old[y] + TaxiPrice_for_new[y] # USD / km

            df_Rates_TF_SalesPurchasesService.loc[ index_taxis, time_range_vector[y] ] = TaxiPrice_vector[y]

        # For *Sedans*: extract the levelized cost of transport similary
        lcot_sedan, lcot_sed_for_new, lcot_sed_produced_km, \
            lcot_sed_fom_vector, lcot_sed_annualized_new_investments, \
            lcot_sed_variable_cost_vector  = \
            calc_lcot(assorted_data_dicts, time_range_vector, 'Techs_Sedan',
                      Fleet_Groups, fleet_Q_perTech_perYear_per_age_imports,
                      df_Unit_T_MarketPrice, df_Rates_TF_SalesPurchasesEnergy,
                      df_Unit_TF_IUC, df_Unit_TF_ElectricityVAT, df_Unit_TF_H2)

        # Now let's dump some prices for independent analysis:
        ele_price_pickle = \
            {'final': ElectricityPrice_vector, 'old': ElectricityPrice_for_old,
             'new': ElectricityPrice_for_new,
             'activity': ElectricityPrice_generated_electricity,
             'fom': ElectricityPrice_fom_vector,
             'inv': ElectricityPrice_annualized_new_investments_vector,
             'var': ElectricityPrice_variable_cost_vector}
        hyd_price_pickle = \
            {'final': HydrogenPrice_vector,
             'activity': HydrogenPrice_generated_H2,
             'fom': HydrogenPrice_fom_vector,
             'inv': HydrogenPrice_annualized_new_investments_vector,
             'var': HydrogenPrice_variable_cost_vector}

        bus_price_pickle = { 'final': BusPrice_vector, 'old':BusPrice_for_old, 'new':BusPrice_for_new, 'activity':BusPrice_produced_km, 'fom':BusPrice_fom_vector, 'inv':BusPrice_annualized_new_investments_vector, 'var':BusPrice_variable_cost_vector, 'ext':BusPrice_external_fixed_cost }
        taxi_price_pickle = { 'final': TaxiPrice_vector, 'old':TaxiPrice_for_old, 'new':TaxiPrice_for_new, 'activity':TaxiPrice_produced_km, 'fom':TaxiPrice_fom_vector, 'inv':TaxiPrice_annualized_new_investments_vector, 'var':TaxiPrice_variable_cost_vector, 'ext':TaxiPrice_external_fixed_cost }
        sedan_lcot_pickle = { 'final': lcot_sedan, 'new':lcot_sed_for_new, 'activity':lcot_sed_produced_km, 'fom':lcot_sed_fom_vector, 'inv':lcot_sed_annualized_new_investments, 'var': lcot_sed_variable_cost_vector}
        price_pickle = {'ele': ele_price_pickle, 'hyd': hyd_price_pickle,
                        'bus': bus_price_pickle, 'taxi': taxi_price_pickle,
                        'sed': sedan_lcot_pickle, 'lcoe': lcoe_per_pp }
        with open( output_adress + '/' + scenario_string + '_PricePickle' + '.pickle' , 'wb') as handle:
            pickle.dump(price_pickle, handle, protocol=pickle.HIGHEST_PROTOCOL)
        handle.close()

        # FCM_7 - Calculate transfers:

        discounted_or_not = 'Discounted' # DEPRICATED: does not matter anymore

        list_of_variables = params['list_of_variables']

        fcm_table_header =  params['fcm_table_header'] + list_of_variables

        results_list = [] # this will be discounted and undiscounted

        ''' 'TYPE 1 ACTORS:' // Government '''
        print('Initial Part - Performing FCM_7 - Calculate government transfers')
        for n in range( len( type_1_actor ) ):
            ''' ------------------------------------------
            '''
            # Function 1a: gather_derecho_arancelario
            print('     Within FCM_7 - Calculate *Derecho Arancelario* Revenue')
            this_returnable = type_1_actor[n].gather_derecho_arancelario( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_DerechoArancelario , m , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

            # Function 1b: gather_valor_aduanero
            print('     Within FCM_7 - Calculate *Valor Aduanero* Revenue')
            this_returnable = type_1_actor[n].gather_valor_aduanero( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_ValorAduanero , m , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

            # Function 1c: gather_selectivo_al_consumo
            print('     Within FCM_7 - Calculate *Selectivo al Consumo* Revenue')
            this_returnable = type_1_actor[n].gather_selectivo_al_consumo( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_SelectivoAlConsumo , m , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

            # Function 1d: gather_import_vat
            print('     Within FCM_7 - Calculate *Import VAT* Revenue')
            this_returnable = type_1_actor[n].gather_import_vat( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_ImportVAT , m , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

            # Function 1 PLUS: gather_total_import_taxes
            print('     Within FCM_7 - Calculate *Total Import Taxes* Revenue')
            this_returnable = type_1_actor[n].gather_total_import_taxes( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_TotalTaxes , m , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )

            ''' ------------------------------------------ '''
            # Function 2a: gather_iuc
            print('     Within FCM_7 - Calculate *IUC* Revenue')
            fuels_produced_by_techs = params['fuels_produced_by_techs_2']
            for k in range( len( fuels_produced_by_techs ) ):
                this_returnable = type_1_actor[n].gather_iuc( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_TF_IUC , m , fuels_produced_by_techs[k], 'NO_df_new_Rates' )
                lists_of_lists_to_print = deepcopy( this_returnable )
                for l in range( len( lists_of_lists_to_print ) ):
                    results_list.append( lists_of_lists_to_print[l] )

            # Function 2b: gather_electricity_vat
            print('     Within FCM_7 - Calculate *Electricity VAT* Revenue')
            fuels_produced_by_techs = params['fuels_produced_by_techs_3']
            for k in range( len( fuels_produced_by_techs ) ):
                this_returnable = type_1_actor[n].gather_electricity_vat( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_TF_ElectricityVAT , m , fuels_produced_by_techs[k], 'NO_df_new_Rates' )
                lists_of_lists_to_print = deepcopy( this_returnable )
                for l in range( len( lists_of_lists_to_print ) ):
                    results_list.append( lists_of_lists_to_print[l] )

            # Function 2c: gather_h2
            print('     Within FCM_7 - Calculate *H2* Revenue')
            fuels_produced_by_techs = params['fuels_produced_by_techs_4']
            for k in range( len( fuels_produced_by_techs ) ):
                this_returnable = type_1_actor[n].gather_h2( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_TF_H2 , m , fuels_produced_by_techs[k], 'NO_df_new_Rates' )
                lists_of_lists_to_print = deepcopy( this_returnable )
                for l in range( len( lists_of_lists_to_print ) ):
                    results_list.append( lists_of_lists_to_print[l] )

            ''' ------------------------------------------ '''
            # Function 3: gather_property_tax
            print('     Within FCM_7 - Calculate *Property Tax* Revenue')
            this_returnable = type_1_actor[n].gather_property_tax( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_PropertyTax , m , 'NO_df_new_Rates' )
            lists_of_lists_to_print = deepcopy( this_returnable )
            for l in range( len( lists_of_lists_to_print ) ):
                results_list.append( lists_of_lists_to_print[l] )
            ''' ------------------------------------------ '''

        # $*$ Think of a unit-oriented estimation of the "marchamo" // this will be super useful
        print('         SO-2.b. Here we are about to start the calculation of the property tax in the first years.')
        df_tech_list = df_tax_assign['Technology'].tolist()
        df_tech_list_unique = list( set( df_tech_list ) )
        dict_Unit_PropertyTax = {}
        for t in range( len( df_tech_list_unique ) ):
            this_tech = df_tech_list_unique[t]

            dict_Unit_PropertyTax.update( { this_tech:{} } )               

            for a_y in range( len( time_range_vector ) ):
                query_year = time_range_vector[ a_y ]
                dict_Unit_PropertyTax[ this_tech ].update( { query_year:{  } } )
                list_ages_raw = list( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ].keys() )
                list_ages = [ i for i in list_ages_raw if type(i) == int ]

                # note: *age_y* has the same components as *list_ages* when the dictionary is not empty
                for age_y in list_ages:
                    dict_Unit_PropertyTax[ this_tech ][ query_year ].update( { age_y:0 } )

                    if dict_Property_Tax_Applicable[ this_tech ] == 'Table':

                        this_q = fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ][ age_y ]
                        this_vf = fiscal_value_perTech_perYear_per_age[ this_tech ][ query_year ][ age_y ]

                        all_scales = list( dict_Rates_T_PropertyTax_query[ query_year ].keys() )
                        this_fiscal_value = this_vf

                        for a_scale in range( len( all_scales ) ):
                            min_threshold = dict_Rates_T_PropertyTax_query[ query_year ][ all_scales[a_scale] ]['Min']
                            max_threshold = dict_Rates_T_PropertyTax_query[ query_year ][ all_scales[a_scale] ]['Max']
                            if this_fiscal_value >= min_threshold and this_fiscal_value <= max_threshold:
                                correct_scale = a_scale

                        if this_fiscal_value > max_threshold:
                            correct_scale = len( all_scales )-1 # the last of scales

                        used_scales = all_scales[ :correct_scale+1 ]
                        this_pt_amount_contribution = 0
                        for u_scale in range( len( used_scales ) ): # EV EXONERATIONS SHOULD BE PROGRAMMED HERE
                            this_pt_unit = dict_Rates_T_PropertyTax_query[ query_year ][ used_scales[u_scale] ]['Unit']

                            if this_pt_unit == 'Nominal':
                                this_pt_amount_contribution += dict_Rates_T_PropertyTax_query[ query_year ][ used_scales[u_scale] ]['Rate'] # THIS REPEATS, SO CNTRL*F
                            else:  # This means the rate is a percent

                                this_pt_rate = dict_Rates_T_PropertyTax_query[ query_year ][ used_scales[u_scale] ]['Rate']
                                min_threshold = dict_Rates_T_PropertyTax_query[ query_year ][ used_scales[u_scale] ]['Min'] # THIS REPEATS, SO CNTRL*F
                                max_threshold = dict_Rates_T_PropertyTax_query[ query_year ][ used_scales[u_scale] ]['Max'] # THIS REPEATS, SO CNTRL*F

                                if u_scale < len( used_scales )-1 :
                                    this_pt_amount_contribution += ( max_threshold-min_threshold )*this_pt_rate

                                else: # this means *u_scale == len( used_scales )-1* and it is the correct value
                                    this_pt_amount_contribution += ( this_fiscal_value-min_threshold )*this_pt_rate

                        if this_fiscal_value == 0:
                            this_pt_amount_contribution = 0
                    else:
                        this_pt_amount_contribution = ( dict_Property_Tax_Applicable[ this_tech ] / dict_ER_per_year[ query_year ] )

                    dict_Unit_PropertyTax[ this_tech ][ query_year ][ age_y ] += deepcopy( this_pt_amount_contribution )

        #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
        # FCM_7.b - Calculate remaining transfers:
        print('Initial Part - Performing FCM_7.b - Calculate remaining transfers')
        # print( '    *let us skip this just for testing*' )
        results_list = calculate_transfers( m, discounted_or_not, results_list, assorted_data_dicts, type_1_actor, type_2_actor, type_3_actor, type_4_actor, type_5_actor,
                                            df_Rates_TF_SalesPurchasesEnergy, df_Unit_T_DerechoArancelario, df_Unit_T_ValorAduanero, df_Unit_T_SelectivoAlConsumo, df_Unit_T_ImportVAT,
                                            df_Unit_T_TotalTaxes, df_Unit_T_GananciaEstimada, df_Unit_T_MarketPrice, df_Unit_TF_IUC, df_Unit_TF_ElectricityVAT, df_Unit_TF_H2,
                                            'nothing', df_Unit_T_PropertyTax, df_Rates_TF_SalesPurchasesService, 'Initial' )

        # Here we can append the remaining metrics that go into *results_list*
        # for later printing
        this_returnable = additional_levelized_costs(m, lcot_sedan, lcoe_per_pp, time_range_vector)
        lists_of_lists_to_print = deepcopy( this_returnable )
        for l in range( len( lists_of_lists_to_print ) ):
            results_list.append( lists_of_lists_to_print[l] )

        # FCM_8 - Incorporate Prices:
        print('Initial Part - Performing FCM_8 - Incorporate outputs')
        q_p_t_list = [  df_Rates_TF_SalesPurchasesEnergy, # P
                        df_Unit_TF_IUC, # T
                        df_Unit_TF_ElectricityVAT, # T
                        df_Rates_TF_ElectricityVAT, # T
                        df_Unit_TF_H2, # T
                        df_Rates_TF_SalesPurchasesService, # P
                        #
                        df_Unit_T_TotalTaxes, # T
                        df_Unit_T_MarketPrice, # P
                        df_Unit_T_SelectivoAlConsumo, # T
                        df_Unit_T_CIF, # P
                        #
                        fleet_Q_perTech_perYear_per_age_imports, # Q
                        #
                        '', # T
                        #
                        fleet_Q_perTech_perYear_per_age, # Q
                        #
                        fiscal_value_perTech_perYear_per_age,
                        dict_Unit_PropertyTax, # T
                        #
                        fleet_Q_per_actor_perTech_perYear_per_age, # Q
                        fleet_Q_per_actor_perTech_perYear_per_age_imp, # Q
                        #
                        ]
        results_list = incorporate_qs_ps_ts( m, results_list, assorted_data_dicts, q_p_t_list, 'Normal' )

        # FCM_9 - Print outputs:
        print('Initial Part - Performing FCM_9 - Print outputs')
        print_transfers( m, results_list, fcm_table_header, output_adress, scenario_string, 'Normal', '' )
        '''
        NOTE: HERE HE HAVE FINISHED EMBEDDING THE FCM INTO THE MODEL OUTPUT PROCESSING
        But we need to adjust the rates to avoid a fiscal hole. So, what do we do? We estimate the difference between the scenarios and find the new rates that avoid a hole.
        *Remember to stay within the indentation limits*.
        '''   
        print('\n')
        if case_strategy_alphabet != 'BAU': # this means we are in a decarbonization scenario, so we must adjust the rates // also applies exonerations
            print('#############################################################################################')
            print(' SMART OPTIMIZATION: We will now start optimizing the contributions. This is a CRITICAL step.')
 
            if base_or_fut == 'base':
                output_adress_BAU = './Executables/' + str( first_list[0] )
                BAU_Cost_Distribution = pd.read_csv( output_adress_BAU + '/' + str( first_list[0] ) + '_TEM' + '.csv' )
                This_Scenario_Cost_Distribution = pd.read_csv( output_adress + '/' + str( first_list[case] ) + '_TEM' + '.csv' )
                this_decarb_f = 0

            if base_or_fut == 'fut':
                output_adress_BAU = params['Experi_Plat'] + params['Futures'] + params['Bau_Bau'] + case.split('_')[-1]
                BAU_Cost_Distribution = pd.read_csv( output_adress_BAU + '/BAU_' + case.split('_')[-1] + '_TEM' + '.csv' )
                This_Scenario_Cost_Distribution = pd.read_csv( output_adress + '/' + scenario_string + '_TEM' + '.csv' )
                this_decarb_f = int( case.split('_')[-1] )

            verification_filename = output_adress + '/' + scenario_string + params['Verif']
            verification_file = open( verification_filename, "w" )

            print('     SO-1. We have called some input files. Now let us initialize some data.')
            # Extracting the government revenue: # we should call the remaining agents to work on this
            BAU_Government_Revenue = deepcopy( BAU_Cost_Distribution.loc[ BAU_Cost_Distribution['Actor'] == 'central_government' ] )
            This_Scenario_Government_Revenue = deepcopy( This_Scenario_Cost_Distribution.loc[ This_Scenario_Cost_Distribution['Actor'] == 'central_government' ] )
            BAU_Government_Revenue_yearly = []
            This_Scenario_Government_Revenue_yearly = []

            # Do not forget to list the taxes that must be assorted here:
            # tax_type_list = ['Import and Sales Tax', 'Energy Tax', 'Property Tax']
            tax_type_list = params['tax_type_list']
            BAU_revenue_per_tax_type = {} # this is an optional variable, we kept it just in case
            This_Scenario_revenue_per_tax_type = {} # this is an optional variable, we kept it just in case
            This_Scenario_relative_revenue_shortfall_per_tax_type = {} # this is an optional variable, we kept it just in case
            This_Scenario_relative_revenue_shortfall_total = {} # this is an optional variable, we kept it just in case

            # We should extract the remaining benefits of the remaining actors so that we can implement the system:
            actor_j_list = params['actor_j_list']

            BAU_Actor_Costs = {}
            This_Scenario_Actor_Costs = {}
            BAU_Actor_Costs_yearly = {}
            This_Scenario_Actor_Costs_yearly = {}
            for j in actor_j_list:
                BAU_Actor_Costs.update( { j:deepcopy( BAU_Cost_Distribution.loc[ BAU_Cost_Distribution['Actor'] == j ] ) } )
                This_Scenario_Actor_Costs.update( { j:deepcopy( This_Scenario_Cost_Distribution.loc[ This_Scenario_Cost_Distribution['Actor'] == j ] ) } )
                BAU_Actor_Costs_yearly.update( { j:[] } )
                This_Scenario_Actor_Costs_yearly.update( { j:[] } )

            BAU_Actor_Income = {}
            This_Scenario_Actor_Income = {}
            BAU_Actor_Income_yearly = {}
            This_Scenario_Actor_Income_yearly = {}
            for j in actor_j_list:
                BAU_Actor_Income.update( { j:deepcopy( BAU_Cost_Distribution.loc[ BAU_Cost_Distribution['Actor'] == j ] ) } )
                This_Scenario_Actor_Income.update( { j:deepcopy( This_Scenario_Cost_Distribution.loc[ This_Scenario_Cost_Distribution['Actor'] == j ] ) } )
                BAU_Actor_Income_yearly.update( { j:[] } )
                This_Scenario_Actor_Income_yearly.update( { j:[] } )

            actor_expense_list = params['actor_expense_list'] # The vehicle taxes are embedded in the Vehicle Purchase expense, but the eenergy taxes are separated,
            actor_income_list = params['actor_income_list']
            BAU_expenses_per_actor_per_exp_type = {}
            This_Scenario_expenses_per_actor_per_exp_type = {}
            This_Scenario_relative_benefit_per_actor_per_exp_type = {}
            This_Scenario_relative_benefit_per_actor_total = {}

            '''
            HERE WE NEED TO INCLUDE SOME NEW SCRIPTS THAT WILL REPLACE THE PREVIOUS IMPLEMENTATION (minimum legacy). THE THING WAS A RE-DO.
            '''
            # Let's start with a brief checklist of the elements we already have:
            #       actor_expense_list
            #       BAU_expenses_per_actor_per_exp_type
            #       This_Scenario_expenses_per_actor_per_exp_type
            #       This_Scenario_relative_benefit_per_actor_per_exp_type
            #       This_Scenario_relative_benefit_per_actor_total
            #   
            # Now, we will initialize all the restrictions of the problem and store them in dictionaries per m_y as we have done:
            c_jt_max_dict = {}
            benefits_per_actor = {}
            shape_restrictions = {}

            print('     SO-2. We have initialized some important data. Now let us initialize some more inputs that will be used for later adjustment.')

            # PART A)
            # We need to coulpe techs and fuels, since techs are the ones related to ownership.
            Rel_FT_df_Fuels_and_Techs = df_fuels_and_techs
            Rel_FT_df_Fuels_all = Rel_FT_df_Fuels_and_Techs['Fuels'].tolist()
            Rel_FT_df_Fuels = list( set( Rel_FT_df_Fuels_all ) )
            Rel_FT_df_Techs_all = Rel_FT_df_Fuels_and_Techs['Vehicle_Techs'].tolist()
            Rel_FT_df_Techs = list( set( Rel_FT_df_Techs_all ) )

            techs_and_fuels_that_are_used = {}
            for t in Rel_FT_df_Techs:
                techs_and_fuels_that_are_used.update( { t:[] } )

            fuels_and_techs_that_use_them = {}
            for f in Rel_FT_df_Fuels:
                fuels_and_techs_that_use_them.update( { f:{ 'Tech':[], 'Coef':[] } } )

            for tf in range( len( Rel_FT_df_Fuels_all ) ):
                this_tf = Rel_FT_df_Fuels_all[tf]
                fuels_and_techs_that_use_them[ this_tf ][ 'Tech' ].append( Rel_FT_df_Techs_all[tf] )
                fuels_and_techs_that_use_them[ this_tf ][ 'Coef' ].append( 0 ) # This can then be replaced by the corresponding value, average of the period
                # NOTE: the coefficient is the ratio of total quantity of fuel used by an actor
            #
            for tf in range( len( Rel_FT_df_Techs_all ) ):
                this_tf = Rel_FT_df_Techs_all[tf]
                techs_and_fuels_that_are_used[ this_tf ].append( Rel_FT_df_Fuels_all[tf] )

            # PART B)
            # Call the years in which you must perform the adjustment:
            milestone_years_df = df_milestones
            milestone_years = milestone_years_df['Milestone_Years'].tolist()
            time_range_vector_applicable = [ n for n in range( milestone_years[0], milestone_years[-1]+1 ) ]

            milestone_years_end = [ i-1 for i in milestone_years[1:] ]
            milestone_years_end.append( milestone_years[-1] )
            milestone_years_period_lenght = [ milestone_years_end[i] - milestone_years[i] + 1 for i in range( len( milestone_years ) ) ]

            # let us define the period years:
            milestone_years_periods = {}
            for m_y in range( len( milestone_years ) ):
                milestone_years_periods.update( { milestone_years[m_y]:[ i for i in range( milestone_years[m_y], milestone_years_end[m_y]+1 ) ] } )

            # PART C) # let's create a control dictionary for the strategies with the layers: 'strategy', 'tax', 'type', 'years'
            iuc_subtract = {}

            dict_strategy_controller = {}
            df_strategies_list = df_strategies['Strategy'].tolist()
            df_strategies_list_unique = list( set( df_strategies_list ) )
            df_tax_list = df_strategies['Tax'].tolist()
            df_tax_list_unique = list( set( df_tax_list ) ) # // remove the unique trait to differentiate among fuels
            df_strategies_years = [ i for i in df_strategies.columns.tolist() if type(i) == int ]
            for n in range( len( df_strategies_list_unique ) ):
                this_n = df_strategies_list_unique[n]
                dict_strategy_controller.update( { this_n:{} } )
                iuc_subtract.update( { this_n:{} } )
                for t in range( len( df_tax_list_unique ) ):
                    this_tax = df_tax_list_unique[t]

                    dict_strategy_controller[ this_n ].update( { this_tax: {} } )

                    df_strategies_local = df_strategies.loc[ ( df_strategies['Strategy'] == this_n ) & ( df_strategies['Tax'] == this_tax ) ]
                    df_strategies_list_type = df_strategies_local['Type'].tolist()
                    for k in range( len( df_strategies_list_type ) ):
                        type_num = k+1
                        list_of_fuels = df_strategies_list_type[k].replace(' ','').split(';')
                        dict_strategy_controller[ this_n ][ this_tax ].update( { type_num: {} } )

                        for y in range( len( df_strategies_years ) ):
                            this_year = df_strategies_years[ y ]
                            df_strategies_list_values = df_strategies_local[this_year].tolist()
                            this_value = df_strategies_list_values[k]

                            # And now, add:
                            for y2 in range( len( milestone_years_periods[ this_year ] ) ):
                                query_year = milestone_years_periods[ this_year ][ y2 ]
                                dict_strategy_controller[ this_n ][ this_tax ][ type_num ].update( { query_year:{ 'Type':list_of_fuels, 'Value':this_value } } )

                                if this_tax == 'IUC' and k == 0:
                                    iuc_subtract[ this_n ].update( { query_year:0 } )
                                if this_tax == 'IUC':
                                    iuc_subtract[ this_n ][ query_year ] += this_value

            # PART D)
            dict_Q_type_match = {}
            df_tax_assign_list = df_tax_assign['Tax'].tolist()
            df_tax_assign_list_unique = list( set( df_tax_assign_list ) )
            for t in range( len( df_tax_assign_list_unique ) ):
                df_tax_assign_local = df_tax_assign.loc[ df_tax_assign['Tax'] == df_tax_assign_list_unique[t] ]
                dict_Q_type_match.update( { df_tax_assign_list_unique[t]:{} } )

                df_tech_assign_list = df_tax_assign_local['Technology'].tolist()
                df_fuel_assign_list = df_tax_assign_local['Fuel'].tolist()
                df_set_type_assign_list = df_tax_assign_local['Set_Type'].tolist()
                df_type_assign_list = df_tax_assign_local['Type'].tolist()
                df_var_assign_list = df_tax_assign_local['Query_Variable'].tolist()

                for n in range( len( df_tech_assign_list ) ):
                    this_tech = df_tech_assign_list[n]
                    this_fuel = df_fuel_assign_list[n]
                    this_set_type = df_set_type_assign_list[n]
                    this_type = df_type_assign_list[n]
                    this_variable = df_var_assign_list[n]
                    dict_Q_type_match[ df_tax_assign_list_unique[t] ].update( { this_tech:{
                        'set_type':this_set_type ,
                        'type':this_type ,
                        'variable':this_variable,
                        'fuel':this_fuel} } )

            ''' This is an adjustment to consider IUC non-differentiable trait '''
            dict_Q_iuc_per_tech = {}
            dict_Q_iuc_whole = {}
            iuc_techs = list( dict_Q_type_match['IUC'].keys() )
            iuc_techs_gas = {}
            iuc_techs_diesel = {}
            '''
            iuc_techs_glp = {}
            '''
            for n in range( len( iuc_techs ) ):
                years_dict = {}
                for y in range( len( time_range_vector ) ):
                    query_year = time_range_vector[y]
                    years_dict.update( { query_year:0 } )
                if ( 'GSL' in dict_Q_type_match['IUC'][ iuc_techs[n] ]['fuel'] ) or ( 'LPG' in dict_Q_type_match['IUC'][ iuc_techs[n] ]['fuel'] ):
                    iuc_techs_gas.update( { iuc_techs[n]:deepcopy( years_dict ) } )
                if 'DSL' in dict_Q_type_match['IUC'][ iuc_techs[n] ]['fuel']:
                    iuc_techs_diesel.update( { iuc_techs[n]:deepcopy( years_dict ) } )
                '''
                if 'GSL' in dict_Q_type_match['IUC'][ iuc_techs[n] ]['fuel']:
                    iuc_techs_gas.update( { iuc_techs[n]:deepcopy( years_dict ) } )
                #
                if 'LPG' in dict_Q_type_match['IUC'][ iuc_techs[n] ]['fuel']:
                    iuc_techs_glp.update( { iuc_techs[n]:deepcopy( years_dict ) } )
                '''

            dict_Q_iuc_per_tech.update( { 'GSL':iuc_techs_gas } )
            dict_Q_iuc_whole.update( { 'GSL':deepcopy( years_dict ) } )

            dict_Q_iuc_per_tech.update( { 'DSL':iuc_techs_diesel } )
            dict_Q_iuc_whole.update( { 'DSL':deepcopy( years_dict ) } )

            '''
            dict_Q_iuc_per_tech.update( { 'LPG':iuc_techs_glp } )
            dict_Q_iuc_whole.update( { 'LPG':deepcopy( years_dict ) } )
            '''
            '''  ************************************************************* '''
            # We must lay out the Qs owned by each actor and then assign the % of the contribution to the tech/tax combination: *# this is the curcial step*
            dict_Q_per_actor_per_tax_per_tech = {} # the Q of tech or fuel must be repeated for each tax, but we have to check the variables.
            dict_VP_per_actor_per_tax_per_tech = {}

            dict_Q_per_actor_per_tax_per_tech_property = {}
            dict_Value_per_actor_per_tax_per_tech_property = {}
            dict_Q_per_actor_per_tax_per_tech_imports = {}
            dict_Value_per_actor_per_tax_per_tech_imports = {}

            for j in range( len( actor_j_list ) ):
                this_actor = actor_j_list[j]
                dict_Q_per_actor_per_tax_per_tech.update( { this_actor:{} } )
                dict_VP_per_actor_per_tax_per_tech.update( { this_actor:{} } )
                this_actor_techs = in_relationship_ownership[ this_actor ]

                # Add the removal of rail if it appears:
                if 'TRXTRAIFREELE' in this_actor_techs:
                    this_actor_techs.remove('TRXTRAIFREELE')

                dict_Q_per_actor_per_tax_per_tech_property.update( { this_actor:{} } )
                dict_Value_per_actor_per_tax_per_tech_property.update( { this_actor:{} } )
                dict_Q_per_actor_per_tax_per_tech_imports.update( { this_actor:{} } )
                dict_Value_per_actor_per_tax_per_tech_imports.update( { this_actor:{} } )

                for t1 in range( len( df_tax_assign_list_unique ) ): # iterate across the taxes
                    this_tax = df_tax_assign_list_unique[t1]
                    dict_Q_per_actor_per_tax_per_tech[ this_actor ].update( { this_tax:{} } )
                    dict_VP_per_actor_per_tax_per_tech[ this_actor ].update( { this_tax:{} } )

                    for y in range( len( time_range_vector ) ):
                        query_year = time_range_vector[y]

                        this_Q_sum = 0
                        this_Q_times_P = 0

                        for t2 in range( len( this_actor_techs ) ): # iterate across the technologies
                            this_tech = this_actor_techs[t2]

                            if this_tax in ['Electromobility', 'IUC', 'Energy']: # in this case, we must check the fuels that are used by the techs

                                if this_tax == 'Electromobility':
                                    local_fuel_list = [ i for i in techs_and_fuels_that_are_used[ this_tech ] if ('ELE' in i) or ('HYD' in i) ]
                                if this_tax == 'IUC':
                                    local_fuel_list = [ i for i in techs_and_fuels_that_are_used[ this_tech ] if ('ELE' not in i) and ('HYD' not in i) ]
                                if this_tax == 'Energy':
                                    local_fuel_list = [ i for i in techs_and_fuels_that_are_used[ this_tech ] ]

                                for f in range( len( local_fuel_list ) ):
                                    this_fuel = local_fuel_list[ f ]

                                    value_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( this_tech in x ) and ( this_fuel in x ) and ( int( query_year ) in x ) and ( 'UseByTechnology' in x ) ]
                                    if len(value_indices) != 0:
                                        data_index =  value_indices[0]
                                        this_Q = float( assorted_data_dicts['t_f'][ data_index ][-1] )
                                    else:
                                        this_Q = 0

                                    if y == 0:
                                        if f == 0:
                                            dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ].update( { this_tech:{ this_fuel:{} } } )

                                        else:
                                            dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ].update( { this_fuel:{} } )

                                    dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ][ this_fuel ].update( { query_year:this_Q } )

                                    if this_tax == 'IUC' and ( 'GSL' in this_fuel or 'LPG' in this_fuel ):
                                        dict_Q_iuc_per_tech['GSL'][ this_tech ][ query_year ] += deepcopy( this_Q )
                                        dict_Q_iuc_whole['GSL'][ query_year ] += deepcopy( this_Q )

                                    if this_tax == 'IUC' and 'DSL' in this_fuel:
                                        dict_Q_iuc_per_tech['DSL'][ this_tech ][ query_year ] += deepcopy( this_Q )
                                        dict_Q_iuc_whole['DSL'][ query_year ] += deepcopy( this_Q )

                                    '''
                                    if this_tax == 'IUC' and 'LPG' in this_fuel:
                                        dict_Q_iuc_per_tech['LPG'][ this_tech ][ query_year ] += deepcopy( this_Q )
                                        dict_Q_iuc_whole['LPG'][ query_year ] += deepcopy( this_Q )
                                    '''
                            else:  # in this case, we must check the techs directly
                                this_Q = 0

                                if this_tax == 'Property':
                                    if y == 0:
                                        dict_Q_per_actor_per_tax_per_tech_property[ this_actor ].update( { this_tech:{} } )
                                        dict_Value_per_actor_per_tax_per_tech_property[ this_actor ].update( { this_tech:{} } )

                                    dict_Q_per_actor_per_tax_per_tech_property[ this_actor ][ this_tech ].update( { query_year:{} } )
                                    dict_Value_per_actor_per_tax_per_tech_property[ this_actor ][ this_tech ].update( { query_year:{} } )

                                    age_list = list( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ].keys() )
                                    for a in age_list:
                                        this_Q += fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ][ a ]
                                        dict_Q_per_actor_per_tax_per_tech_property[ this_actor ][ this_tech ][ query_year ].update( { a:deepcopy( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ][ a ] ) } )
                                        dict_Value_per_actor_per_tax_per_tech_property[ this_actor ][ this_tech ][ query_year ].update( { a:fiscal_value_perTech_perYear_per_age[ this_tech ][ query_year ][ a ] } )

                                        this_Q_times_P += fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ][ a ] * fiscal_value_perTech_perYear_per_age[ this_tech ][ query_year ][ a ]
                                        this_Q_sum += fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ][ a ]

                                if this_tax == 'Imports':

                                    if y == 0:
                                        dict_Q_per_actor_per_tax_per_tech_imports[ this_actor ].update( { this_tech:{} } )
                                        dict_Value_per_actor_per_tax_per_tech_imports[ this_actor ].update( { this_tech:{} } )

                                    dict_Q_per_actor_per_tax_per_tech_imports[ this_actor ][ this_tech ].update( { query_year:{} } )
                                    dict_Value_per_actor_per_tax_per_tech_imports[ this_actor ][ this_tech ].update( { query_year:{} } )

                                    age_list = list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ].keys() )
                                    for a in age_list:
                                        this_Q += fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ][ a ]
                                        dict_Q_per_actor_per_tax_per_tech_imports[ this_actor ][ this_tech ][ query_year ].update( { a:fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ][ a ] } )
                                        dict_Value_per_actor_per_tax_per_tech_imports[ this_actor ][ this_tech ][ query_year ].update( { a:df_Unit_T_MarketPrice[ query_year ][ this_tech ][ a ] } )

                                        this_Q_times_P += fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ][ a ] * df_Unit_T_MarketPrice[ query_year ][ this_tech ][ a ]
                                        this_Q_sum += fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ][ a ]

                                if this_tax == 'VMT':
                                    this_Q_km = 0
                                    value_indices = [i for i, x in enumerate( assorted_data_dicts_i['t'] ) if ( this_tech in x ) and ( int( query_year ) in x ) and ( 'DistanceDriven' in x ) ]
                                    if len(value_indices) != 0:
                                        data_index =  value_indices[0]
                                        this_Q_km = float( assorted_data_dicts_i['t'][ data_index ][-1] )

                                    this_Q_f = 0
                                    age_list_raw = list( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ].keys() )
                                    age_list = [ i for i in age_list_raw if type(i) == int ]
                                    for a in age_list:
                                        this_Q_f += fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ][ a ]

                                    this_Q += this_Q_km*this_Q_f

                                if y == 0:
                                    dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ].update( { this_tech:{} } )
                                dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ].update( { query_year:this_Q } )

                        if this_tax == 'Property' or this_tax == 'Imports':
                            if this_Q_sum != 0:
                                dict_VP_per_actor_per_tax_per_tech[ this_actor ][ this_tax ].update( { query_year:this_Q_times_P/this_Q_sum } )

            # PART E)
            # Now the purpose of this component is to find the current MUSD value that should be added, per unit, to the price of the good.
            dict_strategy_tax_tech_price = {}
            for t1 in range( len( df_tax_assign_list_unique ) ):
                unique_tech_for_iuc_and_electromobility = []

                this_tax = df_tax_assign_list_unique[t1]
                df_tax_assign_local = df_tax_assign.loc[ df_tax_assign['Tax'] == df_tax_assign_list_unique[t1] ]
                dict_strategy_tax_tech_price.update( { df_tax_assign_list_unique[t1]:{} } )

                df_tech_assign_list = df_tax_assign_local['Technology'].tolist()
                df_fuel_assign_list = df_tax_assign_local['Fuel'].tolist()

                for t2 in range( len( df_tech_assign_list ) ):
                    this_tech = df_tech_assign_list[t2]
                    this_fuel = df_fuel_assign_list[t2]

                    if this_tax in ['Electromobility', 'IUC', 'Energy']:
                        if this_tech not in unique_tech_for_iuc_and_electromobility:
                            unique_tech_for_iuc_and_electromobility.append( this_tech )
                            dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ].update( { this_tech:{} } )
                            dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ].update( { this_fuel:{} } )
                        else:
                            dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ].update( { this_fuel:{} } )
                    else:
                        dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ].update( { this_tech:{} } )

                    for y in range( len( time_range_vector ) ):
                        query_year = time_range_vector[y]
                        if this_tax in ['Electromobility', 'IUC', 'Energy']:
                            dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ][ this_fuel ].update( { query_year:{ 'price_change':{} } } )
                        else:
                            if this_tax == 'Property':
                                dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ].update( { query_year:{} } )
                                for a in list( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ].keys() ):
                                    dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ][ query_year ].update( { a:{ 'price_change':{} } } )

                            if this_tax == 'Imports':
                                dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ].update( { query_year:{} } )
                                for a in list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ].keys() ):
                                    dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ][ query_year ].update( { a:{ 'price_change':{} } } )

                            if this_tax == 'VMT':
                                dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ].update( { query_year:{ 'price_change':{} } } )
                        for n in range( len( df_strategies_list_unique ) ):
                            if this_tax in ['Electromobility', 'IUC', 'Energy']:
                                dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ].update( { df_strategies_list_unique[n]:0 } )
                            else:
                                if this_tax == 'Property':
                                    for a in list( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ].keys() ):
                                        dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ][ query_year ][ a ][ 'price_change' ].update( { df_strategies_list_unique[n]:0 } )
                                if this_tax == 'Imports':
                                    for a in list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ].keys() ):
                                        dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ][ query_year ][ a ][ 'price_change' ].update( { df_strategies_list_unique[n]:0 } )
                                if this_tax == 'VMT':
                                    dict_strategy_tax_tech_price[ df_tax_assign_list_unique[t1] ][ this_tech ][ query_year ][ 'price_change' ].update( { df_strategies_list_unique[n]:0 } )

            # OPTIMIZATION
            # All controllers are open, now let's perform the optimization every year.
            actor_j_contribution = {}
            for y in range( len( time_range_vector_applicable ) ):
                query_year = time_range_vector_applicable[y]

                BAU_Government_Revenue_yearly.append( deepcopy( BAU_Government_Revenue.loc[ BAU_Government_Revenue['Year'].isin( [ query_year ] ) ] ) )
                This_Scenario_Government_Revenue_yearly.append( deepcopy( This_Scenario_Government_Revenue.loc[ This_Scenario_Government_Revenue['Year'].isin( [ query_year ] ) ] ) )

                for j in actor_j_list:
                    # We had used this for the single-year approach, but we will act with averages instead:
                    this_BAU_Actor_Costs_yearly = deepcopy( BAU_Actor_Costs[j].loc[ BAU_Actor_Costs[j]['Year'].isin( [ query_year ] ) ] )
                    BAU_Actor_Costs_yearly[j].append( deepcopy( this_BAU_Actor_Costs_yearly.loc[ this_BAU_Actor_Costs_yearly['GorS'] == 'Spend' ] ) )

                    this_NDP_Actor_Costs_yearly = deepcopy( This_Scenario_Actor_Costs[j].loc[ This_Scenario_Actor_Costs[j]['Year'].isin( [ query_year ] ) ] )
                    This_Scenario_Actor_Costs_yearly[j].append( deepcopy( this_NDP_Actor_Costs_yearly.loc[ this_NDP_Actor_Costs_yearly['GorS'] == 'Spend' ] ) )

                    #---------------------------------------------------------#
                    # $*$ we should include income later on, i.e. GorS = Gather
                    this_BAU_Actor_Income_yearly = deepcopy( BAU_Actor_Income[j].loc[ BAU_Actor_Income[j]['Year'].isin( [ query_year ] ) ] )
                    BAU_Actor_Income_yearly[j].append( deepcopy( this_BAU_Actor_Income_yearly.loc[ this_BAU_Actor_Income_yearly['GorS'] == 'Gather' ] ) )

                    this_NDP_Actor_Income_yearly = deepcopy( This_Scenario_Actor_Income[j].loc[ This_Scenario_Actor_Income[j]['Year'].isin( [ query_year ] ) ] )
                    This_Scenario_Actor_Income_yearly[j].append( deepcopy( this_NDP_Actor_Income_yearly.loc[ this_NDP_Actor_Income_yearly['GorS'] == 'Gather' ] ) )

                This_Scenario_relative_revenue_shortfall_total.update( { query_year:0 } )
                for j in actor_j_list:
                    This_Scenario_relative_benefit_per_actor_total.update( { j:{ query_year:0 } } )

                if y == 0: # We are creating here the dictionaries / we had never created them before
                    for a_tax in range( len( tax_type_list ) ):
                        BAU_revenue_per_tax_type.update( { tax_type_list[a_tax]:{} } )
                        This_Scenario_revenue_per_tax_type.update( { tax_type_list[a_tax]:{} } )
                        This_Scenario_relative_revenue_shortfall_per_tax_type.update( { tax_type_list[a_tax]:{} } )

                    for j in actor_j_list:
                        BAU_expenses_per_actor_per_exp_type.update( { j:{} } )
                        This_Scenario_expenses_per_actor_per_exp_type.update( { j:{} } )
                        This_Scenario_relative_benefit_per_actor_per_exp_type.update( { j:{} } )

                        for a_expense in range( len( actor_expense_list ) ):
                            BAU_expenses_per_actor_per_exp_type[j].update( { actor_expense_list[ a_expense ]:{} } )
                            This_Scenario_expenses_per_actor_per_exp_type[j].update( { actor_expense_list[ a_expense ]:{} } )
                            This_Scenario_relative_benefit_per_actor_per_exp_type[j].update( { actor_expense_list[ a_expense ]:{} } )

                for a_tax in range( len( tax_type_list ) ):
                    BAU_Government_Revenue_yearly[-1][ tax_type_list[a_tax] ] = BAU_Government_Revenue_yearly[-1][ tax_type_list[a_tax] ].fillna(0.0) # This is a column
                    This_Scenario_Government_Revenue_yearly[-1][ tax_type_list[a_tax] ] = This_Scenario_Government_Revenue_yearly[-1][ tax_type_list[a_tax] ].fillna(0.0) # This is a column

                    BAU_revenue_per_tax_type[ tax_type_list[a_tax] ].update( { query_year:sum( BAU_Government_Revenue_yearly[-1][ tax_type_list[a_tax] ].tolist() ) } )
                    This_Scenario_revenue_per_tax_type[ tax_type_list[a_tax] ].update( { query_year:sum( This_Scenario_Government_Revenue_yearly[-1][ tax_type_list[a_tax] ].tolist() ) } )

                    this_difference = BAU_revenue_per_tax_type[ tax_type_list[a_tax] ][ query_year ] - This_Scenario_revenue_per_tax_type[ tax_type_list[a_tax] ][ query_year ]
                    This_Scenario_relative_revenue_shortfall_per_tax_type[ tax_type_list[a_tax] ].update( { query_year:this_difference } )

                    This_Scenario_relative_revenue_shortfall_total[ query_year ] += deepcopy( this_difference )

                # Let us avoid adjusting "negative shortfalls" that don't make sense, or even very low ones:
                if This_Scenario_relative_revenue_shortfall_total[ query_year ] < 0:
                    This_Scenario_relative_revenue_shortfall_total[ query_year ] = 0

                # We must call the distributed cost per actor from the distributed cost actors (without adjustment), for the particular year:
                sum_actor_benefit = 0
                for j in actor_j_list:
                    for a_expense in range( len( actor_expense_list ) ):
                        BAU_Actor_Costs_yearly[j][-1][ actor_expense_list[a_expense] ] = BAU_Actor_Costs_yearly[j][-1][ actor_expense_list[a_expense] ].fillna(0.0) # This is a column
                        This_Scenario_Actor_Costs_yearly[j][-1][ actor_expense_list[a_expense] ] = This_Scenario_Actor_Costs_yearly[j][-1][ actor_expense_list[a_expense] ].fillna(0.0) # This is a column

                        BAU_expenses_per_actor_per_exp_type[j][ actor_expense_list[ a_expense ] ].update( { query_year:sum( BAU_Actor_Costs_yearly[j][-1][ actor_expense_list[a_expense] ].tolist() ) } )
                        This_Scenario_expenses_per_actor_per_exp_type[j][ actor_expense_list[ a_expense ] ].update( { query_year:sum( This_Scenario_Actor_Costs_yearly[j][-1][ actor_expense_list[a_expense] ].tolist() ) } )

                        these_BAU_expenses = BAU_expenses_per_actor_per_exp_type[j][ actor_expense_list[ a_expense ] ][ query_year ]
                        these_PdD_expenses = This_Scenario_expenses_per_actor_per_exp_type[j][ actor_expense_list[ a_expense ] ][ query_year ]

                        this_relative_benefit = these_BAU_expenses - these_PdD_expenses

                        This_Scenario_relative_benefit_per_actor_per_exp_type[j][ actor_expense_list[ a_expense ] ].update( { query_year:this_relative_benefit } )

                        This_Scenario_relative_benefit_per_actor_total[j][ query_year ] += deepcopy( this_relative_benefit )
                        sum_actor_benefit += this_relative_benefit

                    for an_income in range( len( actor_income_list ) ):
                        BAU_Actor_Income_yearly[j][-1][ actor_income_list[an_income] ] = BAU_Actor_Income_yearly[j][-1][ actor_income_list[an_income] ].fillna(0.0) # This is a column
                        This_Scenario_Actor_Income_yearly[j][-1][ actor_income_list[an_income] ] = This_Scenario_Actor_Income_yearly[j][-1][ actor_income_list[an_income] ].fillna(0.0) # This is a column

                        these_BAU_incomes = sum( BAU_Actor_Income_yearly[j][-1][ actor_income_list[an_income] ].tolist() )
                        these_PdD_incomes = sum( This_Scenario_Actor_Income_yearly[j][-1][ actor_income_list[an_income] ].tolist() )

                        this_relative_benefit = these_PdD_incomes - these_BAU_incomes

                        This_Scenario_relative_benefit_per_actor_total[j][ query_year ] += deepcopy( this_relative_benefit )
                        sum_actor_benefit += this_relative_benefit

                average_actor_benefit = sum_actor_benefit / len( actor_j_list )

                # THIS CODE BLEOW IS KEY IF WE WANT TO LATER EXPLORE
                # THE EFFECTS OF SUBSIDIES (ANAÑYZE AND TRY TO REMEMBER WHAT
                # THIS WAS)
                c_jt_max_dict.update( { query_year:{} } )
                benefits_per_actor.update( { query_year:{} } )
                shape_restrictions.update( { query_year:{} } )
                for j in actor_j_list:
                    benefit_sa_j = This_Scenario_relative_benefit_per_actor_total[j][ query_year ]
                    average_benefit_ca_j = average_actor_benefit

                    if benefit_sa_j - average_benefit_ca_j > 0:
                        c_jt_max_dict[ query_year ].update( { j: benefit_sa_j - average_benefit_ca_j } )
                    else:
                        c_jt_max_dict[ query_year ].update( { j:0 } )

                    benefits_per_actor[ query_year ].update( { j: benefit_sa_j } )

                    if benefit_sa_j > 0:
                        shape_restrictions[ query_year ].update( { j: 0 } )
                    else:
                        shape_restrictions[ query_year ].update( { j: benefit_sa_j } )

                # The code below optimizes min/max without subsidies:
                # Size of variables:
                lengekko = len( actor_j_list ) + 1
                benj1 = benefits_per_actor[ query_year ][ actor_j_list[ 0 ] ] # 'bus_companies'
                benj2 = benefits_per_actor[ query_year ][ actor_j_list[ 1 ] ] # 'special_transport_companies'
                benj3 = benefits_per_actor[ query_year ][ actor_j_list[ 2 ] ] # 'taxi_industry'
                benj4 = benefits_per_actor[ query_year ][ actor_j_list[ 3 ] ] # 'light_truck_companies'
                benj5 = benefits_per_actor[ query_year ][ actor_j_list[ 4 ] ] # 'heavy_freight_companies'
                benj6 = benefits_per_actor[ query_year ][ actor_j_list[ 5 ] ] # 'private_transport_owners'
                benTotal = benj1 + benj2 + benj3 + benj4 + benj5 + benj6

                shaperes1 = shape_restrictions[ query_year ][ actor_j_list[ 0 ] ] # 'bus_companies'
                shaperes2 = shape_restrictions[ query_year ][ actor_j_list[ 1 ] ] # 'special_transport_companies'   
                shaperes3 = shape_restrictions[ query_year ][ actor_j_list[ 2 ] ] # 'taxi_industry'   
                shaperes4 = shape_restrictions[ query_year ][ actor_j_list[ 3 ] ] # 'light_truck_companies'   
                shaperes5 = shape_restrictions[ query_year ][ actor_j_list[ 4 ] ] # 'heavy_freight_companies'   
                shaperes6 = shape_restrictions[ query_year ][ actor_j_list[ 5 ] ] # 'private_transport_owners'   

                mg = GEKKO(remote=False)
                mg.options.SOLVER = 1
                v1, v2, v3, v4, v5, v6, Z = mg.Array( mg.Var, lengekko )
                mg.Maximize(Z)
                mg.Equation( v1+v2+v3+v4+v5+v6 == This_Scenario_relative_revenue_shortfall_total[ query_year ] )
                # mg.Equations( [ Z<=benj1-v1, Z<=benj2-v2, Z<=benj3-v3, Z<=benj3-v3, Z<=benj4-v4, Z<=benj5-v5, Z<=benj6-v6,
                #                 v1>=0, v2>=0, v3>=0, v4>=0, v5>=0, v6>=0,
                #                 benj1-v1>=shaperes1, benj2-v2>=shaperes2, benj3-v3>=shaperes3, benj4-v4>=shaperes4, benj5-v5>=shaperes5, benj6-v6>=shaperes6 ] )
                mg.Equations( [ Z<=benj1-v1, Z<=benj2-v2, Z<=benj3-v3, Z<=benj4-v4, Z<=benj5-v5, Z<=benj6-v6,
                                v1>=0, v2>=0, v3>=0, v4>=0, v5>=0, v6>=0,
                                benj1-v1>shaperes1, benj2-v2>shaperes2, benj3-v3>shaperes3, benj4-v4>shaperes4, benj5-v5>shaperes5, benj6-v6>shaperes6 ] )  
                try:
                    mg.solve()
                except:
                    # For some futures, the optimization is infeasible because positive benefits are smaller than the fiscal impact. In this case, we allow actors with negative benefits to pay more taxes, in order to have a zero fiscal impact.                
                    mg = GEKKO(remote=False)
                    mg.options.SOLVER = 1
                    v1,v2,v3,v4,v5,v6,Z = mg.Array( mg.Var, lengekko )
                    mg.Maximize(Z)
                    mg.Equation( v1+v2+v3+v4+v5+v6 == This_Scenario_relative_revenue_shortfall_total[ query_year ] * ( 1 - iuc_subtract[ query_year ] ) )
                    mg.Equations( [ Z<=benj1-v1, Z<=benj2-v2, Z<=benj3-v3, Z<=benj4-v4, Z<=benj5-v5, Z<=benj6-v6,
                                    v1>=0, v2>=0, v3>=0, v4>=0, v5>=0, v6>=0 ] )  
                    mg.solve()

                contributions = v1.value[0] + v2.value[0] + v3.value[0] + v4.value[0] + v5.value[0] + v6.value[0]
                #------------------------------------------------------#
                if v1.value[0] > 0:
                    v1_value = v1.value[0]
                else:
                    v1_value = 0

                if v2.value[0] > 0:
                    v2_value = v2.value[0]
                else:
                    v2_value = 0

                if v3.value[0] > 0:
                    v3_value = v3.value[0]
                else:
                    v3_value = 0

                if v4.value[0] > 0:
                    v4_value = v4.value[0]
                else:
                    v4_value = 0

                if v5.value[0] > 0:
                    v5_value = v5.value[0]
                else:
                    v5_value = 0

                if v6.value[0] > 0:
                    v6_value = v6.value[0]
                else:
                    v6_value = 0
                #------------------------------------------------------#
                verification_file.write( str( query_year ) )
                print_this_string = 'Shortfall: ' + str( This_Scenario_relative_revenue_shortfall_total[ query_year ] ) + '\n'
                verification_file.write( print_this_string )

                print_this_string = '\n\n'
                verification_file.write( print_this_string )

                print_this_string = 'Contribution of Bus companies: ' + str( v1_value ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Contribution of Special Transport companies: ' + str( v2_value ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Contribution of Taxi companies: ' + str( v3_value ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Contribution of Light Truck companies: ' + str( v4_value ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Contribution of Heavy Truck companies: ' + str( v5_value ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Contribution of Private companies: ' + str( v6_value ) + '\n'
                verification_file.write( print_this_string )

                print_this_string = '\n\n'
                verification_file.write( print_this_string )

                print_this_string = 'Previous benefits Bus companies: ' + str( benj1 ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Previous benefits Special Transport companies: ' + str( benj2 ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Previous benefits Taxi companies: ' + str( benj3 ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Previous benefits Light Truck companies: ' + str( benj4 ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Previous benefits Heavy Truck companies: ' + str( benj5 ) + '\n'
                verification_file.write( print_this_string )
                print_this_string = 'Previous benefits Private companies: ' + str( benj6 ) + '\n'
                verification_file.write( print_this_string )

                print_this_string = '\n\n'
                verification_file.write( print_this_string )
                print_this_string = '#################################################'
                verification_file.write( print_this_string )
                #------------------------------------------------------#
                actor_j_contribution.update( params['query_year'] )

            # ADJUSTMENT CALCULATION:
            # The optimization part is executed. Now, let's do the distribution of the contributions:
            for j in range( len( actor_j_list ) ):
                this_actor = actor_j_list[j]

                tax_list = list( dict_Q_per_actor_per_tax_per_tech[ this_actor ].keys() )
                for t1 in range( len( tax_list ) ):
                    this_tax = tax_list[ t1 ]

                    tech_list = list( dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ].keys() )

                    for n in range( len( df_strategies_list_unique ) ):
                        k_list = list( dict_strategy_controller[ df_strategies_list_unique[n] ][ this_tax ].keys() )
                        for k in range( len( k_list ) ):
                            this_k = k_list[k]

                            for y in range( len( time_range_vector_applicable ) ): # this is the maximum depth of the analysis
                                total_Q = 0 # we have to sum all the technologies that are pertinent
                                query_year = time_range_vector_applicable[y]

                                query_type_list = dict_strategy_controller[ df_strategies_list_unique[n] ][ this_tax ][ this_k ][ query_year ]['Type']
                                for t2 in range( len( tech_list ) ):
                                    this_tech = tech_list[ t2 ] # could be a fuel or a tech
                                    tech_math_type = dict_Q_type_match[ this_tax ][ this_tech ][ 'type' ]

                                    if ( tech_math_type in query_type_list ) or ( 'ALL' in query_type_list ): # means this is an adequate match for the controller type, and that assignations can procede
                                        if this_tax in ['Electromobility', 'IUC', 'Energy']:
                                            fuel_list = list( dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ].keys() )
                                            for f in range( len( fuel_list ) ):
                                                this_fuel = fuel_list[f]
                                                total_Q += dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ][ this_fuel ][ query_year ]

                                        else:
                                            total_Q += dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ][ query_year ]

                                query_fuel = dict_strategy_controller[ df_strategies_list_unique[n] ][ this_tax ][ this_k ][ query_year ]['Type'] # assume there is only 1 fuel

                                if total_Q != 0:
                                    this_contribution = actor_j_contribution[ query_year ][ this_actor ]
                                    monetary_slice_of_contribution = this_contribution * dict_strategy_controller[ df_strategies_list_unique[n] ][ this_tax ][ this_k ][ query_year ]['Value']/100
                                    monetary_slice_of_contribution_unit = monetary_slice_of_contribution/total_Q

                                    for t2 in range( len( tech_list ) ):
                                        this_tech = tech_list[ t2 ] # could be a fuel or a tech
                                        if this_tax in ['Electromobility', 'Energy']:
                                            fuel_list = list( dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ].keys() )
                                            for f in range( len( fuel_list ) ):
                                                this_fuel = fuel_list[f]
                                                dict_strategy_tax_tech_price[ this_tax ][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ][ df_strategies_list_unique[n] ] += monetary_slice_of_contribution_unit

                                        if this_tax in ['IUC'] and ( 'GSL' in query_fuel or 'LPG' in query_fuel ) and ( this_tech in list( dict_Q_iuc_per_tech['GSL'].keys() ) ):
                                            monetary_slice_of_iuc = This_Scenario_relative_revenue_shortfall_total[ query_year ] * dict_strategy_controller[ df_strategies_list_unique[n] ][ this_tax ][ this_k ][ query_year ]['Value']/100
                                            total_Q_iuc = dict_Q_iuc_whole['GSL'][ query_year ]
                                            # if total_Q_iuc != 0:
                                            monetary_slice_of_iuc_unit = monetary_slice_of_iuc / total_Q_iuc
 
                                            fuel_list = list( dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ].keys() )
                                            for f in range( len( fuel_list ) ):
                                                this_fuel = fuel_list[f]
                                                dict_strategy_tax_tech_price[ this_tax ][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ][ df_strategies_list_unique[n] ] += monetary_slice_of_iuc_unit

                                        if this_tax in ['IUC'] and ( 'DSL' in query_fuel ) and ( this_tech in list( dict_Q_iuc_per_tech['DSL'].keys() ) ):
                                            monetary_slice_of_iuc = This_Scenario_relative_revenue_shortfall_total[ query_year ] * dict_strategy_controller[ df_strategies_list_unique[n] ][ this_tax ][ this_k ][ query_year ]['Value']/100
                                            total_Q_iuc = dict_Q_iuc_whole['DSL'][ query_year ]
                                            # if total_Q_iuc != 0:
                                            monetary_slice_of_iuc_unit = monetary_slice_of_iuc / total_Q_iuc

                                            fuel_list = list( dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ].keys() )
                                            for f in range( len( fuel_list ) ):
                                                this_fuel = fuel_list[f]
                                                dict_strategy_tax_tech_price[ this_tax ][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ][ df_strategies_list_unique[n] ] += monetary_slice_of_iuc_unit
                                        '''
                                        if this_tax in ['IUC'] and ( 'LPG' in query_fuel ) and ( this_tech in list( dict_Q_iuc_per_tech['LPG'].keys() ) ):
                                            monetary_slice_of_iuc = This_Scenario_relative_revenue_shortfall_total[ query_year ] * dict_strategy_controller[ df_strategies_list_unique[n] ][ this_tax ][ this_k ][ query_year ]['Value']/100
                                            total_Q_iuc = dict_Q_iuc_whole['LPG'][ query_year ]
                                            # if total_Q_iuc != 0:
                                            monetary_slice_of_iuc_unit = monetary_slice_of_iuc / total_Q_iuc
                                            #
                                            fuel_list = list( dict_Q_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ this_tech ].keys() )
                                            for f in range( len( fuel_list ) ):
                                                this_fuel = fuel_list[f]
                                                dict_strategy_tax_tech_price[ this_tax ][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ][ df_strategies_list_unique[n] ] += monetary_slice_of_iuc_unit
                                            #
                                        '''
                                        if this_tax not in ['Electromobility', 'IUC', 'Energy']:
                                            #
                                            if this_tax == 'Property':
                                                for a in list( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ].keys() ):
                                                    #
                                                    this_price_change = monetary_slice_of_contribution_unit * dict_Value_per_actor_per_tax_per_tech_property[ this_actor ][ this_tech ][ query_year ][a] / dict_VP_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ query_year ]
                                                    dict_strategy_tax_tech_price[ this_tax ][ this_tech ][ query_year ][ a ][ 'price_change' ][ df_strategies_list_unique[n] ] += deepcopy( this_price_change )

                                            if this_tax == 'Imports':
                                                #
                                                for a in list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ].keys() ):
                                                    this_price_change = monetary_slice_of_contribution_unit * dict_Value_per_actor_per_tax_per_tech_imports[ this_actor ][ this_tech ][ query_year ][a] / dict_VP_per_actor_per_tax_per_tech[ this_actor ][ this_tax ][ query_year ]
                                                    dict_strategy_tax_tech_price[ this_tax ][ this_tech ][ query_year ][ a ][ 'price_change' ][ df_strategies_list_unique[n] ] += deepcopy( this_price_change )

                                            if this_tax == 'VMT':
                                                dict_strategy_tax_tech_price[ this_tax ][ this_tech ][ query_year ][ 'price_change' ][ df_strategies_list_unique[n] ] += monetary_slice_of_contribution_unit

                                else:
                                    if query_year == 2025:
                                        print('careful with', this_actor, this_tax, df_strategies_list_unique[n], this_k, query_type_list, query_year)

            verification_file.close()
            '''
            Now, the results of the optimization and distribution are going to be used to update prices, for each stated strategy: 
            '''
            for an_n in range( len( df_strategies_list_unique ) ):
                # Before starting the quantification of the average additional tax per period-after-milestone-year, we must define some general copies of data that would enable us future adjustments.
                #   A.0) For MaxImport Prices:
                df_Unit_T_ImportVAT_new = deepcopy( df_Unit_T_ImportVAT )
                df_Unit_T_GananciaEstimada_new = deepcopy( df_Unit_T_GananciaEstimada )
                df_Unit_T_TotalTaxes_new = deepcopy( df_Unit_T_TotalTaxes )
                df_Unit_T_MarketPrice_new = deepcopy( df_Unit_T_MarketPrice )
                df_Rates_T_SelectivoAlConsumo_new = deepcopy( df_Rates_T_SelectivoAlConsumo ) # this is the mechanism we want to control for the import taxes.
                df_Unit_T_SelectivoAlConsumo_new = deepcopy( df_Unit_T_SelectivoAlConsumo )

                #   B.0) For MaxProperty Taxes:
                dict_Unit_PropertyTax_new = deepcopy( dict_Unit_PropertyTax )

                #   C.0) For MaxEnergy Taxes:
                df_Rates_TF_IUC_new = deepcopy( df_Rates_TF_IUC )
                df_Rates_TF_H2_new = deepcopy( df_Rates_TF_H2 )
                df_Rates_TF_ElectricityVAT_new = deepcopy( df_Rates_TF_ElectricityVAT )

                df_Unit_TF_IUC_new = deepcopy( df_Unit_TF_IUC )
                df_Unit_TF_H2_new = deepcopy( df_Unit_TF_H2 )
                df_Unit_TF_ElectricityVAT_new = deepcopy( df_Unit_TF_ElectricityVAT )

                this_n = df_strategies_list_unique[an_n] # we gotta do this for each alternative strategy

                # This is key, gotta be used as a new feature of the system:
                this_vmt_rates_per_tech = {}
                for y2 in range( time_range_vector[0], time_range_vector_applicable[0] ):
                    this_vmt_rates_per_tech.update( { y2:{} } )

                for y in range( len( time_range_vector_applicable ) ):
                    query_year = time_range_vector_applicable[y]

                    # SECTION FOR IMPORTS:
                    technologies_that_pay_imports = list( dict_strategy_tax_tech_price['Imports'].keys() )
                    for t in range( len( technologies_that_pay_imports ) ):
                        this_tech = technologies_that_pay_imports[t]
                        list_ages_raw = list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ query_year ].keys() )
                        list_ages = [ i for i in list_ages_raw if type(i) == int ]

                        for a in range( len( list_ages ) ):
                            age_y = list_ages[ a ]

                            # *Call the unit monetary change*:
                            delta_Timp = float( dict_strategy_tax_tech_price['Imports'][ this_tech ][ query_year ][ age_y ][ 'price_change' ][ this_n ] ) * 1e6

                            this_import_VAT_rate = deepcopy( df_Rates_T_ImportVAT[ query_year ][ this_tech ][ age_y ] )
                            this_GE_rate = deepcopy( df_Rates_T_GananciaEstimada[ query_year ][ this_tech ][ age_y ] )

                            this_old_market_price = deepcopy( df_Unit_T_MarketPrice[ query_year ][ this_tech ][ age_y ] )

                            delta_SC = deepcopy( delta_Timp )/( 1 + this_import_VAT_rate/100 )

                            # So we must simply calculate the new unit SC, as well as the new rate //// we STORE here as well:
                            if float( df_Unit_T_CIF[ query_year ][ this_tech ][ age_y ] ) != 0.0:
                                df_Unit_T_SelectivoAlConsumo_new[ query_year ][ this_tech ][ age_y ] = deepcopy( df_Unit_T_SelectivoAlConsumo[ query_year ][ this_tech ][ age_y ] ) + 1.005*delta_SC
                                df_Rates_T_SelectivoAlConsumo_new[ query_year ][ this_tech ][ age_y ] = 100*deepcopy( round( df_Unit_T_SelectivoAlConsumo_new[ query_year ][ this_tech ][ age_y ] / df_Unit_T_CIF[ query_year ][ this_tech ][ age_y ], 4 ) )

                                #****************************************
                                if df_Unit_T_SelectivoAlConsumo_new[ query_year ][ this_tech ][ age_y ] < (-1e-9):
                                    print( 'ALERT ', query_year, this_tech, c, delta_SC, df_Unit_T_SelectivoAlConsumo_new[ query_year ][ this_tech ][ age_y ] )
                                    print( '-----------' )
                                #****************************************

                                # We must recalculate the variables from below according to the updated taxes //// starting with the fixed unit-values:
                                component_1 = deepcopy( df_Unit_T_CIF[ query_year ][ this_tech ][ age_y ] )
                                component_2 = deepcopy( df_Unit_T_SelectivoAlConsumo_new[ query_year ][ this_tech ][ age_y ] )
                                component_3 = deepcopy( df_Unit_T_ValorAduanero[ query_year ][ this_tech ][ age_y ] )                            
                                component_4 = deepcopy( df_Unit_T_DerechoArancelario[ query_year ][ this_tech ][ age_y ] )                            

                                this_cif_with_import_taxes = component_1 + component_2 + component_3 + component_4
                                this_GE_unit = ( this_GE_rate/100 )*component_1
                                this_VAT_unit = ( this_import_VAT_rate/100 )*( this_cif_with_import_taxes + this_GE_unit )

                                this_market_price = ( 1 + this_import_VAT_rate/100 )*( this_cif_with_import_taxes + this_GE_unit )

                                # Let us store our findings:
                                df_Unit_T_ImportVAT_new[ query_year ][ this_tech ][ age_y ] = deepcopy( this_VAT_unit )
                                df_Unit_T_GananciaEstimada_new[ query_year ][ this_tech ][ age_y ] = deepcopy( this_GE_unit )
                                df_Unit_T_TotalTaxes_new[ query_year ][ this_tech ][ age_y ] = deepcopy( component_2 + component_3 + component_4 + this_VAT_unit ) # these are only import taxes
                                df_Unit_T_MarketPrice_new[ query_year ][ this_tech ][ age_y ] = deepcopy( this_market_price )

                        # The update on import taxes is finished!

                    # SECTION FOR PROPERTY:
                    technologies_that_pay_property = list( dict_strategy_tax_tech_price['Property'].keys() )
                    for t in range( len( technologies_that_pay_property ) ):
                        this_tech = technologies_that_pay_property[t]

                        # We must assign the contribution based on the age. We will have to use this very same approach for the imports when we update the model: 
                        list_ages_raw = list( dict_Unit_PropertyTax[ this_tech ][ query_year ].keys() )
                        list_ages = [ i for i in list_ages_raw if type(i) == int ]

                        valid_ages = list( fleet_Q_perTech_perYear_per_age[ this_tech ][ query_year ].keys() )

                        for a in range( len( list_ages ) ):
                            age_y = list_ages[ a ]

                            if age_y in valid_ages:
                                # *Call the unit monetary change*:
                                delta_Tf = dict_strategy_tax_tech_price['Property'][ this_tech ][ query_year ][ age_y ][ 'price_change' ][ this_n ] * 1e6

                                dict_Unit_PropertyTax_new[ this_tech ][ query_year ][ age_y ] += deepcopy( delta_Tf )
                    
                    # SECTION FOR VMT:
                    technologies_that_pay_vmt = list( dict_strategy_tax_tech_price['VMT'].keys() )
                    this_vmt_rates_per_tech.update( { query_year:{} } )

                    for t in range( len( technologies_that_pay_vmt ) ):
                        this_tech = technologies_that_pay_vmt[t]

                        if query_year == time_range_vector_applicable[0]:
                            for y2 in range( time_range_vector[0], time_range_vector_applicable[0] ):
                                this_vmt_rates_per_tech[ y2 ].update( { this_tech:0 } )

                        this_vmt_rate = dict_strategy_tax_tech_price['VMT'][ this_tech ][ query_year ][ 'price_change' ][ this_n ]
                        this_vmt_rates_per_tech[ query_year ].update( { this_tech:this_vmt_rate } )

                    techs_IUC = df_Unit_TF_IUC['Technology'].tolist()
                    techs_electricity = df_Unit_TF_ElectricityVAT['Technology'].tolist()
                    techs_H2 = df_Unit_TF_H2['Technology'].tolist()

                    # First, let's update the IUC:
                    for t in range( len( techs_IUC ) ):
                        this_tech = techs_IUC[ t ]
                        if this_tech in list( dict_strategy_tax_tech_price['IUC'].keys() ):
                            for this_fuel in list( dict_strategy_tax_tech_price['IUC'][ this_tech ].keys() ):

                                this_additional_tax = dict_strategy_tax_tech_price['IUC'][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ][ this_n ]

                                rate_index_list_tech = df_Unit_TF_IUC['Technology'].tolist()
                                rate_index_list_fuel = df_Unit_TF_IUC['Fuel'].tolist()

                                rate_row_index_tech = [i for i, x in enumerate(rate_index_list_tech) if x == this_tech]
                                rate_row_index_fuel = [i for i, x in enumerate(rate_index_list_fuel) if x == this_fuel]
                                rate_row_index_list = intersection_2(rate_row_index_tech , rate_row_index_fuel)

                                if len( rate_row_index_list ) != 0:
                                    rate_row_index = rate_row_index_list[0]
                                    horizon_year_index = time_range_vector.index( query_year )
                                    # horizon_year_index = time_range_vector.index( query_year ) # seems unused
                                    df_Unit_TF_IUC_new.loc[ rate_row_index, query_year ] += deepcopy( this_additional_tax )
                                    # Following line 4350 and surroundings, we must apply some conversions to obtain the rate in the original units.
                                    if 'DSL' in this_tech: # $*$ Here we pick automotive-type diesel
                                        from_L_to_PJ = 38.6*(1e-9) # MJ/l * PJ/MJ = PJ/L
                                    elif 'GSL' in this_tech: # $*$ Here we pick automotive-type gasoline
                                        from_L_to_PJ = 34.2*(1e-9) # MJ/l * PJ/MJ = PJ/L
                                    elif 'LPG' in this_tech: # $*$ We will use a mixture of propane and butane
                                        from_L_to_PJ = 25.7*(1e-9) # MJ/l * PJ/MJ = PJ/L

                                    df_Rates_TF_IUC_new.loc[ rate_row_index, query_year ] = deepcopy( df_Unit_TF_IUC_new.loc[ rate_row_index, query_year ] ) * ( from_L_to_PJ )*(1/1e6) * float( list_ER[horizon_year_index] )

                    # Second, let's update the Electromobility tax:
                    for t in range( len( techs_electricity ) ):
                        this_tech = techs_electricity[t]
                        if this_tech in list( dict_strategy_tax_tech_price['Electromobility'].keys() ):
                            for this_fuel in list( dict_strategy_tax_tech_price['Electromobility'][ this_tech ].keys() ):
                                this_additional_tax = dict_strategy_tax_tech_price['Electromobility'][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ][ this_n ]

                                rate_index_list_tech = df_Unit_TF_ElectricityVAT['Technology'].tolist()
                                rate_index_list_fuel = df_Unit_TF_ElectricityVAT['Fuel'].tolist()

                                rate_row_index_tech = [i for i, x in enumerate(rate_index_list_tech) if x == this_tech]
                                rate_row_index_fuel = [i for i, x in enumerate(rate_index_list_fuel) if x == this_fuel]
                                rate_row_index_list = intersection_2(rate_row_index_tech , rate_row_index_fuel)

                                if len( rate_row_index_list ) != 0:
                                    rate_row_index = rate_row_index_list[0]
                                    horizon_year_index = time_range_vector.index( query_year )

                                    df_Unit_TF_ElectricityVAT_new.loc[ rate_row_index, query_year ] += deepcopy( this_additional_tax )
                                    df_Rates_TF_ElectricityVAT_new.loc[ rate_row_index, query_year ] = deepcopy( round( df_Unit_TF_ElectricityVAT_new.loc[ rate_row_index, query_year ] / ElectricityPrice_vector[horizon_year_index], 4 ) )
 
                    # Third, let's update the H2 tax:
                    for t in range( len( techs_H2 ) ):
                        this_tech = techs_H2[t]
                        if this_tech in list( dict_strategy_tax_tech_price['Electromobility'].keys() ):
                            this_fuel = list( dict_strategy_tax_tech_price['Electromobility'][ this_tech ].keys() )[0]
                            this_additional_tax = dict_strategy_tax_tech_price['Electromobility'][ this_tech ][ this_fuel ][ query_year ][ 'price_change' ][ this_n ]

                            rate_index_list_tech = df_Unit_TF_H2['Technology'].tolist()
                            rate_index_list_fuel = df_Unit_TF_H2['Fuel'].tolist()

                            rate_row_index_tech = [i for i, x in enumerate(rate_index_list_tech) if x == this_tech]
                            rate_row_index_fuel = [i for i, x in enumerate(rate_index_list_fuel) if x == this_fuel]
                            rate_row_index_list = intersection_2(rate_row_index_tech , rate_row_index_fuel)

                            if len( rate_row_index_list ) != 0:
                                rate_row_index = rate_row_index_list[0]
                                horizon_year_index = time_range_vector.index( query_year )

                                df_Unit_TF_H2_new.loc[ rate_row_index, query_year ] += deepcopy( this_additional_tax )
                                df_Rates_TF_H2_new.loc[ rate_row_index, query_year ] += deepcopy( df_Unit_TF_H2_new.loc[ rate_row_index, query_year ] ) # we do not use any conversion here

                # B) Let's re-estimate all the transfers based on the compensation requirement:
                '''
                We must act on the TYPE 1 ACTORS first to get a grasp of the re-strcuturing of the system.
                '''
                results_list = []
                #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
                ''' 'TYPE 1 ACTORS - MODIFIED:' // Government '''
                print('Adjustment Part - Performing FCM_7 - Calculate government transfers') # skip, just see expenditures
                for n in range( len( type_1_actor ) ):
                    # Function 1a: gather_derecho_arancelario
                    print('     Within FCM_7 - RE-calculate *Derecho Arancelario* Revenue')
                    this_returnable = type_1_actor[n].gather_derecho_arancelario( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_DerechoArancelario , m , 'NO_df_new_Rates' )
                    lists_of_lists_to_print = deepcopy( this_returnable )
                    for l in range( len( lists_of_lists_to_print ) ):
                        results_list.append( lists_of_lists_to_print[l] )

                    # Function 1b: gather_valor_aduanero 
                    print('     Within FCM_7 - RE-calculate *Valor Aduanero* Revenue')
                    this_returnable = type_1_actor[n].gather_valor_aduanero( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_ValorAduanero , m , 'NO_df_new_Rates' )
                    lists_of_lists_to_print = deepcopy( this_returnable )
                    for l in range( len( lists_of_lists_to_print ) ):
                        results_list.append( lists_of_lists_to_print[l] )

                    ''' MODIFY THIS RATE ''' # Function 1c: gather_selectivo_al_consumo
                    print('     Within FCM_7 - ADJUST *Selectivo al Consumo* Revenue')
                    this_returnable = type_1_actor[n].gather_selectivo_al_consumo( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_SelectivoAlConsumo_new , m , 'NO_df_new_Rates' )
                    lists_of_lists_to_print = deepcopy( this_returnable )
                    for l in range( len( lists_of_lists_to_print ) ):
                        results_list.append( lists_of_lists_to_print[l] )

                    print('     Adjustment Part - *Selectivo al consumo* rates have been adjusted')
                    ''' MODIFY THIS RATE ''' # Function 1d: gather_import_vat
                    print('     Within FCM_7 - RE-calculate *Import VAT* Revenue')
                    this_returnable = type_1_actor[n].gather_import_vat( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_ImportVAT_new , m , 'NO_df_new_Rates' )
                    lists_of_lists_to_print = deepcopy( this_returnable )
                    for l in range( len( lists_of_lists_to_print ) ):
                        results_list.append( lists_of_lists_to_print[l] )

                    ''' We must adjust the resulting market price of the new vehicles based on the new taxes '''
                    # Function 1 PLUS: gather_total_import_taxes:
                    print('     Within FCM_7 - RE-calculate *Total Import Taxes* Revenue')
                    this_returnable = type_1_actor[n].gather_total_import_taxes( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_T_TotalTaxes_new , m , 'df_new_Rates' )
                    lists_of_lists_to_print = deepcopy( this_returnable )
                    for l in range( len( lists_of_lists_to_print ) ):
                        results_list.append( lists_of_lists_to_print[l] )

                    print('     Adjustment Part - *Import VAT* rates have been adjusted')

                    ''' MODIFY THIS RATE ''' # Function 2a: gather_iuc
                    print('     Within FCM_7 - Calculate *IUC* Revenue')
                    fuels_produced_by_techs = params['fuels_produced_by_techs_2']
                    for k in range( len( fuels_produced_by_techs ) ):
                        this_returnable = type_1_actor[n].gather_iuc( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_TF_IUC_new , m , fuels_produced_by_techs[k], 'df_new_Rates' )
                        lists_of_lists_to_print = deepcopy( this_returnable )
                        for l in range( len( lists_of_lists_to_print ) ):
                            results_list.append( lists_of_lists_to_print[l] )

                    print('     Adjustment Part - *IUC* rates have been adjusted')

                    ''' MODIFY THIS RATE ''' # Function 2b: gather_electricity_vat
                    print('     Within FCM_7 - Calculate *Electricity VAT* Revenue')
                    fuels_produced_by_techs = params['fuels_produced_by_techs_3']
                    for k in range( len( fuels_produced_by_techs ) ):
                        this_returnable = type_1_actor[n].gather_electricity_vat( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_TF_ElectricityVAT_new , m , fuels_produced_by_techs[k], 'df_new_Rates' )
                        lists_of_lists_to_print = deepcopy( this_returnable )
                        for l in range( len( lists_of_lists_to_print ) ):
                            results_list.append( lists_of_lists_to_print[l] )

                    print('     Adjustment Part - *Electricity VAT* rates have been adjusted')

                    ''' MODIFY THIS RATE ''' # Function 2c: gather_h2 (using "UseByTechnology")
                    print('     Within FCM_7 - Calculate *H2* Revenue')
                    fuels_used_by_techs = params['fuels_used_by_techs_5']
                    for k in range( len( fuels_used_by_techs ) ):
                        this_returnable = type_1_actor[n].gather_h2( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , df_Unit_TF_H2_new , m , fuels_used_by_techs[k] , 'NO_df_new_Rates' )
                        lists_of_lists_to_print = deepcopy( this_returnable )
                        for l in range( len( lists_of_lists_to_print ) ):
                            results_list.append( lists_of_lists_to_print[l] )

                    print('     Adjustment Part - *H2* rates have been adjusted')

                    ''' MODIFY THIS RATE ''' # Function 3: gather_property_tax
                    print('     Within FCM_7 - RE-calculate *Property Tax* Revenue') # the method must change slighly, but should be very similar for both cases.
                    this_returnable = type_1_actor[n].gather_property_tax( discounted_or_not, assorted_data_dicts, type_1_actor[n].techs_gather , type_1_actor[n].name_ID , type_1_actor[n].discount_rate , dict_Unit_PropertyTax_new , m , 'df_new_Rates' )
                    lists_of_lists_to_print = deepcopy( this_returnable )
                    for l in range( len( lists_of_lists_to_print ) ):
                        results_list.append( lists_of_lists_to_print[l] )
                #--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%--%
                print('Initial Part - Performing FCM_6 - Extracting Rates of Services Sales/Purchases')
                df_Rates_TF_SalesPurchasesService_new = deepcopy( df_Rates_TF_SalesPurchasesService )

                index_buses = df_Rates_TF_SalesPurchasesService['Technology'].tolist().index( 'Techs_Buses' )
                index_taxis = df_Rates_TF_SalesPurchasesService['Technology'].tolist().index( 'Techs_Taxis' )
                base_bus_rate = df_Rates_TF_SalesPurchasesService['Factor'].tolist()[ index_buses ]
                base_taxis_rate = df_Rates_TF_SalesPurchasesService['Factor'].tolist()[ index_taxis ]

                # ---
                # For *Buses*:
                fleet_techs = in_relationship_ownership['bus_companies']
                production_techs = in_relationship_sell['bus_companies']

                # Depreciation factors: already open

                BusPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
                BusPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
                BusPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
                BusPrice_variable_cost_vector = [ 0 for y in range( len(time_range_vector) ) ]
                BusPrice_external_fixed_cost = [ 0 for y in range( len(time_range_vector) ) ]
                BusPrice_produced_km = [ 0 for y in range( len(time_range_vector) ) ]

                for y in range( len( time_range_vector ) ):
                    # ---
                    prod_pass_km = 0 # here we should select the % of trips produced by the "concesionario" fleet
                    for t in range( len( production_techs ) ):
                        prod_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( production_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

                        if len(prod_tech_indices) != 0:
                            prod_tech_index =  prod_tech_indices[0]
                            this_pkm_production = float( assorted_data_dicts['t_f'][ prod_tech_index ][-1] )*1e9 # of 'Techs_Buses', unit in *kilometers*
                        else:
                            this_pkm_production = 0

                        prod_pass_km += this_pkm_production

                    BusPrice_produced_km[y] = prod_pass_km
                    # ---
                    capital_expense = 0
                    this_q_per_tech = [ 0 for t in range( len( fleet_techs ) ) ]
                    # We must use the fleet here:
                    for t in range( len( fleet_techs ) ):
                        this_tech = fleet_techs[t]
                        these_ages_raw = list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ].keys() )
                        these_ages = [ i for i in these_ages_raw if type(i) == int ]
                        this_inv = 0
                        for a in these_ages:
                            this_q_a = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ][ a ] # let's work only with the imported fleet in order to have a comparable methodology to electricity rate
                            this_market_price = df_Unit_T_MarketPrice[ time_range_vector[y] ][ this_tech ][ a ]
                            this_inv += this_q_a*this_market_price/1e6
                            this_q_per_tech[t] += this_q_a

                        capital_expense += this_inv

                    BusPrice_new_investments[y] = capital_expense

                    fill_y_counter = 0
                    for fill_y in range( y, len( time_range_vector ) ):
                        if fill_y <= y+15: # here we will replace the annualized approach with the depreciation/proift factor approach
                            depreciation_expense = capital_expense * df_bus_rates_dep_factor[ fill_y_counter ]
                            capital_profit_amount = capital_expense * df_bus_rates_profit_factor[ fill_y_counter ] * df_bus_rates_profit_rate[ fill_y_counter ]
                            BusPrice_annualized_new_investments_vector[fill_y] += depreciation_expense + capital_profit_amount
                            fill_y_counter += 1
                    # ---
                    technical_FOM = 0
                    for t in range( len( fleet_techs ) ):
                        fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'AnnualFixedOperatingCost' in x ) ]
                        if len(fleet_techs_indices) != 0:
                            fleet_tech_index =  fleet_techs_indices[0]
                            this_fleet_tech_FOM = float( assorted_data_dicts['t'][ fleet_tech_index ][-1] ) # of 'bus technology'
                        else:
                            this_fleet_tech_FOM = 0
                        technical_FOM += this_fleet_tech_FOM

                        try:  # add the km tax
                            technical_FOM += this_vmt_rates_per_tech[ time_range_vector[y] ][ fleet_techs[t] ]
                        except:
                            pass

                    BusPrice_fom_vector[y] = technical_FOM
                    # ---
                    external_fixed_costs = 0
                    external_fixed_costs_types = fixed_admin_costs_buses['Type'].tolist()
                    for t in range( len( external_fixed_costs_types ) ):
                        if t > 1:
                            growth_rate = fixed_admin_costs_buses['Growth'].tolist()[t]
                        else:
                            growth_rate = 0
                        this_cost = fixed_admin_costs_buses['Costs'].tolist()[t]
                        this_frequency = fixed_admin_costs_buses['Frequency_per_year'].tolist()[t]

                        this_cost_updated = ( this_cost*this_frequency*( 1+growth_rate/100 )/dict_ER_per_year[ time_range_vector[y] ] )/1e6
                        external_fixed_costs += this_cost_updated

                    BusPrice_external_fixed_cost[y] = external_fixed_costs * sum( this_q_per_tech )
                    # ---
                    technical_variable_cost = 0
                    for t in range( len( fleet_techs ) ):
                        fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'UseByTechnology' in x ) ]
                        if len(fleet_techs_indices) != 0:
                            for n in range( len( fleet_techs_indices ) ):
                                fleet_tech_index =  fleet_techs_indices[n]
                                this_fleet_fuel_consumption = float( assorted_data_dicts['t_f'][ fleet_tech_index ][-1] ) # of 'bus technology' in PJ
                                this_fleet_fuel = assorted_data_dicts['t_f'][ fleet_tech_index ][1] # the fuels

                                if fleet_techs[t] in df_Unit_TF_IUC_new['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_IUC_new['Fuel'].tolist():
                                    df_Unit_Tax = deepcopy( df_Unit_TF_IUC_new )
                                if fleet_techs[t] in df_Unit_TF_ElectricityVAT_new['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_ElectricityVAT_new['Fuel'].tolist():
                                    df_Unit_Tax = deepcopy( df_Unit_TF_ElectricityVAT_new )
                                if fleet_techs[t] in df_Unit_TF_H2_new['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_H2_new['Fuel'].tolist():
                                    df_Unit_Tax = deepcopy( df_Unit_TF_H2_new )

                                tech_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Technology'].tolist() ) if element == fleet_techs[t] ]
                                fuel_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Fuel'].tolist() ) if element == this_fleet_fuel ]
                                tax_index = list( set(tech_indices_tax) & set(fuel_indices_tax) )[0]

                                df_Unit_Price = deepcopy( df_Rates_TF_SalesPurchasesEnergy )
                                tech_indices_price = [index for index, element in enumerate( df_Unit_Price['Technology'].tolist() ) if element == fleet_techs[t] ]
                                fuel_indices_price = [index for index, element in enumerate( df_Unit_Price['Fuel'].tolist() ) if element == this_fleet_fuel ]
                                price_index = list( set(tech_indices_price) & set(fuel_indices_price) )[0]

                                unit_fuel_cost = df_Unit_Tax.loc[ tax_index, time_range_vector[y] ] + df_Unit_Price.loc[ price_index, time_range_vector[y] ] # per PJ cost
                                technical_variable_cost += unit_fuel_cost * this_fleet_fuel_consumption

                    BusPrice_variable_cost_vector[y] = technical_variable_cost

                BusPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]
                BusPrice_for_new = [ 0 for y in range( len(time_range_vector) ) ]
                BusPrice_for_old = [ 0 for y in range( len(time_range_vector) ) ]

                F = ( BusPrice_produced_km[0] * base_bus_rate / dict_ER_per_year[ time_range_vector[0] ] ) / 1e6 # this pays for the existing fleet and reflects the income of the fleet in the base year

                for y in range( 0, len( time_range_vector ) ):
                    BusPrice_for_new[y] = ( BusPrice_variable_cost_vector[y] + BusPrice_fom_vector[y] + BusPrice_annualized_new_investments_vector[y] + BusPrice_external_fixed_cost[y] ) / BusPrice_produced_km[y]
                    BusPrice_for_old[y] = ( F - BusPrice_for_new[0]*BusPrice_produced_km[0] ) / BusPrice_produced_km[y]
                    BusPrice_vector[y] = BusPrice_for_old[y] + BusPrice_for_new[y] # USD / km

                    df_Rates_TF_SalesPurchasesService_new.loc[ index_buses, time_range_vector[y] ] = BusPrice_vector[y]
                # ---
                # For *Taxis*:
                fleet_techs = in_relationship_ownership['taxi_industry']
                production_techs = in_relationship_sell['taxi_industry']

                TaxiPrice_annualized_new_investments_vector = [ 0 for y in range( len(time_range_vector) ) ]
                TaxiPrice_new_investments = [ 0 for y in range( len(time_range_vector) ) ]
                TaxiPrice_fom_vector = [ 0 for y in range( len(time_range_vector) ) ]
                TaxiPrice_variable_cost_vector = [ 0 for y in range( len(time_range_vector) ) ]
                TaxiPrice_external_fixed_cost = [ 0 for y in range( len(time_range_vector) ) ]
                TaxiPrice_produced_km = [ 0 for y in range( len(time_range_vector) ) ]

                for y in range( len( time_range_vector ) ):
                    # ---
                    prod_pass_km = 0 # here we should select the % of trips produced by the "concesionario" fleet
                    for t in range( len( production_techs ) ):
                        prod_tech_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( production_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'ProductionByTechnology' in x ) ]

                        if len(prod_tech_indices) != 0:
                            prod_tech_index =  prod_tech_indices[0]
                            this_pkm_production = float( assorted_data_dicts['t_f'][ prod_tech_index ][-1] )*1e9 # of 'Techs_Taxis', unit in *kilometers*
                        else:
                            this_pkm_production = 0
                        prod_pass_km += this_pkm_production

                    TaxiPrice_produced_km[y] = prod_pass_km
                    # ---
                    capital_expense = 0
                    this_q_per_tech = [ 0 for t in range( len( fleet_techs ) ) ]
                    # We must use the fleet here:
                    for t in range( len( fleet_techs ) ):
                        this_tech = fleet_techs[t]
                        these_ages_raw = list( fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ].keys() )
                        these_ages = [ i for i in these_ages_raw if type(i) == int ]
                        this_inv = 0
                        for a in these_ages:
                            this_q_a = fleet_Q_perTech_perYear_per_age_imports[ this_tech ][ time_range_vector[y] ][ a ] # let's work only with the imported fleet in order to have a comparable methodology to electricity rate
                            this_market_price = df_Unit_T_MarketPrice[ time_range_vector[y] ][ this_tech ][ a ]
                            this_inv += this_q_a*this_market_price/1e6
                            this_q_per_tech[t] += this_q_a

                        capital_expense += this_inv

                    TaxiPrice_new_investments[y] = capital_expense

                    fill_y_counter = 0
                    for fill_y in range( y, len( time_range_vector ) ): # here we will replace the annualized approach with the depreciation/proift factor approach // we take the same data as buses, for now
                        if fill_y <= y+15:
                            depreciation_expense = capital_expense * df_bus_rates_dep_factor[ fill_y_counter ]
                            capital_profit_amount = capital_expense * df_bus_rates_profit_factor[ fill_y_counter ] * df_bus_rates_profit_rate[ fill_y_counter ]
                            TaxiPrice_annualized_new_investments_vector[fill_y] += depreciation_expense + capital_profit_amount
                            fill_y_counter += 1
                    # ---
                    technical_FOM = 0
                    for t in range( len( fleet_techs ) ):
                        fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'AnnualFixedOperatingCost' in x ) ]

                        if len(fleet_techs_indices) != 0:
                            fleet_tech_index =  fleet_techs_indices[0]
                            this_fleet_tech_FOM = float( assorted_data_dicts['t'][ fleet_tech_index ][-1] ) # of 'taxi technology'
                        else:
                            this_fleet_tech_FOM = 0
                        technical_FOM += this_fleet_tech_FOM

                        try:  # add the km tax
                            technical_FOM += this_vmt_rates_per_tech[ time_range_vector[y] ][ fleet_techs[t] ]
                        except:
                            pass
                    TaxiPrice_fom_vector[y] = technical_FOM
                    # ---
                    external_fixed_costs = 0
                    external_fixed_costs_types = fixed_admin_costs_taxis['Type'].tolist()
                    for t in range( len( external_fixed_costs_types ) ):
                        if t > 1:
                            growth_rate = fixed_admin_costs_taxis['Growth'].tolist()[t]
                        else:
                            growth_rate = 0
                        this_cost = fixed_admin_costs_taxis['Costs'].tolist()[t]
                        this_frequency = fixed_admin_costs_taxis['Frequency_per_year'].tolist()[t]

                        this_cost_updated = ( this_cost*this_frequency*( 1+growth_rate/100 )/dict_ER_per_year[ time_range_vector[y] ] )/1e6
                        external_fixed_costs += this_cost_updated

                    TaxiPrice_external_fixed_cost[y] = external_fixed_costs * sum( this_q_per_tech )
                    # ---
                    technical_variable_cost = 0
                    for t in range( len( fleet_techs ) ):
                        fleet_techs_indices = [i for i, x in enumerate( assorted_data_dicts['t_f'] ) if ( fleet_techs[t] in x ) and ( time_range_vector[y] in x ) and ( 'UseByTechnology' in x ) ]

                        if len(fleet_techs_indices) != 0:
                            for n in range( len( fleet_techs_indices ) ):
                                fleet_tech_index =  fleet_techs_indices[n]
                                this_fleet_fuel_consumption = float( assorted_data_dicts['t_f'][ fleet_tech_index ][-1] ) # of 'taxi technology' in PJ
                                this_fleet_fuel = assorted_data_dicts['t_f'][ fleet_tech_index ][1] # the fuels

                                if fleet_techs[t] in df_Unit_TF_IUC_new['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_IUC_new['Fuel'].tolist():
                                    df_Unit_Tax = deepcopy( df_Unit_TF_IUC_new )
                                if fleet_techs[t] in df_Unit_TF_ElectricityVAT_new['Technology'].tolist() and this_fleet_fuel in df_Unit_TF_ElectricityVAT_new['Fuel'].tolist():
                                    df_Unit_Tax = deepcopy( df_Unit_TF_ElectricityVAT_new )

                                tech_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Technology'].tolist() ) if element == fleet_techs[t] ]
                                fuel_indices_tax = [index for index, element in enumerate( df_Unit_Tax['Fuel'].tolist() ) if element == this_fleet_fuel ]
                                tax_index = list( set(tech_indices_tax) & set(fuel_indices_tax) )[0]

                                df_Unit_Price = deepcopy( df_Rates_TF_SalesPurchasesEnergy )
                                tech_indices_price = [index for index, element in enumerate( df_Unit_Price['Technology'].tolist() ) if element == fleet_techs[t] ]
                                fuel_indices_price = [index for index, element in enumerate( df_Unit_Price['Fuel'].tolist() ) if element == this_fleet_fuel ]
                                price_index = list( set(tech_indices_price) & set(fuel_indices_price) )[0]

                                unit_fuel_cost = df_Unit_Tax.loc[ tax_index, time_range_vector[y] ] + df_Unit_Price.loc[ price_index, time_range_vector[y] ] # per PJ cost
                                technical_variable_cost += unit_fuel_cost * this_fleet_fuel_consumption

                    TaxiPrice_variable_cost_vector[y] = technical_variable_cost

                TaxiPrice_vector = [ 0 for y in range( len(time_range_vector) ) ]
                TaxiPrice_for_new = [ 0 for y in range( len(time_range_vector) ) ]
                TaxiPrice_for_old = [ 0 for y in range( len(time_range_vector) ) ]

                F = ( TaxiPrice_produced_km[0] * base_taxis_rate / dict_ER_per_year[ time_range_vector[0] ] ) / 1e6 # this pays for the existing fleet and reflects the income of the fleet in the base year

                for y in range( 0, len( time_range_vector ) ):
                    TaxiPrice_for_new[y] = ( TaxiPrice_variable_cost_vector[y] + TaxiPrice_fom_vector[y] + TaxiPrice_annualized_new_investments_vector[y] + TaxiPrice_external_fixed_cost[y] ) / TaxiPrice_produced_km[y]
                    TaxiPrice_for_old[y] = ( F - TaxiPrice_for_new[0]*TaxiPrice_produced_km[0] ) / TaxiPrice_produced_km[y]
                    TaxiPrice_vector[y] = TaxiPrice_for_old[y] + TaxiPrice_for_new[y] # USD / km

                    df_Rates_TF_SalesPurchasesService_new.loc[ index_taxis, time_range_vector[y] ] = TaxiPrice_vector[y]
           
                ''' CRUCIALLY, WE MUST RE-CALCULATE ALL THE RATES BASED ON THE RESULTS OF TRANSFERS FROM THE GOVERNMENT '''
                ''' SINCE WE OBTAINED THE NEW RATES IN THE SECTION OF THE GOVERNMENT EXPENDITURES, WE JUST COMPLETE THE COMPUTATION OF THE RESULTS AS WE HAD DONE BEFORE THE ADJUSTMENT'''
                # FCM_7.b - Calculate remaining transfers:
                print('Adjustment Part - Performing FCM_7.b - Calculate remaining transfers')
                # print( '    *let us skip this just for testing*' )
                m['adjustment_id'] = deepcopy( this_n )
                results_list = calculate_transfers( m, discounted_or_not, results_list, assorted_data_dicts, type_1_actor, type_2_actor, type_3_actor, type_4_actor, type_5_actor,
                                                    df_Rates_TF_SalesPurchasesEnergy, df_Unit_T_DerechoArancelario, df_Unit_T_ValorAduanero, df_Unit_T_SelectivoAlConsumo_new, df_Unit_T_ImportVAT_new,
                                                    df_Unit_T_TotalTaxes_new, df_Unit_T_GananciaEstimada_new, df_Unit_T_MarketPrice_new, df_Unit_TF_IUC_new, df_Unit_TF_ElectricityVAT_new, df_Unit_TF_H2_new,
                                                    this_vmt_rates_per_tech, dict_Unit_PropertyTax_new, df_Rates_TF_SalesPurchasesService_new, 'Adjustment' )

                # Here we can append the remaining metrics that go into *results_list*
                # for later printing
                this_returnable = additional_levelized_costs(m, lcot_sedan, lcoe_per_pp, time_range_vector)
                lists_of_lists_to_print = deepcopy( this_returnable )
                for l in range( len( lists_of_lists_to_print ) ):
                    results_list.append( lists_of_lists_to_print[l] )

                # FCM_8 - Incorporate Prices:
                print('Adjustment Part - Performing FCM_8 - Incorporate outputs')
                q_p_t_list = [  df_Rates_TF_SalesPurchasesEnergy, # P
                                df_Unit_TF_IUC_new, # T
                                df_Unit_TF_ElectricityVAT_new, # T
                                df_Rates_TF_ElectricityVAT_new, # T
                                df_Unit_TF_H2_new, # T
                                df_Rates_TF_SalesPurchasesService, # P
                                #
                                df_Unit_T_TotalTaxes_new, # T
                                df_Unit_T_MarketPrice_new, # P
                                df_Unit_T_SelectivoAlConsumo_new, # T
                                df_Unit_T_CIF, # P
                                #
                                fleet_Q_perTech_perYear_per_age_imports, # Q
                                #
                                this_vmt_rates_per_tech, # T
                                #
                                fleet_Q_perTech_perYear_per_age, # Q
                                #
                                fiscal_value_perTech_perYear_per_age,
                                dict_Unit_PropertyTax_new, # T
                                #
                                '', # Q
                                '', # Q
                                #
                                ]
                results_list = incorporate_qs_ps_ts( m, results_list, assorted_data_dicts, q_p_t_list, 'Upgrade' )

                # FCM_9 - Print outputs:
                print('Adjustment Part - Performing FCM_9 - Print outputs')
                print_transfers( m, results_list, fcm_table_header, output_adress, scenario_string, 'Upgrade', this_n )

                print('     *The TEM has run for the ' + str(this_n) + ' strategy in the ' + str( scenario_string ) + ' scenario*\n')

        print('*We have finished running the TEM for the ' + str( scenario_string ) + ' scenario*\n')


if __name__ == '__main__':
    """
    *Abbreviations:*
    prms: parameters
    """

    start1 = time.time()

    # Read yaml file with parameterization
    with open('MOMF_T3a_TEM_SimuMode.yaml', 'r') as file:
        # Load content file
        params = yaml.safe_load(file)

    # Before deploying this system, we need to open all the supporting data;
    # this action will make the system run faster.

    # -------------------------------------------------------------------------
    print('General data input 1 - We call the default parameters for later use'
          )  # DONE
    list_param_default_value = \
        pd.read_excel(params['Scen_Default_Param'],
                      sheet_name=params['Default_Val'])
    list_param_default_value_params = list(list_param_default_value
                                           [params['Param']])
    list_param_default_value_value = list(list_param_default_value
                                          [params['Default_Val']])

    base_configuration_overall = \
        pd.read_excel(params['Scen_Default_Param'],
                      sheet_name=params['Over_Param'])
    global Initial_Year_of_Uncertainty
    for n in range(len(base_configuration_overall.index)):
        if (str(base_configuration_overall.loc[n, 'Parameter']) ==
                'Initial_Year_of_Uncertainty'):
            Initial_Year_of_Uncertainty = int(base_configuration_overall
                                              .loc[n, 'Value'])

    df_prm_def_content = [list_param_default_value_params,
                          list_param_default_value_value,
                          Initial_Year_of_Uncertainty]

    # -------------------------------------------------------------------------
    print('General data input 2 - Extract the relationship table')  # DONE
    df_Relations = pd.read_excel(params['Relat_Tabl_file'],
                                 sheet_name=params['Relshee'])
    agent_list = [i for i in df_Relations.columns.tolist() if 'Set' not in i]
    all_techs_list = df_Relations['Set_Name'].tolist()
    all_techs_list_unique = list(set(all_techs_list))

    # For relationships:
    in_relationship_techs = df_Relations['Set_Name'].tolist()
    in_relationship_ownership = {}
    in_relationship_gather = {}
    in_relationship_sell = {}
    in_relationship_buy = {}
    for j in range(len(agent_list)):
        in_relationship_ownership.update({agent_list[j]: []})
        in_relationship_gather.update({agent_list[j]: []})
        in_relationship_sell.update({agent_list[j]: []})
        in_relationship_buy.update({agent_list[j]: []})

        j_tech_list = df_Relations[agent_list[j]].tolist()
        for t in range(len(j_tech_list)):
            try:
                this_j_tech_list_elements = \
                    j_tech_list[t].replace(' ', '').split(';')
                if 'own' in this_j_tech_list_elements:
                    in_relationship_ownership[agent_list[j]] \
                        .append(in_relationship_techs[t])
                if 'gather_taxes' in this_j_tech_list_elements:
                    in_relationship_gather[agent_list[j]] \
                        .append(in_relationship_techs[t])
                if 'sell' in this_j_tech_list_elements:
                    in_relationship_sell[agent_list[j]] \
                        .append(in_relationship_techs[t])
                if 'buy' in this_j_tech_list_elements:
                    in_relationship_buy[agent_list[j]] \
                        .append(in_relationship_techs[t])
            except Exception:
                pass

    # -------------------------------------------------------------------------
    print('General data input 3 - Extract the rates')
    pd_discount_rates = pd.read_excel(params['TEM_Rates'], sheet_name=params['Disc'])
    r_government = float(pd_discount_rates.loc[0, 'Government'])
    r_energy_companies = float(pd_discount_rates.loc[0, 'Energy_Companies'])
    r_public_transport_companies = \
        float(pd_discount_rates.loc[0, 'Public_Transport_Operator'])
    r_freight_transport_companies = \
        float(pd_discount_rates.loc[0, 'Freight_Transport_Owner'])
    r_private_owner = \
        float(pd_discount_rates.loc[0, 'Private_Transport_Owner'])
    r_public_user = float(pd_discount_rates.loc[0, 'Public_Transport_User'])

    content_df_Relations = [agent_list, all_techs_list_unique,
                            in_relationship_techs, in_relationship_ownership,
                            in_relationship_gather, in_relationship_sell,
                            in_relationship_buy]

    df_ER = pd.read_excel(open(params['TEM_Rates'], 'rb'), sheet_name=params['ER'])
    list_ER = df_ER['Colones_per_Dollar'].tolist()
    list_ER_years = df_ER['Year'].tolist()
    global dict_ER_per_year
    dict_ER_per_year = {}
    for i in range(len(list_ER_years)):
        dict_ER_per_year.update({list_ER_years[i]: list_ER[i]})

    # ----
    # Extracting Rates of Services Sales/Purchases:
    df_Rates_TF_SalesPurchasesService = \
        pd.read_excel(open(params['TEM_Rates'], 'rb'),
                      sheet_name=params['rat_spserv'])

    # ----
    # Let's estimate the price of fossil fuels / let's provisionally include
    # the price structure we had in November
    # $*$ This is a provisional method for fossil fuel additional costs.
    df_Rates_TF_SalesPurchasesEnergy = \
        pd.read_excel(open(params['TEM_Rates'], 'rb'),
                      sheet_name=params['rat_spene'])

    # ----
    # Procedure: we must bring the rates we know into the program.
    # The rates are in colones for fuels or in % for electricity.
    df_Rates_TF_TaxEnergy = \
        pd.read_excel(open(params['TEM_Rates'], 'rb'),
                      sheet_name=params['rat_sptax'])

    content_TEM_rates = [pd_discount_rates, dict_ER_per_year, list_ER,
                         df_Rates_TF_SalesPurchasesService,
                         df_Rates_TF_SalesPurchasesEnergy,
                         df_Rates_TF_TaxEnergy]

    # -------------------------------------------------------------------------
    print('General data input 4 - Extract the TEM controller')
    df_tax_assign = pd.read_excel('_TEM_Control_File.xlsx',
                                  sheet_name=params['Tax_Ass'])
    df_strategies = pd.read_excel('_TEM_Control_File.xlsx',
                                  sheet_name=params['Strat'])
    df_milestones = pd.read_excel('_TEM_Control_File.xlsx',
                                  sheet_name=params['Miles'])
    df_fuels_and_techs = pd.read_excel('_TEM_Control_File.xlsx',
                                       sheet_name=params['Fuels_and_Techs'])

    content_TEM_control_file = [df_tax_assign, df_strategies,
                                df_milestones, df_fuels_and_techs]

    # -------------------------------------------------------------------------
    print('General data input 5 - Extract the Transport Tech List')

    # 5.1
    technology_list_cif = pd.read_excel(params['TEM_Trans_Tech_list'],
                                        sheet_name=params['Imp_techs'])
    technology_list_transport_dict_cif = {}
    for i in range(len(technology_list_cif['Technology'].tolist())):
        technology_list_transport_dict_cif \
            .update({technology_list_cif['Technology'].tolist()[i]:
                     technology_list_cif['Technology_CIF'].tolist()[i]})

    # 5.2
    technology_list_existing = pd.read_excel(params['TEM_Trans_Tech_list'],
                                             sheet_name=params['Exis_techs'])
    technology_list_transport_dict_existing = {}
    for i in range(len(technology_list_existing['Technology'].tolist())):
        technology_list_transport_dict_existing \
            .update({technology_list_existing['Technology'].tolist()[i]:
                     technology_list_existing['Technology_FiscalValue']
                     .tolist()[i]})

    # 5.3
    technology_list_transport = pd.read_excel(params['TEM_Trans_Tech_list'],
                                              sheet_name=params['All_techs'])
    technology_list_transport_techs = \
        technology_list_transport[params['Tech']].tolist()

    # 5.4
    df_Property_Tax_Ranges = pd.read_excel(params['TEM_Trans_Tech_list'],
                                           sheet_name=params['TBL_Prop'])
    df_Property_Tax_Ranges_columns = params[params['Prop_Tax_Range']]

    dict_property_tax_fiscal_value_scales = {}

    min_index = list(df_Property_Tax_Ranges['Char']).index('Min')
    max_index = list(df_Property_Tax_Ranges['Char']).index('Max')
    rate_index = list(df_Property_Tax_Ranges['Char']).index('Rate')
    unit_index = list(df_Property_Tax_Ranges['Char']).index('Unit')

    df_Property_Tax_Ranges_columns_scales = \
        df_Property_Tax_Ranges_columns[1: -1]
    for a_scale in range(len(df_Property_Tax_Ranges_columns_scales)):
        this_scale = df_Property_Tax_Ranges_columns_scales[a_scale]
        this_unit = list(df_Property_Tax_Ranges[this_scale])[unit_index]
        this_rate = list(df_Property_Tax_Ranges[this_scale])[rate_index]
        this_min = list(df_Property_Tax_Ranges[this_scale])[min_index]
        this_max = list(df_Property_Tax_Ranges[this_scale])[max_index]

        dict_property_tax_fiscal_value_scales \
            .update({this_scale: {'Unit': this_unit, 'Rate': this_rate,
                                  'Min': this_min, 'Max': this_max}})

    # 5.5
    df_Property_Tax_Applicable = pd.read_excel(params['TEM_Trans_Tech_list'],
                                               sheet_name=params['TBL_Prop_Apply'])
    dict_Property_Tax_Applicable = {}
    for i in range(len(df_Property_Tax_Applicable['Technology'].tolist())):
        dict_Property_Tax_Applicable \
            .update({df_Property_Tax_Applicable['Technology'].tolist()[i]:
                     df_Property_Tax_Applicable['Property_Value'].tolist()[i]})

    # 5.6
    df_Property_Growth = pd.read_excel(params['TEM_Trans_Tech_list'],
                                       sheet_name=params['Fleet_Gro'])
    factor_Property_Growth = df_Property_Growth.loc[0, 'growth_of_base']

    # 5.7
    table_depreciation = pd.read_excel(params['TEM_Trans_Tech_list'],
                                       sheet_name=params['Dep_TBL'])
    table_depreciation_age = table_depreciation[params['Age']].tolist()
    table_depreciation_factor = \
        table_depreciation[params['Depre_Fac']].tolist()

    # 5.8
    df_depreciation_bus_rates = pd.read_excel(params['TEM_Trans_Tech_list'],
                                              sheet_name=params['Dep_TBL_Bus_Rate'])
    df_bus_rates_age = \
        df_depreciation_bus_rates[params['Age']].tolist()
    df_bus_rates_dep_factor = \
        df_depreciation_bus_rates[params['Depre']].tolist()
    df_bus_rates_profit_factor = \
        df_depreciation_bus_rates[params['Cap_Pro_Fac']].tolist()
    df_bus_rates_profit_rate = \
        df_depreciation_bus_rates[params['Cap_Pro_Rate']].tolist()

    # 5.9
    pd_shares_fiscalvalue_per_modelyear = \
        pd.read_excel(params['TEM_Trans_Tech_list'],
                      sheet_name=params['Share_FV'])
    pd_shares_fiscalvalue_per_modelyear.fillna(0, inplace=True)
    pd_shares_fiscalvalue_col = \
        pd_shares_fiscalvalue_per_modelyear.columns.tolist()  # don't bring
    pd_shares_fiscalvalue_modelyears = \
        [i for i in pd_shares_fiscalvalue_col if type(i) == int]
    pd_shares_fiscalvalue_projyear = \
        list(set(pd_shares_fiscalvalue_per_modelyear['Year'].tolist()))
    pd_shares_fiscalvalue_projyear.sort()

    # 5.10
    pd_shares_cif_rates_per_age = \
        pd.read_excel(params['TEM_Trans_Tech_list'],
                      sheet_name=params['Share_CIF'])
    pd_shares_cif_rates_per_age.fillna(0, inplace=True)
    pd_shares_cif_col = pd_shares_cif_rates_per_age.columns.tolist()

    # 5.11
    fixed_admin_costs_buses = pd.read_excel(params['TEM_Trans_Tech_list'],
                                            sheet_name=params['Add_Cost_Bus'])
    fixed_admin_costs_taxis = pd.read_excel(params['TEM_Trans_Tech_list'],
                                            sheet_name=params['Add_Cost_Taxis'])

    content_trn_tech_list = [technology_list_cif,  # 5.1
                             technology_list_transport_dict_cif,  # 5.1
                             technology_list_existing,  # 5.2
                             technology_list_transport_dict_existing,  # 5.2
                             technology_list_transport,  # 5.3
                             technology_list_transport_techs,  # 5.3
                             df_Property_Tax_Ranges,  # 5.4
                             df_Property_Tax_Ranges_columns_scales,  # 5.4
                             dict_property_tax_fiscal_value_scales,  # 5.4
                             dict_Property_Tax_Applicable,  # 5.5
                             factor_Property_Growth,  # 5.6
                             table_depreciation_age,  # 5.7
                             table_depreciation_factor,  # 5.7
                             df_bus_rates_age,  # 5.8
                             df_bus_rates_dep_factor,  # 5.8
                             df_bus_rates_profit_factor,  # 5.8
                             df_bus_rates_profit_rate,  # 5.8
                             pd_shares_fiscalvalue_per_modelyear,  # 5.9
                             pd_shares_fiscalvalue_col,  # 5.9
                             pd_shares_fiscalvalue_modelyears,  # 5.9
                             pd_shares_fiscalvalue_projyear,  # 5.9
                             pd_shares_cif_rates_per_age,  # 5.10
                             pd_shares_cif_col,  # 5.10
                             fixed_admin_costs_buses,  # 5.11
                             fixed_admin_costs_taxis]  # 5.11

    # -------------------------------------------------------------------------
    print('General data input 6 - This is the distribution of vehicle imports'
          + ' and fleet ownership of private actor (households and businesses)'
          )  # DONE
    df_enigh2tem_raw = pd.read_excel(params['ENI_File'], sheet_name=params['ENI'])
    Actors = params['Actors']
    Actors_Final = params['Actors_Final']
    Actor_Equivalence = params['Actor_Equivalence']

    # let's call the household data and have it around:
    df_enigh2tem_raw = pd.read_excel(params['ENI_File'])
    content_df_enigh2tem = {}

    first_list = set_first_list(params)
    for case in range(len(first_list)):
        case_element_list = first_list[case].split('_')
        case_strategy_alphabet = case_element_list[0]

        df_enigh2tem = deepcopy(df_enigh2tem_raw
                                .loc[df_enigh2tem_raw['Strategy'] ==
                                    case_strategy_alphabet])
        df_enigh2tem.reset_index(inplace=True)

        all_actors_enigh2tem = list(set(df_enigh2tem['Actor'].tolist()))
        all_actors_enigh2tem.sort()

        time_range_vector = []
        for t in df_enigh2tem.columns.tolist():
            try:
                time_range_vector.append(int(t))
            except Exception:
                pass

        share_autos = {}
        share_motos = {}
        share_imports_autos = {}
        share_imports_motos = {}
        share_consumption_buses = {}
        share_consumption_taxis = {}
        for y in range(len(time_range_vector)):
            share_autos.update({time_range_vector[y]: {}})
            share_motos.update({time_range_vector[y]: {}})
            share_imports_autos.update({time_range_vector[y]: {}})
            share_imports_motos.update({time_range_vector[y]: {}})
            share_consumption_buses.update({time_range_vector[y]: {}})
            share_consumption_taxis.update({time_range_vector[y]: {}})
            for n in range(len(Actors)):
                share_autos[time_range_vector[y]
                            ].update({Actor_Equivalence
                                    [all_actors_enigh2tem[n]]: 0})
                share_motos[time_range_vector[y]
                            ].update({Actor_Equivalence
                                      [all_actors_enigh2tem[n]]: 0})
                share_imports_autos[time_range_vector[y]
                                    ].update({Actor_Equivalence
                                            [all_actors_enigh2tem[n]]: 0})
                share_imports_motos[time_range_vector[y]
                                    ].update({Actor_Equivalence
                                            [all_actors_enigh2tem[n]]: 0})
                share_consumption_buses[time_range_vector[y]
                                        ].update({Actor_Equivalence
                                                [all_actors_enigh2tem[n]]: 0})
                share_consumption_taxis[time_range_vector[y]
                                        ].update({Actor_Equivalence
                                                [all_actors_enigh2tem[n]]: 0})

        for y in range(len(time_range_vector)):
            query_year = time_range_vector[y]
            for n in range(len(df_enigh2tem.index.tolist())):
                this_actor = Actor_Equivalence[df_enigh2tem.loc[n, 'Actor']]
                this_share = df_enigh2tem.loc[n, query_year]
                if (df_enigh2tem.loc[n, 'Variable'] in
                        ['Share_Private_Autos_Fleet',
                        'Share_Private_Autos_Fleet_Hogares']):
                    share_autos[query_year][this_actor] = this_share
                if (df_enigh2tem.loc[n, 'Variable'] in
                        ['Share_Private_Motos_Fleet',
                        'Share_Private_Motos_Fleet_Hogares']):
                    share_motos[query_year][this_actor] = this_share
                if (df_enigh2tem.loc[n, 'Variable'] in
                        ['Share_Imports_Private_Autos_Fleet',
                        'Share_Imports_Private_Autos_Fleet_Hogares']):
                    share_imports_autos[query_year][this_actor] = this_share
                if (df_enigh2tem.loc[n, 'Variable'] in
                        ['Share_Imports_Private_Motos_Fleet',
                        'Share_Imports_Private_Motos_Fleet_Hogares']):
                    share_imports_motos[query_year][this_actor] = this_share
                if (df_enigh2tem.loc[n, 'Variable'] in
                        ['Share_Bus_Consumption']):
                    share_consumption_buses[query_year][this_actor] = \
                        this_share
                if (df_enigh2tem.loc[n, 'Variable'] in
                        ['Share_Taxi_Consumption']):
                    share_consumption_taxis[query_year][this_actor] = \
                        this_share

        add_2_content = [share_autos, share_motos, share_imports_autos,
                         share_imports_motos, share_consumption_buses,
                         share_consumption_taxis]

        content_df_enigh2tem.update({case_strategy_alphabet: add_2_content})

    # -------------------------------------------------------------------------
    print('General data input 7 - Open fleet pickles')  # DONE
    Fleet_Groups = \
        pickle.load(open(params['From_Conf'] + params['Fleet_Group'], "rb"))
    # Fleet_Groups['Techs_Microbuses'] += [ 'TRMBUSHYD' ]
    # this is an add on, kind of a patch
    Fleet_Groups_Distance = \
        pickle.load(open(params['From_Conf'] + params['Fleet_Group_Dist'], "rb"))
    Fleet_Groups_OR = \
        pickle.load(open(params['From_Conf'] + params['Fleet_Group_OR'], "rb"))
    Fleet_Groups_techs_2_dem = \
        pickle.load(open(params['From_Conf'] + params['Fleet_Group_T2D'], "rb"))

    content_fleet_groups = params['content_fleet_groups']

    # -------------------------------------------------------------------------
    ''' # Action 1: Work on the different tax options. '''
    # Conditions for the CIF values // per age:
    # distribution and relative cost of weighted-average CIF:
    dict_cif_distribution = {}
    dict_cif_relative_cif = {}

    # Gather imports per age of vehicle imported:
    dict_import_sc_rates = {}
    # dict_import_sc_rates_exo = {}
    dict_import_dai = {}
    dict_import_6946 = {}
    dict_import_iva_relcif = {}

    # Extract the information for the existing fleet,
    # in order to produce a coherent residual fleet over the horizon.
    dict_residual_fiscal_value_wo_depreciation = {}
    dict_residual_fiscal_value = {}  # we must depreciate this
    dict_residual_fiscal_usd = {}
    dict_residual_fleet_distribution = {}
    #
    for t in range(len(technology_list_transport_techs)):
        this_tech = technology_list_transport_techs[t]
        check_tech_cif = technology_list_transport_dict_cif[this_tech]
        # this must check whether technology 't' has the behaviour
        check_tech_existing = \
            technology_list_transport_dict_existing[this_tech]
        # this must check whether technology 't' has the behaviour

        dict_cif_relative_cif.update({this_tech: {}})
        dict_import_sc_rates.update({this_tech: {}})
        # dict_import_sc_rates_exo.update( { this_tech:{} } )
        dict_import_dai.update({this_tech: {}})
        dict_import_6946.update({this_tech: {}})
        dict_import_iva_relcif.update({this_tech: {}})
        dict_cif_distribution.update({this_tech: {}})
        #
        # Let's focus on the imports technology
        df_cif = \
            pd_shares_cif_rates_per_age \
            .loc[(pd_shares_cif_rates_per_age['Technology'] == check_tech_cif)
                 & (pd_shares_cif_rates_per_age['Parameter'] ==
                    'CIF.Ratio.Avg')]
        df_cif_self_index = df_cif.index.tolist()[0]
        df_sc = \
            pd_shares_cif_rates_per_age \
            .loc[(pd_shares_cif_rates_per_age['Technology'] == check_tech_cif)
                 & (pd_shares_cif_rates_per_age['Parameter'] ==
                    'SC.P')]
        df_sc_self_index = df_sc.index.tolist()[0]

        df_dai = \
            pd_shares_cif_rates_per_age \
            .loc[(pd_shares_cif_rates_per_age['Technology'] == check_tech_cif)
                 & (pd_shares_cif_rates_per_age['Parameter'] ==
                    'DAI.P')]
        df_dai_self_index = df_dai.index.tolist()[0]
        df_6946 = \
            pd_shares_cif_rates_per_age\
            .loc[(pd_shares_cif_rates_per_age['Technology'] == check_tech_cif)
                 & (pd_shares_cif_rates_per_age['Parameter'] ==
                    '6946.P')]
        df_6946_self_index = df_6946.index.tolist()[0]
        df_iva_relcif = \
            pd_shares_cif_rates_per_age\
            .loc[(pd_shares_cif_rates_per_age['Technology'] == check_tech_cif)
                 & (pd_shares_cif_rates_per_age['Parameter'] ==
                    'IVA.P')]
        df_iva_relcif_self_index = df_iva_relcif.index.tolist()[0]
        df_distribution = \
            pd_shares_cif_rates_per_age\
            .loc[(pd_shares_cif_rates_per_age['Technology'] == check_tech_cif)
                 & (pd_shares_cif_rates_per_age['Parameter'] ==
                    'Distribution')]
        df_distribution_self_index = df_distribution.index.tolist()[0]
        for i in pd_shares_cif_col:  # this is correlated to age
            dict_cif_relative_cif[this_tech]\
                .update({i: df_cif.loc[df_cif_self_index, i]})
            dict_import_sc_rates[this_tech]\
                .update({i: df_sc.loc[df_sc_self_index, i]})
            dict_import_dai[this_tech]\
                .update({i: df_dai.loc[df_dai_self_index, i]})
            dict_import_6946[this_tech]\
                .update({i: df_6946.loc[df_6946_self_index, i]})
            dict_import_iva_relcif[this_tech]\
                .update({i: df_iva_relcif.loc[df_iva_relcif_self_index, i]})
            dict_cif_distribution[this_tech]\
                .update({i: df_distribution.loc[df_distribution_self_index, i]
                         })

        # Let's focus on the existing technology,
        # the projection and the depreciation
        if check_tech_existing != 'Only_new':
            # we proceed with storing the data in the corresponding dictionary
            dict_residual_fleet_distribution\
                .update({check_tech_existing: {}})
            dict_residual_fiscal_value\
                .update({check_tech_existing: {}})
            dict_residual_fiscal_usd\
                .update({check_tech_existing: {}})
            dict_residual_fiscal_value_wo_depreciation\
                .update({check_tech_existing: {}})

            for y in pd_shares_fiscalvalue_projyear:
                df_residual_distribution = \
                    pd_shares_fiscalvalue_per_modelyear\
                    .loc[(pd_shares_fiscalvalue_per_modelyear['Year'] == y)
                         & (pd_shares_fiscalvalue_per_modelyear['Parameter']
                            == 'Distribution') &
                         (pd_shares_fiscalvalue_per_modelyear['Technology']
                          == check_tech_existing)]
                df_residual_distribution_self_index = \
                    df_residual_distribution.index.tolist()[0]
                dict_residual_fleet_distribution[check_tech_existing]\
                    .update({y: {}})

                df_residual_fiscal_value = \
                    pd_shares_fiscalvalue_per_modelyear\
                    .loc[(pd_shares_fiscalvalue_per_modelyear['Year'] == y) &
                         (pd_shares_fiscalvalue_per_modelyear['Parameter'] ==
                          'Fiscal_Value')
                         & (pd_shares_fiscalvalue_per_modelyear['Technology']
                            == check_tech_existing)]
                # this fiscal value is in colones
                df_residual_fiscal_value_self_index = \
                    df_residual_fiscal_value.index.tolist()[0]
                dict_residual_fiscal_value[check_tech_existing]\
                    .update({y: {}})
                dict_residual_fiscal_usd[check_tech_existing].update({y: {}})
                dict_residual_fiscal_value_wo_depreciation[check_tech_existing
                                                           ].update({y: {}})

                # these are the columns
                for my in pd_shares_fiscalvalue_modelyears:
                    distribution_value = \
                        df_residual_distribution\
                        .loc[df_residual_distribution_self_index, my]
                    fiscal_value_local_currency = \
                        df_residual_fiscal_value\
                        .loc[df_residual_fiscal_value_self_index, my]
                    age = int(y) - int(my)
                    age_endogenous = y - pd_shares_fiscalvalue_projyear[0]

                    if distribution_value > 0:
                        if (age > 0 and age <= table_depreciation_age[-1] and
                                age_endogenous > 0):
                            old_depreciation_multiplier_index = \
                                table_depreciation_age.index( age-1 )
                            new_depreciation_multiplier_index = \
                                table_depreciation_age.index( age )
                            old_depreciation_multiplier = \
                                table_depreciation_factor[old_depreciation_multiplier_index]
                            new_depreciation_multiplier = \
                                table_depreciation_factor[new_depreciation_multiplier_index]
                            depreciation_factor = \
                                new_depreciation_multiplier/old_depreciation_multiplier
                        elif (((age > 0 and age > table_depreciation_age[-1])
                                or age == 0) and age_endogenous > 0):
                            depreciation_factor = 1
                        if age_endogenous == 0:
                            depreciation_factor = 1

                        dict_residual_fleet_distribution[check_tech_existing][y].update({age: distribution_value})
                        dict_residual_fiscal_value[check_tech_existing][y].update({age: fiscal_value_local_currency*depreciation_factor})
                        dict_residual_fiscal_usd[check_tech_existing][y].update({age: fiscal_value_local_currency*depreciation_factor/dict_ER_per_year[y]})
                        dict_residual_fiscal_value_wo_depreciation[check_tech_existing][y].update({age: fiscal_value_local_currency})

    content_tax_rates = [dict_cif_distribution, dict_cif_relative_cif, 
                         dict_import_sc_rates, dict_import_dai, 
                         dict_import_6946, dict_import_iva_relcif, 
                         dict_residual_fiscal_value_wo_depreciation, 
                         dict_residual_fiscal_value, 
                         dict_residual_fiscal_usd, 
                         dict_residual_fleet_distribution]

    # ------------------------------------------------------------------------
    # Store all the external data and open within the function:
    content_all = [df_prm_def_content, content_df_Relations, content_TEM_rates,
                   content_TEM_control_file, content_trn_tech_list,
                   content_df_enigh2tem, content_fleet_groups,
                   content_tax_rates]

    # sys.exit()

    # Control inputs:
    max_x_per_iter = 40  # FLAG: This is an input for parallelization

    print('* We must now execute the TEM.')

    first_list = set_first_list(params)  # creates the global variable *first_list*
    for n in range(len(first_list)):
        # Creates the global variable *first_list_d*
        first_list_d = set_first_list_d(first_list[n].split('_')[0])

        x = len(first_list_d)
        print(x)

        y = (x+1) / max_x_per_iter
        y_ceil = math.ceil(y)

        for n2 in range(0, y_ceil):
            print('###')
            n_ini = n2*max_x_per_iter
            processes = []

            if n_ini + max_x_per_iter < x:
                max_iter = n_ini + max_x_per_iter
            else:
                max_iter = x+1

            for n3 in range(n_ini, max_iter):
                if n3 == 0:
                    #
                    print(first_list[n])
                    p = mp.Process(target=data_processor,
                                   args=(n, 'base', content_all,))
                    processes.append(p)
                    p.start()
                else:
                    print(first_list_d[n3-1])
                    p = mp.Process(target=data_processor,
                                   args=(first_list_d[n3-1],
                                         'fut', content_all,))
                    processes.append(p)
                    p.start()
            for process in processes:
                process.join()

    end_1 = time.time()
    time_elapsed_1 = -start1 + end_1
    print(str(time_elapsed_1) + ' seconds /', str(time_elapsed_1/60) +
          ' minutes')
    print('*: For all effects, we have finished the work of this script.')
