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

def compare_dataframes_with_key_columns_with_tolerance(df1, df2, key_columns=['Year', 'Technology', 'Fuel', 'Emission'], tolerance=0.05):
    """
    Compare two DataFrames based on specific key columns, and for matching rows,
    compare cell by cell for all other columns, ignoring rows where both compared values are NaN or within a specified tolerance percentage.
    Additionally, include 'TECHNOLOGY', 'YEAR', 'FUEL', and 'EMISSION' in the comparison and results.
    Return a dictionary of DataFrames with differences, including key contextual information.

    Parameters:
    df1 (pandas.DataFrame): The first DataFrame to compare.
    df2 (pandas.DataFrame): The second DataFrame to compare.
    key_columns (list): List of columns to use as keys for comparison.
    tolerance (float): The tolerance percentage for considering values as equal.

    Returns:
    dict: A dictionary with column names as keys and DataFrames of differences as values.
    """
    # Ensure key columns are present in both DataFrames
    if not all(col in df1.columns and col in df2.columns for col in key_columns):
        raise ValueError("One of the key columns is missing in one of the DataFrames.")
    
    # Merge DataFrames on key columns
    merged_df = pd.merge(df1, df2, on=key_columns, suffixes=('_original', '_yaml'))

    # Initialize dictionary for differences
    column_diffs = {}

    # Loop through columns excluding key columns
    comparison_columns = [col for col in merged_df.columns if col not in key_columns and ('_original' in col or '_yaml' in col)]
    for col in comparison_columns:
        col_name = col.rsplit('_', 1)[0]
        if col_name + '_original' in merged_df and col_name + '_yaml' in merged_df:
            col_original = col_name + '_original'
            col_yaml = col_name + '_yaml'

            # Calculate the absolute percentage difference
            percentage_diff = np.abs((merged_df[col_original] - merged_df[col_yaml]) / merged_df[col_original].replace(0, np.nan))
            
            # Identify rows with differences outside the tolerance
            diff_mask = (percentage_diff > tolerance) & (~(np.isnan(merged_df[col_original]) & np.isnan(merged_df[col_yaml])))

            if diff_mask.any():
                diff_df = merged_df[diff_mask][key_columns + [col_original, col_yaml]]
                diff_df.rename(columns={col_original: f'Value in original ({col_name})', col_yaml: f'Value in yaml ({col_name})'}, inplace=True)
                column_diffs[col_name] = diff_df

    return column_diffs

def add_case_column_for_glpk_case(df1, df2):
    """
    Add a 'Case' column to the beginning of two DataFrames. 
    The first DataFrame gets all values in this column set to 'Benchmark',
    and the second DataFrame gets all values set to 'Yaml'.

    Parameters:
    df1 (pandas.DataFrame): The first DataFrame to modify.
    df2 (pandas.DataFrame): The second DataFrame to modify.

    Returns:
    tuple: A tuple containing the modified DataFrames (df1_modified, df2_modified).
    """
    df1.insert(0, 'Case', 'Benchmark') # original
    df2.insert(0, 'Case', 'Yaml') # yaml
    
    return df1, df2

def concatenate_dataframes(df1, df2):
    """
    Concatenate two DataFrames vertically, appending df2 below df1.

    Parameters:
    df1 (pandas.DataFrame): The first DataFrame to concatenate.
    df2 (pandas.DataFrame): The second DataFrame to concatenate.

    Returns:
    pandas.DataFrame: The concatenated DataFrame.
    """
    # Concatenar los DataFrames verticalmente
    concatenated_df = pd.concat([df1, df2], axis=0, ignore_index=True)
    
    return concatenated_df

