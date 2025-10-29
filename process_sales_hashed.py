import pandas as pd
import hashlib
import re

def normalize_and_hash(value):
    """Normalizes and hashes a string value using SHA-256."""
    if pd.isna(value):
        return ""

    # Convert to string and remove leading/trailing whitespace, then lowercase
    value_str = str(value).strip().lower()

    return hashlib.sha256(value_str.encode('utf-8')).hexdigest()

def normalize_and_hash_phone(value):
    """Normalizes phone number and hashes using SHA-256."""
    if pd.isna(value):
        return ""
    # Remove non-numeric characters
    value_str = str(value)
    # First, remove the '+' if it exists, as it's not needed for hashing with country code
    if value_str.startswith('+'):
        value_str = value_str[1:]

    # Remove all non-numeric characters
    cleaned_number = re.sub(r'\D', '', value_str)
    return hashlib.sha256(cleaned_number.encode('utf-8')).hexdigest()


def normalize_and_hash_zip(value):
    """Normalizes zip code and hashes using SHA-256."""
    if pd.isna(value):
        return ""
    # Remove non-numeric characters
    cleaned_zip = re.sub(r'\D', '', str(value))
    return hashlib.sha256(cleaned_zip.encode('utf-8')).hexdigest()

# Load the sales data
try:
    df = pd.read_csv('temp_original_data.csv')
except FileNotFoundError:
    print("Error: temp_original_data.csv not found.")
    exit()

# --- Data Transformation ---
# Create a new DataFrame for the formatted data
formatted_df = pd.DataFrame()

# Combine DDD and Telefone
# Fill NaN values with empty strings to avoid errors during concatenation
df['full_phone'] = df['DDD'].fillna('').astype(str) + df['Telefone'].fillna('').astype(str)

# Apply hashing to PII columns
formatted_df['em'] = df['Email'].apply(normalize_and_hash)
formatted_df['ph'] = df['full_phone'].apply(normalize_and_hash_phone)

# Accessing the buyer name column by its index (16) due to header parsing issues.
buyer_name_column = df.iloc[:, 16]
formatted_df['fn'] = buyer_name_column.apply(normalize_and_hash)
formatted_df['ln'] = buyer_name_column.apply(normalize_and_hash) # Using full name for both
formatted_df['ct'] = df['Cidade'].apply(normalize_and_hash)
formatted_df['st'] = df['Estado'].apply(normalize_and_hash)
formatted_df['zp'] = df['CEP'].apply(normalize_and_hash_zip)
# The 'País' column might have missing values.
formatted_df['country'] = df['País'].apply(normalize_and_hash)

# Process other required columns
# The 'Faturamento líquido' column is already a numeric value.
formatted_df['value'] = df['Faturamento líquido'].astype(float)

# Add 'event_name'
formatted_df['event_name'] = 'Purchase'

# Convert 'event_time' to Unix timestamp
formatted_df['event_time'] = pd.to_datetime(df['Data de Venda'], dayfirst=True).astype(int) // 10**9

# Add 'order_id'
formatted_df['order_id'] = df['Transação']


# --- Finalizing the DataFrame ---
# Define the final column order as recommended by Meta
final_columns = [
    'em', 'ph', 'fn', 'ln', 'zp', 'ct', 'st', 'country',
    'value', 'event_name', 'event_time', 'order_id'
]

# Reorder the DataFrame to match the final column order
formatted_df = formatted_df[final_columns]

# --- Save to CSV ---
output_filename = 'compradores_formatado_meta_final_hashed.csv'
formatted_df.to_csv(output_filename, index=False)

print(f"File '{output_filename}' created successfully with hashed PII.")
print(formatted_df.head())
