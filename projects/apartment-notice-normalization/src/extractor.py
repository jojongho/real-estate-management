import os
import sys
import json
import csv
import glob
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# pandas optional import
try:
    import pandas as pd
    USE_PANDAS = True
except ImportError:
    USE_PANDAS = False

class PDFDataExtractor:
    """PDF에서 아파트 분양 데이터를 자동으로 추출 (Gemini API 활용)"""

    def __init__(self, pdf_path: Path, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.apartment_name = self._extract_apartment_name()

        # 환경 변수 로드
        load_dotenv()
        
        # API Key 확인
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
            
        genai.configure(api_key=api_key)
        
        # 모델 설정
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash') # 최신 모델 
        self.model = genai.GenerativeModel(model_name)
        
    def _extract_apartment_name(self) -> str:
        """파일명에서 단지명 스마트 추출"""
        filename = self.pdf_path.stem
        # "입주자모집공고" 등 불필요한 텍스트 제거하고 단지명만 추출 시도
        name = filename.split('입주자모집공고')[0]
        # 점(.)으로 시작하는 경우 제거, 공백 정리
        name = name.strip()
        return name

    def process(self):
        """전체 추출 프로세스 실행"""
        print(f"🔄 처리 시작: {self.apartment_name}")
        
        # 엑셀 시트별로 저장할 데이터 수집
        collected_data = {}

        # 1. 분양가 추출
        pricing_data = self._process_pricing()
        if pricing_data: collected_data['분양가'] = pricing_data
        
        # 2. 발코니 확장비 추출
        balcony_data = self._process_balcony()
        if balcony_data: collected_data['발코니'] = balcony_data

        # 3. 옵션 추출
        options_data = self._process_options()
        if options_data: collected_data['유상옵션'] = options_data
        
        # 4. 단지 일정 추출
        schedule_data = self._process_schedule()
        if schedule_data: collected_data['일정'] = schedule_data
        
        # 5. 타입 정보 추출
        supply_data = self._process_supply_info()
        if supply_data: collected_data['공급정보'] = supply_data

        # 6. 단지 배치 정보 추출 및 Full List 생성 (앱시트용)
        layout_data = self._process_layout()
        if layout_data and pricing_data:
            full_list = self._generate_full_list(layout_data, pricing_data)
            if full_list: collected_data['전체세대(앱시트용)'] = full_list
        
        # 최종 엑셀 저장
        if collected_data:
            self._save_final_excel(collected_data)
        
        print(f"✅ 처리 완료: {self.output_dir}")

    def _process_layout(self):
        """단지 배치 정보(동/라인/타입/최고층) 추출"""
        print("   - 단지 배치 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_layout.md"
        result = self._run_gemini(prompt_path)
        if not result: return None
        
        try:
            data = json.loads(result)
            return data.get('배치정보', [])
        except Exception as e:
            print(f"   ❌ 배치 정보 처리 중 오류: {e}")
            return None

    def _generate_full_list(self, layout_data, pricing_data):
        """배치 정보와 분양가 정보를 결합하여 전체 세대 리스트 생성"""
        print("   - 앱시트용 전체 세대 리스트 생성 중...")
        full_list = []
        
        # 분양가 Lookup: (타입, 층) -> 가격
        price_map = {} # {'84A': {3: 50000, 4: 51000...}}
        for p in pricing_data:
            t = self._normalize_type(p.get('타입'))
            floors = self._parse_floor_range(p.get('층구분', ''))
            
            if t not in price_map: price_map[t] = {}
            for min_f, max_f in floors:
                # 층 범위 내의 모든 층에 가격 매핑
                # 단, 여기서 min_f가 10이고 max_f가 20이면 10~20층 모두 같은 가격
                # 너무 넓은 범위(예: 10~29)는 나중에 매칭할 때 처리
                price_map[t][(min_f, max_f)] = p

        for item in layout_data:
            dong = item.get('동')
            line = self._safe_int(item.get('라인', 0))
            type_name = self._normalize_type(item.get('타입'))
            max_floor = self._safe_int(item.get('최고층', 1))
            skip_floors = item.get('제외층', [])
            
            for floor in range(1, max_floor + 1):
                if floor in skip_floors: continue
                
                # 호수 생성 (예: 101, 201...)
                ho = floor * 100 + line
                
                unit_data = {
                    '동': dong,
                    '호': ho,
                    '타입': type_name,
                    '층': floor,
                    '라인': line
                }
                
                # 가격 매칭
                price_info = self._find_price_for_floor(price_map, type_name, floor)
                if price_info:
                    unit_data['분양가'] = price_info.get('분양가', 0)
                    unit_data['확장비'] = 0 # TODO: 발코니 정보 매칭 필요 시 추가
                    unit_data['합계'] = int(price_info.get('분양가', 0))
                else:
                    unit_data['분양가'] = 0
                    unit_data['합계'] = 0
                    
                full_list.append(unit_data)
                
        print(f"   ✨ 총 {len(full_list)}세대 데이터 생성 완료")
        return full_list

    def _find_price_for_floor(self, price_map, type_name, floor):
        """특정 타입/층에 해당하는 분양가 정보 찾기"""
        if type_name not in price_map: return None
        
        # 해당 타입의 모든 가격대 순회
        # 키는 (min_f, max_f) 튜플
        for (min_f, max_f), info in price_map[type_name].items():
            if min_f <= floor <= max_f:
                return info
        return None

    def _normalize_type(self, type_str):
        """타입 문자열 정규화"""
        if not type_str: return "Unknown"
        return str(type_str).strip()

    def _safe_int(self, value):
        """안전하게 정수로 변환 ("5~9" -> 9)"""
        try:
            return int(value)
        except:
            s = str(value).strip()
            # 숫자 외 문자 제거
            import re
            numbers = re.findall(r'\d+', s)
            if numbers:
                return int(numbers[-1]) # 가장 마지막 숫자 (예: 5~9 -> 9)
            return 0

    def _parse_floor_range(self, floor_str):
        """층 범위 문자열 파싱 (예: '3~10' -> [(3, 10)])"""
        ranges = []
        if not floor_str: return [(1, 1)] # 기본값
        
        # '층' 제거
        s = str(floor_str).replace('층', '').strip()
        
        parts = s.split(',')
        for part in parts:
            part = part.strip()
            if '~' in part:
                try:
                    start, end = part.split('~')
                    ranges.append((int(start), int(end)))
                except:
                    pass
            elif '-' in part:
                 try:
                    start, end = part.split('-')
                    ranges.append((int(start), int(end)))
                 except:
                    pass
            else:
                try:
                    val = int(part)
                    ranges.append((val, val))
                except:
                    pass
                    
        return ranges if ranges else [(1, 1)]

    def _process_pricing(self):
        """분양가 정보 처리"""
        print("   - 분양가 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_pricing.md"
        result = self._run_gemini(prompt_path)
        if not result: return None

        try:
            data = json.loads(result)
            items = data.get('분양가', [])
            
            # 단지명 컬럼 추가
            for item in items:
                item['단지명'] = self.apartment_name
                
            return items
        except json.JSONDecodeError:
            print("   ❌ AI 응답 JSON 파싱 실패")
            return None
        except Exception as e:
            print(f"   ❌ 분양가 처리 중 오류: {e}")
            return None

    def _process_balcony(self):
        """발코니 확장비 처리"""
        print("   - 발코니 확장 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_balcony.md"
        result = self._run_gemini(prompt_path)
        if not result: return None
        
        try:
            data = json.loads(result)
            items = data.get('발코니', [])
            for item in items:
                item['단지명'] = self.apartment_name
            return items
        except Exception as e:
            print(f"   ❌ 발코니 처리 중 오류: {e}")
            return None

    def _process_options(self):
        """옵션 정보 처리"""
        print("   - 옵션 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_options.md"
        result = self._run_gemini(prompt_path)
        if not result: return None
        
        try:
            data = json.loads(result)
            items = data.get('옵션', [])
            for item in items:
                item['단지명'] = self.apartment_name
            return items
        except Exception as e:
            print(f"   ❌ 옵션 처리 중 오류: {e}")
            return None

    def _process_schedule(self):
        """일정 확정"""
        print("   - 일정 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_schedule.md"
        result = self._run_gemini(prompt_path)
        if not result: return None
        
        try:
            data = json.loads(result)
            items = data.get('일정', [])
            for item in items:
                item['단지명'] = self.apartment_name
            return items
        except Exception as e:
             print(f"   ❌ 일정 처리 중 오류: {e}")
             return None

    def _process_supply_info(self):
        """공급 정보 추출"""
        print("   - 공급 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_supply_info.md"
        result = self._run_gemini(prompt_path)
        if not result: return None
        
        try:
            data = json.loads(result)
            items = data.get('타입정보', [])
            return items
        except Exception as e:
            print(f"   ❌ 공급정보 처리 중 오류: {e}")
            return None

    def _run_gemini(self, prompt_file: Path) -> str:
        if not prompt_file.exists():
            print(f"   ⚠️ 프롬프트 파일 없음: {prompt_file}")
            return ""
            
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        max_retries = 3
        retry_delay = 10
        
        import time

        for attempt in range(max_retries):
            uploaded_file = None
            try:
                uploaded_file = genai.upload_file(str(self.pdf_path))
                
                # API 호출 전 잠시 대기 (Rate Limit 완화)
                if attempt > 0: time.sleep(retry_delay * attempt)
                else: time.sleep(2)
                
                response = self.model.generate_content([prompt_content, uploaded_file])
                text = response.text
                
                # Clean Markdown formatting
                if '```json' in text:
                    text = text.split('```json')[1].split('```')[0].strip()
                elif '```' in text:
                    text = text.split('```')[1].split('```')[0].strip()
                return text
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ⚠️ Gemini API 오류 (시도 {attempt+1}/{max_retries}): {error_msg}")
                
                if "429" in error_msg or "Resource exhausted" in error_msg:
                    print(f"      ⏳ Rate Limit 발생. {retry_delay * (attempt+1)}초 대기 후 재시도...")
                    time.sleep(retry_delay * (attempt+1))
                else:
                    # 429 외의 에러는 재시도하지 않거나, 필요 시 정책 추가
                    if attempt == max_retries - 1: return ""
                    time.sleep(5)
            finally:
                if uploaded_file:
                    try:
                        genai.delete_file(uploaded_file.name)
                    except:
                        pass
                        
        print("   ❌ 최대 재시도 횟수 초과.")
        return ""

    def _save_final_excel(self, collected_data):
        """모든 데이터를 하나의 엑셀 파일로 저장"""
        out_filename = f"{self.apartment_name}_분양정보.xlsx"
        out_path = self.output_dir / out_filename
        
        if not USE_PANDAS:
            print("   ⚠️ pandas가 설치되지 않아 엑셀 저장을 건너뜁니다.")
            return

        try:
            with pd.ExcelWriter(out_path, engine='openpyxl') as writer:
                # 1. 공급정보 (가장 기본이 되는 정보)
                if '공급정보' in collected_data:
                    pd.DataFrame(collected_data['공급정보']).to_excel(writer, sheet_name='공급정보', index=False)
                
                # 2. 분양가
                if '분양가' in collected_data:
                    pd.DataFrame(collected_data['분양가']).to_excel(writer, sheet_name='분양가', index=False)
                    
                # 3. 발코니
                if '발코니' in collected_data:
                    pd.DataFrame(collected_data['발코니']).to_excel(writer, sheet_name='발코니', index=False)
                
                # 4. 유상옵션
                if '유상옵션' in collected_data:
                    pd.DataFrame(collected_data['유상옵션']).to_excel(writer, sheet_name='유상옵션', index=False)
                    
                # 5. 일정
                if '일정' in collected_data:
                    pd.DataFrame(collected_data['일정']).to_excel(writer, sheet_name='일정', index=False)
                    
            print(f"   💾 엑셀 저장 완료: {out_path.name}")
            
        except Exception as e:
            print(f"   ❌ 엑셀 저장 중 오류 발생: {e}")
