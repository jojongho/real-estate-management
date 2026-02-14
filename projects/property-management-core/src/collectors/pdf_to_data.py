#!/usr/bin/env python3
"""
입주자 모집공고문 PDF → 정규화된 데이터 자동 추출
Gemini Python SDK를 사용한 완전 자동화 파이프라인
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Google Cloud 로깅 경고 메시지 숨기기
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'

# pandas 임포트 시도 (없으면 CSV 직접 사용)
try:
    import pandas as pd
    USE_PANDAS = True
except ImportError:
    USE_PANDAS = False
    print("⚠️  pandas 미설치 - CSV 직접 저장 모드")

# Gemini SDK 임포트
try:
    import google.generativeai as genai
except ImportError:
    print("❌ Gemini SDK가 설치되지 않았습니다")
    print("   설치: pip install google-generativeai")
    sys.exit(1)

class PDFDataExtractor:
    """PDF에서 아파트 분양 데이터를 자동으로 추출"""

    def __init__(self, pdf_path: str, output_dir: str = None):
        self.pdf_path = Path(pdf_path)
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent
        self.apartment_name = self._extract_apartment_name()

        # .env 파일 로드
        load_dotenv()

        # Gemini API 설정
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY 환경변수가 설정되지 않았습니다")
            print("   .env 파일에 GEMINI_API_KEY를 설정하거나")
            print("   환경변수로 설정해주세요: $env:GEMINI_API_KEY='your-key'")
            sys.exit(1)

        genai.configure(api_key=api_key)

        # 모델 설정
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
        self.model = genai.GenerativeModel(model_name)

        print(f"🤖 Gemini 모델: {model_name}")

    def _extract_apartment_name(self) -> str:
        """PDF 파일명에서 단지명 추출"""
        filename = self.pdf_path.stem

        # 일반적인 패턴 제거
        name = filename
        name = name.split('입주자모집공고')[0]
        name = name.split('.')[-1]
        name = ' '.join(name.split()[1:])
        name = name.replace(' ', '')

        return name

    def extract_all_data(self):
        """모든 데이터 유형 추출"""
        print(f"\n📂 처리 중: {self.pdf_path.name}")
        print(f"🏢 단지명: {self.apartment_name}")
        print(f"📁 출력 폴더: {self.output_dir}\n")

        # 1. 분양가 정보
        print("1️⃣ 분양가 정보 추출 중...")
        pricing_data = self._extract_pricing()
        if pricing_data:
            self._save_csv(pricing_data, f"{self.apartment_name}_분양가.csv")
            print(f"   ✅ {len(pricing_data)}건 추출 완료")

        # 2. 옵션 정보
        print("2️⃣ 옵션 정보 추출 중...")
        option_data = self._extract_options()
        if option_data:
            self._save_csv(option_data, f"{self.apartment_name}_옵션.csv")
            print(f"   ✅ {len(option_data)}건 추출 완료")

        # 3. 단지 일정
        print("3️⃣ 단지 일정 추출 중...")
        schedule_data = self._extract_schedule()
        if schedule_data:
            self._save_csv(schedule_data, f"{self.apartment_name}_단지일정.csv")
            print(f"   ✅ {len(schedule_data)}건 추출 완료")

        # 4. 타입별 공급 정보
        print("4️⃣ 타입별 공급 정보 추출 중...")
        supply_data = self._extract_supply_info()
        if supply_data:
            self._save_csv(supply_data, f"{self.apartment_name}_타입.csv")
            print(f"   ✅ {len(supply_data)}건 추출 완료")

        print(f"\n🎉 모든 데이터 추출 완료!")
        print(f"📂 저장 위치: {self.output_dir}")

    def _extract_pricing(self) -> list:
        """분양가 정보 추출 (세대정보 파일 기반)"""
        # 1. 세대정보 파일 로드
        household_file = self.output_dir / f"{self.apartment_name} - 분양가 매핑전.csv"

        if not household_file.exists():
            # 파일명 패턴 검색
            import glob
            pattern = str(self.output_dir / "*분양가 매핑전*.csv")
            matches = glob.glob(pattern)

            if matches:
                household_file = Path(matches[0])
                print(f"   📋 세대정보 파일 발견: {household_file.name}")
            else:
                print(f"   ⚠️  분양가 매핑전.csv 파일이 없습니다")
                print(f"   📁 필요 위치: {self.output_dir}")
                print(f"   💡 '{self.apartment_name} - 분양가 매핑전.csv' 파일을 먼저 제공해주세요")
                return []

        # 2. 세대정보 읽기
        household_data = []
        try:
            with open(household_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    household_data.append({
                        '동': int(row.get('동', 0)),
                        '호': int(row.get('호', 0)),
                        '타입': row.get('타입', '')
                    })
            print(f"   📋 세대정보: {len(household_data)}세대 로드됨")
        except Exception as e:
            print(f"   ❌ 세대정보 파일 읽기 오류: {e}")
            return []

        # 3. 분양가 정보 추출 (PDF)
        prompt_file = Path(__file__).parent.parent.parent / "prompts" / "extract_pricing.md"
        result = self._run_gemini_api(prompt_file)

        if not result:
            return []

        # 4. 세대정보와 분양가 매칭
        try:
            data = json.loads(result)
            normalized = []

            # PDF에서 추출한 타입×층별 금액 정보를 층 범위 형태로 변환
            pricing_lookup = {}  # {(타입, 층): {대지비, 건축비, ...}}

            for item in data.get('분양가', []):
                타입 = item.get('타입', '')
                층구분 = item.get('층구분', '')

                # 층 범위 파싱 (예: "3층" → [(3,3)], "5~9층" → [(5,9)])
                floor_ranges = self._parse_floor_range(층구분)

                # 각 층에 대해 금액 정보 저장
                for min_floor, max_floor in floor_ranges:
                    for floor in range(min_floor, max_floor + 1):
                        pricing_lookup[(타입, floor)] = {
                            '대지비': item.get('대지비', 0),
                            '건축비': item.get('건축비', 0),
                            '부가가치세': item.get('부가가치세', 0),
                            '분양가': item.get('분양가', 0),
                            '1차계약금': item.get('1차계약금', 0),
                            '2차계약금': item.get('2차계약금', 0),
                            '중도금1회': item.get('중도금1회', 0),
                            '중도금2회': item.get('중도금2회', 0),
                            '중도금3회': item.get('중도금3회', 0),
                            '중도금4회': item.get('중도금4회', 0),
                            '중도금5회': item.get('중도금5회', 0),
                            '중도금6회': item.get('중도금6회', 0),
                            '잔금': item.get('잔금', 0)
                        }

            # 각 세대에 금액 정보 매칭
            for household in household_data:
                동 = household['동']
                호 = household['호']
                타입 = household['타입']

                # 호수에서 층 추출 (305호 → 3층, 1005호 → 10층)
                floor = int(str(호)[:-2]) if len(str(호)) >= 3 else 1

                # 해당 타입×층에 대한 금액 정보 조회
                pricing = pricing_lookup.get((타입, floor))

                if pricing:
                    normalized.append({
                        '동': 동,
                        '호': 호,
                        '타입': 타입,
                        '대지비': pricing['대지비'],
                        '건축비': pricing['건축비'],
                        '부가가치세': pricing['부가가치세'],
                        '분양가': pricing['분양가'],
                        '1차계약금': pricing['1차계약금'],
                        '2차계약금': pricing['2차계약금'],
                        '중도금1회': pricing['중도금1회'],
                        '중도금2회': pricing['중도금2회'],
                        '중도금3회': pricing['중도금3회'],
                        '중도금4회': pricing['중도금4회'],
                        '중도금5회': pricing['중도금5회'],
                        '중도금6회': pricing['중도금6회'],
                        '잔금': pricing['잔금']
                    })

            print(f"   ✅ 매칭 완료: {len(normalized)}세대")
            return normalized
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _extract_options(self) -> list:
        """옵션 정보 추출"""
        prompt_file = Path(__file__).parent.parent.parent / "prompts" / "extract_options.md"

        result = self._run_gemini_api(prompt_file)

        if not result:
            return []

        try:
            data = json.loads(result)
            normalized = []

            for item in data.get('옵션', []):
                normalized.append({
                    '단지명': self.apartment_name,
                    '옵션구분': item.get('옵션구분', ''),
                    '타입': item.get('타입', ''),
                    '품목': item.get('품목', ''),
                    '품목세부': item.get('품목세부', ''),
                    '설치내역': item.get('설치내역', ''),
                    '공급금액': item.get('공급금액', 0)
                })

            return normalized
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return []

    def _extract_schedule(self) -> list:
        """단지 일정 추출"""
        prompt_file = Path(__file__).parent.parent.parent / "prompts" / "extract_schedule.md"

        result = self._run_gemini_api(prompt_file)

        if not result:
            return []

        try:
            data = json.loads(result)
            normalized = []

            for item in data.get('일정', []):
                normalized.append({
                    '단지명': self.apartment_name,
                    '일정명': item.get('일정명', ''),
                    '시작일': item.get('시작일', ''),
                    '종료일': item.get('종료일', '')
                })

            return normalized
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return []

    def _extract_supply_info(self) -> list:
        """타입별 공급 정보 추출"""
        prompt_file = Path(__file__).parent.parent.parent / "prompts" / "extract_supply_info.md"

        result = self._run_gemini_api(prompt_file)

        if not result:
            return []

        try:
            data = json.loads(result)
            return data.get('타입정보', [])
        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return []

    def _run_gemini_api(self, prompt_file: Path) -> str:
        """Gemini API 실행"""
        if not prompt_file.exists():
            print(f"   ⚠️  프롬프트 파일 없음: {prompt_file}")
            return ""

        try:
            # 프롬프트 파일 읽기
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()

            # PDF 파일 업로드
            print(f"   📤 PDF 업로드 중...")
            uploaded_file = genai.upload_file(str(self.pdf_path))

            # Gemini API 호출
            print(f"   🤖 AI 분석 중...")
            response = self.model.generate_content([prompt, uploaded_file])

            # 업로드된 파일 삭제
            genai.delete_file(uploaded_file.name)

            # 응답에서 JSON 추출
            text = response.text

            # JSON 블록 추출 (```json ... ``` 형식일 수 있음)
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()

            return text

        except Exception as e:
            print(f"   ❌ Gemini API 오류: {e}")
            return ""

    def _expand_dong_ho(self, dong_str: str, ho_str: str) -> list:
        """동-호 문자열을 개별 (동, 호) 튜플 리스트로 확장"""
        # 동 파싱
        dong_list = []
        dong_str = dong_str.replace('동', '').strip()

        # ~ 또는 - 둘 다 범위로 처리
        if '~' in dong_str or '-' in dong_str:
            sep = '~' if '~' in dong_str else '-'
            parts = dong_str.split(sep)
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            dong_list = list(range(start, end + 1))
        elif ',' in dong_str:
            dong_list = [int(d.strip()) for d in dong_str.split(',')]
        else:
            dong_list = [int(dong_str)]

        # 호 파싱
        ho_list = []
        ho_str = ho_str.replace('호', '').strip()

        if '~' in ho_str or '-' in ho_str:
            # 호도 범위 가능 (예: 1~4호)
            sep = '~' if '~' in ho_str else '-'
            parts = ho_str.split(sep)
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            ho_list = list(range(start, end + 1))
        elif ',' in ho_str:
            ho_list = [int(h.strip()) for h in ho_str.split(',')]
        else:
            ho_list = [int(ho_str)]

        # 교차 곱
        result = []
        for dong in dong_list:
            for ho in ho_list:
                result.append((dong, ho))

        return result

    def _parse_floor_range(self, floor_str: str) -> list:
        """층 구분 문자열을 (최저층, 최고층) 튜플 리스트로 파싱

        예시:
        - "3층" → [(3, 3)]
        - "5~9층" → [(5, 9)]
        - "10층 이상" → [(10, 99)]
        - "최상층" → [(99, 99)]
        """
        floor_str = floor_str.replace('층', '').strip()

        # 특수 케이스 처리
        if '최상' in floor_str or '최고' in floor_str:
            return [(99, 99)]
        elif '최하' in floor_str or '최저' in floor_str:
            return [(1, 1)]

        if '~' in floor_str or '-' in floor_str:
            sep = '~' if '~' in floor_str else '-'
            parts = floor_str.split(sep)
            try:
                min_floor = int(parts[0].strip())
                max_floor = int(parts[1].strip())
                return [(min_floor, max_floor)]
            except ValueError:
                print(f"   ⚠️  층 범위 파싱 오류: {floor_str}")
                return []

        elif '이상' in floor_str:
            try:
                min_floor = int(floor_str.replace('이상', '').strip())
                return [(min_floor, 99)]
            except ValueError:
                print(f"   ⚠️  층 파싱 오류: {floor_str}")
                return []

        elif '이하' in floor_str:
            try:
                max_floor = int(floor_str.replace('이하', '').strip())
                return [(1, max_floor)]
            except ValueError:
                print(f"   ⚠️  층 파싱 오류: {floor_str}")
                return []

        else:
            try:
                floor = int(floor_str)
                return [(floor, floor)]
            except ValueError:
                print(f"   ⚠️  층 파싱 오류: {floor_str} (숫자 변환 실패)")
                return []

    def _expand_floor_price(self, floor_str: str, price: int) -> list:
        """층 구분 문자열을 (최저층, 최고층, 가격) 튜플 리스트로 확장"""
        floor_str = floor_str.replace('층', '').strip()

        if '~' in floor_str or '-' in floor_str:
            sep = '~' if '~' in floor_str else '-'
            parts = floor_str.split(sep)
            min_floor = int(parts[0].strip())
            max_floor = int(parts[1].strip())
            return [(min_floor, max_floor, price)]

        elif '이상' in floor_str:
            min_floor = int(floor_str.replace('이상', '').strip())
            return [(min_floor, 99, price)]

        elif '이하' in floor_str:
            max_floor = int(floor_str.replace('이하', '').strip())
            return [(1, max_floor, price)]

        else:
            floor = int(floor_str)
            return [(floor, floor, price)]

    def _save_csv(self, data: list, filename: str):
        """데이터를 CSV로 저장"""
        if not data:
            return

        output_path = self.output_dir / filename

        if USE_PANDAS:
            # pandas 사용
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        else:
            # CSV 직접 저장
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)

        print(f"   💾 저장: {output_path}")


def main():
    """메인 실행 함수"""
    # Windows 콘솔 UTF-8 인코딩 설정
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        print("사용법: python pdf_to_data.py <PDF 파일 경로>")
        print("예시: python pdf_to_data.py 힐스테이트두정역/입주자모집공고문.pdf")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"❌ 파일을 찾을 수 없습니다: {pdf_path}")
        sys.exit(1)

    extractor = PDFDataExtractor(pdf_path)
    extractor.extract_all_data()


if __name__ == "__main__":
    main()
