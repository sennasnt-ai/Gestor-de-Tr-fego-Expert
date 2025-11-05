import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
INPUT_FILENAME = 'temp_original_data.csv'
OUTPUT_FILENAME = 'compradores_meta_modelo_correto.csv'
DAYS_TO_FILTER = 90
COUNTRY_CODE_MAP = {
    'brasil': 'BR',
    'estados unidos': 'US',
    'portugal': 'PT',
    'argentina': 'AR',
    'chile': 'CL',
    'colombia': 'CO',
    'espanha': 'ES',
    'franca': 'FR',
    'reino unido': 'GB',
    'japao': 'JP',
    # Add other mappings as necessary
}

# --- Helper Functions ---

def split_name(full_name):
    """Splits a full name into first and last name."""
    if pd.isna(full_name) or not isinstance(full_name, str):
        return "", ""
    parts = full_name.strip().split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first_name, last_name

def format_phone(ddd, phone):
    """Formats phone number by combining DDD and phone."""
    ddd_str = str(ddd).strip() if pd.notna(ddd) else ''
    phone_str = str(phone).strip() if pd.notna(phone) else ''
    # Remove non-numeric characters
    ddd_clean = ''.join(filter(str.isdigit, ddd_str))
    phone_clean = ''.join(filter(str.isdigit, phone_str))

    full_phone = f"{ddd_clean}{phone_clean}"
    if not full_phone:
        return ""
    return full_phone

def get_country_code(country_name):
    """Converts country name to ISO 3166-1 alpha-2 code."""
    if pd.isna(country_name) or not isinstance(country_name, str):
        return ""
    return COUNTRY_CODE_MAP.get(country_name.lower().strip(), "")


# --- Main Script ---

# 1. Load Data
try:
    df = pd.read_csv(INPUT_FILENAME)
except FileNotFoundError:
    print(f"Error: Input file '{INPUT_FILENAME}' not found.")
    exit()

# 2. Filter by Date (Last 90 Days)
# Convert 'Data de Venda' to datetime objects, handling potential errors
df['Data de Venda'] = pd.to_datetime(df['Data de Venda'], errors='coerce', dayfirst=True)
df = df.dropna(subset=['Data de Venda']) # Drop rows where date conversion failed

# Calculate the cutoff date
ninety_days_ago = datetime.now() - timedelta(days=DAYS_TO_FILTER)
df_filtered = df[df['Data de Venda'] >= ninety_days_ago]

if df_filtered.empty:
    print("No sales found within the last 90 days. The output file will be empty.")
    pd.DataFrame().to_csv(OUTPUT_FILENAME, index=False)
    exit()

# 3. Create a new DataFrame for Meta format
meta_df = pd.DataFrame()

# 4. Map and Transform Data (in plain text)
meta_df['email'] = df_filtered['Email'].fillna('')

# Accessing the buyer name column by its index (16)
buyer_name_column = df_filtered.iloc[:, 16]
names = buyer_name_column.apply(split_name)
meta_df['fn'] = [n[0] for n in names]
meta_df['ln'] = [n[1] for n in names]

meta_df['phone'] = df_filtered.apply(lambda row: format_phone(row['DDD'], row['Telefone']), axis=1)
meta_df['zip'] = df_filtered['CEP'].fillna('')
meta_df['ct'] = df_filtered['Cidade'].fillna('')
meta_df['st'] = df_filtered['Estado'].fillna('')
meta_df['country'] = df_filtered['País'].apply(get_country_code)

# Add columns from the example that we don't have data for
meta_df['dob'] = ''
meta_df['gen'] = ''
meta_df['age'] = ''
meta_df['madid'] = '' # Mobile Advertiser ID

# Map event data
meta_df['event_name'] = 'Purchase'
# Format event_time to ISO 8601 format
meta_df['event_time'] = df_filtered['Data de Venda'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
meta_df['value'] = df_filtered['Faturamento líquido'].astype(float).fillna(0.0)
meta_df['currency'] = 'BRL'


# 5. Define final column order based on the screenshot
final_columns = [
    'email', 'phone', 'madid', 'fn', 'ln', 'zip', 'ct', 'st', 'country',
    'dob', 'gen', 'age', 'event_name', 'event_time', 'value', 'currency'
]
# Add any missing columns from the list, filling with empty strings
for col in final_columns:
    if col not in meta_df.columns:
        meta_df[col] = ''

meta_df = meta_df[final_columns]

# 6. Save to CSV
meta_df.to_csv(OUTPUT_FILENAME, index=False)

print(f"File '{OUTPUT_FILENAME}' created successfully with {len(meta_df)} records from the last 90 days.")
print("Columns are formatted according to the Meta example (plain text, ISO date).")
print(meta_df.head())
