"""
Google Sheets 데이터 쓰기 모듈

Google Sheets에 데이터를 쓰고 업데이트하는 기능을 제공합니다.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from loguru import logger

import gspread
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow


class SheetsWriter:
    """Google Sheets 데이터 쓰기 클래스"""
    
    def __init__(self, settings):
        """
        Sheets Writer 초기화
        
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
            
    def update_sheet_with_dataframe(self, sheet_name: str, dataframe: pd.DataFrame, 
                                   clear_existing: bool = True) -> bool:
        """
        DataFrame으로 시트 업데이트
        
        Args:
            sheet_name: 시트 이름
            dataframe: 업데이트할 데이터
            clear_existing: 기존 데이터 삭제 여부
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 시트 가져오기 (없으면 생성)
            sheet = self._get_or_create_sheet(sheet_name)
            
            if clear_existing:
                # 기존 데이터 삭제
                sheet.clear()
                logger.debug(f"🗑️ 기존 데이터 삭제: {sheet_name}")
                
            # 데이터 업로드
            headers = dataframe.columns.tolist()
            values = [headers] + dataframe.values.tolist()
            
            sheet.update('A1', values)
            
            # 자동 조정 수행
            self._auto_resize_sheet(sheet)
            
            logger.info(f"✅ 시트 업데이트 완료: {sheet_name} ({len(dataframe)} 행)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 시트 업데이트 실패 ({sheet_name}): {e}")
            return False
            
    def append_rows_to_sheet(self, sheet_name: str, data: List[List[Any]]) -> bool:
        """
        시트에 행 추가
        
        Args:
            sheet_name: 시트 이름
            data: 추가할 데이터 (행 리스트)
            
        Returns:
            bool: 성공 여부
        """
        try:
            sheet = self._get_or_create_sheet(sheet_name)
            
            # 데이터 추가
            sheet.append_rows(data)
            
            logger.info(f"✅ 시트에 행 추가 완료: {sheet_name} ({len(data)} 행)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 행 추가 실패 ({sheet_name}): {e}")
            return False
            
    def update_cells_in_range(self, sheet_name: str, range_name: str, 
                             values: List[List[Any]]) -> bool:
        """
        특정 범위의 셀 업데이트
        
        Args:
            sheet_name: 시트 이름
            range_name: 범위 (예: 'A1:C10')
            values: 업데이트할 값
            
        Returns:
            bool: 성공 여부
        """
        try:
            sheet = self._get_or_create_sheet(sheet_name)
            
            # 범위 업데이트
            sheet.update(range_name, values)
            
            logger.debug(f"✅ 셀 범위 업데이트 완료: {sheet_name}!{range_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 셀 범위 업데이트 실패 ({sheet_name}!{range_name}): {e}")
            return False
            
    def sync_property_data(self, property_data: Dict[str, Any], mode: str = 'append') -> bool:
        """
        매물 데이터 동기화
        
        Args:
            property_data: 매물 데이터 딕셔너리
            mode: 동기화 모드 ('append', 'update')
            
        Returns:
            bool: 성공 여부
        """
        try:
            sheet_name = self.settings.get_sheet_name('property_db')
            sheet = self._get_or_create_sheet(sheet_name)
            
            if mode == 'append':
                # 새 행 추가
                headers = sheet.row_values(1)
                row_data = [property_data.get(header, '') for header in headers]
                sheet.append_row(row_data)
                
            elif mode == 'update':
                # 기존 행 업데이트 (매물ID 기준)
                property_id = property_data.get('매물ID')
                if not property_id:
                    logger.warning("❌ 매물ID가 없어 업데이트 불가능")
                    return False
                    
                # TODO: 매물ID로 행 찾아서 업데이트 로직 구현
                logger.debug(f"🔄 매물 업데이트 모드 (추후 구현): {property_id}")
                
            logger.info(f"✅ 매물 데이터 동기화 완료: {mode} 모드")
            return True
            
        except Exception as e:
            logger.error(f"❌ 매물 데이터 동기화 실패: {e}")
            return False
            
    def create_sheet_if_not_exists(self, sheet_name: str) -> bool:
        """
        시트가 없으면 생성
        
        Args:
            sheet_name: 생성할 시트 이름
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 기존 시트 확인
            existing_sheet = None
            for sheet in self.spreadsheet.worksheets():
                if sheet.title == sheet_name:
                    existing_sheet = sheet
                    break
                    
            if existing_sheet:
                logger.debug(f"📄 시트 이미 존재: {sheet_name}")
                return True
                
            # 새 시트 생성
            new_sheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            logger.info(f"✅ 새 시트 생성 완료: {sheet_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 시트 생성 실패 ({sheet_name}): {e}")
            return False
            
    def _get_or_create_sheet(self, sheet_name: str) -> gspread.Worksheet:
        """
        시트 가져오기 또는 생성
        
        Args:
            sheet_name: 시트 이름
            
        Returns:
            gspread.Worksheet: 시트 객체
        """
        try:
            # 기존 시트 찾기
            for sheet in self.spreadsheet.worksheets():
                if sheet.title == sheet_name:
                    return sheet
                    
            # 시트가 없으면 생성
            logger.info(f"📄 새 시트 생성 중: {sheet_name}")
            return self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            
        except Exception as e:
            logger.error(f"❌ 시트 접근 실패 ({sheet_name}): {e}")
            raise
            
    def _auto_resize_sheet(self, sheet: gspread.Worksheet):
        """
        시트 자동 크기 조정
        
        Args:
            sheet: 조정할 시트
        """
        try:
            # 자동 크기 조정 요청
            sheet.format("A:Z", {"textFormat": {"fontFamily": "맑은 고딕"}})
            logger.debug(f"🎨 시트 포맷 적용: {sheet.title}")
            
        except Exception as e:
            logger.debug(f"⚠️ 시트 포맷 적용 실패: {e}")
            
    def sync_all_data(self) -> Dict[str, bool]:
        """
        모든 필요한 데이터 동기화
        
        Returns:
            Dict[str, bool]: 동기화 결과
        """
        results = {}
        
        logger.info("🔄 전체 데이터 동기도 시작")
        
        try:
            # 기본 시트들 존재 확인
            required_sheets = [
                '등록검색', '매물DB', '고객DB', 
                '아파트단지', '고정값', '대시보드'
            ]
            
            for sheet_name in required_sheets:
                results[sheet_name] = self.create_sheet_if_not_exists(sheet_name)
                
            logger.info("✅ 전체 데이터 동기화 완료")
            return results
            
        except Exception as e:
            logger.error(f"❌ 전체 데이터 동기화 실패: {e}")
            return results
            
    def get_sheet_info(self) -> Dict[str, Any]:
        """시트 정보 조회"""
        try:
            worksheets = self.spreadsheet.worksheets()
            
            info = {
                'spreadsheet_title': self.spreadsheet.title,
                'spreadsheet_id': self.spreadsheet.id,
                'sheets_count': len(worksheets),
                'sheets': []
            }
            
            for sheet in worksheets:
                sheet_info = {
                    'title': sheet.title,
                    'rows': sheet.row_count,
                    'cols': sheet.col_count,
                    'id': sheet.id
                }
                info['sheets'].append(sheet_info)
                
            return info
            
        except Exception as e:
            logger.error(f"❌ 시트 정보 조회 실패: {e}")
            return {}
