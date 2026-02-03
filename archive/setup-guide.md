# 🛠️ 설치 및 설정 가이드

아파트 매물관리 자동화 시스템을 처음부터 설치하고 설정하는 방법을 단계별로 설명합니다.

## 📋 사전 준비사항

- **Python 3.10+** 설치
- **Google 계정** (Gmail 권장)
- **Chrome 브라우저** (웹 크롤링용)
- **Git** 설치

## 🚀 1단계: 프로젝트 클론 및 환경 설정

### 1.1 저장소 클론

```bash
# GitHub에서 클론
git clone https://github.com/cao25/apartment-automation.git
cd apartment-automation

# 또는 로컬에서 복사
cp -r "원본경로" "D:/Projects/apartment-automation"
cd apartment-automation
```

### 1.2 Python 가상환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 1.3 개발 도구 설치 (선택사항)

```bash
# 코드 포맷팅 및 린팅
pip install black flake8 mypy pre-commit

# 테스트 프레임워크
pip install pytest pytest-cov
```

## 🔐 2단계: Google API 설정

### 2.1 Google Cloud Console 설정

1. **[Google Cloud Console](https://console.cloud.google.com/)** 접속
2. **새 프로젝트 생성**:
   - 프로젝트명: `apartment-automation-2025`
   - 지역: `asia-northeast1 (도쿄)`

3. **API 활성화**:
   - 검색창에서 "Google Sheets API" 검색 → 활성화
   - 다시 "Google Drive API" 검색 → 활성화

### 2.2 서비스 계정 생성

1. **좌측 메뉴**: `IAM 및 관리` → `서비스 계정`
2. **서비스 계정 생성** 클릭:
   - 이름: `apartment-automation-service`
   - 설명: `매물관리 시스템용 서비스 계정`
   - 체크박스 선택 후 계속

3. **역할 부여**:
   - `Google Sheets 및 Drive 관리자` 또는 `편집자` 권한 부여

### 2.3 인증 키 생성

1. 생성된 서비스 계정 클릭
2. **키** 탭 → **키 추가** → **새 키 만들기**
3. **JSON** 선택 → 키 파일 다운로드
4. 다운로드받은 파일을 `apartment-automation/config/credentials.json`으로 이동

## 📊 3단계: Google Sheets 설정

### 3.1 새 스프레드시트 생성

1. **[Google Sheets](https://sheets.google.com/)** 접속
2. **새 스프레드시트** 생성: `아파트 매물 DB - 자동화`
3. **공유 설정**:
   - 생성한 서비스 계정 이메일 추가 (편집자 권한)
   - 서비스 계정 이메일 형식: `apartment-automation-service@프로젝트ID.iam.gserviceaccount.com`

### 3.2 시트 구조 생성

다음 시트들을 생성합니다:

1. **등록검색** - 매물 등록/검색 인터페이스
2. **매물DB** - 매물 정보 저장소
3. **고객DB** - 고객 정보 저장소
4. **아파트단지** - 단지 마스터 데이터
5. **고정값** - 드롭다운 옵션 목록
6. **대시보드** - 분석 및 시각화

구체적인 시트 구조는 [시트 구조 가이드](sheet-structure.md)를 참조하세요.

### 3.3 스프레드시트 ID 확인

URL에서 스프레드시트 ID를 확인합니다:
```
https://docs.google.com/spreadsheets/d/1ABC_DEF_실제ID_HERE/edit#gid=0
```

`1ABC_DEF_실제ID_HERE` 부분을 복사하여 환경 변수에 설정합니다.

## ⚙️ 4단계: 환경 변수 설정

### 4.1 환경 변수 파일 생성

```bash
# 환경 변수 템플릿 복사
cp env.example .env

# .env 파일 편집
notepad .env  # Windows
vim .env      # Linux/Mac
```

### 4.2 필수 변수 설정

```env
# Google Sheets 설정
GOOGLE_SHEETS_ID=실제_스프레드시트_ID_여기에_입력
GOOGLE_CREDENTIALS_FILE=config/credentials.json

# API 키 설정 (다음 단계에서 설정)
GEMINI_API_KEY=your_gemini_api_key_here
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here

# 사용자 정보
USER_NAME=cao25
USER_EMAIL=your_email@example.com
```

### 4.3 Google Drive 폴더 설정

1. Google Drive에서 **새 폴더** 생성: `매물관리 시스템`
2. 폴더 URL에서 폴더 ID 확인:
   ```
   https://drive.google.com/drive/folders/폴더ID여기에있다
   ```
3. `.env` 파일에 추가:
   ```env
   GOOGLE_DRIVE_PARENT_FOLDER_ID=폴더ID여기에있다
   ```

## 🤖 5단계: Apps Script 설정

### 5.1 스크립트 에디터 열기

1. 설정한 Google Sheets에서 **확장프그램** → **Apps Script** 클릭
2. 새 프로젝트 생성 확인

### 5.2 메인 스크립트 복사

`apps-script/통합_최종_스크립트.js` 파일의 내용을 전체 복사하여 에디터에 붙여넣기 합니다.

### 5.3 권한 승인

1. **저장** (Ctrl+S) 클릭
2. 함수명을 `registerPropertyAndClient`로 설정
3. **실행** 버튼 클릭
4. **권한 검토** → **계정 선택** → **고급** → **apartment-automation으로 이동(안전하지 않음)** → **허용**

### 5.4 트리거 설정

```javascript
// Apps Script 에디터에서 다음 함수 실행
function setupTriggers() {
  // 기존 트리거 삭제
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'generateDailyBriefing') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // 매일 오전 9시 트리거 설정
  ScriptApp.newTrigger('generateDailyBriefing')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
    
  Logger.log('일일 브리핑 트리거 설정 완료');
}

// 실행 후 권한 다시 승인 확인
```

## 🔧 6단계: 초기 데이터 준비

### 6.1 단지 마스터 데이터 입력

**아파트단지** 시트에 다음 데이터 입력:

| A열 단지명 | B열 도로명주소 | C열 지번주소 | D열 세대수 | E열 단지명축약 |
|------------|----------------|--------------|------------|----------------|
| 힐스테이트두정역 | 천안시 서북구 두정동 1234 | 두정동 1234 | 1500 | 힐두정 |
| 천안아이파크시티 | 천안시 서북구 두정동 5678 | 두정동 5678 | 1200 | 천아이파 |

### 6.2 드롭다운 옵션 설정

**고정값** 시트에 옵션 목록 생성:

1. **거래유형**: 매매, 전세, 월세
2. **거래상태**: 접수, 계약가능, 계약완료, 보류
3. **거래카테고리**: 매도인, 손님

```javascript
// Apps Script에서 드롭다운 설정 함수 실행
function setupDataValidation() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const fixedSourceSheet = ss.getSheetByName('고정값');
  const regSheet = ss.getSheetByName('등록검색');
  
  // 거래유형 드롭다운
  const range1 = regSheet.getRange('C11'); // 거래유형 셀
  range1.setDataValidation(
    SpreadsheetApp.newDataValidation()
      .requireValueInRange(fixedSourceSheet.getRange('A2:A4'))
      .build()
  );
  
  Logger.log('데이터 검증 설정 완료');
}
```

## ✅ 7단계: 연결 테스트

### 7.1 Python 연결 테스트

```bash
# 가상환경 활성화 후
cd apartment-automation
python -c "from src.config.settings import Settings; Settings().print_config()"
```

성공적으로 실행되면 설정 정보가 출력됩니다.

### 7.2 Google Sheets 연결 테스트

```python
# Python 셸에서 실행
python
>>> from src.sheets.writer import SheetsWriter
>>> from src.config.settings import Settings
>>> settings = Settings()
>>> writer = SheetsWriter(settings)
>>> info = writer.get_sheet_info()
>>> print(info)
```

### 7.3 Apps Script 테스트

1. Google Sheets에서 **테스트 데이터** 입력:
   - 단지명: 힐스테이트두정역
   - 동: 101
   - 호: 1401
   - 타입: 3BR/2BA
   - 거래유형: 매매
   - 거래상태: 접수
   - 성: 홍
   - 연락처: 010-1234-5678

2. **매물 등록** 메뉴에서 **매물 등록** 클릭
3. 성공적으로 등록되는지 확인

## 🚨 문제 해결

### 인증 오류

```
AuthenticationError: Invalid credentials
```

**해결방법**:
1. `credentials.json` 파일 경결 확인
2. 서비스 계정 이메일로 스프레드시트 공유 확인
3. API 활성화 상태 확인

### 권한 오류

```
PermissionError: The caller does not have permission
```

**해결방법**:
1. Google Cloud Console에서 서비스 계정 권한 확인
2. 스프레드시트 공유 설정 확인
3. Apps Script 권한 재승인

### 인코딩 오류

```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**해결방법**:
1. CSV 파일의 인코딩 확인 (`cp949`, `euc-kr`)
2. `src/collectors/csv_importer.py`의 인코딩 순서 조정

## 📞 지원

문제가 해결되지 않으면 다음 방법으로 지원을 요청하세요:

1. **GitHub Issues**: 버그 리포트 또는 기능 요청
2. **이메일**: cao25@example.com
3. **문서**: [Wiki](../wiki) 페이지 참조

---

**🎉 설정이 완료되면 매물관리 자동화의 혜택을 누리실 수 있습니다!**
