
import csv

pricing_data = {
    # This data should be extracted from the specific PDF for the target complex
}

input_file = 'path/to/your_template.csv'
output_file = 'path/to/your_output.csv'

def get_floor(ho):
    return int(str(ho)[:-2])

def find_price_info(unit_type, floor):
    if unit_type not in pricing_data:
        return None
    for tier in pricing_data[unit_type]:
        if tier["range"][0] <= floor <= tier["range"][1]:
            return tier
    return None

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    header = next(reader)
    writer.writerow(header)
    
    for row in reader:
        dong, ho, unit_type = row[0], row[1], row[2]
        
        try:
            floor = get_floor(ho)
            price_info = find_price_info(unit_type, floor)
            
            if price_info:
                # Adjust the row construction based on the actual CSV header
                new_row = [dong, ho, unit_type] + [price_info.get(h, '') for h in header[3:]]
                writer.writerow(new_row)
            else:
                writer.writerow(row)
        except (ValueError, IndexError):
            writer.writerow(row)

print(f"Processing complete. Output saved to {output_file}")
