import csv
import io
import datetime

# Country codes mapping
country_codes = {
    "Brasil": "BR",
    "Angola": "AO",
    "Portugal": "PT",
    "Estados Unidos": "US",
    "França": "FR",
    "Reino Unido": "GB",
    "Suíça": "CH",
    "Bélgica": "BE",
    "Canadá": "CA",
    "África do Sul": "ZA",
    "Afeganistão": "AF",
    "Alemanha": "DE",
    "Itália": "IT",
    "Noruega": "NO",
    "Moçambique": "MZ",
    "Japão": "JP",
    "Espanha": "ES",
    "Irlanda": "IE"
}

def get_country_code(country_name):
    return country_codes.get(country_name.strip(), "")

def format_phone(ddd, phone, country):
    if not phone or not isinstance(phone, str) or not phone.strip():
        return ""

    country_phone_code = ""
    if country.strip() == "Brasil":
        country_phone_code = "55"
    # This is a simplification. A more robust solution would have a full mapping.
    elif country.strip() in ["Portugal", "Angola", "Moçambique"]:
        # Example codes, would need a proper map
        if country.strip() == "Portugal": country_phone_code = "351"
        if country.strip() == "Angola": country_phone_code = "244"
        if country.strip() == "Moçambique": country_phone_code = "258"
    else:
        # Fallback for other countries - assuming phone might be complete
        return "".join(filter(str.isdigit, phone))

    full_phone = ""
    if ddd and isinstance(ddd, str) and ddd.strip():
        full_phone = f"{country_phone_code}{ddd.strip()}{phone.strip()}"
    else:
        full_phone = f"{country_phone_code}{phone.strip()}"

    return "".join(filter(str.isdigit, full_phone))

def get_unix_timestamp(date_str):
    try:
        # Format: "20/09/2025 06:42:57"
        dt_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        return int(dt_obj.timestamp())
    except (ValueError, TypeError):
        return ""

def process_data(input_filepath):
    header = [
        "Nome do Produtor", "Transação", "Meio de Pagamento", "Origem", "Moeda_1",
        "Preço do Produto", "Moeda_2", "Preço da Oferta", "Taxa de Câmbio",
        "Moeda_3", "Preço Original", "Número da Parcela", "Recorrência",
        "Data de Venda", "Data de Confirmação", "Status", "fn_full", "Documento",
        "Email", "DDD", "Telefone", "CEP", "Cidade", "Estado", "Bairro", "País",
        "Endereço", "Número", "Complemento", "chave", "Código do Produto",
        "Código da Afiliação", "Código de Oferta", "Origem de Checkout",
        "Tipo de Pagamento", "Período Grátis", "Tem co-produção",
        "Venda feita como", "Preço Total", "Tipo pagamento oferta",
        "Taxa de Câmbio Real", "Preço Total Convertido", "Quantidade de itens",
        "Oferta de Upgrade", "Cupom", "Moeda_4", "Valor que você recebeu convertido",
        "Taxa de Câmbio do valor recebido", "Data Vencimento", "Instagram",
        "Origem da venda", "Moeda de recebimento", "Faturamento líquido",
        "Código do assinante", "Nota Fiscal", "Valor do frete bruto"
    ]

    processed_records = []
    with open(input_filepath, 'r', encoding='utf-8') as f:
        # Skip the first two header lines
        next(f)
        next(f)
        reader = csv.reader(f)
        for row in reader:
            if not row or not any(row):  # Skip empty rows
                continue

            record = dict(zip(header, row))

            full_name = record.get("fn_full", "").strip()
            name_parts = full_name.split(" ", 1)
            fn = name_parts[0]
            ln = name_parts[1] if len(name_parts) > 1 else ""

            email = record.get("Email", "").lower().strip()
            phone = format_phone(record.get("DDD"), record.get("Telefone"), record.get("País"))
            country = get_country_code(record.get("País", ""))
            value = record.get("Preço Total", "0.00").replace(",", ".").strip()
            event_time = get_unix_timestamp(record.get("Data de Venda", ""))
            order_id = record.get("Transação", "").strip()

            processed_records.append({
                "email": email,
                "phone": phone,
                "fn": fn,
                "ln": ln,
                "country": country,
                "value": value,
                "event_name": "Purchase",
                "event_time": event_time,
                "order_id": order_id
            })

    output_io = io.StringIO()
    if processed_records:
        fieldnames = processed_records[0].keys()
        writer = csv.DictWriter(output_io, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_records)

    return output_io.getvalue()

if __name__ == '__main__':
    # The script now expects the input file path as an argument,
    # but for direct execution, we will hardcode it to the temp file.
    # A better practice would be to use sys.argv.
    input_file = 'temp_original_data.csv'

    # Read the content from the provided file
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = f.read()

    # Create a new file with the content to be processed, simulating the upload
    with open('temp_processing_file.csv', 'w', encoding='utf-8') as f:
        f.write(raw_data)

    final_csv_content = process_data('temp_processing_file.csv')

    with open('compradores_formatado_meta_avancado.csv', 'w', newline='') as f:
        f.write(final_csv_content)

    print("Arquivo 'compradores_formatado_meta_avancado.csv' gerado com sucesso.")
