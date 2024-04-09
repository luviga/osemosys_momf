# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 16:54:24 2024

@author: andreysava19
"""

import pandas as pd
import numpy as np

def modify_and_sort_columns(file_path, columns_to_remove):
    """
    This function reads a CSV file, removes specified columns, and sorts the remaining columns alphabetically.
    
    Parameters:
    file_path (str): The file path of the CSV file.
    columns_to_remove (list): A list of columns to remove from the DataFrame.
    
    Returns:
    pandas.DataFrame: The modified DataFrame with specified columns removed and remaining columns sorted.
    """
    try:
        # Try to read the file with default encoding and comma as separator
        df = pd.read_csv(file_path, sep=',')
    except UnicodeDecodeError:
        # If default encoding fails, try ISO-8859-1 encoding
        df = pd.read_csv(file_path, sep=',', encoding='ISO-8859-1')
    
    # Drop the specified columns
    df.drop(columns_to_remove, axis=1, inplace=True, errors='ignore')
    
    # Sort the remaining columns alphabetically
    df = df.reindex(sorted(df.columns), axis=1)
    df = drop_all_nan_columns(df)
    
    return df

def drop_all_nan_columns(df):
    """
    Drop columns from a DataFrame where all values are NaN.
    
    Parameters:
    df (pandas.DataFrame): The DataFrame to analyze and modify.
    
    Returns:
    pandas.DataFrame: The DataFrame with the all-NaN columns removed.
    """
    # Drop columns where all values are NaN
    df_dropped = df.dropna(axis=1, how='all')
    return df_dropped

def compare_dataframe_columns(df1, df2):
    """
    Compare the column names of two DataFrames and print out the differences.
    
    Parameters:
    df1 (pandas.DataFrame): The first DataFrame for comparison.
    df2 (pandas.DataFrame): The second DataFrame for comparison.
    """
    # Get the set difference of columns from df1 that are not in df2
    difference_in_df1 = df1.columns.difference(df2.columns)
    # Get the set difference of columns from df2 that are not in df1
    difference_in_df2 = df2.columns.difference(df1.columns)
    
    # Print the differences
    print(f"Columns in out_original not in out_yaml: {difference_in_df1.tolist()}")
    print(f"Columns in out_yaml not in out_original: {difference_in_df2.tolist()}")

def compare_dataframes(df1, df2):
    """
    Compare two DataFrames cell by cell, after rounding to 10 significant digits.
    Return a dictionary containing DataFrames of differences for each column.

    Parameters:
    df1 (pandas.DataFrame): The first DataFrame to compare.
    df2 (pandas.DataFrame): The second DataFrame to compare.

    Returns:
    dict: A dictionary where each key is a column name with differences, and the value is a DataFrame detailing those differences.
    """
    # First, align both DataFrames to have the same column and row indices
    df1_aligned, df2_aligned = df1.align(df2, join='inner')

    # Round the values to 10 significant digits
    df1_rounded = df1_aligned.round(decimals=5)
    df2_rounded = df2_aligned.round(decimals=5)

    # Initialize an empty dictionary to store the differences
    column_diffs = {}

    for col in df1_rounded.columns:
        # Check if the column exists in both DataFrames and if there are any differences
        if col in df2_rounded and not df1_rounded[col].equals(df2_rounded[col]):
            diff_indices = df1_rounded[col] != df2_rounded[col]
            # Check for at least one difference
            if diff_indices.any():
                # Construct a DataFrame for the differences in the current column
                diff_df = pd.DataFrame({
                    'Index': diff_indices[diff_indices].index,
                    'Value in original': df1_rounded[col][diff_indices],
                    'Value in yaml': df2_rounded[col][diff_indices]
                }).reset_index(drop=True)
                
                # Filter out rows where both values are NaN (just in case)
                diff_df.dropna(subset=['Value in original', 'Value in yaml'], how='all', inplace=True)

                # Add the DataFrame to the dictionary if there are remaining differences
                if not diff_df.empty:
                    column_diffs[col] = diff_df

    return column_diffs

def compare_dataframes_with_key_columns(df1, df2, key_columns=['YEAR', 'TECHNOLOGY', 'FUEL', 'EMISSION']):
    """
    Compare two DataFrames based on specific key columns, and for matching rows,
    compare cell by cell for all other columns, ignoring rows where both compared values are NaN.
    Additionally, include 'TECHNOLOGY', 'YEAR', 'FUEL', and 'EMISSION' in the comparison and results.
    Return a dictionary of DataFrames with differences, including key contextual information.

    Parameters:
    df1 (pandas.DataFrame): The first DataFrame to compare.
    df2 (pandas.DataFrame): The second DataFrame to compare.
    key_columns (list): List of columns to use as keys for comparison, including 'TECHNOLOGY', 'YEAR', 'FUEL', 'EMISSION'.

    Returns:
    dict: A dictionary with column names as keys and DataFrames of differences as values, excluding comparisons of NaN values and including key columns.
    """
    # Ensure key columns are present in both DataFrames
    if not all(col in df1.columns and col in df2.columns for col in key_columns):
        raise ValueError("One of the key columns is missing in one of the DataFrames.")
    
    # Merge DataFrames on key columns to ensure row matches based on these columns
    merged_df = pd.merge(df1, df2, on=key_columns, suffixes=('_original', '_yaml'))

    # Initialize an empty dictionary to store the differences
    column_diffs = {}

    # Exclude key columns from comparison
    comparison_columns = [col for col in merged_df.columns if col not in key_columns and ('_original' in col or '_yaml' in col)]
    for col in comparison_columns:
        # Column name without suffix
        col_name = col.rsplit('_', 1)[0]
        if col_name + '_original' in merged_df and col_name + '_yaml' in merged_df:
            col_original = col_name + '_original'
            col_yaml = col_name + '_yaml'

            # Identify rows with differences
            diff_mask = (merged_df[col_original] != merged_df[col_yaml]) & \
                        (~(np.isnan(merged_df[col_original]) & np.isnan(merged_df[col_yaml])))

            if diff_mask.any():
                diff_df = merged_df[diff_mask][key_columns + [col_original, col_yaml]]
                # Rename columns to match original and yaml naming
                diff_df.rename(columns={col_original: f'Value in original ({col_name})',
                                        col_yaml: f'Value in yaml ({col_name})'}, inplace=True)
                column_diffs[col_name] = diff_df

    return column_diffs

# Original case
file_path = 'BAU_1_Output.csv'
columns_to_remove = [
    'Strategy',
    'Future.ID',
    # 'Fuel',
    # 'Technology',
    # 'Emission',
    # 'Year',
    'ProducedMobility',
    'DistanceDriven',     
    'Fleet',
    'NewFleet',
    'FilterFuelType',
    'FilterVehicleType',
    'Capex2023',
    'FixedOpex2023',
    'VarOpex2023',
    'Opex2023',
    'Externalities2023',
    'Capex_GDP',
    'FixedOpex_GDP',
    'VarOpex_GDP',
    'Opex_GDP',
    'Externalities_GDP'
]

out_original = modify_and_sort_columns(file_path, columns_to_remove)

out_original.rename(columns={'Technology': 'TECHNOLOGY'}, inplace=True)
out_original.rename(columns={'Year': 'YEAR'}, inplace=True)
out_original.rename(columns={'Fuel': 'FUEL'}, inplace=True)
out_original.rename(columns={'Emission': 'EMISSION'}, inplace=True)

out_original = out_original.round(5)

# Yaml case
file_path = 'Data_Output_1.csv'
# file_path = 'BAU_1_Output_Copy.csv'
# To use with new xlsl
columns_to_remove = [
    # 'REGION',
    # 'MODE_OF_OPERATION',
    # 'TECHNOLOGY',
    # 'FUEL',
    # 'EMISSION',
    #'YEAR',
    # 'TIMESLICE',
    'Unnamed: 0'
    ]
# To use with old xlsl
# columns_to_remove = [
#     'Strategy',
#     'Strategy.ID',
#     'Future.ID',
#     #'Fuel',
#     'Technology',
#     #'Emission',
#     'Year',
#     'ProducedMobility',
#     'DistanceDriven',     
#     'Fleet',
#     'NewFleet',
#     'FilterFuelType',
#     'FilterVehicleType',
#     'Capex2023',
#     'FixedOpex2023',
#     'VarOpex2023',
#     'Opex2023',
#     'Externalities2023',
#     'Capex_GDP',
#     'FixedOpex_GDP',
#     'VarOpex_GDP',
#     'Opex_GDP',
#     'Externalities_GDP'
# ]


out_yaml = modify_and_sort_columns(file_path, columns_to_remove)

# out_yaml.rename(columns={'Emission': 'YEAR'}, inplace=True)
# out_yaml.rename(columns={'Fuel': 'TECHNOLOGY'}, inplace=True)

out_yaml = out_yaml.round(5)

compare_dataframe_columns(out_original, out_yaml)

# differences_df = compare_dataframes(out_original, out_yaml)
differences_df = compare_dataframes_with_key_columns(out_original, out_yaml)
