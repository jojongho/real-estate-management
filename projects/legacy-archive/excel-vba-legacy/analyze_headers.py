
import pandas as pd
import os

files = ['아파트.xlsx', '근생.xlsx', '주택_공장_토지.xlsx']
output_file = 'header_analysis.txt'

with open(output_file, 'w', encoding='utf-8') as out:
    for f in files:
        try:
            path = os.path.join(os.getcwd(), f)
            xl = pd.ExcelFile(path)
            out.write(f"=== {f} ===\n")
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet, nrows=0)
                headers = list(df.columns)
                out.write(f"Sheet: {sheet}\nHeaders: {headers}\n\n")
        except Exception as e:
            out.write(f"Error reading {f}: {str(e)}\n\n")
