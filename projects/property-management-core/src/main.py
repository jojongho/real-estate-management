#!/usr/bin/env python3
"""
아파트 매물관리 자동화 시스템 - 메인 엔트리 포인트

이 시스템은 Google Sheets를 중심으로 한 매물관리 시스템으로, 다음 기능들을 제공합니다:
- CSV/PDF 데이터 자동 수집 및 처리
- 네이버 부동산 크롤링
- 실거래가 API 연동
- 자동 콘텐츠 생성 및 발행
- 일일 브리핑 자동화

Author: cao25
Created: 2025-01-15
Updated: 2025-11-29 (Google Sheets로 롤백)
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from loguru import logger

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.settings import Settings
from src.sheets.reader import SheetsReader
from src.sheets.writer import SheetsWriter
from src.collectors.csv_importer import CSVImporter
from src.collectors.pdf_parser import PDFParser
from src.collectors.naver_crawler import NaverCrawler
from src.collectors.api_client import APIClient
from src.processors.normalizer import DataNormalizer
from src.generators.briefing import BriefingGenerator
from src.generators.marketing import MarketingGenerator


def setup_logging():
    """로깅 설정"""
    # 기존 로거 제거
    logger.remove()
    
    # 콘솔 로그
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 파일 로그
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "apartment_automation_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )


def initialize_system():
    """시스템 초기화"""
    logger.info("🏠 아파트 매물관리 자동화 시스템 초기화 시작")
    
    try:
        # 설정 로드
        settings = Settings()
        logger.info(f"✅ 설정 로드 완료: {settings.project_name}")
        
        # 필요한 디렉토리 생성
        dirs_to_create = [
            "data/raw",
            "data/processed", 
            "logs",
            "temp"
        ]
        
        for dir_path in dirs_to_create:
            (project_root / dir_path).mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ 시스템 초기화 완료")
        return settings
        
    except Exception as e:
        logger.error(f"❌ 시스템 초기화 실패: {e}")
        raise


def run_data_collection(settings):
    """데이터 수집 실행"""
    logger.info("📥 데이터 수집 작업 시작")
    
    try:
        # CSV 가져오기
        csv_importer = CSVImporter(settings)
        csv_importer.process_all_csv_files()
        
        # PDF 파싱 (해당 폴더에 PDF가 있는 경우)
        pdf_parser = PDFParser(settings)
        pdf_parser.process_apartment_notices()
        
        # 네이버 부동산 크롤링
        naver_crawler = NaverCrawler(settings)
        naver_crawler.fetch_new_listings()
        
        # 실거래가 API 호출
        api_client = APIClient(settings)
        api_client.fetch_real_price_data()
        
        logger.info("✅ 데이터 수집 작업 완료")
        
    except Exception as e:
        logger.error(f"❌ 데이터 수집 실패: {e}")


def run_data_processing(settings):
    """데이터 처리 및 정규화"""
    logger.info("🔄 데이터 처리 작업 시작")
    
    try:
        normalizer = DataNormalizer(settings)
        normalizer.normalize_all_data()
        
        logger.info("✅ 데이터 처리 완료")
        
    except Exception as e:
        logger.error(f"❌ 데이터 처리 실패: {e}")


def run_content_generation(settings):
    """콘텐츠 생성"""
    logger.info("📝 콘텐츠 생성 작업 시작")
    
    try:
        # 일일 브리핑 생성
        briefing_generator = BriefingGenerator(settings)
        briefing_generator.generate_daily_briefing()
        
        # 마케팅 콘텐츠 생성
        marketing_generator = MarketingGenerator(settings)
        marketing_generator.generate_property_content()
        
        logger.info("✅ 콘텐츠 생성 완료")
        
    except Exception as e:
        logger.error(f"❌ 콘텐츠 생성 실패: {e}")


def update_sheets_database(settings):
    """Google Sheets 데이터베이스 업데이트"""
    logger.info("📊 Google Sheets 데이터베이스 업데이트 시작")

    try:
        sheets_writer = SheetsWriter(settings)
        sheets_reader = SheetsReader(settings)

        # TODO: 데이터 처리 로직 구현
        # 예: 처리된 데이터를 Google Sheets에 저장

        logger.info("✅ Google Sheets 데이터베이스 업데이트 완료")

    except Exception as e:
        logger.error(f"❌ Google Sheets 데이터베이스 업데이트 실패: {e}")


def main():
    """메인 실행 함수"""
    try:
        # 시스템 초기화
        settings = initialize_system()
        
        logger.info(f"🚀 {settings.project_name} 실행 시작")
        
        # 데이터 수집
        run_data_collection(settings)
        
        # 데이터 처리
        run_data_processing(settings)

        # Google Sheets 데이터베이스 업데이트
        update_sheets_database(settings)

        # 콘텐츠 생성
        run_content_generation(settings)
        
        logger.info("🎉 모든 작업 완료!")
        
    except KeyboardInterrupt:
        logger.info("👋 사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"💥 예상치 못한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
