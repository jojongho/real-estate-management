#!/usr/bin/env python3
"""
Google Sheets OAuth 재인증 스크립트

토큰이 만료되었거나 무효한 경우 이 스크립트를 실행하여 재인증합니다.
"""

import os
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
CREDENTIALS_FILE = CONFIG_DIR / "oauth_credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"

# 필요한 권한 범위
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def reauthenticate():
    """Google Sheets OAuth 재인증 수행"""
    
    print("=" * 60)
    print("Google Sheets OAuth 재인증")
    print("=" * 60)
    
    # 파일 경로 확인
    if not CREDENTIALS_FILE.exists():
        print(f"❌ 오류: {CREDENTIALS_FILE} 파일을 찾을 수 없습니다.")
        print("\nOAuth 인증 정보 파일이 필요합니다.")
        print("Google Cloud Console에서 OAuth 클라이언트 ID를 생성하고")
        print(f"다운로드한 JSON 파일을 {CREDENTIALS_FILE}에 저장하세요.")
        return False
    
    print(f"✅ 인증 정보 파일 확인: {CREDENTIALS_FILE}")
    
    # 기존 토큰 확인
    creds = None
    if TOKEN_FILE.exists():
        print(f"\n📄 기존 토큰 파일 발견: {TOKEN_FILE}")
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            print("   기존 토큰 로드 완료")
            
            # 토큰이 유효한지 확인
            if creds.valid:
                print("✅ 기존 토큰이 아직 유효합니다!")
                print("   재인증이 필요하지 않습니다.")
                return True
            
            # 토큰이 만료되었지만 refresh token이 있으면 갱신 시도
            if creds.expired and creds.refresh_token:
                print("🔄 토큰이 만료되었습니다. refresh token으로 갱신 시도...")
                try:
                    creds.refresh(Request())
                    print("✅ 토큰 갱신 성공!")
                    
                    # 갱신된 토큰 저장
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    print(f"   갱신된 토큰을 {TOKEN_FILE}에 저장했습니다.")
                    return True
                except Exception as e:
                    print(f"❌ 토큰 갱신 실패: {e}")
                    print("   새 인증이 필요합니다.")
        except Exception as e:
            print(f"⚠️  기존 토큰 파일 읽기 오류: {e}")
            print("   새 인증을 진행합니다.")
    
    # 새 인증 진행
    print("\n" + "=" * 60)
    print("새 OAuth 인증 시작")
    print("=" * 60)
    print("\n다음 단계를 진행합니다:")
    print("1. 브라우저가 자동으로 열립니다")
    print("2. Google 계정으로 로그인하세요")
    print("3. 권한 요청을 승인하세요 (Google Sheets 및 Drive 접근 권한)")
    print("\n준비되셨으면 Enter 키를 누르세요...", end="")
    input()
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), SCOPES)
        
        print("\n🌐 브라우저에서 인증을 진행하세요...")
        creds = flow.run_local_server(port=0)
        
        # 토큰 저장
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        
        print("\n" + "=" * 60)
        print("✅ 인증 성공!")
        print("=" * 60)
        print(f"\n토큰이 {TOKEN_FILE}에 저장되었습니다.")
        print("\n이제 MCP 서버가 Google Sheets에 접근할 수 있습니다.")
        print("\n⚠️  중요: Cursor를 재시작하여 MCP 연결을 새로고침하세요.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 인증 실패: {e}")
        print("\n문제 해결:")
        print("1. OAuth 인증 정보 파일이 올바른지 확인")
        print("2. Google Cloud Console에서 API가 활성화되었는지 확인")
        print("3. 인터넷 연결 상태 확인")
        return False


if __name__ == "__main__":
    success = reauthenticate()
    sys.exit(0 if success else 1)

