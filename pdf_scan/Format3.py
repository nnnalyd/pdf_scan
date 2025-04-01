import pdfplumber
import pandas as pd
import re

def extract_format3(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()

    match = re.search(r'Confirmation of Order\n(.*?)\nDelivery note', text, re.DOTALL)
    if not match:
        return None
    else:
        orderNumber = re.search(r'Order\s+number\s*:\s*([A-Za-z0-9-]+)', text, re.IGNORECASE)

        if orderNumber:
            order_number = orderNumber.group(1)
            print(order_number) 

        order_text = match.group(1).strip()
        
        order_lines = [line.strip() for line in order_text.split('\n') if line.strip()]
        
        structured_data = []
        for line in order_lines:
            parts = re.split(r'\s+', line)  
            if len(parts) >= 3:  
                qty = parts[0] 
                item_code = parts[2]  
                structured_data.append([item_code, qty])
        
        df = pd.DataFrame(structured_data, columns=["Code", "Qty"])
        df = df.drop([0]).reset_index(drop=True)
        df["Code"] = df["Code"].apply(lambda x: f"{x[:2]}:{x}" if len(x) > 2 else x)

        return df, order_number

