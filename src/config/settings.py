"""
설정 관리 모듈

Google Sheets, API 키, 환경 변수 등을 관리합니다.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class GoogleSheetsConfig:
    """Google Sheets 관련 설정"""
    spreadsheet_id: str
    credentials_file: str
    scopes: list[str] = field(default_factory=lambda: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ])


@dataclass 
class APIConfig:
    """외부 API 관련 설정"""
    naver_client_id: Optional[str] = None
    naver_client_secret: Optional[str] = None
    gemini_api_key: Optional[str] = None
    molit_api_key: Optional[str] = None


@dataclass
class PathsConfig:
    """파일 경로 설정"""
    project_root: Path
    data_raw_dir: Path
    data_processed_dir: Path
    config_dir: Path
    logs_dir: Path
    temp_dir: Path

@dataclass
class ExcelConfig:
    """로컬 Excel 백엔드 설정 (현재는 사용 안 함)"""
    file_path: str
    backend: str = "sheets"  # sheets | excel (롤백됨: 2025-11-29)


@dataclass
class DatabaseConfig:
    """데이터베이스/시트 구조 설정"""
    sheets: Dict[str, str] = field(default_factory=lambda: {
        'register_search': '등록검색',
        'property_db': '매물DB', 
        'customer_db': '고객DB',
        'apartment_complex': '아파트단지',
        'fixed_values': '고정값',
        'dashboard': '대시보드',
        'unified_db': '통합DB'
    })


class Settings:
    """설정 관리 클래스"""
    
    def __init__(self):
        """설정 초기화"""
        self.project_name = "아파트 매물관리 자동화 시스템"
        self.version = "1.0.0"
        self.author = "cao25"
        
        # 환경 변수 로드
        self._load_env()
        
        # 경로 설정
        self._setup_paths()
        
        # 백엔드 설정 (기본: Excel)
        self._setup_excel()
        self._setup_google_sheets()
        
        # API 설정
        self._setup_api()
        
        # 데이터베이스 설정
        self._setup_database()
        
    def _load_env(self):
        """환경 변수 로드"""
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            
    def _setup_paths(self):
        """경로 설정"""
        project_root = Path(__file__).parent.parent.parent
        self.paths = PathsConfig(
            project_root=project_root,
            data_raw_dir=project_root / "data" / "raw",
            data_processed_dir=project_root / "data" / "processed", 
            config_dir=project_root / "config",
            logs_dir=project_root / "logs",
            temp_dir=project_root / "temp"
        )

    def _setup_excel(self):
        """로컬 Excel 설정 (레거시)"""
        file_path = os.getenv('EXCEL_FILE_PATH', str(self.paths.project_root / "data" / "local_master.xlsx"))
        backend = os.getenv('EXCEL_BACKEND', 'sheets').lower()  # 기본값: sheets로 변경
        self.excel = ExcelConfig(
            file_path=file_path,
            backend=backend
        )
        
    def _setup_google_sheets(self):
        """Google Sheets 설정"""
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID', '1tkDKc7RTCLRgYPM-6e3CFEBOsHckLlNmddfKlVUX2rQ')
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'config/credentials.json')
        
        self.google_sheets = GoogleSheetsConfig(
            spreadsheet_id=spreadsheet_id,
            credentials_file=credentials_file
        )
        
    def _setup_api(self):
        """API 설정"""
        self.api = APIConfig(
            naver_client_id=os.getenv('NAVER_CLIENT_ID'),
            naver_client_secret=os.getenv('NAVER_CLIENT_SECRET'),
            gemini_api_key=os.getenv('GEMINI_API_KEY'),
            molit_api_key=os.getenv('MOLIT_API_KEY')
        )
        
    def _setup_database(self):
        """데이터베이스 설정"""
        self.database = DatabaseConfig()
        
    def get_sheet_name(self, sheet_type: str) -> str:
        """시트 이름 조회"""
        return self.database.sheets.get(sheet_type, sheet_type)
        
    def get_api_key(self, api_name: str) -> Optional[str]:
        """API 키 조회"""
        api_map = {
            'gemini': self.api.gemini_api_key,
            'naver_client_id': self.api.naver_client_id,
            'naver_client_secret': self.api.naver_client_secret,
            'molit': self.api.molit_api_key
        }
        return api_map.get(api_name)
        
    def create_dirs(self):
        """필요한 디렉토리 생성"""
        dirs = [
            self.paths.data_raw_dir,
            self.paths.data_processed_dir,
            self.paths.config_dir,
            self.paths.logs_dir,
            self.paths.temp_dir
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
    def is_configured(self) -> bool:
        """설정이 완료되었는지 확인"""
        if self.excel.backend == "sheets":
            # Google Sheets 백엔드 확인
            required_settings = [
                self.google_sheets.spreadsheet_id,
                os.path.exists(self.paths.config_dir / self.google_sheets.credentials_file)
            ]
            return all(required_settings)
        else:
            # Excel 백엔드 확인
            return bool(self.excel.file_path)
        
    def print_config(self):
        """현재 설정 출력"""
        print(f"\n{'='*50}")
        print(f"프로젝트: {self.project_name}")
        print(f"버전: {self.version}")
        print(f"작성자: {self.author}")
        print(f"{'='*50}")
        print(f"프로젝트 루트: {self.paths.project_root}")
        print(f"Excel 백엔드: {self.excel.backend}")
        print(f"Excel 파일: {self.excel.file_path}")
        print(f"Google Sheets ID: {self.google_sheets.spreadsheet_id}")
        print(f"데이터 디렉토리: {self.paths.data_raw_dir}")
        print(f"설정 완료 여부: {'✅' if self.is_configured() else '❌'}")
        print(f"{'='*50}\n")
