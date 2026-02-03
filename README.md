# 🏠 아파트 매물관리 자동화 시스템

> 로컬 Excel(OneDrive) 기반 매물관리 및 자동 데이터 수집/분석 시스템  
> *기존 Google Sheets 플로우는 비활성화하고 Excel을 기본 백엔드로 사용합니다.*

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Excel](https://img.shields.io/badge/Excel-217346?logo=microsoft-excel&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Development-yellow.svg)

## 📋 프로젝트 개요

부동산 중개업무의 핵심인 매물 관리를 OneDrive에 저장된 로컬 Excel + AppSheet + Python으로 자동화하는 시스템입니다.

### 🎯 주요 목표

- **기존 시스템 개선**: 데이터 품질 70% → 95%
- **자동화 확장**: 데이터 수집 → 분석 → 콘텐츠 발행  
- **생산성 향상**: 수동 작업 90% 감소

### 💡 핵심 기능

- 📊 **로컬 Excel 중앙 관리**: 매물/고객 DB를 OneDrive 경로에 저장해 AppSheet와 동기화
- 🤖 **Apps Script 자동화**: 매물 등록/수정/검증 자동화 (필요 시)
- 📥 **데이터 자동 수집**: CSV/PDF/웹 크롤링/API 연동
- 📝 **콘텐츠 자동 생성**: 일일 브리핑, 마케팅 문구 생성
- 📈 **분석 및 대시보드**: 실시간 매물 현황 시각화

## 🗂️ 프로젝트 구조

```
apartment-automation/
├── src/                          # Python 소스 코드
│   ├── collectors/              # 데이터 수집
│   │   ├── csv_importer.py     # CSV 파일 가져오기
│   │   ├── pdf_parser.py       # PDF 파싱
│   │   ├── naver_crawler.py    # 네이버 부동산 크롤링
│   │   └── api_client.py       # 실거래가 API
│   ├── processors/              # 데이터 처리
│   │   ├── normalizer.py       # 데이터 정규화
│   │   └── validator.py        # 데이터 검증
│   ├── generators/              # 콘텐츠 생성
│   │   ├── briefing.py         # 일일 브리핑
│   │   ├── marketing.py        # 마케팅 콘텐츠
│   │   └── instagram.py        # 인스타그램 이미지
│   ├── sheets/                  # Google Sheets 연동 (현재는 Excel 백엔드로 전환 예정)
│   │   ├── writer.py           # 데이터 쓰기
│   │   └── reader.py           # 데이터 읽기
│   ├── config/                  # 설정 관리
│   │   └── settings.py         # 시스템 설정
│   └── main.py                  # 메인 엔트리 포인트
├── apps-script/                  # Google Apps Script
│   ├── 통합_최종_스크립트.js      # 메인 스크립트
│   └── triggers.gs             # 트리거 설정
├── workflows/                   # n8n 워크플로우
│   ├── n8n-workflow-read-sheets.json
│   └── n8n-workflow-read-normalized-sheets.json
├── data/                       # 데이터 저장소
│   ├── raw/                    # 원본 CSV/PDF 파일
│   └── processed/              # 처리된 데이터
├── config/                     # 설정 파일
│   ├── settings.yaml           # 시스템 설정
│   └── credentials.json        # Google 인증 파일
├── tests/                      # 테스트 코드
├── docs/                       # 문서
├── logs/                       # 로그 파일
├── .gitignore                  # Git 무시 파일
├── requirements.txt            # Python 의존성
├── package.json               # Node.js 의존성 (기록용)
└── README.md                   # 프로젝트 문서
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/cao25/apartment-automation.git
cd apartment-automation

# Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 로컬 Excel 백엔드 지정 (기본)

1. **Excel 통합 파일 확인**
   - **파일명**: `매물관리.xlsx` (단일 통합 파일)
   - **경로**: `D:\OneDrive\00. 부동산업무\01. 매물관리\매물관리.xlsx`
   - **구성**: 기존 3개 분산 파일을 1개로 통합 완료

2. **환경 변수 설정**
   ```bash
   cp env.example .env
   # .env에서 다음 값 확인:
   # EXCEL_BACKEND=excel
   # EXCEL_FILE_PATH=D:/OneDrive/00. 부동산업무/01. 매물관리/매물관리.xlsx
   ```

### 3. (옵션) Google Sheets 설정

더 이상 기본으로 사용하지 않지만, 필요 시 서비스 계정 키를 `config/credentials.json`에 두고 `GOOGLE_SHEETS_ID`를 설정하면 Sheets 백엔드로도 전환할 수 있습니다.

### 4. Apps Script 설정 (옵션)

기존 Google Sheets 자동화가 필요할 때만 `apps-script/통합_최종_스크립트.js`를 사용해 트리거를 구성합니다.

### 5. 실행

```bash
# 개발 모드 실행
python src/main.py

# 트리거 설정 (Apps Script)
# Apps Script 에디터에서 setupTriggers() 함수 실행
```

## 📊 시트 구조

### 주요 시트 구성

| 시트명 | 역할 | 주요 데이터 |
|--------|------|------------|
| **등록검색** | 사용자 인터페이스 | 매물 등록/검색 폼 |
| **매물DB** | 핵심 데이터베이스 | 매물 상세 정보 (61개 레코드) |
| **고객DB** | CRM 시스템 | 고객 정보 및 상담이력 (25명) |
| **아파트단지** | 마스터 데이터 | 단지 정보 (8개 단지) |
| **고정값** | 참조 데이터 | 드롭다운 옵션 목록 |
| **대시보드** | 분석 및 시각화 | 피벗 테이블 및 차트 |

### 데이터 흐름

```
AppSheet 폼 → OneDrive Excel (매물/고객 DB)
             ↓
        Python 처리 (CSV/PDF/분석)
             ↓
        자동 브리핑/콘텐츠 생성
```

## 🔧 기능별 가이드

### 📝 매물 등록 자동화

1. **등록검색** 시트에서 필수 정보 입력
2. **오른쪽 위 버튼** 클릭으로 자동 등록
3. **검증**: 필수 필드 자동 체크
4. **생성**: 매물ID/고객ID 자동 생성
5. **폴더**: Google Drive 자동 폴더 생성

### 📥 데이터 수집 자동화

```python
# CSV 파일 일괄 처리
python -c "from src.collectors.csv_importer import CSVImporter; CSVImporter().process_all_csv_files()"

# PDF 파싱
python -c "from src.collectors.pdf_parser import PDFParser; PDFParser().process_apartment_notices()"

# 네이버 부동산 크롤링
python -c "from src.collectors.naver_crawler import NaverCrawler; NaverCrawler().fetch_new_listings()"
```

### 📊 일일 브리핑 자동 생성

- **트리거**: 매일 오전 9시 자동 실행
- **내용**: 신규 매물 현황, 계약 가능 매물 수
- **출력**: Google Docs 자동 생성 + 이메일 발송

### 🎨 마케팅 콘텐츠 생성

- **Gemini API** 연동으로 매물별 마케팅 문구 생성
- **Instagram 이미지** 자동 생성
- **해시태그** 자동 추천

## 🛠️ 개발 가이드

### 개발 환경 설정

```bash
# 개발 도구 설치
pip install pytest black flake8 mypy pre-commit

# 코드 포맷팅
black src/ tests/

# 린팅
flake8 src/

# 타입 체크
mypy src/

# 테스트 실행
pytest tests/
```

### Apps Script 개발

1. **시트 연동**: `gspread` 라이브러리 활용
2. **트리거 관리**: 시간 기반 통보 함수
3. **오류 처리**: try-catch 패턴 적용
4. **로깅**: Logger.log() 활용

### 데이터 모델링

- **매물DB**: 정규화된 관계형 구조
- **고객DB**: CRM 기능 확장 가능
- **단지DB**: 마스터 데이터 참조

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest

# 특정 모듈 테스트
pytest tests/test_csv_importer.py

# 커버리지 포함 테스트
pytest --cov=src --cov-report=html
```

## 📈 성과 지표

### Phase 1 목표 (안정화)

- ✅ 데이터 품질 95% 이상
- ✅ 매물ID 자동 생성률 100%
- ✅ 필수 필드 입력률 100%

### 최종 목표

- 🎯 데이터 입력 시간 90% 단축
- 🎯 데이터 정확도 99% 이상  
- 🎯 콘텐츠 발행 100% 자동화
- 🎯 월 매출 30% 증가

## 🔒 보안 고찰

- **개인정보**: 고객 연락처 암호화 저장
- **API 키**: 환경 변수로 관리, Git 추적 방지
- **접근 권한**: Google 계정 기반 권한 관리

## 🌐 Apps Script 웹앱

### WebApp_DongHo (우방아이유쉘 매물접수)

> **배포 URL**: Apps Script 에디터에서 배포 후 Bitly로 단축 권장

**기능:**
- 동/호 연동 드롭다운 (스프레드시트 데이터 기반)
- 거래유형 복수선택 (매매/전세/월세) + 조건부 가격 필드
- 멀티파일 업로드 → Google Drive 저장
- 이메일 알림 (접수 시 관리자에게 발송)

**설정 정보:**
| 항목 | 값 |
|------|---|
| 스프레드시트 ID | `1TE6OgqqbH8VlswI0uYKAEqr4QLtNW_kRjgG8M9RO9z4` |
| 데이터 시트 | `분양가` (A:동, B:호, C:타입) |
| 응답 시트 | `응답` |
| Drive 폴더 ID | `1xOy10OfqLwnGPq-bLssLxabasck4c6K9` |
| 알림 이메일 | `jongho137@gmail.com` |

**파일:**
- `apps-script/WebApp_DongHo_Code.gs` - 서버 코드
- `apps-script/WebApp_DongHo_Index.html` - 클라이언트 UI

### WebApp_MultiComplex (다중 단지 견적 시스템)

**기능:**
- 단지/동/호 3단계 On-Demand 선택
- 분양가 + 옵션 자동 계산
- 외부 스프레드시트에 응답 저장

**설정 정보:**
| 항목 | 값 |
|------|---|
| 데이터베이스 시트 ID | `1s6i-fFhQgKRSmowMtnmO4dIx-3BpPauMSN1e7hezmEQ` |
| 응답 시트 ID | `1FZ3AWouL0poEP1NrpaxHsNqF6u26H8hZfefOePEe7sI` |

**파일:**
- `apps-script/WebApp_MultiComplex_Code.gs`
- `apps-script/WebApp_MultiComplex_Index.html`

---

## 📝 개발 일지

### 2025-02-02: WebApp_DongHo 완성형 구현

**구현 내용:**
- Tally Form 스타일 모던 UI
- 거래유형 체크박스 복수선택 + 조건부 가격 필드 (slideDown 애니메이션)
- 멀티파일 업로드 (FileReader → base64 → DriveApp)
- 서브폴더 자동 생성: `{동}동_{호}호_{timestamp}`
- GmailApp 이메일 알림

**해결한 이슈:**
- `DriveApp.getFolderById` 권한 오류 → GCP OAuth 설정 + testPermissions 함수로 해결
- 파일 공유 설정: "링크가 있는 모든 사용자" 보기 권한

---

## 📚 관련 문서

- [[프로젝트 허브]] - 프로젝트 관리 중심 문서
- [[통합 마스터플랜]] - 단계별 개발 로드맵
- [[시트 구조 분석]] - 데이터베이스 스키마
- [[작업 지침서]] - 실무 운영 가이드

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 연락처

- **개발자**: cao25
- **이메일**: cao25@example.com
- **프로젝트 링크**: https://github.com/cao25/apartment-automation

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

**🚀 "작은 개선부터 시작하자. 완벽한 시스템은 그 다음이다!"**
