import pdfplumber
import pandas as pd
import re

def extract_format2(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text_lines = pdf.pages[0].extract_text().split("\n")
        text = pdf.pages[0].extract_text()

    orderNumber = re.search(r'Order\s+No.\s*([A-Za-z0-9-]+)', text, re.IGNORECASE)

    if orderNumber:
        order_number = orderNumber.group(1)
        print(order_number) 

    extracted_data = []

    for line in text_lines:
        match = re.search(r'(\d{2}:\d{5}[a-zA-Z])\s+.*?\s+(\d+)\s+\S+\s+[\d.]+\s+[\d.]+', line) # match case where sku has letter
        match2 = re.search(r'(\d{2}:\d{5})\s+.*?\s+(\d+)\s+\S+\s+[\d.]+\s+[\d.]+', line) # match case where sku has no letter
        if match:
            item_code, qty = match.groups()
            extracted_data.append([item_code, qty])
        elif match2:
            item_code, qty = match2.groups()
            extracted_data.append([item_code, qty])

   
    df = pd.DataFrame(extracted_data, columns=["Code", "Qty"])
    df["Code"] = df["Code"].apply(lambda x: f"{x[:2]}:{x}" if x.isdigit() and len(x) > 2 else x)
    return df, order_number

