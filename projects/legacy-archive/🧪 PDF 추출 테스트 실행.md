---
tags: [테스트, PDF, 실행가이드]
type: guide
status: 진행중
creation_date: 2025-10-05
---

# 🧪 PDF 추출 테스트 실행

> **테스트 대상**: 아산모종서한이다음노블리스
> **목표**: PDF 자동 추출 시스템 검증

---

## 📋 사전 준비 체크리스트

### 1. Gemini API 키 발급 (필수)

1. **Google AI Studio 접속**: https://makersuite.google.com/app/apikey
2. **"Create API Key" 클릭**
3. **API 키 복사**

### 2. API 키 설정

**방법 1: 환경 변수 (권장)**
```bash
# PowerShell
$env:GEMINI_API_KEY="여기에_복사한_API_키_붙여넣기"
```

**방법 2: .env 파일**
```bash
# D:\Projects\apartment-automation\.env 파일 생성
GEMINI_API_KEY=여기에_복사한_API_키_붙여넣기
```

### 3. Python 패키지 설치

```bash
cd D:\Projects\apartment-automation
pip install pandas python-dotenv
```

---

## 🚀 테스트 실행

### Step 1: VSCode 터미널 열기

1. **VSCode에서 프로젝트 열기**
   - `Ctrl + O` → `D:\Projects\apartment-automation` 선택

2. **터미널 열기**
   - `Ctrl + ` (백틱) 또는 메뉴: Terminal > New Terminal

3. **Python 환경 확인**
   ```bash
   python --version
   # Python 3.10 이상이어야 함
   ```

### Step 2: 테스트 실행 명령어

```bash
# 경로가 길어서 변수로 저장
$PDF_PATH = "d:\Flow System\- Flow\01. Framing\Project\아파트 입주자 모집공고문 데이터 정규화 및 마이그레이션\아산모종서한이다음노블리스\2025000448 아산모종 서한이다음 노블리스(A1BL) 입주자모집공고문.pdf"

# 실행
python src/collectors/pdf_to_data.py $PDF_PATH
```

**또는 한 줄로**:
```bash
python src/collectors/pdf_to_data.py "d:\Flow System\- Flow\01. Framing\Project\아파트 입주자 모집공고문 데이터 정규화 및 마이그레이션\아산모종서한이다음노블리스\2025000448 아산모종 서한이다음 노블리스(A1BL) 입주자모집공고문.pdf"
```

---

## 📊 예상 출력

```
📂 처리 중: 2025000448 아산모종 서한이다음 노블리스(A1BL) 입주자모집공고문.pdf
🏢 단지명: 아산모종서한이다음노블리스
📁 출력 폴더: d:\Flow System\...\아산모종서한이다음노블리스

1️⃣ 분양가 정보 추출 중...
   ✅ XXX건 추출 완료
   💾 저장: 아산모종서한이다음노블리스_분양가.csv

2️⃣ 옵션 정보 추출 중...
   ✅ XX건 추출 완료
   💾 저장: 아산모종서한이다음노블리스_옵션.csv

3️⃣ 단지 일정 추출 중...
   ✅ XX건 추출 완료
   💾 저장: 아산모종서한이다음노블리스_단지일정.csv

4️⃣ 타입별 공급 정보 추출 중...
   ✅ X건 추출 완료
   💾 저장: 아산모종서한이다음노블리스_타입.csv

🎉 모든 데이터 추출 완료!
📂 저장 위치: d:\Flow System\...\아산모종서한이다음노블리스
```

---

## 📁 결과 확인

생성된 CSV 파일 위치:
```
d:\Flow System\- Flow\01. Framing\Project\아파트 입주자 모집공고문 데이터 정규화 및 마이그레이션\아산모종서한이다음노블리스\

아산모종서한이다음노블리스_분양가.csv      ← 분양가 정보
아산모종서한이다음노블리스_옵션.csv        ← 옵션 정보
아산모종서한이다음노블리스_단지일정.csv    ← 일정 정보
아산모종서한이다음노블리스_타입.csv        ← 타입 정보
```

