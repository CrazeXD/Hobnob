# Used to filter the database to only include schools that are in the 9th grade or higher

import pandas as pd

# Load the CSV file into a DataFrame, replacing non-numeric values with 0
x = pd.read_csv("Public_Schools.csv", encoding='unicode_escape', na_values=['NaN', 'N/A', 'na', '--', '-', ''])

# Replace all non-numeric values in the ST_GRADE column with 0
x['ST_GRADE'] = pd.to_numeric(x['ST_GRADE'], errors='coerce').fillna(0).astype('Int64')

# Drop rows where ST_GRADE is less than 9
x = x.drop(x[x['ST_GRADE'] < 9].index)

# Print the updated DataFrame
x.to_csv("Public_Schools.csv", index=False)
