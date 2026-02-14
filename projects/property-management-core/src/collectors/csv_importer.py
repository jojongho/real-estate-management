"""
CSV 파일 가져오기 모듈

단지DB CSV 파일들을 Google Sheets에 자동으로 가져오는 기능을 제공합니다.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from src.config.settings import Settings
from src.sheets.writer import SheetsWriter


class CSVImporter:
    """CSV 파일 가져오기 클래스"""
    
    def __init__(self, settings: Settings):
        """
        CSV 가져오기 초기화
        
        Args:
            settings: 시스템 설정 객체
        """
        self.settings = settings
        self.sheets_writer = SheetsWriter(settings)
        
        # CSV 파일 매핑 (파일명 -> 시트명)
        self.csv_mapping = {
            '통합단지DB - 분양가.csv': '분양가',
            '통합단지DB - 옵션.csv': '옵션',
            '통합단지DB - 타입.csv': '타입',
            '통합단지DB - 발코니.csv': '발코니',
            '통합단지DB - 단지일정.csv': '단지일정'
        }
        
    def process_all_csv_files(self) -> Dict[str, bool]:
        """
        모든 CSV 파일 처리
        
        Returns:
            Dict[str, bool]: 파일별 처리 결과
        """
        results = {}
        raw_data_dir = self.settings.paths.data_raw_dir
        
        logger.info(f"📂 CSV 파일 처리 시작: {raw_data_dir}")
        
        if not raw_data_dir.exists():
            logger.warning(f"❌ 데이터 디렉토리가 존재하지 않음: {raw_data_dir}")
            return results
            
        for csv_file in raw_data_dir.glob("*.csv"):
            try:
                result = self.import_csv_file(csv_file)
                results[csv_file.name] = result
                
                logger.info(f"✅ {csv_file.name} 처리 완료")
                
            except Exception as e:
                logger.error(f"❌ {csv_file.name} 처리 실패: {e}")
                results[csv_file.name] = False
                
        logger.info(f"📊 총 {len(results)}개 파일 처리 완료")
        return results
        
    def import_csv_file(self, csv_path: Path) -> bool:
        """
        단일 CSV 파일 가져오기
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            bool: 처리 성공 여부
        """
        try:
            # CSV 파일 읽기
            df = self._read_csv_file(csv_path)
            
            if df.empty:
                logger.warning(f"⚠️ 빈 CSV 파일: {csv_path}")
                return False
                
            # 타겟 시트명 결정
            sheet_name = self.csv_mapping.get(csv_path.name, csv_path.stem)
            
            # Google Sheets에 업로드
            success = self.sheets_writer.update_sheet_with_dataframe(
                sheet_name=sheet_name,
                dataframe=df,
                clear_existing=True
            )
            
            if success:
                logger.info(f"📤 {csv_file.name} -> {sheet_name} 시트 업로드 완료")
            else:
                logger.error(f"❌ {csv_file.name} 업로드 실패")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ CSV 파일 처리 오류 ({csv_path}): {e}")
            return False
            
    def _read_csv_file(self, csv_path: Path) -> pd.DataFrame:
        """
        CSV 파일 읽기 (인코딩 자동 감지)
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            pd.DataFrame: 읽어들인 데이터
        """
        encodings = ['utf-8', 'cp949', 'euc-kr', 'latin-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                logger.debug(f"✅ 인코딩 확인: {csv_path.name} ({encoding})")
                return df
                
            except UnicodeDecodeError:
                continue
                
        raise ValueError(f"❌ 지원되지 않는 인코딩: {csv_path}")
        
    def validate_csv_structure(self, csv_path: Path) -> bool:
        """
        CSV 파일 구조 검증
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            bool: 구조 유효성
        """
        try:
            df = self._read_csv_file(csv_path)
            
            # 기본 검증 규칙
            checks = [
                (not df.empty, "빈 파일"),
                (len(df.columns) > 0, "컬럼 없음"),
                (len(df) > 0, "데이터 행 없음")
            ]
            
            for check, message in checks:
                if not check:
                    logger.warning(f"⚠️ 검증 실패: {csv_path.name} - {message}")
                    return False
                    
            logger.info(f"✅ 구조 검증 통과: {csv_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 구조 검증 실패: {csv_path} - {e}")
            return False
            
    def get_csv_summary(self, csv_path: Path) -> Dict[str, Any]:
        """
        CSV 파일 요약 정보 조회
        
        Args:
            csv_path: CSV 파일 경로
            
        Returns:
            Dict[str, Any]: 파일 요약 정보
        """
        try:
            df = self._read_csv_file(csv_path)
            
            summary = {
                'file_name': csv_path.name,
                'file_size': csv_path.stat().st_size,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'has_duplicates': df.duplicated().any(),
                'null_counts': df.isnull().sum().to_dict()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 요약 정보 생성 실패: {csv_path} - {e}")
            return {}
