# 🏠 Real Estate Management System - Project Context

> **프로젝트 개요**: 아파트 매물관리 자동화 시스템 (Excel 기반)
> **최종 업데이트**: 2025-11-27
> **백엔드**: 로컬 Excel (OneDrive) + AppSheet 연동

> **워크스페이스 분리 업데이트**: 2026-02-14  
> 루트 단일 프로젝트 구조에서 멀티 프로젝트 구조로 분리됨.
> - `projects/property-management-core`
> - `projects/building-ledger-automation`
> - `projects/apartment-notice-normalization`
> - `projects/legacy-archive`

---

## 📊 프로젝트 현황

### 주요 변경 사항
- ✅ **Google Sheets → Excel 전환 완료** (2025-11-27)
- ✅ 기본 백엔드: 로컬 Excel 파일 (단일 파일로 통합)
- ✅ **Excel 파일 통합 완료** (2025-11-28)
  - 기존 3개 파일 → 1개 통합 파일: `D:\OneDrive\00. 부동산업무\01. 매물관리\매물관리.xlsx`
  - AppSheet 마이그레이션 완료 (Excel 단일 파일 연동)
  - 데이터 한도 여유 확보 (Excel > Google Sheets)
- ✅ `src/excel_handler.py` 신규 구현 (pandas + openpyxl)
- ✅ **Google Sheets 레거시 아카이브 완료** (2025-11-28)
  - `src/sheets/` → `legacy/google-sheets/sheets/` 이동
  - Google Sheets 관련 스크립트 → `legacy/google-sheets/scripts/` 이동
  - `src/main.py`, `src/integration/unified_db.py` Excel 백엔드로 수정

### 현재 기술 스택
```yaml
Backend: Local Excel (OneDrive 동기화)
Primary: Excel → AppSheet → Python
Legacy: Google Sheets API (비활성)
Libraries:
  - pandas: Excel 데이터 처리
  - openpyxl: Excel 파일 읽기/쓰기
  - xlrd/xlsxwriter: 호환성 지원
```

---

## 🗂️ 프로젝트 구조

### 디렉토리 구조 요약
```
real-estate-management/
├── src/
│   ├── excel_handler.py          # ✨ 신규: Excel 통합 핸들러
│   ├── collectors/                # 데이터 수집 (CSV, PDF, 웹)
│   ├── processors/                # 데이터 정규화/검증 (미구현)
│   ├── generators/                # 콘텐츠 생성 (미구현)
│   ├── integration/               # 통합 DB 모듈 (Excel 백엔드)
│   ├── config/                    # 설정 관리
│   └── main.py                    # 메인 엔트리포인트
├── legacy/
│   ├── google-sheets/             # 🗄️ 아카이브: Google Sheets 연동
│   │   ├── sheets/                # reader.py, writer.py, oauth_auth.py
│   │   ├── scripts/               # Google Sheets 유틸리티
│   │   └── README.md              # 복구 가이드
│   └── pdf-normalization/         # 구버전 PDF 정규화 코드
├── apps-script/                   # Google Apps Script (옵션)
├── scripts/                       # 유틸리티 스크립트
├── docs/                          # AppSheet, WordPress 가이드
├── prompts/                       # Gemini CLI 프롬프트
└── config/                        # credentials.json, settings
```

### 핵심 파일

#### 1. **src/excel_handler.py** (신규 핵심 모듈)
```python
class ExcelHandler:
    - read_sheet(sheet_name) → DataFrame
    - write_data(sheet_name, data)
    - sheet_exists(sheet_name) → bool
    - get_all_sheet_names() → List[str]
    - _auto_resize_columns() → 열 너비 자동 조정
```

**사용 예시**:
```python
from src.excel_handler import ExcelHandler

handler = ExcelHandler("path/to/매물관리.xlsx")
df = handler.read_sheet("매물DB")
handler.write_data("고객DB", customer_df)
```

#### 2. **src/config/settings.py** (설정 중앙 관리)
```python
class Settings:
    excel: ExcelConfig
        - file_path: Excel 파일 경로 (환경 변수: EXCEL_FILE_PATH)
        - backend: "excel" | "sheets" (환경 변수: EXCEL_BACKEND)

    google_sheets: GoogleSheetsConfig (레거시)
    api: APIConfig (Gemini, Naver, MOLIT)
    database: DatabaseConfig (시트명 매핑)
```

**환경 변수 예시** (`.env`):
```bash
EXCEL_BACKEND=excel
EXCEL_FILE_PATH=D:/OneDrive/00. 부동산업무/01. 매물관리/매물관리.xlsx
GEMINI_API_KEY=your_api_key_here
```

---

## 📋 데이터베이스 시트 구조

### Excel 통합 파일 정보
- **파일명**: `매물관리.xlsx` (단일 통합 파일)
- **경로**: `D:\OneDrive\00. 부동산업무\01. 매물관리\매물관리.xlsx`
- **이전**: 기존 3개 분산 파일 → 1개 통합 파일
- **장점**: Excel 데이터 한도 여유, 관리 단순화, AppSheet 단일 연결

