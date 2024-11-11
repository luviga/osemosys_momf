# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 22:41:18 2024

@author: luisfernando
"""

import pandas as pd
from copy import deepcopy

# Load the DataFrame
df = pd.read_csv('RDOutput.csv')

# Create a deep copy of the DataFrame for modification and another one for comparison
df_copy = deepcopy(df)
df_copy_original = deepcopy(df)

# Find rows where Sector is 'AFOLU' and Strategy is 'LTSNZ'
condition_ltsnz = (df_copy['Sector'] == 'AFOLU') & (df_copy['Strategy'] == 'LTSNZ')

# Find the corresponding rows for 'Sector = AFOLU' and 'Strategy = LTS'
condition_lts = (df_copy['Sector'] == 'AFOLU') & (df_copy['Strategy'] == 'LTS')

# Count the number of rows that are being replaced
rows_to_replace = df_copy.loc[condition_ltsnz].shape[0]
print(f"Number of rows being replaced: {rows_to_replace}")

# Ensure the rows match and update the LTSNZ rows with values from LTS
for col in df.columns:
    if col != 'Strategy':  # Avoid overwriting the 'Strategy' column itself
        df_copy.loc[condition_ltsnz, col] = df.loc[condition_lts, col].values

# Verify if the DataFrames have the same size after copying
if df.shape == df_copy.shape:
    print("Both DataFrames have the same shape.")
else:
    print("DataFrames do not have the same shape!")

# Now let's calculate the difference between the original and modified DataFrames
difference = df_copy.loc[condition_ltsnz] != df_copy_original.loc[condition_ltsnz]

# Print out the difference (True means the values were changed, False means they were not changed)
print("Differences in the modified rows:")
print(difference)

# Save the modified DataFrame as RDOutput_replaced.csv
df_copy.to_csv('RDOutput_replaced.csv', index=False)

# Print a message indicating success
print("Replacement complete. DataFrame saved as 'RDOutput_replaced.csv'.")


