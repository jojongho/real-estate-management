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
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp') # 최신 모델 권장
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
        
        # 1. 분양가 추출
        self._process_pricing()
        
        # 2. 옵션 추출
        self._process_options()
        
        # 3. 단지 일정 추출
        self._process_schedule()
        
        # 4. 타입 정보 추출
        self._process_supply_info()
        
        print(f"✅ 처리 완료: {self.output_dir}")

    def _process_pricing(self):
        """분양가 정보 처리"""
        print("   - 분양가 정보 추출 중...")
        # 매핑할 세대정보 파일 찾기
        mapping_file = self._find_mapping_file()
        
        if not mapping_file:
            print("   ⚠️ 분양가 매핑전 파일(세대정보)을 찾을 수 없어 매핑을 건너뜁니다.")
            # TODO: 매핑 파일 없이도 기본 분양가표만이라도 추출해서 저장하는 로직 추가 가능
            return

        # PDF에서 데이터 추출
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_pricing.md"
        result = self._run_gemini(prompt_path)
        if not result: return

        try:
            data = json.loads(result)
            normalized_data = self._map_pricing_to_households(data, mapping_file)
            if normalized_data:
                self._save_data(normalized_data, f"{self.apartment_name}_분양가_완료.csv")
        except json.JSONDecodeError:
            print("   ❌ AI 응답 JSON 파싱 실패")
        except Exception as e:
            print(f"   ❌ 분양가 처리 중 오류: {e}")

    def _process_options(self):
        """옵션 정보 처리"""
        print("   - 옵션 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_options.md"
        result = self._run_gemini(prompt_path)
        if result:
            try:
                data = json.loads(result)
                items = data.get('옵션', [])
                # 단지명 컬럼 추가
                for item in items:
                    item['단지명'] = self.apartment_name
                self._save_data(items, f"{self.apartment_name}_옵션.csv")
            except Exception as e:
                print(f"   ❌ 옵션 처리 중 오류: {e}")

    def _process_schedule(self):
        """일정 확정"""
        print("   - 일정 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_schedule.md"
        result = self._run_gemini(prompt_path)
        if result:
            try:
                data = json.loads(result)
                items = data.get('일정', [])
                for item in items:
                    item['단지명'] = self.apartment_name
                self._save_data(items, f"{self.apartment_name}_일정.csv")
            except Exception as e:
                 print(f"   ❌ 일정 처리 중 오류: {e}")

    def _process_supply_info(self):
        """공급 정보 추출"""
        print("   - 공급 정보 추출 중...")
        prompt_path = Path(__file__).parent.parent / "prompts" / "extract_supply_info.md"
        result = self._run_gemini(prompt_path)
        if result:
            try:
                data = json.loads(result)
                items = data.get('타입정보', [])
                self._save_data(items, f"{self.apartment_name}_공급정보.csv")
            except Exception as e:
                print(f"   ❌ 공급정보 처리 중 오류: {e}")

    def _run_gemini(self, prompt_file: Path) -> str:
        if not prompt_file.exists():
            print(f"   ⚠️ 프롬프트 파일 없음: {prompt_file}")
            return ""
            
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        try:
            uploaded_file = genai.upload_file(str(self.pdf_path))
            response = self.model.generate_content([prompt_content, uploaded_file])
            genai.delete_file(uploaded_file.name)
            
            text = response.text
            # Clean Markdown formatting
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            return text
        except Exception as e:
            print(f"   ❌ Gemini API 호출 오류: {e}")
            return ""

    def _find_mapping_file(self):
        """단지 배치 정보(layout) CSV 파일 검색"""
        raw_dir = self.pdf_path.parent
        # "단지입력" 키워드가 포함된 CSV 검색
        matches = list(raw_dir.glob("*단지입력*.csv"))
        if matches: return matches[0]
        return None

    def _map_pricing_to_households(self, ai_data, mapping_file):
        """단지 배치 정보와 AI 추출 분양가 매핑"""
        print(f"   - 단지 배치 정보 로드: {mapping_file.name}")
        
        # 1. 분양가 룩업 테이블 생성
        # (타입, 층) -> 가격 정보
        pricing_lookup = {}
        for item in ai_data.get('분양가', []):
            try:
                # 층 구분 파싱 (예: 5~10 -> [(5,10)])
                floors = self._parse_floor_range(item.get('층구분', ''))
                type_name = self._normalize_type(item.get('타입'))
                
                for min_f, max_f in floors:
                    for f in range(min_f, max_f + 1):
                        pricing_lookup[(type_name, f)] = item
            except Exception as e:
                print(f"     ⚠️ 분양가 룰 파싱 실패 ({item.get('층구분')}): {e}")
                continue

        results = []
        try:
            with open(mapping_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # CSV 컬럼: 동,라인,동,호,타입,최하층,최고층,라인당세대,방향
                    # 호(4번째 컬럼)이 실제로는 라인 번호(1호라인, 2호라인)를 의미함
                    try:
                        dong = row.get('동') or row.get('\ufeff동') # BOM 대응
                        line_no = int(row.get('호', 0)) # 이게 라인 번호
                        type_name = self._normalize_type(row.get('타입', ''))
                        min_floor = int(row.get('최하층', 1))
                        max_floor = int(row.get('최고층', 1))
                        
                        # 해당 라인의 층별 세대 생성
                        for f in range(min_floor, max_floor + 1):
                            # 호수 생성 로직 (층 * 100 + 라인)
                            unit_no = f * 100 + line_no
                            
                            unit_data = {
                                '동': dong,
                                '호': unit_no,
                                '타입': type_name,
                                '층': f,
                                '방향': row.get('방향', '')
                            }
                            
                            # 분양가 매핑
                            price_info = pricing_lookup.get((type_name, f))
                            if price_info:
                                unit_data['분양가'] = price_info.get('분양가', '')
                                unit_data['계약금'] = price_info.get('계약금', '')
                                unit_data['중도금'] = price_info.get('중도금', '')
                                unit_data['잔금'] = price_info.get('잔금', '')
                            else:
                                unit_data['분양가'] = '가격정보없음'
                                
                            results.append(unit_data)
                            
                    except ValueError:
                        continue
                        
        except Exception as e:
            print(f"   ❌ 매핑 로직 오류: {e}")
            return None
            
        print(f"   ✨ 총 {len(results)}세대 데이터 생성 완료")
        return results

    def _normalize_type(self, type_str):
        """타입 명칭 정규화 (공백 제거 등)"""
        if not type_str: return ""
        return str(type_str).replace(" ", "").strip()

    def _parse_floor_range(self, floor_str):
        """층 구분 문자열을 (최저층, 최고층) 튜플 리스트로 파싱"""
        floor_str = str(floor_str).replace('층', '').strip()
        
        # 특수 케이스
        if '최상' in floor_str or '최고' in floor_str:
            return [(99, 99)] # 임의의 고층 번호
        if '최하' in floor_str or '최저' in floor_str:
            return [(1, 1)]
            
        if '~' in floor_str or '-' in floor_str:
            sep = '~' if '~' in floor_str else '-'
            try:
                s, e = floor_str.split(sep)
                return [(int(s.strip()), int(e.strip()))]
            except:
                print(f"   ⚠️ 층 파싱 실패: {floor_str}")
                return []
                
        elif '이상' in floor_str:
            try:
                s = int(floor_str.replace('이상','').strip())
                return [(s, 99)]
            except: return []
            
        elif '이하' in floor_str:
            try:
                e = int(floor_str.replace('이하','').strip())
                return [(1, e)]
            except: return []
            
        elif ',' in floor_str:
            # 1, 3, 5층 같은 경우
            result = []
            parts = floor_str.split(',')
            for p in parts:
                try: result.append((int(p.strip()), int(p.strip())))
                except: pass
            return result
            
        else:
            try:
                val = int(floor_str)
                return [(val, val)]
            except:
                return []

    def _save_data(self, data, filename):
        out_path = self.output_dir / filename
        if USE_PANDAS:
            df = pd.DataFrame(data)
            df.to_csv(out_path, index=False, encoding='utf-8-sig')
        else:
            if not data: return
            with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        print(f"   💾 저장 완료: {out_path.name}")
