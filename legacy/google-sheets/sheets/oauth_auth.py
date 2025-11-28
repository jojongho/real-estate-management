"""
Google Sheets OAuth 2.0 인증 설정 가이드

서비스 계정 키가 차단된 경우 OAuth 2.0 클라이언트 ID를 사용합니다.
"""

import os
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GoogleSheetsOAuth:
    """Google Sheets OAuth 2.0 인증 클래스"""
    
    def __init__(self, credentials_file: str = "config/oauth_credentials.json"):
        self.credentials_file = credentials_file
        self.token_file = "config/token.json"
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.service = None
        
    def authenticate(self):
        """OAuth 2.0 인증 수행"""
        creds = None
        
        # 기존 토큰 파일이 있는지 확인
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            
        # 유효한 자격 증명이 없으면 새로 인증
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                creds = flow.run_local_server(port=0)
                
            # 토큰을 파일에 저장
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
                
        self.service = build('sheets', 'v4', credentials=creds)
        return self.service
        
    def get_service(self):
        """인증된 서비스 객체 반환"""
        if not self.service:
            self.authenticate()
        return self.service

# 사용 예시
if __name__ == "__main__":
    oauth = GoogleSheetsOAuth()
    service = oauth.authenticate()
    print("Google Sheets OAuth 인증 완료!")