### Excel 시트 구성
| 시트명 | 역할 | 주요 컬럼 | 비고 |
|--------|------|-----------|------|
| **등록검색** | 사용자 입력 폼 | 단지명, 거래유형, 고객명 등 | AppSheet 폼 연동 |
| **매물DB** | 매물 마스터 데이터 | 매물ID, 주소, 가격, 상태 | 통합 파일 내 |
| **고객DB** | 고객 CRM 데이터 | 고객ID, 연락처, 상담이력 | 통합 파일 내 |
| **아파트단지** | 단지 마스터 데이터 | 단지명, 주소, 세대수 | 8개 단지 |
| **고정값** | 드롭다운 참조 데이터 | 거래유형, 상태, 카테고리 | 고정값 관리 |
| **대시보드** | 피벗/차트/분석 | 실시간 통계 시각화 | Excel 수식 기반 |
| **통합DB** | 매물+고객 통합뷰 | 자동 생성 | Python 자동 구성 |

### 데이터 흐름
```
AppSheet 폼 입력
    ↓
OneDrive Excel (자동 동기화)
    ↓
Python 처리 (excel_handler.py)
    ↓
분석/콘텐츠 생성 (향후 구현)
```

---

## 🔧 개발 가이드

### 1. 환경 설정
```bash
# Python 가상환경 생성 (Windows)
python -m venv venv
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env.example .env
# .env 파일에서 EXCEL_FILE_PATH 경로 확인/수정
```

### 2. Excel 백엔드 사용 패턴
```python
from src.config.settings import Settings
from src.excel_handler import ExcelHandler

# 설정 로드
settings = Settings()
print(settings.excel.backend)  # "excel"
print(settings.excel.file_path)

# Excel 핸들러 사용
handler = ExcelHandler(settings.excel.file_path)

# 데이터 읽기
properties_df = handler.read_sheet("매물DB")
customers_df = handler.read_sheet("고객DB")

# 데이터 쓰기
handler.write_data("새시트", processed_df)

# 시트 존재 확인
if handler.sheet_exists("통합DB"):
    print("통합DB 시트 존재")
```

### 3. 레거시 Google Sheets 사용 (복구 필요 시)
```python
# ⚠️ 레거시 코드 복구 방법은 legacy/google-sheets/README.md 참조

# .env 설정 변경
EXCEL_BACKEND=sheets
GOOGLE_SHEETS_ID=your_spreadsheet_id

# import 경로 수정 필요
from legacy.google_sheets.sheets.reader import SheetsReader
reader = SheetsReader()
data = reader.read_sheet("매물DB")
```

**⚠️ 주의**: Google Sheets 백엔드는 더 이상 유지보수되지 않습니다.
Excel과 Sheets를 동시에 사용하면 데이터 불일치가 발생할 수 있습니다.

---

## 📝 주요 작업 체크리스트

### 완료된 작업 ✅
- [x] Google Sheets → Excel 전환 결정
- [x] `excel_handler.py` 구현 (pandas + openpyxl)
- [x] `settings.py`에 Excel 백엔드 설정 추가
- [x] README.md 업데이트 (Excel 기반으로)
- [x] requirements.txt 업데이트 (Excel 라이브러리)
- [x] **Excel 파일 통합** (2025-11-28)
  - [x] 기존 3개 분산 파일 → 1개 통합 파일
  - [x] `매물관리.xlsx` 단일 파일 생성
  - [x] AppSheet 마이그레이션 (Excel 통합 파일 연동)
- [x] **Google Sheets 코드 레거시 아카이브** (2025-11-28)
  - [x] `src/sheets/` → `legacy/google-sheets/sheets/` 이동
  - [x] Google Sheets 스크립트 → `legacy/google-sheets/scripts/` 이동
  - [x] `src/main.py` Excel 백엔드로 수정
  - [x] `src/integration/unified_db.py` Excel 백엔드로 수정
  - [x] `legacy/google-sheets/README.md` 작성 (복구 가이드)

### 진행 중 🔄
- [ ] Excel 통합 파일 읽기/쓰기 테스트
- [ ] Excel 기반 데이터 수집 워크플로우 검증
- [ ] unified_db.py 동작 확인

### 향후 작업 📅
- [ ] `collectors/` 모듈 Excel 백엔드 대응
- [ ] `processors/` 데이터 정규화 로직 구현
- [ ] `generators/` 콘텐츠 자동 생성 구현
- [ ] PDF 데이터 추출 → Excel 자동 저장
- [ ] Gemini API 연동 콘텐츠 생성
- [ ] 일일 브리핑 자동화

---

## 🛠️ 의존성 관리

### 핵심 라이브러리
```txt
# Excel 처리
pandas>=1.5.0,<2.1.0
openpyxl>=3.0.0
xlrd>=2.0.0
xlsxwriter>=3.0.0

# 데이터 수집
pdfplumber>=0.7.0
playwright>=1.30.0
selenium>=4.10.0
requests>=2.28.0

# AI/콘텐츠 생성
google-generativeai>=0.3.0

# 유틸리티
python-dotenv>=0.19.0
pyyaml>=6.0.0
loguru>=0.6.0
```

