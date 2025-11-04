
import csv

# This data should be extracted from the specific PDF for the target complex
options_data = []

output_file = 'path/to/your_options_output.csv'

with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['단지명', '옵션구분', '타입', '품목', '품목세부', '설치내역', '공급금액'])
    
    for option in options_data:
        writer.writerow([
            '더샵 신부센트라', # This should be updated for the target complex
            option.get('category', ''),
            option.get('type', ''),
            option.get('item', ''),
            '', # 품목세부 is hard to separate from the current data
            option.get('details', ''),
            option.get('price', '')
        ])

print(f"Processing complete. Output saved to {output_file}")
