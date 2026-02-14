"""
Google Sheets 데이터 읽기 모듈

Google Sheets에서 데이터를 읽어오는 기능을 제공합니다.
"""

import pandas as pd
from typing import Dict, List, Any, Optional
from loguru import logger

import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path


class SheetsReader:
    """Google Sheets 데이터 읽기 클래스"""
    
    def __init__(self, settings):
        """
        Sheets Reader 초기화
        
        Args:
            settings: 시스템 설정 객체
        """
        self.settings = settings
        self.client = None
        self.spreadsheet = None
        
        # Google Sheets 연결
        self._connect_to_sheets()
        
    def _connect_to_sheets(self):
        """Google Sheets에 연결 (OAuth 2.0 또는 서비스 계정)"""
        try:
            # 스코프 설정
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # 먼저 OAuth 2.0 시도
            creds = self._try_oauth_auth(scopes)
            
            # OAuth 실패시 서비스 계정 시도
            if not creds:
                creds = self._try_service_account_auth(scopes)
            
            if not creds:
                raise Exception("인증 실패: OAuth 2.0과 서비스 계정 모두 실패")
                
            # gspread 클라이언트 생성
            self.client = gspread.authorize(creds)
            
            # 스프레드시트 열기
            self.spreadsheet = self.client.open_by_key(self.settings.google_sheets.spreadsheet_id)
            
            logger.info(f"✅ Google Sheets 연결 성공: {self.spreadsheet.title}")
            
        except Exception as e:
            logger.error(f"❌ Google Sheets 연결 실패: {e}")
            raise
            
    def _try_oauth_auth(self, scopes):
        """OAuth 2.0 인증 시도"""
        try:
            oauth_creds_path = Path(self.settings.paths.project_root) / "config/oauth_credentials.json"
            token_path = Path(self.settings.paths.project_root) / "config/token.json"
            
            if not oauth_creds_path.exists():
                logger.debug("OAuth 인증 파일이 없음")
                return None
                
            creds = None
            
            # 기존 토큰 파일이 있는지 확인
            if token_path.exists():
                creds = OAuthCredentials.from_authorized_user_file(str(token_path), scopes)
                
            # 유효한 자격 증명이 없으면 새로 인증
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(oauth_creds_path), scopes)
                    creds = flow.run_local_server(port=0)
                    
                # 토큰을 파일에 저장
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                    
            logger.info("✅ OAuth 2.0 인증 성공")
            return creds
            
        except Exception as e:
            logger.debug(f"OAuth 2.0 인증 실패: {e}")
            return None
            
    def _try_service_account_auth(self, scopes):
        """서비스 계정 인증 시도"""
        try:
            creds_path = Path(self.settings.paths.project_root) / self.settings.google_sheets.credentials_file
            
            if not creds_path.exists():
                logger.debug("서비스 계정 인증 파일이 없음")
                return None
                
            creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
            logger.info("✅ 서비스 계정 인증 성공")
            return creds
            
        except Exception as e:
            logger.debug(f"서비스 계정 인증 실패: {e}")
            return None
    
    def read_sheet_as_dataframe(self, sheet_name: str) -> pd.DataFrame:
        """
        시트를 DataFrame으로 읽기
        
        Args:
            sheet_name: 시트 이름
            
        Returns:
            pd.DataFrame: 시트 데이터
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            
            # 모든 데이터 가져오기
            data = sheet.get_all_values()
            
            if not data:
                logger.warning(f"⚠️ 빈 시트: {sheet_name}")
                return pd.DataFrame()
            
            # 첫 번째 행을 헤더로 사용
            headers = data[0]
            rows = data[1:] if len(data) > 1 else []
            
            # DataFrame 생성
            df = pd.DataFrame(rows, columns=headers)
            
            logger.debug(f"✅ 시트 읽기 완료: {sheet_name} ({len(df)} 행)")
            return df
            
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"❌ 시트를 찾을 수 없음: {sheet_name}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ 시트 읽기 실패 ({sheet_name}): {e}")
            return pd.DataFrame()
    
    def read_sheet_column(self, sheet_name: str, column_letter: str, 
                         start_row: int = 1, end_row: Optional[int] = None) -> List[Any]:
        """
        시트의 특정 열 읽기
        
        Args:
            sheet_name: 시트 이름
            column_letter: 열 문자 (예: 'A', 'D')
            start_row: 시작 행 (1부터 시작)
            end_row: 종료 행 (None이면 마지막까지)
            
        Returns:
            List[Any]: 열 데이터
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            
            # 범위 결정
            if end_row:
                range_name = f"{column_letter}{start_row}:{column_letter}{end_row}"
            else:
                # 마지막 행 찾기
                all_values = sheet.get_all_values()
                if not all_values:
                    return []
                end_row = len(all_values)
                range_name = f"{column_letter}{start_row}:{column_letter}{end_row}"
            
            # 데이터 읽기
            values = sheet.get(range_name)
            
            # 2D 리스트를 1D 리스트로 변환
            result = [row[0] if row else '' for row in values]
            
            logger.debug(f"✅ 열 읽기 완료: {sheet_name}!{range_name} ({len(result)} 개)")
            return result
            
        except Exception as e:
            logger.error(f"❌ 열 읽기 실패 ({sheet_name}!{column_letter}): {e}")
            return []
    
    def read_sheet_row(self, sheet_name: str, row_number: int) -> List[Any]:
        """
        시트의 특정 행 읽기
        
        Args:
            sheet_name: 시트 이름
            row_number: 행 번호 (1부터 시작)
            
        Returns:
            List[Any]: 행 데이터
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            row_data = sheet.row_values(row_number)
            
            logger.debug(f"✅ 행 읽기 완료: {sheet_name} 행 {row_number}")
            return row_data
            
        except Exception as e:
            logger.error(f"❌ 행 읽기 실패 ({sheet_name} 행 {row_number}): {e}")
            return []
    
    def get_all_sheet_names(self) -> List[str]:
        """
        모든 시트 이름 목록 가져오기
        
        Returns:
            List[str]: 시트 이름 목록
        """
        try:
            worksheets = self.spreadsheet.worksheets()
            sheet_names = [sheet.title for sheet in worksheets]
            
            logger.debug(f"✅ 시트 목록 조회 완료: {len(sheet_names)} 개")
            return sheet_names
            
        except Exception as e:
            logger.error(f"❌ 시트 목록 조회 실패: {e}")
            return []
    
    def get_sheet_headers(self, sheet_name: str) -> List[str]:
        """
        시트의 헤더(첫 번째 행) 가져오기
        
        Args:
            sheet_name: 시트 이름
            
        Returns:
            List[str]: 헤더 목록
        """
        try:
            sheet = self.spreadsheet.worksheet(sheet_name)
            headers = sheet.row_values(1)
            
            logger.debug(f"✅ 헤더 읽기 완료: {sheet_name} ({len(headers)} 개)")
            return headers
            
        except Exception as e:
            logger.error(f"❌ 헤더 읽기 실패 ({sheet_name}): {e}")
            return []
    
    def find_column_index(self, sheet_name: str, column_name: str) -> Optional[int]:
        """
        시트에서 특정 컬럼명의 인덱스 찾기 (1부터 시작)
        
        Args:
            sheet_name: 시트 이름
            column_name: 컬럼명
            
        Returns:
            Optional[int]: 컬럼 인덱스 (1부터 시작, 없으면 None)
        """
        try:
            headers = self.get_sheet_headers(sheet_name)
            
            # 대소문자 무시하고 찾기
            for idx, header in enumerate(headers, start=1):
                if header.strip() == column_name.strip():
                    return idx
            
            logger.warning(f"⚠️ 컬럼을 찾을 수 없음: {sheet_name}의 '{column_name}'")
            return None
            
        except Exception as e:
            logger.error(f"❌ 컬럼 인덱스 찾기 실패 ({sheet_name}): {e}")
            return None

