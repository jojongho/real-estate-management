import os
import time
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# 환경 변수 로드
current_path = Path(__file__).resolve().parent
env_path = None

for _ in range(5): # 상위 5단계까지 탐색
    check_path = current_path / '.env'
    if check_path.exists():
        env_path = check_path
        break
    current_path = current_path.parent

if env_path:
    print(f"   🔑 .env 로드: {env_path}")
    load_dotenv(env_path)
else:
    print("   ⚠️ .env 파일을 찾지 못했습니다. 시스템 환경변수를 확인합니다.")
    load_dotenv() # 기본 로드 시도

# Google GenAI 설정
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

genai.configure(api_key=api_key)

class ImageProcessor:
    def __init__(self, raw_dir: str, output_dir: str):
        self.raw_dir = Path(raw_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 모델 설정 (Gemini 2.0 Flash)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def _upload_files(self, image_paths):
        """이미지를 Gemini에 업로드하고 파일 핸들을 반환"""
        print(f"   📤 이미지 {len(image_paths)}장 업로드 중...")
        uploaded_files = []
        for path in image_paths:
            try:
                # 파일 업로드 (MIME type은 자동 감지되지만 명시할 수도 있음)
                f = genai.upload_file(str(path))
                uploaded_files.append(f)
                # Rate Limit 방지용 짧은 대기
                time.sleep(1) 
            except Exception as e:
                print(f"   ❌ 업로드 실패 ({path.name}): {e}")
                
        # 처리 완료될 때까지 대기 (Gemini File API는 비동기 처리됨)
        # 하지만 이미지는 보통 바로 Active 상태가 됨.
        print("   ✅ 업로드 완료. AI 분석 시작...")
        return uploaded_files

    def _cleanup_files(self, uploaded_files):
        """업로드된 파일 삭제 (리소스 정리)"""
        print("   🧹 임시 파일 정리 중...")
        for f in uploaded_files:
            try:
                genai.delete_file(f.name)
            except:
                pass

    def run(self):
        print("🖼️ 이미지 전처리기를 실행합니다...")
        
        # 1. 이미지 파일 수집
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        image_paths = sorted([
            p for p in self.raw_dir.iterdir() 
            if p.suffix.lower() in image_extensions
        ])
        
        if not image_paths:
            print("   ⚠️ 처리할 이미지 파일이 없습니다.")
            return

        print(f"   🔍 발견된 이미지: {len(image_paths)}개")
        
        # 2. 이미지 업로드
        uploaded_files = self._upload_files(image_paths)
        
        if not uploaded_files:
            print("   ⚠️ 업로드된 파일이 없어 종료합니다.")
            return

        # 파일명 목록 생성
        file_map_str = "\n".join([f"- 이미지{i+1}: {p.name}" for i, p in enumerate(image_paths)])
        
        # 중요 파일 강조
        key_layout_file = "단지동호수배치도.jpg"
        layout_emphasis = ""
        if any(key_layout_file in p.name for p in image_paths):
            layout_emphasis = f"""
!!! 중요 !!!
'{key_layout_file}' 이미지가 포함되어 있습니다. 
이 이미지는 **전체 1079세대의 동/호수 배치 정보**를 담고 있는 가장 핵심적인 자료입니다.
이 이미지를 정밀 분석하여 **각 동별, 라인별 최고층수와 필로티 여부, 타입 정보**를 빠짐없이 추출해야 합니다.
"""

        # 3. 프롬프트 작성 (상세 데이터 추출용)
        prompt = f"""
당신은 부동산 데이터 정규화 전문가입니다. 제공된 이미지들을 분석하여 **데이터베이스 구축이 가능한 수준의 상세 Markdown**을 작성해야 합니다.

[이미지 파일 매핑 정보]
{file_map_str}

{layout_emphasis}

**[필수 추출 데이터 항목]**
모든 데이터는 가능한 한 **표(Table)** 형태로 작성하여 엑셀 변환이 용이하게 하세요.

1. **공급 내역 상세**
   - 표 컬럼: 주택형 | 약식표기 | 공급세대수(일반/특별/총계) | 전용면적 | 주거공용 | 공급면적 | 기타공용 | 계약면적 | 대지지분
   - 모든 면적은 소수점 4자리까지 정확하게 기재.

2. **분양가 상세 (가장 중요)**
   - **단순 총액이 아닌 구성요소를 분리해야 함.**
   - 표 컬럼: **타입 | 층구분 | 대지비 | 건축비 | 부가가치세 | 분양가(합계)**
   - 금액은 '원' 단위까지 정확히 기재 (예: 421,000,000). 단위 생략 금지.

3. **납부 일정 및 비율**
   - 계약금(1차/2차), 중도금(1~6회), 잔금의 **비율(%)**과 **금액** 정보를 추출.
   - 예: 계약금 10% (1차 1000만원 정액, 2차 나머지), 중도금 60%, 잔금 30%.
   - 표 또는 텍스트로 명확히 정리.

4. **단지 배치 및 동호수 (정밀)**
   - 엑셀로 '호' 리스트를 생성할 수 있도록 **동별/라인별 규칙**을 서술.
   - 예: "101동: 1~4호 라인. 1,2호는 84A(29층), 3,4호는 84B(29층). 1층 필로티 없음."
   - **필로티 층**이나 **화단 등 비거주 공간**이 있다면 반드시 명시 (예: "105동 1호 라인은 1층 필로티").

5. **발코니 확장비 및 옵션 상세**
   - **발코니 확장비**: 타입 | 총액 | 계약금 | 잔금 (또는 중도금 포함 여부)
   - **시스템 에어컨/가전**: 상세 품목별 가격 표.

**작성 규칙:**
- 이미지 링크 포함: `![설명](data/raw/파일명.jpg)`
- Markdown Table 문법 준수.
- 추측하지 말고 이미지에 있는 내용만 'Fact'로 기재. 없는 내용은 "확인 불가" 표기.
- 금액은 콤마(,)를 포함한 숫자 형식 (예: 541,000,000).
"""

        # 4. 콘텐츠 생성 요청
        try:
            # Gemini 2.0 Flash 호출
            response = self.model.generate_content([prompt, *uploaded_files])
            
            # 결과 저장
            output_file = self.output_dir / "preprocessed.md"
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response.text)
                
            print(f"   ✨ Markdown 저장 완료: {output_file}")
            print(f"   📝 문서 길이: {len(response.text)}자")
            
        except Exception as e:
            print(f"   ❌ AI 생성 중 오류 발생: {e}")
            
        finally:
            # 5. 리소스 정리
            self._cleanup_files(uploaded_files)

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    RAW_DIR = BASE_DIR / "data/raw"
    INTERIM_DIR = BASE_DIR / "data/interim"
    
    processor = ImageProcessor(RAW_DIR, INTERIM_DIR)
    processor.run()
