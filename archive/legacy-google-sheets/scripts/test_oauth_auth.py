#!/usr/bin/env python3
"""
Google Sheets OAuth 인증 스크립트
첫 번째 사용 시 브라우저에서 Google 인증을 완료합니다.
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Sheets API 스코프
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 
          'https://www.googleapis.com/auth/drive']

def authenticate_google_sheets():
    """Google Sheets OAuth 인증을 수행합니다."""
    
    # 파일 경로 설정
    credentials_path = "/Users/jojongho/Projects/real estate management/config/oauth_credentials.json"
    token_path = "/Users/jojongho/Projects/real estate management/config/token.json"
    
    creds = None
    
    # 기존 토큰 파일이 있는지 확인
    if os.path.exists(token_path):
        try:
            with open(token_path, 'r', encoding='utf-8') as token_file:
                token_data = json.load(token_file)
                if token_data:  # 빈 파일이 아닌 경우
                    creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"토큰 파일 읽기 오류: {e}")
    
    # 유효한 인증 정보가 없으면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("토큰 갱신 중...")
            creds.refresh(Request())
        else:
            print("새로운 OAuth 인증을 시작합니다...")
            print("브라우저가 열리면 Google 계정으로 로그인하세요.")
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # 토큰 저장
        with open(token_path, 'w', encoding='utf-8') as token_file:
            token_data = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            json.dump(token_data, token_file, indent=2)
        print(f"인증 토큰이 저장되었습니다: {token_path}")
    
    return creds

def test_google_sheets_connection(creds):
    """Google Sheets 연결을 테스트합니다."""
    try:
        service = build('sheets', 'v4', credentials=creds)
        
        # 테스트할 스프레드시트 ID
        spreadsheet_id = "1tkDKc7RTCLRgYPM-6e3CFEBOsHckLlNmddfKlVUX2rQ"
        
        print(f"스프레드시트 연결 테스트 중... (ID: {spreadsheet_id})")
        
        # 스프레드시트 메타데이터 가져오기
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        print(f"✅ 스프레드시트 연결 성공!")
        print(f"제목: {spreadsheet.get('properties', {}).get('title', 'N/A')}")
        
        # 시트 목록 출력
        sheets = spreadsheet.get('sheets', [])
        print(f"시트 목록 ({len(sheets)}개):")
        for sheet in sheets:
            sheet_props = sheet.get('properties', {})
            print(f"  - {sheet_props.get('title', 'N/A')} (ID: {sheet_props.get('sheetId', 'N/A')})")
        
        return True
        
    except Exception as e:
        print(f"❌ 스프레드시트 연결 실패: {e}")
        return False

if __name__ == "__main__":
    print("=== Google Sheets OAuth 인증 및 연결 테스트 ===")
    
    try:
        # OAuth 인증
        creds = authenticate_google_sheets()
        
        if creds:
            print("✅ OAuth 인증 완료!")
            
            # 연결 테스트
            if test_google_sheets_connection(creds):
                print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
                print("이제 Cursor에서 Google Sheets MCP 서버를 사용할 수 있습니다.")
            else:
                print("\n❌ 연결 테스트 실패")
        else:
            print("❌ OAuth 인증 실패")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n문제 해결 방법:")
        print("1. Google Cloud Console에서 OAuth 클라이언트가 올바르게 설정되었는지 확인")
        print("2. 스프레드시트 ID가 정확한지 확인")
        print("3. 인터넷 연결 상태 확인")

