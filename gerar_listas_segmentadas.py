import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
INPUT_FILENAME = 'temp_original_data.csv'
DAYS_TO_FILTER = 90
HIGH_VALUE_THRESHOLD = 160.62  # Determined from analysis (75th percentile)

COUNTRY_CODE_MAP = {
    'brasil': 'BR', 'brazil': 'BR',
    'estados unidos': 'US', 'united states': 'US',
    'portugal': 'PT',
    # Add other common variations and mappings as necessary
}

# --- Helper Functions (reused from previous script) ---

def split_name(full_name):
    if pd.isna(full_name) or not isinstance(full_name, str): return "", ""
    parts = full_name.strip().split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first_name, last_name

def format_phone(ddd, phone):
    ddd_str = str(ddd).strip() if pd.notna(ddd) else ''
    phone_str = str(phone).strip() if pd.notna(phone) else ''
    ddd_clean = ''.join(filter(str.isdigit, ddd_str))
    phone_clean = ''.join(filter(str.isdigit, phone_str))
    full_phone = f"{ddd_clean}{phone_clean}"
    return full_phone if full_phone else ""

def get_country_code(country_name):
    if pd.isna(country_name) or not isinstance(country_name, str): return ""
    return COUNTRY_CODE_MAP.get(country_name.lower().strip(), "")

# --- Main Script ---

# 1. Load and Clean Full Sales History
try:
    df_full = pd.read_csv(INPUT_FILENAME)
except FileNotFoundError:
    print(f"Error: Input file '{INPUT_FILENAME}' not found.")
    exit()

# Clean email and value columns for entire dataset
df_full['Email'] = df_full['Email'].str.strip().str.lower()
df_full['Faturamento líquido'] = pd.to_numeric(df_full['Faturamento líquido'], errors='coerce')
df_full.dropna(subset=['Email', 'Faturamento líquido'], inplace=True)

# 2. Identify All Repeat Customer Emails
email_counts = df_full['Email'].value_counts()
repeat_customer_emails = email_counts[email_counts > 1].index.tolist()

# 3. Filter for Recent Sales (Last 90 Days)
df_full['Data de Venda'] = pd.to_datetime(df_full['Data de Venda'], errors='coerce', dayfirst=True)
df_full.dropna(subset=['Data de Venda'], inplace=True)
ninety_days_ago = datetime.now() - timedelta(days=DAYS_TO_FILTER)
df_recent = df_full[df_full['Data de Venda'] >= ninety_days_ago].copy()

if df_recent.empty:
    print("No sales found within the last 90 days. No files will be generated.")
    exit()

# 4. Define the Base Formatting Function
def format_for_meta(df_segment, event_name):
    meta_df = pd.DataFrame()
    meta_df['email'] = df_segment['Email']

    # Use iloc for the name column due to parsing issues
    buyer_name_column = df_segment.iloc[:, 16]
    names = buyer_name_column.apply(split_name)
    meta_df['fn'] = [n[0] for n in names]
    meta_df['ln'] = [n[1] for n in names]

    meta_df['phone'] = df_segment.apply(lambda row: format_phone(row['DDD'], row['Telefone']), axis=1)
    meta_df['zip'] = df_segment['CEP'].fillna('')
    meta_df['ct'] = df_segment['Cidade'].fillna('')
    meta_df['st'] = df_segment['Estado'].fillna('')
    meta_df['country'] = df_segment['País'].apply(get_country_code)

    meta_df['event_name'] = event_name
    meta_df['event_time'] = df_segment['Data de Venda'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    meta_df['value'] = df_segment['Faturamento líquido']
    meta_df['currency'] = 'BRL'

    final_columns = ['email', 'phone', 'fn', 'ln', 'zip', 'ct', 'st', 'country',
                     'event_name', 'event_time', 'value', 'currency']

    # Add other empty columns from the example for structure consistency
    for col in ['madid', 'dob', 'gen', 'age']:
        if col not in meta_df.columns:
            meta_df[col] = ''

    # Reorder to match the example
    final_order = ['email', 'phone', 'madid', 'fn', 'ln', 'zip', 'ct', 'st', 'country',
                   'dob', 'gen', 'age', 'event_name', 'event_time', 'value', 'currency']

    return meta_df[final_order]

# 5. Generate Segmented Lists

# a) All Recent Purchases
df_purchase = df_recent
meta_purchase = format_for_meta(df_purchase, 'Purchase')
meta_purchase.to_csv('compradores_recentes.csv', index=False)
print(f"Generated 'compradores_recentes.csv' with {len(meta_purchase)} records.")

# b) High-Value Purchases
df_high_value = df_recent[df_recent['Faturamento líquido'] > HIGH_VALUE_THRESHOLD]
if not df_high_value.empty:
    meta_high_value = format_for_meta(df_high_value, 'HighValuePurchase')
    meta_high_value.to_csv('compradores_alto_valor.csv', index=False)
    print(f"Generated 'compradores_alto_valor.csv' with {len(meta_high_value)} records.")
else:
    print("No high-value purchases found in the last 90 days.")

# c) Repeat Purchases
df_repeat = df_recent[df_recent['Email'].isin(repeat_customer_emails)]
if not df_repeat.empty:
    meta_repeat = format_for_meta(df_repeat, 'RepeatPurchase')
    meta_repeat.to_csv('compradores_recorrentes.csv', index=False)
    print(f"Generated 'compradores_recorrentes.csv' with {len(meta_repeat)} records.")
else:
    print("No repeat customers made a purchase in the last 90 days.")

print("\nAll files generated successfully.")
