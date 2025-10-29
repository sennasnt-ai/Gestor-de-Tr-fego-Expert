import pandas as pd

# --- Configuration ---
INPUT_FILENAME = 'temp_original_data.csv'

# --- Main Analysis Script ---

# 1. Load Data
try:
    df = pd.read_csv(INPUT_FILENAME)
    print(f"Successfully loaded {len(df)} records from '{INPUT_FILENAME}'.")
except FileNotFoundError:
    print(f"Error: Input file '{INPUT_FILENAME}' not found.")
    exit()

# 2. Analyze High-Value Customers
# Ensure the 'Faturamento líquido' column is numeric, coercing errors
df['Faturamento líquido'] = pd.to_numeric(df['Faturamento líquido'], errors='coerce')
# Drop rows where conversion failed
df.dropna(subset=['Faturamento líquido'], inplace=True)

# Calculate the 75th percentile as the high-value threshold
high_value_threshold = df['Faturamento líquido'].quantile(0.75)
print(f"\n--- High-Value Customer Analysis ---")
print(f"The 75th percentile for purchase value is: {high_value_threshold:.2f}")
print(f"Any purchase above this value will be marked as 'HighValuePurchase'.")


# 3. Identify Repeat Customers
# Ensure the 'Email' column is clean
df['Email'] = df['Email'].str.strip().str.lower()
df.dropna(subset=['Email'], inplace=True)

# Count occurrences of each email
email_counts = df['Email'].value_counts()

# Filter for emails that appear more than once
repeat_customer_emails = email_counts[email_counts > 1].index.tolist()

print(f"\n--- Repeat Customer Analysis ---")
if repeat_customer_emails:
    print(f"Found {len(repeat_customer_emails)} unique repeat customers.")
    # print("List of repeat customer emails:", repeat_customer_emails) # Keep this commented for privacy/brevity
else:
    print("No repeat customers found in the dataset.")

# This is just an analysis script, so we don't save a file.
# The results printed above will be used to build the main script.
