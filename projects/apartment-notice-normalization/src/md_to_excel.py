import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import pandas as pd

# 환경 변수 로드
current_path = Path(__file__).resolve().parent
env_path = None
for _ in range(5):
    check_path = current_path / '.env'
    if check_path.exists():
        env_path = check_path
        break
    current_path = current_path.parent
if env_path: load_dotenv(env_path)
else: load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class MarkdownToExcel:
    def __init__(self, md_path: Path, output_dir: Path):
        self.md_path = md_path
        self.output_dir = output_dir
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def _safe_int(self, value):
        """안전하게 정수로 변환"""
        try:
            val = str(value).replace(',', '').strip()
            return int(val)
        except:
            return 0

    def _extract_json(self, section_name, prompt, context_md):
        """LLM을 이용해 MD에서 JSON 데이터 추출"""
        full_prompt = f"""
다음은 아파트 입주자모집공고 MD 문서의 일부입니다.
요청한 **{section_name}** 데이터를 추출하여 **JSON 형식**으로 출력하세요.

[Markdown 문서]
{context_md}

[요청 사항]
{prompt}

JSON 출력 형식:
```json
[ ... ]
```
"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(full_prompt)
                text = response.text
                if '```json' in text:
                    text = text.split('```json')[1].split('```')[0].strip()
                elif '```' in text:
                    text = text.split('```')[1].split('```')[0].strip()
                return json.loads(text)
            except Exception as e:
                print(f"   ⚠️ {section_name} JSON 추출 실패 ({attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1: return []
        return []

    def _normalize_floor_range(self, floor_str):
        """층 문자열을 파싱하여 (min, max) 튜플 리스트 반환"""
        # 예: "1층", "2층", "3~10층", "11층 이상"
        ranges = []
        s = str(floor_str).replace('층', '').replace('이상', '').strip()
        parts = s.split(',')
        for part in parts:
            part = part.strip()
            if '~' in part:
                try:
                    start, end = part.split('~')
                    ranges.append((self._safe_int(start), self._safe_int(end)))
                except: pass
            elif '-' in part:
                 try:
                    start, end = part.split('-')
                    ranges.append((self._safe_int(start), self._safe_int(end)))
                 except: pass
            else:
                 try:
                    v = self._safe_int(part)
                    ranges.append((v, v))
                 except: pass
        return ranges if ranges else [(1, 99)] # default

    def run(self):
        print("📊 상세 데이터 정규화(Excel) 시작...")
        if not self.md_path.exists():
            print("   ❌ Markdown 파일이 없습니다.")
            return

        with open(self.md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 1. 분양가 상세 (대지비, 건축비, 부가세 포함)
        print("   - 분양가 상세 데이터 추출 중...")
        pricing_prompt = """
        '분양가' 또는 '공급금액' 섹션을 찾아 아래 JSON 구조로 추출하세요.
        필드: 타입, 층구분, 대지비, 건축비, 부가가치세, 분양가(합계)
        (금액은 숫자만)
        예: [{"타입": "84A", "층구분": "5~9층", "대지비": 1000, "건축비": 2000, "부가가치세": 200, "분양가": 3200}]
        """
        pricing_data = self._extract_json("분양가", pricing_prompt, md_content)

        # 2. 납부 일정 (계약금, 중도금, 잔금)
        print("   - 납부 일정 추출 중...")
        payment_prompt = """
        '납부 일정' 또는 '분양대금 납부' 섹션에서 계약금/중도금/잔금 비율과 금액 규칙을 찾으세요.
        일반적으로 계약금 10% (1차 1000만원, 2차 나머지), 중도금 60%, 잔금 30% 입니다.
        JSON 필드: 계약금총액비율(%), 계약금1차금액(정액), 중도금비율(%), 잔금비율(%)
        단일 객체로 반환: [{"계약금비율": 10, "계약금1차": 10000000, "중도금비율": 60, "잔금비율": 30}]
        """
        payment_rule = self._extract_json("납부일정", payment_prompt, md_content)
        payment_rule = payment_rule[0] if payment_rule else {}
        
        # 3. 공급 내역 상세 (약식표기, 면적 등)
        print("   - 공급 내역 추출 중...")
        supply_prompt = """
        '공급 내역' 섹션에서 주택형별 상세 정보를 추출하세요.
        필드: 주택형, 약식표기, 공급세대수, 전용면적, 공급면적, 대지지분
        """
        supply_data = self._extract_json("공급내역", supply_prompt, md_content)

        # 4. 발코니 확장비
        print("   - 발코니 데이터 추출 중...")
        balcony_prompt = """
        '발코니' 섹션에서 타입별 확장 금액을 추출하세요.
        필드: 타입, 확장금액, 계약금, 잔금
        """
        balcony_data = self._extract_json("발코니", balcony_prompt, md_content)
        
        # 5. 옵션 (에어컨 등)
        print("   - 옵션 데이터 추출 중...")
        option_prompt = """
        '옵션' 섹션에서 품목별 가격을 추출하세요.
        필드: 옵션구분(시스템에어컨 등), 타입, 품목명, 금액
        """
        option_data = self._extract_json("옵션", option_prompt, md_content)

        # 6. Full List 생성 및 데이터 결합
        print("   - 전체 1079세대 리스트 생성 및 데이터 매핑 중...")
        
        # 단지 배치 정보 추출
        layout_prompt = """
        '단지 배치 및 동호수' 섹션을 분석하여 모든 동의 호수 리스트를 생성할 수 있는 규칙을 JSON으로 추출하세요.
        [{"동": "101", "라인": [1,2,3,4], "타입": "84A", "최고층": 29, "필로티": []}]
        동마다 타입이 섞여 있거나 라인별 최고층이 다르면 객체를 나누세요.
        """
        layout_data = self._extract_json("단지배치", layout_prompt, md_content)
        
        full_list = []
        
        # Pricing Map 구성 (Type -> Floor Range -> Data)
        pricing_map = {}
        for p in pricing_data:
            t = str(p.get('타입')).strip()
            ranges = self._normalize_floor_range(p.get('층구분', ''))
            if t not in pricing_map: pricing_map[t] = {}
            for r in ranges:
                pricing_map[t][r] = p
                
        # Payment Logic
        contract_rate = payment_rule.get('계약금비율', 10) / 100
        contract_1st_fix = self._safe_int(payment_rule.get('계약금1차', 0))
        middle_rate = payment_rule.get('중도금비율', 60) / 100
        balance_rate = payment_rule.get('잔금비율', 30) / 100
        
        for item in layout_data:
            dong = item['동']
            lines = item['라인']
            # 라인 처리
            target_lines = []
            if isinstance(lines, str):
                if '~' in lines: s, e = map(int, lines.replace('호', '').split('~')); target_lines = list(range(s, e+1))
                else: target_lines = [int(lines)]
            elif isinstance(lines, int): target_lines = [lines]
            else: target_lines = lines
            
            main_type = str(item.get('타입')).strip()
            max_floor = self._safe_int(item.get('최고층', 1))
            skips = item.get('필로티', [])
            
            for line in target_lines:
                for floor in range(1, max_floor + 1):
                    if floor in skips: continue
                    ho = floor * 100 + line
                    
                    row = {
                        '동': dong, '호': ho, '타입': main_type, '층': floor
                    }
                    
                    # 가격 매핑
                    price_info = None
                    if main_type in pricing_map:
                        for (min_f, max_f), p_data in pricing_map[main_type].items():
                            if min_f <= floor <= max_f:
                                price_info = p_data
                                break
                    
                    if price_info:
                        total_price = self._safe_int(price_info.get('분양가', 0))
                        row['대지비'] = self._safe_int(price_info.get('대지비', 0))
                        row['건축비'] = self._safe_int(price_info.get('건축비', 0))
                        row['부가가치세'] = self._safe_int(price_info.get('부가가치세', 0))
                        row['분양가'] = total_price
                        
                        # 납부 일정 계산
                        c1 = contract_1st_fix
                        # 계약금 총액 = 분양가 * 비율
                        c_total = int(total_price * contract_rate)
                        c2 = c_total - c1
                        
                        row['1차계약금'] = c1
                        row['2차계약금'] = c2
                        
                        # 중도금 (보통 6회 분할)
                        m_total = int(total_price * middle_rate)
                        m_each = m_total // 6
                        for i in range(1, 7):
                            row[f'중도금{i}회'] = m_each
                            
                        # 잔금
                        row['잔금'] = total_price - c_total - m_total
                    else:
                        row['분양가'] = 0
                        
                    full_list.append(row)
                    
        # 엑셀 저장
        output_file = self.output_dir / "final_normalized_v2.xlsx"
        print(f"   💾 엑셀 저장 중: {output_file.name}")
        
        with pd.ExcelWriter(output_file) as writer:
            # 1. 단지정보 (Summary)
            if supply_data: pd.DataFrame(supply_data).to_excel(writer, sheet_name='단지정보', index=False)
            
            # 2. 분양가 (Full List + Price Detail)
            if full_list: pd.DataFrame(full_list).to_excel(writer, sheet_name='분양가', index=False)
            
            # 3. 발코니
            if balcony_data: pd.DataFrame(balcony_data).to_excel(writer, sheet_name='발코니', index=False)
            
            # 4. 옵션
            if option_data: pd.DataFrame(option_data).to_excel(writer, sheet_name='옵션', index=False)
            
        print("   ✅ 완료!")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    MD_FILE = BASE_DIR / "data/interim/preprocessed.md"
    OUT_DIR = BASE_DIR / "data/processed"
    
    app = MarkdownToExcel(MD_FILE, OUT_DIR)
    app.run()
