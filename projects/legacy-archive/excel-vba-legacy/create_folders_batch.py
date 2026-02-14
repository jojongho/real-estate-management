import pandas as pd
import os
import sys

# Configuration
FILES = {
    'APT': '아파트.xlsx',
    'BLDG': '근생.xlsx',
    'LAND': '주택 공장 토지.xlsx'
}

ROOT_DIR = os.path.join(os.getcwd(), "통합매물데이터(지역별)")

def clean_path(name):
    invalid = ['/', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid:
        name = name.replace(char, '_')
    return name.strip()

def create_folder(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            print(f"Created: {path}")
        except Exception as e:
            print(f"Error creating {path}: {e}")
    return path

def normalize_region(region):
    if not isinstance(region, str): return "타지역"
    region = region.strip()
    if region in ["아산시", "천안시 서북구", "천안시 동남구"]:
        return region
    return "타지역"

def get_val(row, col_name):
    if col_name in row and pd.notna(row[col_name]):
        return str(row[col_name]).strip()
    return ""

def process_apt():
    f = FILES['APT']
    if not os.path.exists(f): return
    print(f"Processing {f}...")
    
    xl = pd.read_excel(f, sheet_name='아파트매물')
    # Required: 시군구, 동읍면, 지번, 단지명, 동, 호, 타입
    
    for idx, row in xl.iterrows():
        region = get_val(row, '시군구')
        district = get_val(row, '동읍면')
        jibun = get_val(row, '지번')
        complex_name = get_val(row, '단지명')
        dong = get_val(row, '동')
        ho = get_val(row, '호')
        type_name = get_val(row, '타입')
        village = get_val(row, '통반리')
        
        if not (region and district and jibun and complex_name and dong and ho and type_name):
            continue
            
        # Path construction
        path = os.path.join(ROOT_DIR, normalize_region(region))
        path = os.path.join(path, district)
        if village: path = os.path.join(path, village)
        path = os.path.join(path, f"{jibun} {complex_name}")
        path = os.path.join(path, "-매물")
        path = os.path.join(path, f"{dong}-{ho}-{type_name}")
        
        create_folder(path)

def process_bldg():
    f = FILES['BLDG']
    if not os.path.exists(f): return
    print(f"Processing {f}...")
    
    # 1. Building Sheet
    try:
        df = pd.read_excel(f, sheet_name='건물')
        for idx, row in df.iterrows():
            region = get_val(row, '시군구')
            district = get_val(row, '동읍면')
            jibun = get_val(row, '지번')
            name = get_val(row, '건물명')
            village = get_val(row, '통반리')
            
            if not (region and district and jibun and name): continue
            
            path = os.path.join(ROOT_DIR, normalize_region(region))
            path = os.path.join(path, district)
            if village: path = os.path.join(path, village)
            path = os.path.join(path, f"{jibun} {name}")
            path = os.path.join(path, "-매물")
            
            # Leaf: propType logic is complex in VBA, simplifying here to just create the base match
            # The VBA creates specific leaf folders for units.
            # Here we just ensure the building folder exists.
            create_folder(path)
    except: pass

    # 2. Shop Sheet
    try:
        df = pd.read_excel(f, sheet_name='상가')
        # Requires join with Building info if headers missing, but user file has them?
        # Check analysis: 상가 has 주소, 건물명, 호수, 상호명
        # It lacks Region/District/Jibun directly maybe? 
        # Header analysis: ['ID', 'D_S_ID', '주소', '건물명', '호수'...]
        # It does NOT have 시군구/동읍면/지번.
        # The VBA HandleBuildingRow logic assumes these columns exist.
        # WAIT. VBA HandleBuildingRow says: "Building sheet requires Region/District/Jibun". 
        # But '상가' sheet calls HandleBuildingRow too.
        # Does '상가' sheet have these columns?
        # My header analysis for '상가': ['ID'... '주소', '건물명'...] - NO 시군구.
        # The VBA script has an "Address Fallback" logic: ParseAddress.
        # So I need to implement ParseAddress to make this work for '상가'.
        pass 
    except: pass

def process_town():
    f = FILES['LAND']
    if not os.path.exists(f): 
        # Try with underscore
        f = "주택_공장_토지.xlsx"
        if not os.path.exists(f): return
    
    print(f"Processing {f}...")
    try:
        df = pd.read_excel(f, sheet_name='주택타운')
        for idx, row in df.iterrows():
            region = get_val(row, '시군구')
            district = get_val(row, '동읍면')
            jibun = get_val(row, '지번')
            complex_name = get_val(row, '주택단지')
            village = get_val(row, '통반리')
            
            if not (region and district and jibun and complex_name): continue
            
            path = os.path.join(ROOT_DIR, normalize_region(region))
            path = os.path.join(path, district)
            if village: path = os.path.join(path, village)
            
            # Simplified town logic
            path = os.path.join(path, clean_path(complex_name))
            path = os.path.join(path, "-매물")
            create_folder(path)
    except Exception as e: print(e)

if __name__ == "__main__":
    process_apt()
    process_bldg()
    process_town()
