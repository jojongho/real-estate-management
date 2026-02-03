
import csv

# This data should be extracted from the specific PDF for the target complex
supply_data = []

output_file = 'path/to/your_supply_info_output.csv'

with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    # Adjust header based on the target schema
    writer.writerow(['주택형', '총공급세대수', '특별공급(계)', '기관추천', '다자녀가구', '신혼부부', '노부모부양', '생애최초', '일반공급'])
    
    for item in supply_data:
        writer.writerow([
            item.get('type',''),
            item.get('total',''),
            item.get('special',''),
            item.get('recommend',''),
            item.get('multi_child',''),
            item.get('newlywed',''),
            item.get('elderly',''),
            item.get('first_time',''),
            item.get('general','')
        ])

print(f"Processing complete. Output saved to {output_file}")
