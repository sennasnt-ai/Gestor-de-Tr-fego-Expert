import csv
import io
import datetime

# Raw CSV data provided by the user
csv_data = """Nome do Produtor,Transação,Meio de Pagamento,Origem,Moeda,Preço do Produto,Moeda
,Preço da Oferta,Taxa de Câmbio,Moeda,Preço Original,Número da Parcela,Recorrênc
ia,Data de Venda,Data de Confirmação,Status,"
fn",Documento,Email,DDD,Telefone,CEP,Cidade,Estado,Bairro,País,Endereço,Número,C
omplemento,chave,Código do Produto,Código da Afiliação,Código de Oferta,Origem d
e Checkout,Tipo de Pagamento,Período Grátis,Tem co-produção,Venda feita como,Pre
ço Total,Tipo pagamento oferta,Taxa de Câmbio Real,Preço Total Convertido,Quanti
dade de itens,Oferta de Upgrade,Cupom,Moeda,Valor que você recebeu convertido,Ta
xa de Câmbio do valor recebido,Data Vencimento,Instagram,Origem da venda,Moeda d
e recebimento,Faturamento líquido,Código do assinante,Nota Fiscal,Valor do frete
 bruto
Cacá Montans,HP0354746990,HotPay,,BRL,197.00,BRL,89.72,,,,1,,20/09/2025 06:42:57
,20/09/2025 06:44:43,Aprovado,Denise Assis,1079001735,dassis.denise@gmail.com,21
,977100000,,,,,Brasil,,,,0n0g6knqc0aqa,3838930,J90994302D,3bij7bdt,HOTMART_SITE,
Pix,Não,Sim,Produtor,197.00,Apenas à vista,1.000.000.000.000,197.00,1,Não,,,,,,,
HOTMART_SITE,BRL,89.72,,Vendedor,0
Cacá Montans,HP1234918965,HotPay,,BRL,47.00,BRL,21.02,,,,1,,14/09/2025 15:14:55,
14/09/2025 15:40:49,Completo,Marja Helena da Silva Lopes de Oliveira,94646422034
,marjahelenaoliveira@gmail.com,,,,,,,Brasil,,,,0myp28369ayfd,6036994,X101273564T
,abhvfydl,www.youtube.com,Pix,Não,Sim,Produtor,47.00,Apenas à vista,1.000.000.00
0.000,47.00,1,Não,,,,,,,,BRL,21.02,,Vendedor,0
Cacá Montans,HP1210392438,HotPay,,BRL,97.00,BRL,87.85,,,,1,,14/09/2025 05:34:20,
14/09/2025 05:35:38,Completo,Erika Ikuta,1717658938,erikaekoji@gmail.com,,810804
2255476,,,,,Brasil,,,,0myhxbtd70bz1,6246693,P101893684Q,rlh34kod,,Pix,Não,Não,Pr
odutor,97.00,Apenas à vista,1.000.000.000.000,97.00,1,Não,,,,,,,,BRL,87.85,,Vend
edor,0
Cacá Montans,HP0707902749,HotPay,,BRL,47.00,BRL,21.02,,,,1,,08/09/2025 07:32:56,
08/09/2025 07:35:12,Completo,Denise Santos,33987060883,denise.santos74@yahoo.com
.br,11,947445142,,,,,Brasil,,,,0mwmyz9f26wm1,6149193,Q101624108N,rmnazcln,,Pix,N
ão,Sim,Produtor,47.00,Apenas à vista,1.000.000.000.000,47.00,1,Não,,,,,,,,BRL,21
.02,,Vendedor,0
Cacá Montans,HP2761014825,HotPay,,BRL,47.00,BRL,21.02,,,,1,,07/09/2025 20:00:55,
07/09/2025 20:01:46,Completo,Marlene Marlene Correia,38773384020,correia47marlen
e@hotmail.com,51,995563550,,,,,Brasil,,,,0mwg0jr3yzs7s,6149193,Q101624108N,rmnaz
cln,,Pix,Não,Sim,Produtor,47.00,Apenas à vista,1.000.000.000.000,47.00,1,Não,,,,
,,,,BRL,21.02,,Vendedor,0
Cacá Montans,HP2185399822,HotPay,,BRL,47.00,BRL,21.02,,,,1,,07/09/2025 19:09:29,
07/09/2025 19:10:34,Completo,Roseli Lourenço Leite FargnoliNunes da Silva ,10788
968874,rosefarg.31@gmail.com,11,981360179,,,,,Brasil,,,,0mwfmsztgdf5s,6149193,Q1
01624108N,rmnazcln,,Pix,Não,Sim,Produtor,47.00,Apenas à vista,1.000.000.000.000,
47.00,1,Não,,,,,,,,BRL,21.02,,Vendedor,0
Cacá Montans,HP2357388038,HotPay,,BRL,47.00,BRL,21.02,,,,1,,07/09/2025 16:13:14,
07/09/2025 16:13:17,Completo,Adriana Xavier da Silva ,17755543846,adrianna.maxim
iano@gmail.com,11,985622448,,,,,Brasil,,,,0mwecfgcst2fj,6149193,Q101624108N,rmna
zcln,,Cartão de Crédito,Não,Sim,Produtor,47.00,Apenas à vista,1.000.000.000.000,
47.00,1,Não,,,,,,,,BRL,21.02,,Vendedor,0
Cacá Montans,HP0436013327,HotPay,,BRL,47.00,BRL,21.02,,,,1,,07/09/2025 10:57:26,
07/09/2025 10:58:23,Completo,Paolla Santiago Silva,5589252946,paollasantiago@gma
il.com,48,996566959,,,,,Brasil,,,,0mwc463tedvs0,6149193,Q101624108N,rmnazcln,,Pi
x,Não,Sim,Produtor,47.00,Apenas à vista,1.000.000.000.000,47.00,1,Não,,,,,,,,BRL
,21.02,,Vendedor,0
Cacá Montans,HP1903644847,HotPay,,BRL,47.00,BRL,21.02,,,,1,,06/09/2025 23:46:11,
07/09/2025 00:00:27,Completo,Rosy Carvalho,,rosecarvalho52@outlook.com,22,999260
020,,,,,Brasil,,,,0mw7aht4xt0py,6149193,Q101624108N,rmnazcln,,Pix,Não,Sim,Produt
or,47.00,Apenas à vista,1.000.000.000.000,47.00,1,Não,,,,,,,,BRL,21.02,,Vendedor
,0
Cacá Montans,HP1383464334,HotPay,,BRL,47.00,BRL,21.02,,,,2,,06/09/2025 23:23:12,
06/09/2025 23:23:16,Completo,Elaine Aparecida Vicente Viana,16145901845,elaineav
viana@gmail.com,11,996106631,,,,,Brasil,,,,0mw759w5ydsdq,6149193,Q101624108N,rmn
azcln,,Cartão de Crédito,Não,Sim,Produtor,49.04,Parcelamento padrão (até 12×),1.
000.000.000.000,49.04,1,Não,,,,,,,,BRL,21.02,,Vendedor,0
Cacá Montans,HP0592531153,HotPay,,BRL,47.00,BRL,21.02,,,,1,,06/09/2025 15:14:29,
06/09/2025 15:17:03,Completo,Viviane Calixto Diz Hott,,vivianediz123@gmail.com,2
4,999476105,,,,,Brasil,,,,0mw3ne0ycq3f0,6149193,Q101624108N,rmnazcln,,Pix,Não,Si
m,Produtor,47.00,Apenas à vista,1.000.000.000.000,47.00,1,Não,,,,,,,,BRL,21.02,,
Vendedor,0
Cacá Montans,HP3247313888,HotPay,,BRL,47.00,BRL,21.02,,,,1,,06/09/2025 14:54:08,
06/09/2025 14:55:37,Completo,Cíntia Agrizzi,5573379763,cintiaagrizzi@hotmail.com
,27,992928382,,,,,Brasil,,,,0mw3grz02zvfp,6149193,Q101624108N,rmnazcln,,Pix,Não,
Sim,Produtor,47.00,Apenas à vista,1.000.000.000.000,47.00,1,Não,,,,,,,,BRL,21.02
,,Vendedor,0
"""

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

