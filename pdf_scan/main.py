import os
import pdfplumber
import re
import pandas as pd
import gui
import datetime


# patterns
item_code_pattern = re.compile(r'\b(?:\d{5}|\d{5}[A-Za-z]|[0-9]{2}:[0-9]{5}|[0-9]{2}:[0-9]{5}[A-Za-z])\b')
order_pattern_inline = re.compile(
    r'(?:'
    r'Order\s+number\s*:\s*'
    r'|Marydias\s+Pty\s+Ltd\s+-\s+PO\s+#'
    r'|Purchase\s+Order\s+No\.\s*:\s*'
    r'|Order:\s*'
    r'|Order\s+No\.\s*'
    r'|Order\s+Number\s*'
    r'|Order\s+No:\s*'
    r'|Customers\s+Order\s+No:\s*'
    r'|PO\s+No.\s*'
    r')'
    r'([A-Za-z0-9-]+)'
)
order_header_pattern = re.compile(r'(Order\s+Number|Order\s+No\.?|P\.O\.\s*No\.?|P\.O\.|Purchase\s+Order|Document\s+Number)', re.I)

# functions

def feed_rows(x: int, fieldName: str) -> dict:
    dict = []
    for i in range(x):
        dict.append(fieldName)
    return dict

def extract_lines_from_pdf(pdf_path):
    """Extract lines from first page of PDF."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            if text:
                return text.split('\n')
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return []

def code_qty(line, results):
    """Extract code and quantity from a line."""
    pattern = re.compile(
        r'(?P<qty1>(?<![\w/:-])\b\d{1,4}\b(?![\w/:-]))\s+(?:.+?\s+)?(?P<code1>\b\d{5}\b|\b\d{5}[A-Za-z]\b|[0-9]{3}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{5}[A-Za-z]?)'
        r'|\b(?P<code2>\d{5}|\d{5}[A-Za-z]|[0-9]{3}:[0-9]{2}:[0-9]{2}|[0-9]{2}:[0-9]{5}[A-Za-z]?)\b\s+(?:.+?\s+)?(?P<qty2>(?<![\w/:-])\b\d{1,4}\b(?![\w/:-]))'
    )
    match = pattern.search(line)
    if match:
        qty = int(match.group("qty1") or match.group("qty2"))
        code = match.group("code1") or match.group("code2")
        results["qty"] = qty
        results["code"] = code
        return True
    return False

def order_number(line, results, previous_line=None, two_lines_ago=None) -> tuple:
    """Extract order number based on current and surrounding lines."""
    matched = False
    number = None

    match = order_pattern_inline.search(line)
    if match:
        candidate = match.group(1)
        if re.search(r'\d', candidate):
            number = candidate.lstrip("#")
            results['PONumber'] = number
            return True, number

    if previous_line and order_header_pattern.search(previous_line):
        possible = re.search(r'#?([A-Za-z0-9-]{4,})', line)
        if possible and re.search(r'\d', possible.group(1)):
            number = possible.group(1)
            results['PONumber'] = number
            return True, number

    if order_header_pattern.search(line):
        for past_line in [previous_line, two_lines_ago]:
            if past_line:
                possible = re.search(r'#?([A-Za-z0-9-]{4,})', past_line)
                if possible and re.search(r'\d', possible.group(1)):
                    number = possible.group(1)
                    results['PONumber'] = number
                    return True, number

    return matched, number

def extracts(dir, dir_str) -> dict:
    """Main extraction loop over all PDF files."""
    frames = []

    for file in os.listdir(dir):
        filename = os.fsdecode(file)
        pdf_path = f'{dir_str}/{filename}'
        lines = extract_lines_from_pdf(pdf_path)
        if not lines:
            continue

        ord_lines = []
        previous_line = None
        two_lines_ago = None

        for line in lines:
            results = {
            }
            ordMatched, ordNumber = order_number(line, results, previous_line, two_lines_ago)
            if code_qty(line, results) or ordMatched:
                ord_lines.append(results)

            customer_name = os.path.splitext(os.path.basename(pdf_path))[0]
            fn, ln = convert_names('pdf_scan/nameconversion.xlsx', customer_name)
            results['First Name'] = fn
            results['Last Name'] = ln

            two_lines_ago = previous_line
            previous_line = line

        print('---------------------------------------------------------------------------------------')
        print(pdf_path)
        print(ord_lines)
        frames.append(ord_lines)

    return frames

def convert_codes(codes):
    data_dict = {}
    with open(codes, "r") as f:
        lines = f.readlines()
        for line in lines:
            lhs, rhs = line.strip().split("\t")
            data_dict[lhs] = rhs

    return data_dict

def convert_names(names_path, cust_name):
    df = pd.read_excel(names_path)
    print(cust_name)
    match = df[df['File name'] == cust_name]

    fn = match['First Name'].values[0] if not match.empty else None
    ln = match['Last Name'].values[0] if not match.empty else None

    return fn, ln

def main() -> None:
    files_path, excel_path = gui.get_customer_details()
    directory = os.fsencode(files_path)

    existing_file = f'{excel_path}'
    df_existing = pd.read_excel(existing_file)

    frames = extracts(dir=directory, dir_str=files_path)
    
    final_rows = []

    for ord_lines in frames:
        current_po = None
        for entry in ord_lines:
            if 'PONumber' in entry:
                current_po = entry['PONumber'] 
            if 'First Name' in entry:
                current_fn = entry['First Name']
            if 'Last Name' in entry:
                current_ln = entry['Last Name']
            if 'code' in entry and 'qty' in entry:
                final_rows.append({
                    'PoNo': current_po,
                    'First Name': current_fn,
                    'Last Name': current_ln,
                    'podate': datetime.datetime.now().strftime("%Y-%m-%d"),
                    'SKU': entry['code'],
                    'Quantity': entry['qty']
                })

    df = pd.DataFrame(final_rows, columns=['PoNo', 'First Name', 'Last Name', 'custnotes', 'podate', 'SKU', 'Quantity', 'UOM', 'Price', 'Discount', 'Vat'])
    df["SKU"] = df["SKU"].apply(lambda x: f"{x[:2]}:{x}" if (len(x) == 5 or len(x) == 6) else x)
    code_dict = convert_codes("pdf_scan/convert.txt")

    df["SKU"] = df["SKU"].replace(code_dict)

    print(df)

    df_new = pd.concat([df_existing, df], ignore_index=True)
    df_new.to_excel(existing_file, index=False)
    
if __name__ == "__main__":
    main()


