# 설정 파일 가이드

## 📁 이 폴더의 역할

시스템 전체의 설정과 인증 파일을 관리합니다.

## 🔑 필요한 파일

### 1. credentials.json (필수)

**Google Service Account 인증 파일**

생성 방법:
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 (예: `apartment-automation`)
3. **API 및 서비스 > 사용 설정된 API 및 서비스**로 이동
4. 다음 API 활성화:
   - Google Sheets API
   - Google Drive API
5. **API 및 서비스 > 사용자 인증 정보**로 이동
6. **사용자 인증 정보 만들기 > 서비스 계정** 선택
7. 서비스 계정 이름 입력 (예: `sheets-automation`)
8. 역할: **편집자** 선택
9. 서비스 계정 생성 후, 해당 계정 클릭
10. **키 > 키 추가 > 새 키 만들기 > JSON** 선택
11. 다운로드된 JSON 파일을 이 폴더에 `credentials.json`으로 저장

**중요**: 이 파일은 절대 Git에 커밋하지 마세요! (`.gitignore`에 이미 포함됨)

### 2. settings.yaml (필수)

시스템 전체 설정 파일입니다. 현재 템플릿이 이미 생성되어 있으며, 필요에 따라 수정하세요.

```yaml
# 주요 설정 항목
google_sheets:
  spreadsheet_id: "1tkDKc7RTCLRgYPM-6e3CFEBOsHckLlNmddfKlVUX2rQ"

data_collection:
  pdf_parsing: true
  web_scraping: true
  api_integration: true

automation:
  daily_briefing: true
  marketing_content: true
```

## 🔐 보안 체크리스트

- [ ] `credentials.json` 파일이 `.gitignore`에 포함되어 있는지 확인
- [ ] `.env` 파일도 `.gitignore`에 포함되어 있는지 확인
- [ ] API 키와 비밀번호는 절대 코드에 하드코딩하지 않기
- [ ] 서비스 계정에 필요한 최소 권한만 부여
- [ ] 정기적으로 API 키 갱신

## 🔧 설정 파일 테스트

설정이 올바른지 확인:

```bash
# Python에서 설정 로드 테스트
python -c "from src.config.settings import load_settings; print(load_settings())"

# Google Sheets 연결 테스트
python -c "from src.sheets.writer import SheetsWriter; SheetsWriter().test_connection()"
```

## 📚 관련 문서

- [[🚀 빠른 시작 가이드]] - 전체 설정 프로세스
- [[프로젝트 허브]] - 프로젝트 관리
- [Google Sheets API 공식 문서](https://developers.google.com/sheets/api)
