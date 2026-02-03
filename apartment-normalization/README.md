# 아파트 데이터 정규화 프로젝트

입주자모집공고 PDF 문서를 AI(Google Gemini)를 활용해 분석하고, DB화 가능한 구조적 데이터(CSV)로 변환하는 도구입니다.

## 📂 폴더 구조
- `data/raw`: 분석할 PDF 파일과 매핑용 CSV(분양가 매핑전)를 넣는 곳
- `data/processed`: 분석 완료된 CSV 파일이 저장되는 곳
- `src`: 소스 코드
- `prompts`: AI에게 지시할 프롬프트 파일들

## 🚀 사용 방법

1. **환경 설정**
   - 상위 폴더의 `.env` 파일에 `GEMINI_API_KEY`가 설정되어 있어야 합니다. (자동 로드됨)
   - 패키지 설치: `pip install -r requirements.txt`

2. **데이터 준비**
   - `data/raw` 폴더에 **입주자모집공고 PDF 파일**을 넣으세요.
   - (선택) 동호수 매핑이 필요한 경우 `단지명 - 분양가 매핑전.csv` 파일도 함께 넣으세요.

3. **실행**
   ```bash
   python main.py
   ```

4. **결과 확인**
   - `data/processed` 폴더에 분양가, 옵션, 일정 파일이 생성됩니다.
