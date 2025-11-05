import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
# The new list of buyers to be processed.
INPUT_FILENAME = 'nova_lista_compradores.csv'
# We still need the full history to identify repeat customers accurately.
FULL_HISTORY_FILENAME = 'temp_original_data.csv'
DAYS_TO_FILTER = 90
HIGH_VALUE_THRESHOLD = 160.62  # Confirmed from combined analysis

COUNTRY_CODE_MAP = {
    'brasil': 'BR', 'brazil': 'BR',
    'estados unidos': 'US', 'united states': 'US',
    'portugal': 'PT',
    # Add other mappings as necessary
}

# --- Helper Functions ---
def split_name(full_name):
    if pd.isna(full_name) or not isinstance(full_name, str): return "", ""
    parts = full_name.strip().split()
    first_name = parts[0]
    last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first_name, last_name

def format_phone(phone):
    phone_str = str(phone).strip() if pd.notna(phone) else ''
    phone_clean = ''.join(filter(str.isdigit, phone_str))
    return phone_clean if phone_clean else ""

def get_country_code(country_name):
    if pd.isna(country_name) or not isinstance(country_name, str): return ""
    return COUNTRY_CODE_MAP.get(country_name.lower().strip(), "")

# --- Main Script ---

# 1. Load Full Sales History to identify all repeat customers
try:
    df_history = pd.read_csv(FULL_HISTORY_FILENAME)
    df_history['Email'] = df_history['Email'].str.strip().str.lower()
    all_historic_emails = df_history['Email'].dropna().unique()
except FileNotFoundError:
    print(f"Warning: Full history file '{FULL_HISTORY_FILENAME}' not found. Repeat customer logic will only apply to the new list.")
    all_historic_emails = []


# 2. Load the New List to be Processed
try:
    df_new = pd.read_csv(INPUT_FILENAME)
except FileNotFoundError:
    print(f"Error: Input file '{INPUT_FILENAME}' not found.")
    exit()

# 3. Rename and Clean Columns for the New List
column_mapping = {
    'Email do(a) Comprador(a)': 'Email',
    'Comprador(a)': 'Nome Completo',
    'Telefone': 'Telefone Completo',
    'País': 'País',
    'Data da transação': 'Data de Venda',
    'Faturamento bruto (sem impostos)': 'Faturamento líquido'
    # CEP, Cidade, Estado are missing in the new file, they will be blank
}
df_new.rename(columns=column_mapping, inplace=True)

# Clean data
df_new['Email'] = df_new['Email'].str.strip().str.lower()
df_new['Faturamento líquido'] = pd.to_numeric(df_new['Faturamento líquido'], errors='coerce')
df_new['Data de Venda'] = pd.to_datetime(df_new['Data de Venda'], errors='coerce', dayfirst=True)
df_new.dropna(subset=['Email', 'Faturamento líquido', 'Data de Venda'], inplace=True)


# 4. Filter New List for Recent Sales (Last 90 Days)
ninety_days_ago = datetime.now() - timedelta(days=DAYS_TO_FILTER)
df_recent = df_new[df_new['Data de Venda'] >= ninety_days_ago].copy()

if df_recent.empty:
    print("No sales found in the new list within the last 90 days. No files will be generated.")
    exit()

# 5. Define the Base Formatting Function
def format_for_meta(df_segment, event_name):
    meta_df = pd.DataFrame()
    meta_df['email'] = df_segment['Email']

    names = df_segment['Nome Completo'].apply(split_name)
    meta_df['fn'] = [n[0] for n in names]
    meta_df['ln'] = [n[1] for n in names]

    meta_df['phone'] = df_segment['Telefone Completo'].apply(format_phone)
    # These columns are not in the new file, so we create them as empty
    for col in ['zip', 'ct', 'st']:
        meta_df[col] = ''
    meta_df['country'] = df_segment['País'].apply(get_country_code)

    meta_df['event_name'] = event_name
    meta_df['event_time'] = df_segment['Data de Venda'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    meta_df['value'] = df_segment['Faturamento líquido']
    meta_df['currency'] = 'BRL'

    # Add other empty columns from the example for structure consistency
    for col in ['madid', 'dob', 'gen', 'age']:
        meta_df[col] = ''

    # Reorder to match the example
    final_order = ['email', 'phone', 'madid', 'fn', 'ln', 'zip', 'ct', 'st', 'country',
                   'dob', 'gen', 'age', 'event_name', 'event_time', 'value', 'currency']

    return meta_df[final_order]

# 6. Generate Segmented Lists from the New Data

# a) All Recent Purchases from the new list
df_purchase = df_recent
meta_purchase = format_for_meta(df_purchase, 'Purchase')
meta_purchase.to_csv('nova_lista_recentes.csv', index=False)
print(f"Generated 'nova_lista_recentes.csv' with {len(meta_purchase)} records.")

# b) High-Value Purchases from the new list
df_high_value = df_recent[df_recent['Faturamento líquido'] > HIGH_VALUE_THRESHOLD]
if not df_high_value.empty:
    meta_high_value = format_for_meta(df_high_value, 'HighValuePurchase')
    meta_high_value.to_csv('nova_lista_alto_valor.csv', index=False)
    print(f"Generated 'nova_lista_alto_valor.csv' with {len(meta_high_value)} records.")
else:
    print("No high-value purchases found in the new list from the last 90 days.")

# c) Repeat Purchases (customers from the new list who are also in the old history)
repeat_emails_in_new_list = df_recent[df_recent['Email'].isin(all_historic_emails)]
if not repeat_emails_in_new_list.empty:
    meta_repeat = format_for_meta(repeat_emails_in_new_list, 'RepeatPurchase')
    meta_repeat.to_csv('nova_lista_recorrentes.csv', index=False)
    print(f"Generated 'nova_lista_recorrentes.csv' with {len(meta_repeat)} records.")
else:
    print("No customers from the new list were found in the previous sales history.")

print("\nAll files for the new list generated successfully.")
