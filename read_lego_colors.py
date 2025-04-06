import pandas as pd

# Read the Lego Colors Excel file
lego_colors_df = pd.read_excel("Lego Colors.xlsx")

# Display the first few rows to understand the structure
print("Lego Colors DataFrame Sample:")
print(lego_colors_df.head())

# Get column names
print("\nColumn Names:")
print(lego_colors_df.columns.tolist())

# Get basic information about the dataframe
print("\nDataFrame Info:")
print(lego_colors_df.info()) 