import camelot
import pdfplumber
import pandas as pd
import re

# making new pandas dataframe out of extracted dataframe
def make_dataframe(dataframe):

    df2 = pd.DataFrame(columns=['Code', 'Qty'])
    df2['Code'] = dataframe[2]
    df2['Qty'] = dataframe[0]
    df2["Code"] = df2["Code"].apply(lambda x: f"{x[:2]}:{x}" if x.isdigit() and len(x) > 2 else x)

    print(df2)

    ## now do the thing
    ## df2.to_excel(out, index=False)

    return df2

# feeding customer name to all rows required
def feed_rows(x: int, customerName: str) -> dict:
    dict = []
    for i in range(x):
        dict.append(customerName)
    return dict

def extract_format1(file_path):
    sample = camelot.read_pdf(file_path)
    df1 = sample[0].df    
    with pdfplumber.open(file_path) as pdf:
        text = pdf.pages[0].extract_text()

    orderNumber = re.search(r'Order:\s*([A-Za-z0-9-]+)', text, re.IGNORECASE)

    if orderNumber:
        order_number = orderNumber.group(1)
        print(order_number) 
    return make_dataframe(dataframe=df1), order_number

