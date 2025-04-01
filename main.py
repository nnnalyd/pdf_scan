import gui
import Format1
import Format2
import Format3
import pandas as pd

def feed_rows(x: int, fieldName: str) -> dict:
    dict = []
    for i in range(x):
        dict.append(fieldName)
    return dict

if __name__ == '__main__':
    customer_name, file_path, excel_path = gui.get_customer_details()

    existing_file = f'{excel_path}'
    df_existing = pd.read_excel(existing_file)

    df = None  

    for format_extractor, format_name in [(Format1.extract_format1, "Format 1"),
                                          (Format2.extract_format2, "Format 2"),
                                          (Format3.extract_format3, "Format 3")]:
        try:
            df, orderNumber = format_extractor(file_path)
            if df is not None and not df.empty:
                print(f'Successfully extracted using {format_name}')
                print(f'{orderNumber}')
                break  
            else:
                print(f'{format_name} returned None or empty DataFrame')
        except Exception as e:
            print(f'{format_name} raised an error: {e}')

    if df is None or df.empty:
        print("All formats failed. Exiting.")
        exit()

    mainData = {
        'CustomerName': feed_rows(df.shape[0], fieldName=customer_name),
        'PONumber' : feed_rows(df.shape[1], fieldName=orderNumber),
        'Code' : df['Code'],
        'Qty' : df['Qty']
    }
    # consider sample3's first line as it reads typeCode and Qty headers, remove them from the dataframe
    df2 = pd.DataFrame(mainData)
   
    print(df2)

    df_new = pd.concat([df_existing, df2], ignore_index=True)
    df_new.to_excel(existing_file, index=False)