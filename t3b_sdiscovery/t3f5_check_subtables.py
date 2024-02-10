# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 08:43:58 2021

@author: luisf
"""
import pandas as pd
import pickle

open_subtbl_ana_1_exp_2 = pickle.load( open( 'subtbl_ana_1_exp_2.pickle', "rb" ))
open_subtbl_ana_7_exp_2 = pickle.load( open( 'subtbl_ana_7_exp_2.pickle', "rb" ))
open_subtbl_ana_8_exp_2 = pickle.load( open( 'subtbl_ana_8_exp_2.pickle', "rb" ))

# Code specific questions to the subtable:
datequery1 = "2022-02-18"
datequery1_on = "off"
# datequery1_on = "on"
if datequery1 == "2022-02-18" and datequery1_on == "on":
    tbl_id = 9  # to check role of capacity factor
    tbl_9_22_30 = open_subtbl_ana_1_exp_2[9][9]['22-30']['o_pure_direct_d_pure_direct']
    tbl_9_31_50 = open_subtbl_ana_1_exp_2[9][9]['31-50']['o_pure_direct_d_pure_direct']
    with pd.ExcelWriter('./_check_subtable_plots/datequery1_' + datequery1 + '.xlsx') as writer:  
        tbl_9_22_30.to_excel(writer, sheet_name='tbl_9_22_30', index = False)
        tbl_9_31_50.to_excel(writer, sheet_name='tbl_9_31_50', index = False)


# Code specific questions to the subtable:
datequery2 = "2022-02-19"
datequery2_on = "off"
# datequery2_on = "on"
if datequery2 == "2022-02-19" and datequery2_on == "on":
    tbl_id = 16  # to check role of capacity factor
    tbl_16_22_30 = open_subtbl_ana_1_exp_2[16][16]['22-30']['o_pure_direct_d_pure_direct']
    tbl_16_31_50 = open_subtbl_ana_1_exp_2[16][16]['31-50']['o_pure_direct_d_pure_direct']
    with pd.ExcelWriter('./_check_subtable_plots/datequery2_' + datequery2 + '.xlsx') as writer:  
        tbl_16_22_30.to_excel(writer, sheet_name='tbl_16_22_30', index = False)
        tbl_16_31_50.to_excel(writer, sheet_name='tbl_16_31_50', index = False)


# Code specific questions to the subtable:
datequery3 = "2022-02-22"
# datequery3_on = "on"
datequery3_on = "off"
if datequery3 == "2022-02-22" and datequery3_on == "on":
    tbl_id = 13  # to check role of capacity factor
    tbl_13_22_30 = open_subtbl_ana_1_exp_2[13][13]['22-30']['o_pure_wrtBAU_d_pure_direct']
    tbl_13_31_50 = open_subtbl_ana_1_exp_2[13][13]['31-50']['o_pure_wrtBAU_d_pure_direct']
    with pd.ExcelWriter('./_check_subtable_plots/datequery3_' + datequery3 + '.xlsx') as writer:  
        tbl_13_22_30.to_excel(writer, sheet_name='tbl_13_22_30', index = False)
        tbl_13_31_50.to_excel(writer, sheet_name='tbl_13_31_50', index = False)


# Code specific questions to the subtable:
datequery4 = "2022-02-22"
datequery4_on = "on"
# datequery2_on = "on"
if datequery4 == "2022-02-22" and datequery4_on == "on":
    tbl_id = 1  # to check role of capacity factor
    tbl_1_22_30 = open_subtbl_ana_7_exp_2[1][1]['22-30']['o_pure_direct_d_disag_wrtBAU']
    tbl_1_31_50 = open_subtbl_ana_7_exp_2[1][1]['31-50']['o_pure_direct_d_disag_wrtBAU']
    with pd.ExcelWriter('./_check_subtable_plots/datequery4_' + datequery4 + '.xlsx') as writer:  
        tbl_1_22_30.to_excel(writer, sheet_name='tbl_1_22_30', index = False)
        tbl_1_31_50.to_excel(writer, sheet_name='tbl_1_31_50', index = False)


# Code specific questions to the subtable:
datequery5 = "2022-03-19"
datequery5_on = "on"
# datequery2_on = "on"
if datequery5 == "2022-03-19" and datequery5_on == "on":
    tbl_id = 1  # to check role of capacity factor
    tbl_1_22_30 = open_subtbl_ana_7_exp_2[1][1]['22-30']['o_pure_direct_d_disag_wrtBAU']
    tbl_1_22_35 = open_subtbl_ana_7_exp_2[1][1]['22-35']['o_pure_direct_d_disag_wrtBAU']
    tbl_1_31_50 = open_subtbl_ana_7_exp_2[1][1]['31-50']['o_pure_direct_d_disag_wrtBAU']
    with pd.ExcelWriter('./_check_subtable_plots/datequery5_' + datequery5 + '.xlsx') as writer:  
        tbl_1_22_30.to_excel(writer, sheet_name='tbl_1_22_30', index = False)
        tbl_1_22_35.to_excel(writer, sheet_name='tbl_1_22_35', index = False)
        tbl_1_31_50.to_excel(writer, sheet_name='tbl_1_31_50', index = False)


# Code specific questions to the subtable:
datequery6 = "2022-03-19"
datequery6_on = "on"
# datequery2_on = "on"
if datequery6 == "2022-03-19" and datequery6_on == "on":
    tbl_id = 1  # to check role of capacity factor
    tbl_1_22_30 = open_subtbl_ana_8_exp_2[1][1]['22-30']['o_pure_direct_d_disag_wrtBAU']
    tbl_1_22_35 = open_subtbl_ana_8_exp_2[1][1]['22-35']['o_pure_direct_d_disag_wrtBAU']
    tbl_1_31_50 = open_subtbl_ana_8_exp_2[1][1]['31-50']['o_pure_direct_d_disag_wrtBAU']
    with pd.ExcelWriter('./_check_subtable_plots/datequery6_' + datequery6 + '.xlsx') as writer:  
        tbl_1_22_30.to_excel(writer, sheet_name='tbl_1_22_30', index = False)
        tbl_1_22_35.to_excel(writer, sheet_name='tbl_1_22_35', index = False)
        tbl_1_31_50.to_excel(writer, sheet_name='tbl_1_31_50', index = False)
