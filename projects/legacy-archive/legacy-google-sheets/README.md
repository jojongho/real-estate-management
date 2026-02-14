# 📦 Google Sheets 레거시 코드

> **상태**: 아카이브됨 (2025-11-28)
> **사유**: Excel 백엔드로 전환
> **유지 이유**: 필요 시 복구 가능하도록 보존

---

## 📋 개요

이 디렉토리는 기존 Google Sheets API 연동 코드를 보관합니다.
프로젝트가 **로컬 Excel(OneDrive) 기반**으로 전환되면서 더 이상 기본 백엔드로 사용되지 않습니다.

### 전환 배경
- ✅ **AppSheet ↔ Excel 연동**: Google Sheets 없이도 AppSheet 사용 가능
- ✅ **로컬 파일 관리**: OneDrive 자동 동기화로 충분
- ✅ **성능 개선**: API 호출 오버헤드 제거
- ✅ **단순화**: 인증 복잡도 감소

---

## 🗂️ 디렉토리 구조

```
legacy/google-sheets/
├── sheets/                     # Google Sheets API 연동 모듈
│   ├── oauth_auth.py          # OAuth 인증
│   ├── reader.py              # 시트 읽기
│   └── writer.py              # 시트 쓰기
├── scripts/                    # 유틸리티 스크립트
│   ├── check_reference_sheet.py
│   ├── reauthenticate_google_sheets.py
│   └── test_oauth_auth.py
└── README.md                   # 이 문서
```

---

## 🔧 복구 방법 (필요 시)

### 1. 환경 변수 설정
```bash
# .env 파일 수정
EXCEL_BACKEND=sheets  # excel → sheets로 변경
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_CREDENTIALS_FILE=config/credentials.json
```

### 2. 의존성 설치
```bash
pip install gspread google-auth google-auth-oauthlib google-auth-httplib2
```

### 3. 코드 경로 수정
```python
# 기존 import 경로
from src.sheets.reader import SheetsReader
from src.sheets.writer import SheetsWriter

# 레거시 경로로 변경
from legacy.google_sheets.sheets.reader import SheetsReader
from legacy.google_sheets.sheets.writer import SheetsWriter
```

### 4. 인증 설정
```bash
# Google Cloud Console에서 서비스 계정 생성
# credentials.json 다운로드 후 config/ 디렉토리에 저장

python legacy/google-sheets/scripts/reauthenticate_google_sheets.py
```

---

## 📚 주요 모듈 설명

### 1. **oauth_auth.py**
- Google OAuth 2.0 인증 처리
- 서비스 계정 및 사용자 인증 지원
- 토큰 갱신 자동 처리

### 2. **reader.py**
- Google Sheets에서 데이터 읽기
- DataFrame 변환 기능
- 범위 지정 읽기 지원

### 3. **writer.py**
- Google Sheets에 데이터 쓰기
- DataFrame → Sheets 자동 변환
- 배치 업데이트 지원

---

## ⚠️ 주의사항

### 사용하지 말아야 할 이유
1. **중복 관리**: Excel과 Sheets 동시 관리는 데이터 불일치 유발
2. **복잡성 증가**: 인증, API 할당량, 오류 처리
3. **성능 저하**: API 호출 지연 시간
4. **유지보수 부담**: 두 개의 백엔드 유지 필요

### 사용해도 되는 경우
- 기존 Google Sheets 워크플로우가 필수적인 경우
- Google Workspace 생태계와의 깊은 통합이 필요한 경우
- 실시간 협업 기능이 반드시 필요한 경우

---

## 🔗 관련 문서

- [Excel 백엔드 가이드](../../CLAUDE.md)
- [프로젝트 구조](../../docs/project-structure.md)
- [Google Sheets API 공식 문서](https://developers.google.com/sheets/api)

---

## 📞 문의

이 레거시 코드에 대한 문의사항은 프로젝트 이슈로 등록해주세요.

**⚠️ 이 코드는 더 이상 유지보수되지 않습니다.**
**새로운 기능은 Excel 백엔드 기반으로 개발해주세요.**