### 개발 도구
```bash
pytest>=7.0.0        # 테스트
black>=22.0.0        # 코드 포맷팅
flake8>=5.0.0        # 린팅
mypy>=1.0.0          # 타입 체크
```

---

## 📚 문서 참조

### 핵심 문서
- [AGENTS.md](AGENTS.md) - 이 문서 (프로젝트 컨텍스트)
- [README.md](README.md) - 프로젝트 소개 (Excel 기반)
- [legacy/google-sheets/README.md](legacy/google-sheets/README.md) - Google Sheets 복구 가이드

### AppSheet 관련
- [AppSheet_고정값_드롭다운_설정.md](docs/AppSheet_고정값_드롭다운_설정.md)
- [AppSheet_매물고객_통합입력_워크플로우.md](docs/AppSheet_매물고객_통합입력_워크플로우.md)
- [appsheet_설정_요약.md](docs/appsheet_설정_요약.md)

### 데이터 처리
- [PDF 데이터 자동 추출 가이드.md](docs/📚%20PDF%20데이터%20자동%20추출%20가이드.md)
- [PDF 데이터 정규화 통합 전략.md](docs/💡%20PDF%20데이터%20정규화%20통합%20전략.md)
- [시트 구조 분석 보고서.md](docs/시트%20구조%20분석%20보고서.md)

### 워크플로우
- [통합 마스터플랜.md](docs/📋%20통합%20마스터플랜%20-%20기존%20시스템%20개선%20+%20확장.md)
- [project-structure.md](docs/project-structure.md)

---

## 🔍 문제 해결

### Excel 파일 경로 오류
```python
# 문제: FileNotFoundError
# 해결: .env 파일에서 절대 경로 확인
EXCEL_FILE_PATH=D:/OneDrive/00. 부동산업무/01. 매물관리/매물관리.xlsx
```

### 시트명 한글 깨짐
```python
# excel_handler.py는 UTF-8 인코딩 자동 처리
# 문제 발생 시 파일 재저장 (Excel → xlsx)
```

### openpyxl 버전 호환성
```python
# pandas 1.4.0 이상 필요 (if_sheet_exists='replace')
# 구버전: 수동 시트 삭제 후 재작성 (코드에 포함됨)
```

---

## 🎯 개발 우선순위

### Phase 1: Excel 백엔드 안정화 (현재)
1. Excel 읽기/쓰기 기본 동작 검증
2. AppSheet ↔ Excel 동기화 테스트
3. 기존 데이터 마이그레이션 (Google Sheets → Excel)

### Phase 2: 데이터 수집 자동화
1. PDF 파싱 → Excel 자동 저장
2. CSV 데이터 → Excel 통합
3. 웹 크롤링 → Excel 업데이트

### Phase 3: 콘텐츠 자동 생성
1. Gemini API 연동
2. 일일 브리핑 자동화
3. 마케팅 문구 생성

### Phase 4: 분석 및 대시보드
1. Excel 피벗 테이블 자동화
2. 차트 생성
3. 실시간 KPI 모니터링

---

## 🔗 외부 연동

### AppSheet
- **연동 방식**: OneDrive Excel 파일 직접 연결
- **동기화**: 자동 (OneDrive 클라우드 동기화)
- **폼**: 매물 등록, 고객 정보 입력

### WordPress (향후)
- **목적**: 고객용 매물 접수 폼
- **연동**: AppSheet → Excel → WordPress 플러그인

### Gemini API
- **용도**: 콘텐츠 자동 생성
- **API 키**: 환경 변수 `GEMINI_API_KEY`
- **프롬프트**: `prompts/` 디렉토리 관리

---

## 💡 코딩 컨벤션

### Python 스타일
```python
# Black 포맷터 사용
black src/ tests/

# 타입 힌팅 권장
def read_sheet(sheet_name: str) -> Optional[pd.DataFrame]:
    pass

# Docstring (Google Style)
"""
함수 설명.

Args:
    sheet_name (str): 시트 이름

Returns:
    Optional[pd.DataFrame]: 데이터프레임 또는 None
"""
```

### 파일명 규칙
- Python: `snake_case.py`
- Markdown: `PascalCase.md` 또는 `kebab-case.md`
- 한글 허용: `매물관리.xlsx`, `시트_구조_분석.md`

### Git 커밋 메시지
```bash
feat: 새로운 기능 추가
fix: 버그 수정
refactor: 코드 리팩토링
docs: 문서 업데이트
test: 테스트 추가/수정
```

---

## 📞 참고 정보

### 개발자
- **GitHub**: cao25
- **프로젝트**: https://github.com/cao25/real-estate-management

### 라이선스
- MIT License

### 프로젝트 버전
- **v1.0.0**: Excel 기반 초기 전환 완료

---

**💡 이 문서는 Codex가 프로젝트 컨텍스트를 이해하고 효율적으로 작업하기 위한 참조 문서입니다.**
**프로젝트 변경 시 이 문서를 함께 업데이트해주세요.**
