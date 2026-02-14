import pandas as pd
from pathlib import Path

def analyze_excel(file_path):
    print(f"\n📊 Analyzing: {file_path.name}")
    try:
        if file_path.suffix == '.csv':
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig', nrows=5)
            except:
                df = pd.read_csv(file_path, encoding='cp949', nrows=5)
            print(f"Columns: {list(df.columns)}")
            print(f"Sample:\n{df.head(2).to_string()}")
            
        else:
            xl = pd.ExcelFile(file_path)
            print(f"Sheets: {xl.sheet_names}")
            for sheet in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet, nrows=5)
                print(f"  [Sheet: {sheet}] Columns: {list(df.columns)}")
                # print(f"  Data:\n{df.head(2).to_string()}")
    except Exception as e:
        print(f"❌ Error: {e}")

base_dir = Path("projects/apartment-normalization/data/raw/excel")
files = [
    base_dir / "서한이다음 분양가 정리.xlsx",
    base_dir / "탕정 대광로제비앙 분양가.xlsx",
    base_dir / "분양가_정규화_최고최저층.csv"
]

for f in files:
    if f.exists():
        analyze_excel(f)
    else:
        print(f"\n⚠️ File not found: {f}")
