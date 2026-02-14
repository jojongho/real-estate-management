"""
PDF 파싱 모듈

입주자모집공고문 PDF에서 핵심 정보를 추출하는 기능을 제공합니다.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

import pdfplumber


class PDFParser:
    """PDF 파싱 클래스"""
    
    def __init__(self, settings=None):
        """
        PDF 파서 초기화
        
        Args:
            settings: 시스템 설정 객체
        """
        self.settings = settings
        
        # 정규식 패턴 정의
        self.patterns = {
            'apartment_name': r'(.+?)\s*입주자모집공고',
            'total_units': r'총\s*(\d+)\s*세대',
            'move_in_date': r'입주예정\s*(\d{4}년\s*\d{1,2}월)',
            'license_numbers': r'민원실\s*(\d{3}-\d{2}-\d{5}|\d{6}-\d{2}-\d{5})',
            'price_per_pyeong': r'(\d+[,.]?\d*)\s*만원.*m²',
            'supply_area': r'공급면적\s*(\d+\.?\d*)\s*m²',
            'unit_types': r'(\d+방[\d\s]*DP|[\d\s]*방[\d\s]*리버스?)'
        }
        
    def process_apartment_notices(self, pdf_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        아파트 입주자모집공고 PDF 파일들 일괄 처리
        
        Args:
            pdf_dir: PDF 파일 디렉토리 (기본값: data/raw)
            
        Returns:
            List[Dict[str, Any]]: 파싱된 데이터 목록
        """
        if pdf_dir is None and self.settings:
            pdf_dir = self.settings.paths.data_raw_dir
        elif pdf_dir is None:
            pdf_dir = Path("data/raw")
            
        logger.info(f"📄 PDF 파싱 시작: {pdf_dir}")
        
        if not pdf_dir.exists():
            logger.warning(f"❌ PDF 디렉토리가 존재하지 않음: {pdf_dir}")
            return []
            
        results = []
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            logger.info("📄 처리할 PDF 파일이 없습니다.")
            return results
            
        for pdf_file in pdf_files:
            try:
                parsed_data = self.parse_apartment_notice(pdf_file)
                if parsed_data:
                    parsed_data['source_file'] = pdf_file.name
                    parsed_data['parsed_at'] = datetime.now().isoformat()
                    results.append(parsed_data)
                    logger.info(f"✅ PDF 파싱 완료: {pdf_file.name}")
                    
            except Exception as e:
                logger.error(f"❌ PDF 파싱 실패: {pdf_file.name} - {e}")
                
        logger.info(f"📊 총 {len(results)}개 PDF 파싱 완료")
        return results
        
    def parse_apartment_notice(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        단일 PDF 파일 파싱
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            Dict[str, Any]: 파싱된 데이터 또는 None
        """
        try:
            # PDF 텍스트 추출
            text = self._extract_text_from_pdf(pdf_path)
            
            if not text or len(text.strip()) < 100:
                logger.warning(f"⚠️ 텍스트 추출 불량: {pdf_path}")
                return None
                
            # 정보 추출
            extracted_data = self._extract_property_info(text)
            
            # 데이터 검증
            if not self._validate_extracted_data(extracted_data):
                logger.warning(f"⚠️ 추출 데이터 검증 실패: {pdf_path}")
                return None
                
            return extracted_data
            
        except Exception as e:
            logger.error(f"❌ PDF 파싱 오류 ({pdf_path}): {e}")
            return None
            
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        PDF에서 텍스트 추출
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            str: 추출된 텍스트
        """
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n[페이지 {page_num + 1}]\n" + page_text
                        
            # 텍스트 정리
            text = text.replace('\n', ' ')
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"❌ PDF 텍스트 추출 실패 ({pdf_path}): {e}")
            return ""
            
    def _extract_property_info(self, text: str) -> Dict[str, Any]:
        """
        텍스트에서 프로퍼티 정보 추출
        
        Args:
            text: PDF에서 추출된 텍스트
            
        Returns:
            Dict[str, Any]: 추출된 정보
        """
        data = {
            '단지명': self._extract_apartment_name(text),
            '총세대수': self._extract_total_units(text),
            '입주예정': self._extract_move_in_date(text),
            '민원실연락처': self._extract_license_numbers(text),
            '공급면적': self._extract_supply_area(text),
            '분양가': self._extract_price_info(text),
            '타입정보': self._extract_unit_types(text)
        }
        
        return data
        
    def _extract_apartment_name(self, text: str) -> Optional[str]:
        """아파트명 추출"""
        pattern = self.patterns['apartment_name']
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
        
    def _extract_total_units(self, text: str) -> Optional[int]:
        """총 세대수 추출"""
        pattern = self.patterns['total_units']
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(re.sub(r'[^\d]', '', match.group(1)))
            except ValueError:
                pass
        return None
        
    def _extract_move_in_date(self, text: str) -> Optional[str]:
        """입주예정일 추출"""
        pattern = self.patterns['move_in_date']
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None
        
    def _extract_license_numbers(self, text: str) -> Optional[str]:
        """민원실 연락처 추출"""
        pattern = self.patterns['license_numbers']
        matches = re.findall(pattern, text)
        return ', '.join(matches) if matches else None
        
    def _extract_supply_area(self, text: str) -> Optional[float]:
        """공급면적 추출"""
        pattern = self.patterns['supply_area']
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                pass
        return None
        
    def _extract_price_info(self, text: str) -> Dict[str, Any]:
        """가격 정보 추출"""
        price_info = {
            'price_per_pyeong': None,
            'price_ranges': []
        }
        
        # 평당 가격 패턴
        pyeong_pattern = r'(\d+[,.]?\d*)\s*만원.*m²'
        pyeong_match = re.search(pyeong_pattern, text)
        if pyeong_match:
            try:
                price_info['price_per_pyeong'] = float(pyeong_match.group(1).replace(',', ''))
            except ValueError:
                pass
                
        # 가격대 추출
        price_range_pattern = r'(\d+)\s*만원\s*[-~]\s*(\d+)\s*만원'
        price_matches = re.findall(price_range_pattern, text)
        for min_price, max_price in price_matches:
            price_info['price_ranges'].append({
                '최저가': int(min_price),
                '최고가': int(max_price)
            })
            
        return price_info
        
    def _extract_unit_types(self, text: str) -> List[str]:
        """타입 정보 추출"""
        unit_patterns = [
            r'(\d+방[\d\s]*DP)',
            r'(\d+방[\d\s]*리버스?)',
            r'(\d+방[\d\s]*)'
        ]
        
        types = []
        for pattern in unit_patterns:
            matches = re.findall(pattern, text)
            types.extend(matches)
            
        return list(set(types))  # 중복 제거
        
    def _validate_extracted_data(self, data: Dict[str, Any]) -> bool:
        """
        추출된 데이터 검증
        
        Args:
            data: 추출된 데이터
            
        Returns:
            bool: 검증 통과 여부
        """
        # 필수 필드 검증
        required_fields = ['단지명']
        
        for field in required_fields:
            if not data.get(field):
                logger.debug(f"❌ 필수 필드 누락: {field}")
                return False
                
        # 총세대수가 있는 경우 숫자 검증
        if data.get('총세대수') and not isinstance(data['총세대수'], int):
            logger.debug("❌ 총세대수 타입 오류")
            return False
            
        return True
        
    def save_parsed_data(self, parsed_data: List[Dict[str, Any]], output_path: Optional[Path] = None):
        """
        파싱된 데이터 저장
        
        Args:
            parsed_data: 파싱된 데이터 목록
            output_path: 출력 파일 경로 (기본값: data/processed)
        """
        if not parsed_data:
            logger.warning("⚠️ 저장할 데이터가 없습니다.")
            return
            
        if output_path is None:
            if self.settings:
                output_dir = self.settings.paths.data_processed_dir
            else:
                output_dir = Path("data/processed")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"parsed_apartment_notices_{timestamp}.json"
            
        try:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"💾 파싱 데이터 저장 완료: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ 데이터 저장 실패: {e}")
