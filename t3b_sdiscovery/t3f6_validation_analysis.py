# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 10:27:00 2021

@author: luisf
"""

import pandas as pd
import numpy as np
import sys
import time
import math
from copy import deepcopy
from functools import reduce
import pickle


def subselect_df(this_df, m_col, od_perc, od_dir):
    if od_dir == 'low':
        this_df_select = this_df[this_df[m_col] < od_perc]
    elif od_dir == 'high':
        this_df_select = this_df[this_df[m_col] > od_perc]
    else:
        print('There is an issue (1): ', m_col)
        sys.exit()
    return this_df_select

def min_max_scaling(df):
    norm_df = deepcopy(df)
    # store these to later re-scale the results back to the original value
    scale_factor = {}
    scale_sum = {}
    scale_zero = {}

    for col in norm_df.columns:
        scale_factor.update({col:
                             deepcopy(float(norm_df[col].max() -
                                      norm_df[col].min()))
                             })
        scale_sum.update({col: deepcopy(norm_df[col].min())})

        try:
            if (norm_df[col].max() != 0 and norm_df[col].max() ==
                    norm_df[col].min()):
                scale_zero.update({col: 0})  # this won't actually matter
            elif norm_df[col].max() == norm_df[col].min():
                scale_zero.update({col: 0})  # this won't actually matter
            else:
                scale_zero.update({col: -1*deepcopy(norm_df[col].min())
                                   / deepcopy(float(norm_df[col].max() -
                                                    norm_df[col].min()))})
        except Exception:
            print('Debug 1')
            print(deepcopy(float(norm_df[col].max() - norm_df[col].min())))
            print(col)
            print(norm_df[col].max(), norm_df[col].min())
            sys.exit()

        norm_df[col] = (norm_df[col] - norm_df[col].min()) / \
            (norm_df[col].max() - norm_df[col].min())

    return norm_df, scale_factor, scale_sum, scale_zero


start_1 = time.time()

'''
references:
1) https://www.geeksforgeeks.org/python-indices-of-numbers-greater-than-k/
2) https://www.pythonpool.com/python-list-intersection/
'''

'''
Objective:
To know how effective found the ranges are.
'''
#######################################################################
# Step 1) Open the inputs avaialbe:
# first, open the results of predominant ranges:
df_ranges = pd.read_excel(open('t3f4_predominant_ranges_a1_e2.xlsx', 'rb'), sheet_name='ranges')
df_ranges_cols = ['Outcome_Type', 'Metric', 'Period', 'Driver',
                  'Driver_Type', 'Max_Norm', 'Min_Norm', 'Case',
                  'Condition', 'Tiebreaker']
df_ranges_drivers_all_unique = list(set(df_ranges['Driver'].tolist()))

# second, open the data tables as per Analysis 7:
data_pickle = pickle.load( open( 'subtbl_ana_7_exp_2.pickle', "rb" ))
except_cols = ['Fut_ID', 'Run_Strat_ID', 'Scenario', 'Strat_ID']

data_df_22_30_raw = data_pickle[1][1]['22-30']['o_pure_direct_d_disag_wrtBAU']
data_df_22_30 = data_df_22_30_raw.loc[(data_df_22_30_raw['Strat_ID'] == 'none')]
data_df_22_30.reset_index(drop=True, inplace=True)
data_df_22_30_col = data_df_22_30.columns.tolist()
data_df_22_30_col_use = [i for i in data_df_22_30_col if i not in except_cols]
data_df_22_30_norm, scale_factor_22_30, scale_sum_22_30, scale_zero_22_30 = \
    min_max_scaling(data_df_22_30[data_df_22_30_col_use])

data_df_22_35_raw = data_pickle[1][1]['22-35']['o_pure_direct_d_disag_wrtBAU']
data_df_22_35 = data_df_22_35_raw.loc[(data_df_22_35_raw['Strat_ID'] == 'none')]
data_df_22_35.reset_index(drop=True, inplace=True)
data_df_22_35_col = data_df_22_35.columns.tolist()
data_df_22_35_col_use = [i for i in data_df_22_35_col if i not in except_cols]
data_df_22_35_norm, scale_factor_22_35, scale_sum_22_35, scale_zero_22_35 = \
    min_max_scaling(data_df_22_35[data_df_22_35_col_use])

data_df_31_50_raw = data_pickle[1][1]['31-50']['o_pure_direct_d_disag_wrtBAU']
data_df_31_50 = data_df_31_50_raw.loc[(data_df_31_50_raw['Strat_ID'] == 'none')]
data_df_31_50.reset_index(drop=True, inplace=True)
data_df_31_50_col = data_df_31_50.columns.tolist()
data_df_31_50_col_use = [i for i in data_df_31_50_col if i not in except_cols]
data_df_31_50_norm, scale_factor_31_50, scale_sum_31_50, scale_zero_31_50 = \
    min_max_scaling(data_df_31_50[data_df_31_50_col_use])

dict_norm_df = {'22-30': data_df_22_30_norm,
                '22-35': data_df_22_35_norm,
                '31-50': data_df_31_50_norm}

# third, keep the boxes around just in case; although, it is likely not needed
data_boxes_pickle = pickle.load( open( 'subtbl_ana_1_exp_1.pickle', "rb" ))
# for example, find the names of the variables that are "metrics of interest"
df_ana1_raw = \
    pd.read_excel(open('./Analysis_1/prim_structure.xlsx', 'rb'), sheet_name='Sequences')
df_ana1_mask = \
    ((~df_ana1_raw['Outcome_Source'].isna()) &
     (df_ana1_raw['Outcome_Type'] == 'Metric of interest'))
df_ana1 = df_ana1_raw.loc[df_ana1_mask]
metric_of_interest_list = df_ana1['Outcome'].tolist()

# above, we have already created the normalized dataframes used to conslult the data

# print('check the scale content')
# sys.exit()

#######################################################################
# Step 2) create an equivalence between the drivers and the columns
drivers_all = []
drivers_2_columns = {}
if (data_df_22_30_col_use == data_df_31_50_col_use) and (data_df_22_30_col_use == data_df_22_35_col_use):
    drivers_all_raw = list(set(data_df_22_30_col_use))
    for this_d in drivers_all_raw:
        if 'Mode shift' in this_d and 'public' in this_d:
            drivers_all.append('Mode shift public')
        elif 'Mode shift' in this_d:
            drivers_all.append('Mode shift nonmot')
        else:
            drivers_all.append(this_d.split('_')[0])
        drivers_2_columns.update({drivers_all[-1]:this_d})

# verify that important dirvers exist in list of all possible drivers:
if set(df_ranges_drivers_all_unique).issubset(set(drivers_all)):
    print("Yes, important drivers are subset of all drivers.")
else:
    print("No, there is an issue with the names of drivers.")

# find the columns that are metrics and the unused drivers:
unused_variables = []
for n in range(len(drivers_all)):
    if drivers_all[n] not in metric_of_interest_list and drivers_all[n] not in df_ranges_drivers_all_unique:
        unused_variables.append(drivers_all[n])

# hence, the equivalence exists.

#######################################################################
# Step 3) Now we must act according to the grouping of data:
i_outcome_type = list(set(df_ranges['Outcome_Type'].tolist()))
i_metric = list(set(df_ranges['Metric'].tolist()))
i_metric.sort(reverse = True)
i_period = list(set(df_ranges['Period'].tolist()))
# i_period = [i for i in i_period if i in ['22-30', '31-50']]
i_period = [i for i in i_period if i in ['22-30', '22-35', '31-50']]
i_period.sort()

# NOTES:
# i) The goal at this stage is to find how the ranges are effective
# at determining the solution space of every metric.
# ii) We must present the metrics with sufficient sensitivity, producing
# a file that shows how good each metric is, and how good a combination of metrics is.
# iii) recall the definitions of *coverage* and *density* as
# mainstream statistics that can facilitate the interpretation of the solution space:

# Strategy space (SS): futures that fall within the *strategy*, i.e., should we focus on levers???
# Metric space (MS): futures that represent the sapce of interest
# Coverage = SS ∩ MS / size(MS)
# Density = SS ∩ MS / size(SS)
# How to define the *Strategy space* ? It must be flexible and linked to our story

# let's open the "classes" sheet to know which ranges are available:
df_classes = \
    pd.read_excel(open('t3f6_validation_analysis_inputs.xlsx', 'rb'),
                  sheet_name='classes')

# remember the selection of metric thresholds:
desirable_outcomes = {\
    'Benefit':'high_75',
    'Emissions National':'low_25',
    'CAPEX':'low_25',
    'Bus Price':'low_25',
    'Electricity price':'low_25'}
risk_outcomes = {\
    'Benefit':'low_25',
    'Emissions National':'high_75',
    'CAPEX':'high_75',
    'Bus Price':'high_75',
    'Electricity price':'high_75'}
outcome_directions = {'Desirable':desirable_outcomes,
                      'Risk':risk_outcomes}

# let's quickly find out if index == futures:
test_index_list = data_df_22_30.index.tolist()
test_future_list = data_df_22_30['Fut_ID'].tolist()
if test_index_list == test_future_list:
    print('Futures and indices are equivalent')

# let's define a dictionary accoriding to the desired columns:
validation_columns = ['Outcome_Type',
                      'Metric',
                      'Period',
                      'Driver',
                      'Driver_Type',
                      'Group',
                      'Sensitivity',
                      'Metric space (# futures)',
                      'Strategy space (# futures)',
                      'Coverage',
                      'Density',
                      'Metric space (ratio)',
                      'Strategy space (ratio)']
validation_dict = {}

# let's also open other inputs support strategy:
df_drivers_2_groups = {}
df_drivers_2_types = {}
df_groups_2_drivers = {}
unique_driver_groups = []
for d in range(len(df_classes.index.tolist())):
    this_d = df_classes['Driver'].tolist()[d]
    this_type = df_classes['Type'].tolist()[d]
    this_sg = df_classes['Story_Group'].tolist()[d]
    if this_sg not in unique_driver_groups:
        unique_driver_groups.append(this_sg)
        df_groups_2_drivers.update({this_sg:[]})
    df_groups_2_drivers[this_sg].append(this_d)
    df_drivers_2_groups.update({this_d:this_sg})
    df_drivers_2_types.update({this_d:this_type})

# now let's define the priorities and additional metrics:
# consider the priority:
# National financial impacts > Electricity prices > Bus prices > Emissions > CAPEX
i_metric_add_alls = ['All-1', 'All-2', 'All-3']
i_metric += i_metric_add_alls

# also, consider the "contrarian" outcome:
outcome_contrarian_directions = \
    {'Desirable':risk_outcomes, 'Risk':desirable_outcomes}

# now, iterate across outcomes:
b_exception_strings, b_success_strings = [], []
for ot in i_outcome_type:
    validation_dict.update({ot:{}})
    for m in i_metric:
        validation_dict[ot].update({m:{}})
        # extract the indictions for the metric space:
        if 'All' in m:  # the number of futures must meet all ranges:
            this_od_benefit = outcome_directions[ot]['Benefit']
            this_od_emissions = \
                outcome_directions[ot]['Emissions National']
            this_od_capex = outcome_directions[ot]['CAPEX']
            this_od_bus = outcome_directions[ot]['Bus Price']
            this_od_electricity = \
                outcome_directions[ot]['Electricity price']

            this_oo_benefit = outcome_contrarian_directions[ot]['Benefit']
            this_oo_emissions = \
                outcome_contrarian_directions[ot]['Emissions National']
            this_oo_capex = outcome_contrarian_directions[ot]['CAPEX']
            this_oo_bus = outcome_contrarian_directions[ot]['Bus Price']
            this_oo_electricity = \
                outcome_contrarian_directions[ot]['Electricity price']
        else:
            this_outcome_direction = outcome_directions[ot][m]
            this_outcome_opposite = outcome_contrarian_directions[ot][m]

        # search for the futures of interest for each period:
        for p in i_period:
            validation_dict[ot][m].update({p:{}})
            # call the dataframes by period:
            this_df = dict_norm_df[p]

            # extract the futures with the metrics of interest (MS):
            if 'All' in m:
                # Extract correct directions:
                od_benefit_dir = this_od_benefit.split('_')[0]
                od_benefit_val = int(this_od_benefit.split('_')[-1])
                m_col_benefit = drivers_2_columns['Benefit']
                m_list_benefit = this_df[m_col_benefit].tolist()
                od_perc_benefit = np.percentile(m_list_benefit, od_benefit_val)
                this_df_select_benefit = \
                    subselect_df(this_df, m_col_benefit, od_perc_benefit, od_benefit_dir)
                m_futures_benefit = this_df_select_benefit.index.tolist()

                od_emissions_dir = this_od_emissions.split('_')[0]
                od_emissions_val = int(this_od_emissions.split('_')[-1])
                m_col_emissions = drivers_2_columns['Emissions National']
                m_list_emissions = this_df[m_col_emissions].tolist()
                od_perc_emissions = np.percentile(m_list_emissions, od_emissions_val)
                this_df_select_emissions = \
                    subselect_df(this_df, m_col_emissions, od_perc_emissions, od_emissions_dir)
                m_futures_emissions = this_df_select_emissions.index.tolist()

                od_capex_dir = this_od_capex.split('_')[0]
                od_capex_val = int(this_od_capex.split('_')[-1])
                m_col_capex = drivers_2_columns['CAPEX']
                m_list_capex = this_df[m_col_capex].tolist()
                od_perc_capex = np.percentile(m_list_capex, od_capex_val)
                this_df_select_capex = \
                    subselect_df(this_df, m_col_capex, od_perc_capex, od_capex_dir)
                m_futures_capex = this_df_select_capex.index.tolist()

                od_bus_dir = this_od_bus.split('_')[0]
                od_bus_val = int(this_od_bus.split('_')[-1])
                m_col_bus = drivers_2_columns['Bus Price']
                m_list_bus = this_df[m_col_bus].tolist()
                od_perc_bus = np.percentile(m_list_bus, od_bus_val)
                this_df_select_bus = \
                    subselect_df(this_df, m_col_bus, od_perc_bus, od_bus_dir)
                m_futures_bus = this_df_select_bus.index.tolist()

                od_electricity_dir = this_od_electricity.split('_')[0]
                od_electricity_val = int(this_od_electricity.split('_')[-1])
                m_col_electricity = drivers_2_columns['Electricity price']
                m_list_electricity = this_df[m_col_electricity].tolist()
                od_perc_electricity = np.percentile(m_list_electricity, od_electricity_val)
                this_df_select_electricity = \
                    subselect_df(this_df, m_col_electricity, od_perc_electricity, od_electricity_dir)
                m_futures_electricity = this_df_select_electricity.index.tolist()

                # Extract opposites:
                oo_benefit_dir = this_oo_benefit.split('_')[0]
                oo_benefit_val = int(this_oo_benefit.split('_')[-1])
                m_col_benefit_opp = drivers_2_columns['Benefit']
                m_list_benefit_opp = this_df[m_col_benefit_opp].tolist()
                oo_perc_benefit = np.percentile(m_list_benefit_opp, oo_benefit_val)
                this_df_select_benefit_opp = \
                    subselect_df(this_df, m_col_benefit_opp, oo_perc_benefit, oo_benefit_dir)
                m_futures_benefit_opp = this_df_select_benefit_opp.index.tolist()

                oo_emissions_dir = this_oo_emissions.split('_')[0]
                oo_emissions_val = int(this_oo_emissions.split('_')[-1])
                m_col_emissions_opp = drivers_2_columns['Emissions National']
                m_list_emissions_opp = this_df[m_col_emissions_opp].tolist()
                oo_perc_emissions = np.percentile(m_list_emissions_opp, oo_emissions_val)
                this_df_select_emissions_opp = \
                    subselect_df(this_df, m_col_emissions_opp, oo_perc_emissions, oo_emissions_dir)
                m_futures_emissions_opp = this_df_select_emissions_opp.index.tolist()

                oo_capex_dir = this_oo_capex.split('_')[0]
                oo_capex_val = int(this_oo_capex.split('_')[-1])
                m_col_capex_opp = drivers_2_columns['CAPEX']
                m_list_capex_opp = this_df[m_col_capex_opp].tolist()
                oo_perc_capex = np.percentile(m_list_capex_opp, oo_capex_val)
                this_df_select_capex_opp = \
                    subselect_df(this_df, m_col_capex_opp, oo_perc_capex, oo_capex_dir)
                m_futures_capex_opp = this_df_select_capex_opp.index.tolist()

                oo_bus_dir = this_oo_bus.split('_')[0]
                oo_bus_val = int(this_oo_bus.split('_')[-1])
                m_col_bus_opp = drivers_2_columns['Bus Price']
                m_list_bus_opp = this_df[m_col_bus_opp].tolist()
                oo_perc_bus = np.percentile(m_list_bus_opp, oo_bus_val)
                this_df_select_bus_opp = \
                    subselect_df(this_df, m_col_bus_opp, oo_perc_bus, oo_bus_dir)
                m_futures_bus_opp = this_df_select_bus_opp.index.tolist()

                oo_electricity_dir = this_oo_electricity.split('_')[0]
                oo_electricity_val = int(this_oo_electricity.split('_')[-1])
                m_col_electricity_opp = drivers_2_columns['Electricity price']
                m_list_electricity_opp = this_df[m_col_electricity_opp].tolist()
                oo_perc_electricity = np.percentile(m_list_electricity_opp, oo_electricity_val)
                this_df_select_electricity_opp = \
                    subselect_df(this_df, m_col_electricity_opp, oo_perc_electricity, oo_electricity_dir)
                m_futures_electricity_opp = this_df_select_electricity_opp.index.tolist()

                # Finding the futures of interest:
                if m == 'All':
                    m_futures_all_set = \
                        set(m_futures_benefit) & set(m_futures_emissions) \
                        & set(m_futures_capex) & set(m_futures_bus) \
                        & set(m_futures_electricity)
                    m_futures = list(m_futures_all_set)

                    m_futures_all_set_opp = \
                        set(m_futures_benefit_opp) & set(m_futures_emissions_opp) \
                        & set(m_futures_capex_opp) & set(m_futures_bus_opp) \
                        & set(m_futures_electricity_opp)
                    m_futures_opp = list(m_futures_all_set_opp)

                if m == 'All-1':
                    m_futures_all_set = \
                        set(m_futures_benefit) & set(m_futures_emissions) \
                        & set(m_futures_bus) & set(m_futures_electricity)
                    m_futures = list(m_futures_all_set)

                    m_futures_all_set_opp = \
                        set(m_futures_benefit_opp) & set(m_futures_emissions_opp) \
                        & set(m_futures_bus_opp) & set(m_futures_electricity_opp)
                    m_futures_opp = list(m_futures_all_set_opp)

                if m == 'All-2':
                    m_futures_all_set = \
                        set(m_futures_benefit) & \
                        set(m_futures_bus) & set(m_futures_electricity)
                    m_futures = list(m_futures_all_set)

                    m_futures_all_set_opp = \
                        set(m_futures_benefit_opp) & \
                        set(m_futures_bus_opp) & set(m_futures_electricity_opp)
                    m_futures_opp = list(m_futures_all_set_opp)

                if m == 'All-3':
                    m_futures_all_set = \
                        set(m_futures_benefit) \
                        & set(m_futures_electricity)
                    m_futures = list(m_futures_all_set)

                    m_futures_all_set_opp = \
                        set(m_futures_benefit_opp) \
                        & set(m_futures_electricity_opp)
                    m_futures_opp = list(m_futures_all_set_opp)

            else:
                od_dir = this_outcome_direction.split('_')[0]
                od_val = int(this_outcome_direction.split('_')[-1])
                m_col = drivers_2_columns[m]
                m_list = this_df[m_col].tolist()
                od_perc = np.percentile(m_list, od_val)
                this_df_select = \
                    subselect_df(this_df, m_col, od_perc, od_dir)
                m_futures = this_df_select.index.tolist()

                oo_dir = this_outcome_opposite.split('_')[0]
                oo_val = int(this_outcome_opposite.split('_')[-1])
                m_col_opp = drivers_2_columns[m]
                m_list_opp = this_df[m_col_opp].tolist()
                oo_perc = np.percentile(m_list_opp, oo_val)
                this_df_select_opp = \
                    subselect_df(this_df, m_col_opp, oo_perc, oo_dir)
                m_futures_opp = this_df_select_opp.index.tolist()

            # storing data of the metric space:
            ms = len(m_futures)
            ms_ratio = ms/len(test_index_list)
            ms_opp = len(m_futures_opp)
            ms_ratio_opp = ms_opp/len(test_index_list)

            # extract the ranges of interest:
            if 'All' in m:
                reg_mask = ((df_ranges['Outcome_Type'] == ot) &
                            (df_ranges['Metric'] == 'All') &
                            (df_ranges['Period'] == p))
            else:
                reg_mask = ((df_ranges['Outcome_Type'] == ot) &
                            (df_ranges['Metric'] == m) &
                            (df_ranges['Period'] == p))
            df_local = df_ranges.loc[reg_mask]

            # a) we can iterate across the elements of *df_local*, i.e., individual drivers:
            # aiming at finding the list of futures corresponding with each driver of
            # the ot/m/p combination
            validation_dict[ot][m][p].update({'Driver':{}})
            this_d_futs_dict = {}
            for this_d in df_local['Driver'].tolist():
                this_d_col = drivers_2_columns[this_d]
                this_condition = df_local.loc[(df_local['Driver'] == this_d), 'Condition'].iloc[0]
                this_driver_type = df_local.loc[(df_local['Driver'] == this_d), 'Driver_Type'].iloc[0]
                if this_condition == 'definitive':
                    this_min = df_local.loc[(df_local['Driver'] == this_d), 'Min_Norm'].iloc[0]
                    this_max = df_local.loc[(df_local['Driver'] == this_d), 'Max_Norm'].iloc[0]
                    this_d_df = this_df.loc[((this_df[this_d_col] >= this_min) &
                                            (this_df[this_d_col] <= this_max))]
                    this_d_futs = this_d_df.index.tolist()
                    this_d_futs_dict.update({this_d:this_d_futs})

                    ss = len(this_d_futs)
                    ss_intersect_ms = \
                        list(set(this_d_futs) & set(m_futures))
                    cov = len(ss_intersect_ms)/ms
                    den = len(ss_intersect_ms)/ss
                    ss_ratio = ss/len(test_index_list)

                    ss_intersect_ms_opp = \
                        list(set(this_d_futs) & set(m_futures_opp))
                    cov_opp = len(ss_intersect_ms_opp)/ms_opp
                    den_opp = len(ss_intersect_ms_opp)/ss

                    add_dict = {'Driver_Type': this_driver_type,
                                'Metric space (# futures)': ms,
                                'Strategy space (# futures)': ss,
                                'Coverage': cov,
                                'Density': den,
                                'Metric space (ratio)': ms_ratio,
                                'Strategy space (ratio)': ss_ratio,
                                #
                                'Metric space (# futures)-opp': ms_opp,
                                'Coverage-opp': cov_opp,
                                'Density-opp': den_opp,
                                'Metric space (ratio)-opp': ms_ratio_opp}
                    validation_dict[ot][m][p]['Driver'].update({this_d: deepcopy(add_dict)})

                    ### print('check what to do now')
                    ### sys.exit()

            # b) we can iterate across Story_Groups:
            validation_dict[ot][m][p].update({'Group':{}})
            for g in unique_driver_groups:
                this_g_d_list_raw, this_g_d_list = df_groups_2_drivers[g], []
                for this_d in this_g_d_list_raw:
                    if df_drivers_2_types[this_d] != 'Intermediary':
                        this_g_d_list.append(this_d)
                this_d_counter, unused_ds, used_ds = 0, [], []
                for this_d in this_g_d_list:
                    if this_d_counter == 0:
                        try:
                            this_ref_set = set(this_d_futs_dict[this_d])
                            this_d_counter += 1
                            used_ds.append(this_d)
                        except Exception:
                            unused_ds.append(this_d)
                    else:
                        try:
                            this_g_set = set(this_ref_set) & set(this_d_futs_dict[this_d])
                            this_ref_set = deepcopy(this_g_set)
                            used_ds.append(this_d)
                        except Exception:
                            unused_ds.append(this_d)

                if this_d_counter != 0:
                    this_g_futs = list(this_g_set)

                    ss = len(this_g_futs)
                    ss_intersect_ms = \
                        list(set(this_g_futs) & set(m_futures))
                    cov = len(ss_intersect_ms)/ms
                    den = len(ss_intersect_ms)/ss
                    ss_ratio = ss/len(test_index_list)

                    ss_intersect_ms_opp = \
                        list(set(this_g_futs) & set(m_futures_opp))
                    cov_opp = len(ss_intersect_ms_opp)/ms_opp
                    den_opp = len(ss_intersect_ms_opp)/ss

                    add_dict = {'Metric space (# futures)': ms,
                                'Strategy space (# futures)': ss,
                                'Coverage': cov,
                                'Density': den,
                                'Metric space (ratio)': ms_ratio,
                                'Strategy space (ratio)': ss_ratio,
                                #
                                'Metric space (# futures)-opp': ms_opp,
                                'Coverage-opp': cov_opp,
                                'Density-opp': den_opp,
                                'Metric space (ratio)-opp': ms_ratio_opp}
                    validation_dict[ot][m][p]['Group'].update({g: deepcopy(add_dict)})

                    this_str = 'Results for group: ' + g + \
                               '; outcome: ' + ot + ' ; metric: ' + m \
                               + '; period: ' + p
                    b_success_strings.append(this_str)
                else:
                    this_str = 'No results for group: ' + g + \
                               '; outcome: ' + ot + ' ; metric: ' + m \
                               + '; period: ' + p
                    b_exception_strings.append(this_str)

            ### if m == 'All-1':
            ###    print('is this happening?')
            ###    sys.exit()

            # c) we can iterate across the sensitivity of driver groups:
            validation_dict[ot][m][p].update({'Sensitivity':{}})
            df_local_def = df_local.loc[(df_local['Condition'] == 'definitive')]
            def_drivers = df_local_def['Driver'].tolist()
            futures_25per_drivers = []
            futures_40per_drivers = []
            futures_50per_drivers = []
            futures_60per_drivers = []
            futures_65per_drivers = []
            futures_70per_drivers = []
            futures_75per_drivers = []
            futures_80per_drivers = []
            futures_85per_drivers = []
            futures_90per_drivers = []
            futures_95per_drivers = []
            sensitivities_list = \
                ['25%', '40%', '50%', '60%', '65%', '70%', '75%',
                 '80%', '85%', '90%', '95%']
            sensitivities_dict = {}

            for f in test_index_list:
                counter_f_ss = 0
                for this_d in def_drivers:
                    if f in this_d_futs_dict[this_d]:
                        counter_f_ss += 1
                if counter_f_ss >= math.ceil(len(def_drivers)*0.25):
                    futures_25per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.40):
                    futures_40per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.50):
                    futures_50per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.60):
                    futures_60per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.65):
                    futures_65per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.70):
                    futures_70per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.75):
                    futures_75per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.80):
                    futures_80per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.85):
                    futures_85per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.90):
                    futures_90per_drivers.append(f)
                if counter_f_ss >= math.ceil(len(def_drivers)*0.95):
                    futures_95per_drivers.append(f)

            for sense in sensitivities_list:
                if sense == '25%':
                    sensitivities_dict.update({sense: futures_25per_drivers})
                if sense == '40%':
                    sensitivities_dict.update({sense: futures_40per_drivers})
                if sense == '50%':
                    sensitivities_dict.update({sense: futures_50per_drivers})
                if sense == '60%':
                    sensitivities_dict.update({sense: futures_60per_drivers})
                if sense == '65%':
                    sensitivities_dict.update({sense: futures_65per_drivers})
                if sense == '70%':
                    sensitivities_dict.update({sense: futures_70per_drivers})
                if sense == '75%':
                    sensitivities_dict.update({sense: futures_75per_drivers})
                if sense == '80%':
                    sensitivities_dict.update({sense: futures_80per_drivers})
                if sense == '85%':
                    sensitivities_dict.update({sense: futures_85per_drivers})
                if sense == '90%':
                    sensitivities_dict.update({sense: futures_90per_drivers})
                if sense == '95%':
                    sensitivities_dict.update({sense: futures_95per_drivers})

                sensitivities_list = sensitivities_dict[sense]

                ss = len(sensitivities_list)
                ss_intersect_ms = \
                    list(set(sensitivities_list) & set(m_futures))
                cov = len(ss_intersect_ms)/ms
                den = len(ss_intersect_ms)/ss
                ss_ratio = ss/len(test_index_list)

                ss_intersect_ms_opp = \
                    list(set(sensitivities_list) & set(m_futures_opp))
                cov_opp = len(ss_intersect_ms_opp)/ms_opp
                den_opp = len(ss_intersect_ms_opp)/ss

                add_dict = {'Metric space (# futures)': ms,
                            'Strategy space (# futures)': ss,
                            'Coverage': cov,
                            'Density': den,
                            'Metric space (ratio)': ms_ratio,
                            'Strategy space (ratio)': ss_ratio,
                            #
                            'Metric space (# futures)-opp': ms_opp,
                            'Coverage-opp': cov_opp,
                            'Density-opp': den_opp,
                            'Metric space (ratio)-opp': ms_ratio_opp}
                validation_dict[ot][m][p]['Sensitivity'].update({sense: deepcopy(add_dict)})

                ### print('check what to do now')
                ### sys.exit()

# Step 4) let's print the elements to review the validation results
print('We are finished estimating validation metrics. Now print the validation table.')
list_Outcome_Type = []
list_Metric = []
list_Period = []
list_Driver = []
list_Driver_Type = []
list_Group = []
list_Sensitivity = []
list_Metric_space_futs = []
list_Strategy_space_futs = []
list_Coverage = []
list_Density = []
list_Metric_space_ratio = []
list_Strategy_space_ratio = []
#
list_Metric_space_futs_opp = []
list_Coverage_opp = []
list_Density_opp = []
list_Metric_space_ratio_opp = []

for ot in i_outcome_type:
    for m in i_metric:
        for p in i_period:
            access_dict = validation_dict[ot][m][p]
            # a) iterate across "drivers" types
            driver_list = list(access_dict['Driver'].keys())
            for d in driver_list:
                this_driver = d
                this_driver_type = access_dict['Driver'][d]['Driver_Type']
                this_group = ''
                this_sensitivity = ''
                this_ms_futs = access_dict['Driver'][d]['Metric space (# futures)']
                this_ss_futs = access_dict['Driver'][d]['Strategy space (# futures)']
                this_cov = access_dict['Driver'][d]['Coverage']
                this_den = access_dict['Driver'][d]['Density']
                this_ms_ratio = access_dict['Driver'][d]['Metric space (ratio)']
                this_ss_ratio = access_dict['Driver'][d]['Strategy space (ratio)']
                #
                this_ms_futs_opp = access_dict['Driver'][d]['Metric space (# futures)-opp']
                this_cov_opp = access_dict['Driver'][d]['Coverage-opp']
                this_den_opp = access_dict['Driver'][d]['Density-opp']
                this_ms_ratio_opp = access_dict['Driver'][d]['Metric space (ratio)-opp']
                #
                list_Outcome_Type.append(ot)
                list_Metric.append(m)
                list_Period.append(p)
                list_Driver.append(this_driver)
                list_Driver_Type.append(this_driver_type)
                list_Group.append(this_group)
                list_Sensitivity.append(this_sensitivity)
                list_Metric_space_futs.append(this_ms_futs)
                list_Strategy_space_futs.append(this_ss_futs)
                list_Coverage.append(this_cov)
                list_Density.append(this_den)
                list_Metric_space_ratio.append(this_ms_ratio)
                list_Strategy_space_ratio.append(this_ss_ratio)
                #
                list_Metric_space_futs_opp.append(this_ms_futs_opp)
                list_Coverage_opp.append(this_cov_opp)
                list_Density_opp.append(this_den_opp)
                list_Metric_space_ratio_opp.append(this_ms_ratio_opp)

            # b) iterate across "group" types
            group_list = list(access_dict['Group'].keys())
            for g in group_list:
                this_driver = ''
                this_driver_type = ''
                this_group = g
                this_sensitivity = ''
                this_ms_futs = access_dict['Group'][g]['Metric space (# futures)']
                this_ss_futs = access_dict['Group'][g]['Strategy space (# futures)']
                this_cov = access_dict['Group'][g]['Coverage']
                this_den = access_dict['Group'][g]['Density']
                this_ms_ratio = access_dict['Group'][g]['Metric space (ratio)']
                this_ss_ratio = access_dict['Group'][g]['Strategy space (ratio)']
                #
                this_ms_futs_opp = access_dict['Group'][g]['Metric space (# futures)-opp']
                this_cov_opp = access_dict['Group'][g]['Coverage-opp']
                this_den_opp = access_dict['Group'][g]['Density-opp']
                this_ms_ratio_opp = access_dict['Group'][g]['Metric space (ratio)-opp']
                #
                list_Outcome_Type.append(ot)
                list_Metric.append(m)
                list_Period.append(p)
                list_Driver.append(this_driver)
                list_Driver_Type.append(this_driver_type)
                list_Group.append(this_group)
                list_Sensitivity.append(this_sensitivity)
                list_Metric_space_futs.append(this_ms_futs)
                list_Strategy_space_futs.append(this_ss_futs)
                list_Coverage.append(this_cov)
                list_Density.append(this_den)
                list_Metric_space_ratio.append(this_ms_ratio)
                list_Strategy_space_ratio.append(this_ss_ratio)
                #
                list_Metric_space_futs_opp.append(this_ms_futs_opp)
                list_Coverage_opp.append(this_cov_opp)
                list_Density_opp.append(this_den_opp)
                list_Metric_space_ratio_opp.append(this_ms_ratio_opp)

            # c) iterate across "sensitivity" types
            sense_list = list(access_dict['Sensitivity'].keys())
            for s in sense_list:
                this_driver = ''
                this_driver_type = ''
                this_group = ''
                this_sensitivity = s
                this_ms_futs = access_dict['Sensitivity'][s]['Metric space (# futures)']
                this_ss_futs = access_dict['Sensitivity'][s]['Strategy space (# futures)']
                this_cov = access_dict['Sensitivity'][s]['Coverage']
                this_den = access_dict['Sensitivity'][s]['Density']
                this_ms_ratio = access_dict['Sensitivity'][s]['Metric space (ratio)']
                this_ss_ratio = access_dict['Sensitivity'][s]['Strategy space (ratio)']
                #
                this_ms_futs_opp = access_dict['Sensitivity'][s]['Metric space (# futures)-opp']
                this_cov_opp = access_dict['Sensitivity'][s]['Coverage-opp']
                this_den_opp = access_dict['Sensitivity'][s]['Density-opp']
                this_ms_ratio_opp = access_dict['Sensitivity'][s]['Metric space (ratio)-opp']
                #
                list_Outcome_Type.append(ot)
                list_Metric.append(m)
                list_Period.append(p)
                list_Driver.append(this_driver)
                list_Driver_Type.append(this_driver_type)
                list_Group.append(this_group)
                list_Sensitivity.append(this_sensitivity)
                list_Metric_space_futs.append(this_ms_futs)
                list_Strategy_space_futs.append(this_ss_futs)
                list_Coverage.append(this_cov)
                list_Density.append(this_den)
                list_Metric_space_ratio.append(this_ms_ratio)
                list_Strategy_space_ratio.append(this_ss_ratio)
                #
                list_Metric_space_futs_opp.append(this_ms_futs_opp)
                list_Coverage_opp.append(this_cov_opp)
                list_Density_opp.append(this_den_opp)
                list_Metric_space_ratio_opp.append(this_ms_ratio_opp)

end_result_dict = {'Outcome_Type': list_Outcome_Type,
                   'Metric': list_Metric,
                   'Period': list_Period,
                   'Driver': list_Driver,
                   'Driver_Type': list_Driver_Type,
                   'Group': list_Group,
                   'Sensitivity': list_Sensitivity,
                   'Metric space (# futures)': list_Metric_space_futs,
                   'Strategy space (# futures)': list_Strategy_space_futs,
                   'Coverage': list_Coverage,
                   'Density': list_Density,
                   'Metric space (ratio)': list_Metric_space_ratio,
                   'Strategy space (ratio)': list_Strategy_space_ratio,
                   #
                   'Metric space (# futures)-opp': list_Metric_space_futs_opp,
                   'Coverage-opp': list_Coverage_opp,
                   'Density-opp': list_Density_opp,
                   'Metric space (ratio)-opp': list_Metric_space_ratio_opp}

end_result_df = pd.DataFrame(end_result_dict)  

# the content we want to print is:
sheet_names = ['validation']
df_list = [end_result_df]

# storing the data:
filename_end_result = \
    't3f6_validation_analysis_output.xlsx'
writer_fn_end_result = pd.ExcelWriter(filename_end_result,
                                      engine='xlsxwriter')
for n in range(len(sheet_names)):
    df_list[n].to_excel(writer_fn_end_result,
                        sheet_name=sheet_names[n], index=False)
writer_fn_end_result.save()

print('The validation table is complete.')

