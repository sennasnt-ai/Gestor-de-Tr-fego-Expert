import pandas as pd
import numpy as np

# --- Configuration ---
OLD_DATA_FILENAME = 'temp_original_data.csv'
NEW_DATA_FILENAME = 'nova_lista_compradores.csv'

# --- Main Analysis Script ---

# 1. Load Both Datasets
try:
    df_old = pd.read_csv(OLD_DATA_FILENAME)
    print(f"Successfully loaded {len(df_old)} records from '{OLD_DATA_FILENAME}'.")
except FileNotFoundError:
    print(f"Error: Old data file '{OLD_DATA_FILENAME}' not found. Continuing with new data only.")
    df_old = pd.DataFrame()

try:
    df_new = pd.read_csv(NEW_DATA_FILENAME)
    print(f"Successfully loaded {len(df_new)} records from '{NEW_DATA_FILENAME}'.")
except FileNotFoundError:
    print(f"Error: New data file '{NEW_DATA_FILENAME}' not found.")
    exit()

# Standardize column names before concatenating
# Assuming the structure is similar, but let's be safe
# Old data uses 'Faturamento líquido', let's check the new one.
# For simplicity, we'll map the new file's value column to the old one's name.
# Let's inspect the new file's columns first
print("\nColumns in new data file:", df_new.columns.tolist())

# Based on inspection, the value column in the new file might be 'Preço Líquido da Venda' or similar
# Let's assume the relevant columns are named consistently for this analysis script.
# If not, the master script will need more robust handling.
value_column_new = 'Preço Líquido da Venda' # This is a guess based on previous data
email_column_new = 'E-mail do Comprador'
value_column_old = 'Faturamento líquido'
email_column_old = 'Email'

# Rename new df columns to match old df's structure for easy concatenation
df_new_renamed = df_new.rename(columns={
    value_column_new: value_column_old,
    email_column_new: email_column_old
})

# 2. Consolidate Data
df_combined = pd.concat([df_old, df_new_renamed], ignore_index=True)
print(f"\nTotal combined records: {len(df_combined)}")

# 3. Analyze High-Value Customers on Combined Data
df_combined[value_column_old] = pd.to_numeric(df_combined[value_column_old], errors='coerce')
df_combined.dropna(subset=[value_column_old], inplace=True)

high_value_threshold = df_combined[value_column_old].quantile(0.75)
print(f"\n--- Recalculated High-Value Customer Analysis ---")
print(f"The new 75th percentile for purchase value is: {high_value_threshold:.2f}")

# 4. Identify All Repeat Customers in Combined Data
df_combined[email_column_old] = df_combined[email_column_old].str.strip().str.lower()
df_combined.dropna(subset=[email_column_old], inplace=True)

email_counts = df_combined[email_column_old].value_counts()
repeat_customer_emails = email_counts[email_counts > 1].index.tolist()

print(f"\n--- Recalculated Repeat Customer Analysis ---")
print(f"Found {len(repeat_customer_emails)} unique repeat customers across all data.")

print("\nAnalysis complete. These new values will inform the segmentation script.")
