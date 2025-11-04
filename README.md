# 🏠 아파트 매물관리 자동화 시스템

> Google Sheets를 중심으로 한 매물관리 및 자동 데이터 수집/분석 시스템

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Google Sheets](https://img.shields.io/badge/Google_Sheets-4285F4?logo=google-sheets&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Development-yellow.svg)

## 📋 프로젝트 개요

부동산 중개업무의 핵심인 매물 관리를 Google Sheets + Apps Script + Python으로 완전 자동화하는 시스템입니다.

### 🎯 주요 목표

- **기존 시스템 개선**: 데이터 품질 70% → 95%
- **자동화 확장**: 데이터 수집 → 분석 → 콘텐츠 발행  
- **생산성 향상**: 수동 작업 90% 감소

### 💡 핵심 기능

- 📊 **Google Sheets 중앙 관리**: 매물/고객 DB 통합 관리
- 🤖 **Apps Script 자동화**: 매물 등록/수정/검증 자동화
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
│   ├── sheets/                  # Google Sheets 연동
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

### 2. Google Sheets 설정

1. **Google Cloud Console**에서 새 프로젝트 생성
2. **Google Sheets API** 및 **Google Drive API** 활성화
3. **서비스 계정** 생성 및 JSON 키 파일 다운로드
4. 키 파일을 `config/credentials.json`으로 저장
5. 환경 변수 설정:
   ```bash
   cp env.example .env
   # .env 파일 편집하여 실제 값 입력
   ```

### 3. Apps Script 설정

1. Google Sheets에서 **확장프그램 > Apps Script** 열기
2. 기존 코드를 `apps-script/통합_최종_스크립트.js` 내용으로 교체
3. 권한 승인 및 저장

### 4. 실행

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
등록검색 시트 → Apps Script → 매물DB/고객DB
                ↓
          Python 주기적 처리 → 분양가/옵션 시트
                ↓
          자동 브리핑 생성 → Google Docs/이메일
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
