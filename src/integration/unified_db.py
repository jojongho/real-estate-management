"""
통합DB 구축 모듈

모든 매물DB 시트의 데이터를 통합DB로 수집합니다.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from loguru import logger

from src.config.settings import Settings
from src.sheets.reader import SheetsReader
from src.sheets.writer import SheetsWriter


class UnifiedDBBuilder:
    """통합DB 구축 클래스"""
    
    def __init__(self, settings: Settings):
        """
        통합DB 구축 초기화
        
        Args:
            settings: 시스템 설정 객체
        """
        self.settings = settings
        self.reader = SheetsReader(settings)
        self.writer = SheetsWriter(settings)
        self.unified_sheet_name = '통합DB'
        
        # 시트 타입별 D_ID 컬럼명 매핑
        self.d_id_column_mapping = {
            '아파트매물': 'D_AD_ID',
            '주택타운': 'D_H_ID',
            '상가': 'D_S_ID',
            '원투룸': 'D_O_ID',
            '건물': 'D_B_ID',
            '공장창고': 'D_F_ID',
            '토지': 'D_L_ID'
        }
        
    def build_unified_db(self) -> bool:
        """
        통합DB 구축 (D_ID와 주소 칼럼)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("🔄 통합DB 구축 시작")
            
            # 1. 모든 시트 목록 가져오기
            all_sheets = self.reader.get_all_sheet_names()
            logger.info(f"📋 전체 시트 수: {len(all_sheets)}")
            
            # 2. 매물DB 시트 찾기 (매물DB로 끝나는 시트들)
            property_sheets = self._find_property_sheets(all_sheets)
            logger.info(f"🏠 매물DB 시트 발견: {len(property_sheets)} 개")
            
            if not property_sheets:
                logger.warning("⚠️ 매물DB 시트를 찾을 수 없습니다")
                return False
            
            # 3. 각 매물DB 시트에서 데이터 수집
            unified_data = []
            for sheet_name in property_sheets:
                logger.info(f"📖 데이터 수집 중: {sheet_name}")
                sheet_data = self._collect_sheet_data(sheet_name)
                if sheet_data:
                    unified_data.extend(sheet_data)
            
            if not unified_data:
                logger.warning("⚠️ 수집된 데이터가 없습니다")
                return False
            
            logger.info(f"✅ 총 {len(unified_data)} 개의 레코드 수집 완료")
            
            # 4. 통합DB 시트에 데이터 쓰기
            success = self._write_to_unified_db(unified_data)
            
            if success:
                logger.info(f"✅ 통합DB 구축 완료: {self.unified_sheet_name}")
            else:
                logger.error("❌ 통합DB 구축 실패")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 통합DB 구축 오류: {e}")
            return False
    
    def _find_property_sheets(self, all_sheets: List[str]) -> List[str]:
        """
        매물DB 시트 찾기
        
        Args:
            all_sheets: 전체 시트 목록
            
        Returns:
            List[str]: 매물DB 시트 목록
        """
        # 매물 시트 목록 (명시적 지정)
        property_sheet_names = [
            '아파트매물',
            '주택타운',
            '건물',
            '상가',
            '원투룸',
            '공장창고',
            '토지'
        ]
        
        property_sheets = []
        
        # 제외할 시트 목록
        exclude_sheets = [
            '통합DB',
            '등록검색',
            '고객DB',
            '아파트단지',
            '고정값',
            '고정값(수정X)',
            '대시보드',
            '분양가',
            '옵션',
            '타입',
            '발코니',
            '단지일정'
        ]
        
        for sheet_name in all_sheets:
            # 제외 목록에 없고, 매물 시트 목록에 있거나 'DB'/'매물'이 포함된 시트
            if sheet_name not in exclude_sheets:
                if sheet_name in property_sheet_names or 'DB' in sheet_name or '매물' in sheet_name:
                    property_sheets.append(sheet_name)
        
        return property_sheets
    
    def _get_d_id_column_name(self, sheet_name: str) -> Optional[str]:
        """
        시트 이름으로부터 D_ID 컬럼명 찾기
        
        Args:
            sheet_name: 시트 이름
            
        Returns:
            Optional[str]: D_ID 컬럼명 (없으면 None)
        """
        # 시트 이름에서 매물 타입 찾기
        for property_type, column_name in self.d_id_column_mapping.items():
            if property_type in sheet_name:
                return column_name
        
        # 매핑에 없으면 D열(4번째 열)을 기본으로 사용
        logger.warning(f"⚠️ {sheet_name}: 시트 타입을 찾을 수 없어 D열을 기본으로 사용합니다")
        return None
    
    def _collect_sheet_data(self, sheet_name: str) -> List[Dict[str, Any]]:
        """
        시트에서 통합DB 데이터 수집
        
        통합DB 구조:
        - A열: ID
        - B열: 관련파일
        - C열: 폴더ID
        - D열: D_ID (디스플레이 아이디)
        - E열: 주소
        - F열: 매물유형 (원본 시트명)
        
        건물 시트의 경우:
        - M열(13번째 열)의 "통매매" 체크박스가 체크된 것만 매물로 간주
        
        Args:
            sheet_name: 시트 이름
            
        Returns:
            List[Dict[str, Any]]: 수집된 데이터 리스트
        """
        try:
            # 시트를 DataFrame으로 읽기
            df = self.reader.read_sheet_as_dataframe(sheet_name)
            
            if df.empty:
                logger.warning(f"⚠️ 빈 시트: {sheet_name}")
                return []
            
            collected_data = []
            
            # 고정 컬럼 위치 (A=ID, B=관련파일, C=폴더ID, D=D_ID, E=주소)
            id_col_idx = 0      # A열 (0-based)
            url_col_idx = 1     # B열 (0-based)
            folder_id_col_idx = 2  # C열 (0-based)
            d_id_col_idx = 3    # D열 (0-based)
            address_col_idx = 4 # E열 (0-based)
            
            # 건물 시트의 경우 M열(13번째 열, 인덱스 12)의 통매매 체크박스 확인
            is_building_sheet = sheet_name == '건물'
            통매매_col_idx = 12  # M열은 13번째 열 (0-based로 12)
            
            # 각 행에서 데이터 추출
            for idx, row in df.iterrows():
                # 건물 시트의 경우 통매매 체크박스 확인
                if is_building_sheet:
                    if len(df.columns) > 통매매_col_idx:
                        통매매_value = row.iloc[통매매_col_idx] if pd.notna(row.iloc[통매매_col_idx]) else ''
                        # 체크박스가 체크되지 않았으면 건너뛰기
                        # 체크박스 값은 보통 TRUE/FALSE, "TRUE"/"FALSE", 또는 체크 표시
                        if not self._is_checked(통매매_value):
                            continue
                    else:
                        # M열이 없으면 모든 건물 포함 (하위 호환성)
                        logger.debug(f"⚠️ {sheet_name}: M열(통매매)이 없어 모든 건물 포함")
                
                # A열: ID
                id_value = ''
                if len(df.columns) > id_col_idx:
                    id_value = str(row.iloc[id_col_idx]) if pd.notna(row.iloc[id_col_idx]) else ''
                
                # B열: 관련파일
                url_value = ''
                if len(df.columns) > url_col_idx:
                    url_value = str(row.iloc[url_col_idx]) if pd.notna(row.iloc[url_col_idx]) else ''
                
                # C열: 폴더ID
                folder_id_value = ''
                if len(df.columns) > folder_id_col_idx:
                    folder_id_value = str(row.iloc[folder_id_col_idx]) if pd.notna(row.iloc[folder_id_col_idx]) else ''
                
                # D열: D_ID (디스플레이 아이디)
                d_id = ''
                if len(df.columns) > d_id_col_idx:
                    d_id = str(row.iloc[d_id_col_idx]) if pd.notna(row.iloc[d_id_col_idx]) else ''
                
                # E열: 주소
                address = ''
                if len(df.columns) > address_col_idx:
                    address = str(row.iloc[address_col_idx]) if pd.notna(row.iloc[address_col_idx]) else ''
                
                # 빈 D_ID는 건너뛰기
                if not d_id or d_id.strip() == '':
                    continue
                
                collected_data.append({
                    'ID': id_value.strip(),
                    '관련파일': url_value.strip(),
                    '폴더ID': folder_id_value.strip(),
                    'D_ID': d_id.strip(),
                    '주소': address.strip(),
                    '매물유형': sheet_name
                })
            
            logger.info(f"✅ {sheet_name}: {len(collected_data)} 개 레코드 수집")
            return collected_data
            
        except Exception as e:
            logger.error(f"❌ 시트 데이터 수집 실패 ({sheet_name}): {e}")
            return []
    
    def _is_checked(self, value: Any) -> bool:
        """
        체크박스 값이 체크되었는지 확인
        
        Args:
            value: 체크박스 값 (TRUE/FALSE, "TRUE"/"FALSE", 체크 표시 등)
            
        Returns:
            bool: 체크되었으면 True
        """
        if pd.isna(value):
            return False
        
        value_str = str(value).strip().upper()
        
        # TRUE, "TRUE", 체크 표시 등
        checked_values = ['TRUE', '1', 'YES', 'Y', '✓', '✔', 'CHECKED', '체크']
        
        return value_str in checked_values
    
    def _construct_address_from_row(self, row: pd.Series, columns: List[str]) -> str:
        """
        행 데이터에서 주소 구성 시도
        형식: "시군구 동읍면 통반리 지번"
        예: "충청남도 아산시 배방읍 공수리 1730"
        
        Args:
            row: 행 데이터
            columns: 컬럼 목록
            
        Returns:
            str: 구성된 주소
        """
        address_parts = []
        
        # 시군구 찾기
        시군구 = ''
        for col in ['시군구', '시도', '시']:
            if col in columns and pd.notna(row[col]):
                시군구 = str(row[col]).strip()
                if 시군구:
                    break
        
        # 동읍면 찾기
        동읍면 = ''
        for col in ['동읍면', '읍면동', '동']:
            if col in columns and pd.notna(row[col]):
                동읍면 = str(row[col]).strip()
                if 동읍면:
                    break
        
        # 통반리 찾기 (선택적)
        통반리 = ''
        for col in ['통반리', '리', '통']:
            if col in columns and pd.notna(row[col]):
                통반리 = str(row[col]).strip()
                if 통반리:
                    break
        
        # 지번 찾기
        지번 = ''
        for col in ['지번', '번지', '번지수']:
            if col in columns and pd.notna(row[col]):
                지번 = str(row[col]).strip()
                if 지번:
                    break
        
        # 주소 구성: 시군구 동읍면 통반리 지번
        if 시군구:
            address_parts.append(시군구)
        if 동읍면:
            address_parts.append(동읍면)
        if 통반리:
            address_parts.append(통반리)
        if 지번:
            address_parts.append(지번)
        
        return ' '.join(address_parts) if address_parts else ''
    
    def _write_to_unified_db(self, data: List[Dict[str, Any]]) -> bool:
        """
        통합DB 시트에 데이터 쓰기
        
        통합DB 구조:
        - A열: ID (D_ID 값 사용)
        - B열: 관련파일 (빈 값, 나중에 폴더 URL로 채워질 수 있음)
        - C열: 폴더ID (빈 값, 나중에 폴더 ID로 채워질 수 있음)
        - D열: D_ID
        - E열: 주소
        - F열: 출처시트
        
        Args:
            data: 작성할 데이터
            
        Returns:
            bool: 성공 여부
        """
        try:
            # DataFrame 생성
            df = pd.DataFrame(data)
            
            # 중복 제거 (D_ID 기준)
            initial_count = len(df)
            df = df.drop_duplicates(subset=['D_ID'], keep='first')
            if len(df) < initial_count:
                logger.info(f"🔄 중복 제거: {initial_count} → {len(df)} 개")
            
            # 통합DB 구조에 맞게 컬럼 재구성
            # 이미 수집된 데이터에 ID, 관련파일, 폴더ID가 포함되어 있음
            # 컬럼 순서: ID, 관련파일, 폴더ID, D_ID, 주소, 매물유형
            column_order = ['ID', '관련파일', '폴더ID', 'D_ID', '주소', '매물유형']
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            # 통합DB 시트에 쓰기
            success = self.writer.update_sheet_with_dataframe(
                sheet_name=self.unified_sheet_name,
                dataframe=df,
                clear_existing=True
            )
            
            if success:
                logger.info(f"✅ 통합DB 시트 업데이트 완료: {len(df)} 행")
                logger.info(f"📋 컬럼 구조: A=ID, B=관련파일, C=폴더ID, D=D_ID, E=주소, F=매물유형")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 통합DB 쓰기 실패: {e}")
            return False
    
    def update_unified_db(self) -> bool:
        """
        통합DB 업데이트 (기존 데이터 유지하면서 추가/수정)
        
        Returns:
            bool: 성공 여부
        """
        try:
            logger.info("🔄 통합DB 업데이트 시작")
            
            # 기존 통합DB 읽기
            existing_df = self.reader.read_sheet_as_dataframe(self.unified_sheet_name)
            
            # 모든 매물DB 시트에서 최신 데이터 수집
            all_sheets = self.reader.get_all_sheet_names()
            property_sheets = self._find_property_sheets(all_sheets)
            
            unified_data = []
            for sheet_name in property_sheets:
                sheet_data = self._collect_sheet_data(sheet_name)
                if sheet_data:
                    unified_data.extend(sheet_data)
            
            if not unified_data:
                logger.warning("⚠️ 수집된 데이터가 없습니다")
                return False
            
            # 새 데이터를 DataFrame으로 변환
            new_df = pd.DataFrame(unified_data)
            
            # 통합DB 구조에 맞게 컬럼 정렬
            column_order = ['ID', '관련파일', '폴더ID', 'D_ID', '주소', '매물유형']
            existing_columns = [col for col in column_order if col in new_df.columns]
            new_df = new_df[existing_columns]
            
            # 기존 데이터와 병합 (D_ID 기준)
            if not existing_df.empty and 'D_ID' in existing_df.columns:
                # 기존 데이터의 ID, 관련파일, 폴더ID는 유지
                # 새 데이터와 병합 (D_ID 기준)
                merged_df = pd.concat([existing_df, new_df], ignore_index=True)
                merged_df = merged_df.drop_duplicates(subset=['D_ID'], keep='last')
                
                # 병합 후에도 구조 유지 (ID, 관련파일, 폴더ID가 없으면 추가)
                if 'ID' not in merged_df.columns:
                    merged_df['ID'] = merged_df['D_ID']
                if '관련파일' not in merged_df.columns:
                    merged_df['관련파일'] = ''
                if '폴더ID' not in merged_df.columns:
                    merged_df['폴더ID'] = ''
                
                # 컬럼 순서 정렬
                column_order = ['ID', '관련파일', '폴더ID', 'D_ID', '주소', '매물유형']
                existing_columns = [col for col in column_order if col in merged_df.columns]
                other_columns = [col for col in merged_df.columns if col not in column_order]
                merged_df = merged_df[existing_columns + other_columns]
            else:
                merged_df = new_df
            
            # 통합DB 시트에 쓰기
            success = self.writer.update_sheet_with_dataframe(
                sheet_name=self.unified_sheet_name,
                dataframe=merged_df,
                clear_existing=True
            )
            
            if success:
                logger.info(f"✅ 통합DB 업데이트 완료: {len(merged_df)} 행")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 통합DB 업데이트 실패: {e}")
            return False


def main():
    """메인 실행 함수"""
    try:
        # 설정 로드
        settings = Settings()
        
        # 통합DB 구축
        builder = UnifiedDBBuilder(settings)
        success = builder.build_unified_db()
        
        if success:
            print("✅ 통합DB 구축 완료!")
        else:
            print("❌ 통합DB 구축 실패")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ 실행 오류: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