**확인 방법**:
1. Obsidian에서 해당 폴더 열기
2. 또는 엑셀로 CSV 파일 열기
3. 데이터 정확성 검증

---

## 🐛 예상되는 오류 및 해결

### 오류 1: `ModuleNotFoundError: No module named 'pandas'`

**해결**:
```bash
pip install pandas
```

### 오류 2: `gemini: command not found`

**원인**: Gemini CLI가 설치되지 않음

**해결**:
```bash
npm install -g @google/generative-ai-cli

# 또는 npx 사용 (설치 없이)
# python 스크립트 수정 필요
```

### 오류 3: `GEMINI_API_KEY not found`

**해결**:
```bash
# PowerShell에서
$env:GEMINI_API_KEY="your-api-key"

# 확인
echo $env:GEMINI_API_KEY
```

### 오류 4: `JSONDecodeError`

**원인**: Gemini가 JSON이 아닌 텍스트 반환

**임시 해결**:
1. 프롬프트 파일 확인: `prompts/extract_*.md`
2. API 키 quota 확인
3. 나중에 다시 시도

### 오류 5: 파일명 한글 인코딩 오류

**해결**:
```python
# pdf_to_data.py 수정 필요 시
# UTF-8 인코딩 명시
```

---

## ✅ 성공 기준

1. **4개 CSV 파일 생성됨**
2. **각 CSV에 데이터가 있음** (헤더만 있지 않음)
3. **분양가 데이터 예시**:
   - 단지명, 동, 호, 타입, 최저층, 최고층, 분양가
   - 최소 50건 이상 추출됨
4. **옵션 데이터 예시**:
   - 발코니 확장, 시스템에어컨 등 포함
   - 최소 10건 이상
5. **일정 데이터**:
   - 청약 일정, 납부 일정 포함
   - 최소 10건 이상

---

## 🔍 데이터 검증 방법

### 1. 엑셀에서 열어보기

```bash
# 분양가 파일 열기
start excel "d:\Flow System\...\아산모종서한이다음노블리스_분양가.csv"
```

### 2. 수동 비교

1. **원본 PDF 열기**
2. **추출된 CSV 열기**
3. **샘플 데이터 3-5건 비교**:
   - 분양가 금액 일치?
   - 동-호 정보 정확?
   - 옵션 금액 정확?

### 3. Google Sheets 업로드 (다음 단계)

```python
# 추후 구현 예정
from src.sheets.writer import SheetsWriter

writer = SheetsWriter()
writer.upload_csv("아산모종서한이다음노블리스_분양가.csv", "분양가")
```

---

## 📝 테스트 후 기록

### 테스트 결과 체크리스트

- [ ] Gemini API 키 설정 완료
- [ ] Python 스크립트 실행 성공
- [ ] 4개 CSV 파일 생성됨
- [ ] 분양가 데이터 정확성 확인
- [ ] 옵션 데이터 정확성 확인
- [ ] 일정 데이터 정확성 확인
- [ ] 타입 데이터 정확성 확인

### 발견된 문제점

```
문제 1:
- 증상:
- 원인:
- 해결 방법:

문제 2:
- 증상:
- 원인:
- 해결 방법:
```

### 개선 아이디어

```
1. 프롬프트 개선이 필요한 부분:

2. 스크립트 수정이 필요한 부분:

3. 추가 기능 아이디어:
```

---

## 🎯 다음 단계

테스트 성공 후:

1. **다른 PDF 테스트** (힐스테이트두정역, 천안신부더샵센트라)
2. **일괄 처리 테스트** (`batch_process_pdfs.bat`)
3. **Google Sheets 자동 업로드 구현**
4. **웹 인터페이스 개발** (Streamlit)

---

## 📞 도움이 필요한 경우

1. **프로젝트 허브**에 문제 기록
2. **Obsidian 노트**로 해결 과정 문서화
3. **Claude Code**에게 다시 질문

---

**준비되셨나요? 위의 명령어를 실행해보세요!** 🚀

**작성일**: 2025-10-05
**버전**: 1.0
