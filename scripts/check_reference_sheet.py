#!/usr/bin/env python3
"""
고정값 참조 시트 구조 확인 스크립트
"""
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import gspread
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
except ImportError as e:
    print(f"Error: Required modules not installed: {e}")
    print("Please run: pip install gspread google-auth google-auth-oauthlib")
    sys.exit(1)

def main():
    # Configuration
    token_path = 'config/token.json'
    sheet_id = '1cFePAgehODmcTiPoWoDKOg2kIZSd2Zu2ZaiFL36ucVE'

    # Load credentials
    if not os.path.exists(token_path):
        print(f"Error: Token file not found: {token_path}")
        sys.exit(1)

    with open(token_path, 'r') as token:
        token_data = json.load(token)
        creds = Credentials.from_authorized_user_info(token_data)

    # Refresh if needed
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Connect to Google Sheets
    client = gspread.authorize(creds)

    try:
        # Open spreadsheet
        spreadsheet = client.open_by_key(sheet_id)

        print("=" * 60)
        print(f"📊 Spreadsheet: {spreadsheet.title}")
        print("=" * 60)
        print(f"Total Sheets: {len(spreadsheet.worksheets())}")
        print()

        # Iterate through worksheets
        for i, worksheet in enumerate(spreadsheet.worksheets(), 1):
            print(f"\n{'─' * 60}")
            print(f"Sheet {i}: {worksheet.title}")
            print(f"{'─' * 60}")
            print(f"Size: {worksheet.row_count} rows × {worksheet.col_count} columns")

            # Get first 5 rows to show structure
            try:
                values = worksheet.get_all_values()
                if values:
                    # Show headers
                    headers = values[0] if len(values) > 0 else []
                    print(f"\nColumns: {', '.join([h for h in headers if h])}")

                    # Show data count
                    data_rows = len([row for row in values[1:] if any(cell.strip() for cell in row)])
                    print(f"Data rows: {data_rows}")

                    # Show sample data (first 3 rows)
                    if len(values) > 1:
                        print(f"\nSample data (first 3 rows):")
                        for j, row in enumerate(values[1:4], 1):
                            non_empty = [cell for cell in row if cell.strip()]
                            if non_empty:
                                print(f"  Row {j}: {' | '.join(non_empty[:5])}")  # Show first 5 columns
                else:
                    print("  (Empty sheet)")
            except Exception as e:
                print(f"  Error reading data: {e}")

        print("\n" + "=" * 60)
        print("✅ Sheet structure analysis complete!")
        print("=" * 60)

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Spreadsheet not found with ID: {sheet_id}")
        print("Please check the spreadsheet ID and sharing permissions.")
        sys.exit(1)
    except Exception as e:
        print(f"Error accessing spreadsheet: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