def process_data(raw_data):
    # The header is broken into two lines, we need to manually create the correct one
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

    # Skip the first two lines of the raw data which are the malformed headers
    data_io = io.StringIO('\\n'.join(raw_data.split('\\n')[2:]))
    reader = csv.reader(data_io)

    processed_records = []
    for row in reader:
        if not row or not any(row):  # Skip empty rows
            continue

        record = dict(zip(header, row))

        # Split name into first and last
        full_name = record.get("fn_full", "").strip()
        name_parts = full_name.split(" ", 1)
        fn = name_parts[0]
        ln = name_parts[1] if len(name_parts) > 1 else ""

        # Format data
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

    # Generate new CSV
    output_io = io.StringIO()
    if processed_records:
        fieldnames = processed_records[0].keys()
        writer = csv.DictWriter(output_io, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_records)

    return output_io.getvalue()

# Main execution
if __name__ == '__main__':
    # Since this script will be executed directly, we read the data, process it,
    # and write it to the final file.

    # Reading the full data from the file provided in the previous step
    # (Simulated here with the local variable `csv_data`)

    final_csv_content = process_data(csv_data)

    with open('compradores_formatado_meta_avancado.csv', 'w', newline='') as f:
        f.write(final_csv_content)

    print("Arquivo 'compradores_formatado_meta_avancado.csv' gerado com sucesso.")