def manipulate_dataframe_columns(df, sce, num):
    """
    Manipulate the columns of a DataFrame by removing a specific column, adding new columns at the beginning, 
    and reordering columns to a specified sequence.

    Parameters:
    df (pandas.DataFrame): The DataFrame to manipulate.
    sce (str): The value to fill the 'Strategy' column.
    num (str): The value to fill the 'Future.ID' column.

    Returns:
    pandas.DataFrame: The manipulated DataFrame.
    """
    # 1. Remove the 'Unnamed: 0' column if it exists
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)

    # 2. Add 'Strategy' and 'Future.ID' columns at the beginning with sce and num as their respective values
    df.insert(0, 'Future.ID', num)
    df.insert(0, 'Strategy', sce)
    
    # 3. Define the desired order of the initial columns
    initial_columns = ['Strategy', 'Future.ID', 'Fuel', 'Technology', 'Emission', 'Year', 'Demand', 'NewCapacity']
    
    # Ensure all desired initial columns are in the DataFrame; filter out any that are not present to avoid errors
    initial_columns = [col for col in initial_columns if col in df.columns]

    # Create a list of the rest of the columns that aren't in the initial_columns list
    remaining_columns = [col for col in df.columns if col not in initial_columns]
    
    # Concatenate the two lists to form the new column order
    new_column_order = initial_columns + remaining_columns
    
    # Reorder the DataFrame according to the new column order
    df = df[new_column_order]

    return df


if __name__ == '__main__':
    
    sector = 'PIUP'
    sce = 'BAU'
    num = 1
    scen = f'{sector}/{sce}/{num}/'
    out_name = f'{sector}_{sce}_{num}' 
    case = 'old' # 'old' or 'new'
    
    # Original case
    file_path = scen + 'BAU_1_Output.csv'
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
    out_original_to_merge = pd.read_csv(file_path, sep=',')
    
    # out_original.rename(columns={'Technology': 'TECHNOLOGY'}, inplace=True)
    # out_original.rename(columns={'Year': 'YEAR'}, inplace=True)
    # out_original.rename(columns={'Fuel': 'FUEL'}, inplace=True)
    # out_original.rename(columns={'Emission': 'EMISSION'}, inplace=True)
    out_original = out_original.round(5)
    
    
    # Yaml case
    if case == 'old':
        file_path = scen + 'BAU_1_Output_yaml.csv'
        # To use with new workflow but with glpk old dataprocessor
        columns_to_remove = [
            'Strategy',
            'Strategy.ID',
            'Future.ID',
            #'Fuel',
            # 'Technology',
            #'Emission',
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
    
    if case == 'new':
        file_path = scen + 'Data_Output_1.csv'
        # To use with new workflow with otoole
        columns_to_remove = [
            'REGION',
            'MODE_OF_OPERATION',
            # 'TECHNOLOGY',
            # 'FUEL',
            # 'EMISSION',
            # 'YEAR',
            'TIMESLICE',
            'Unnamed: 0'
            ]
    
    out_yaml = modify_and_sort_columns(file_path, columns_to_remove)
    out_yaml_to_merge = pd.read_csv(file_path, sep=',')
    
    if case == 'new':
        out_yaml.rename(columns={'TECHNOLOGY': 'Technology'}, inplace=True)
        out_yaml.rename(columns={'YEAR': 'Year'}, inplace=True)
        out_yaml.rename(columns={'FUEL': 'Fuel'}, inplace=True)
        out_yaml.rename(columns={'EMISSION': 'Emission'}, inplace=True)
        out_yaml_to_merge = manipulate_dataframe_columns(out_yaml_to_merge, sce, num)
    out_yaml = out_yaml.round(5)

    # Diferences of columns    
    compare_dataframe_columns(out_original, out_yaml)
    
    # differences_df = compare_dataframes(out_original, out_yaml)
    # differences_df_keys = compare_dataframes_with_key_columns(out_original, out_yaml)
    differences_df_keys_tolerance = compare_dataframes_with_key_columns_with_tolerance(out_original, out_yaml, tolerance=0.05)
    
    
    
    # Create new dfs with the indentifier column
    df_ori_modified, df_yaml_modified = add_case_column_for_glpk_case(out_original_to_merge, out_yaml_to_merge)
    combined_df = concatenate_dataframes(df_ori_modified, df_yaml_modified)
    combined_df.to_csv(scen + f'outputs_merge_{case}_workflow_{out_name}.csv')