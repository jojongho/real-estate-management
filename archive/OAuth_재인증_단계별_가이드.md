# Google OAuth 재인증 단계별 가이드

## 📝 준비 단계

### 1단계: Google Cloud Console 접속 및 프로젝트 확인

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단 프로젝트 선택 드롭다운에서 **프로젝트 선택**
   - 기존 프로젝트: `ide-mcp` (현재 사용 중)
   - 또는 새 프로젝트 생성 (선택사항)

### 2단계: API 활성화 확인

1. **API 및 서비스 > 사용 설정된 API** 메뉴로 이동
2. 다음 API가 활성화되어 있는지 확인:
   - ✅ **Google Sheets API**
   - ✅ **Google Drive API**
3. 없으면 **+ API 및 서비스 사용 설정** 클릭 → 검색해서 활성화

### 3단계: OAuth 클라이언트 ID 생성 (또는 기존 것 사용)

#### 방법 A: 기존 OAuth 클라이언트 ID 사용 (권장)

1. **API 및 서비스 > 사용자 인증 정보** 메뉴로 이동
2. **OAuth 2.0 클라이언트 ID** 섹션에서 기존 클라이언트 확인
3. 클라이언트 타입: **데스크톱 앱**
4. 클라이언트 ID: `487975124917-brr9ii3drgjv34alemopc70u23oa51id.apps.googleusercontent.com`

#### 방법 B: 새 OAuth 클라이언트 ID 생성 (필요시)

1. **API 및 서비스 > 사용자 인증 정보** 메뉴로 이동
2. 상단 **+ 사용자 인증 정보 만들기** 클릭
3. **OAuth 클라이언트 ID** 선택
4. 애플리케이션 유형: **데스크톱 앱**
5. 이름 입력 (예: "Cursor MCP Google Sheets")
6. **만들기** 클릭
7. **JSON 다운로드** 클릭

### 4단계: OAuth 동의 화면 설정 확인

1. **API 및 서비스 > OAuth 동의 화면** 메뉴로 이동
2. 사용자 유형 선택:
   - **내부**: 조직 내부 사용 (Google Workspace)
   - **외부**: 일반 사용자 (대부분의 경우)
3. **범위 추가 또는 삭제** 버튼 클릭
4. 다음 범위가 포함되어 있는지 확인:
   - `https://www.googleapis.com/auth/spreadsheets`
   - `https://www.googleapis.com/auth/drive`
5. 없으면 추가하고 저장

## 📥 파일 다운로드 및 저장

### JSON 파일 저장 위치

**다운로드한 JSON 파일**을 다음 위치에 저장하세요:

```
/Users/jojongho/Projects/real estate management/config/oauth_credentials.json
```

**주의사항**:
- 파일명이 정확히 `oauth_credentials.json`인지 확인
- 기존 파일이 있다면 백업 후 교체:
  ```bash
  cd "/Users/jojongho/Projects/real estate management"
  cp config/oauth_credentials.json config/oauth_credentials.json.backup
  # 다운로드한 새 파일을 config/oauth_credentials.json로 복사
  ```

## ✅ 파일 확인

JSON 파일이 다음 형식인지 확인하세요:

```json
{
  "installed": {
    "client_id": "숫자-문자열.apps.googleusercontent.com",
    "project_id": "프로젝트-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-문자열",
    "redirect_uris": ["http://localhost"]
  }
}
```

**중요**: 파일 내용이 `{"installed": {...}}` 형식이어야 합니다!

## 🔐 재인증 실행

### 방법 1: 재인증 스크립트 사용 (권장)

```bash
cd "/Users/jojongho/Projects/real estate management"
python3 scripts/reauthenticate_google_sheets.py
```

**실행 과정**:
1. 스크립트가 브라우저를 자동으로 엽니다
2. Google 계정으로 로그인
3. 권한 승인 (Google Sheets 및 Drive 접근)
4. 토큰이 자동으로 `config/token.json`에 저장됩니다

### 방법 2: Python 직접 실행

```bash
cd "/Users/jojongho/Projects/real estate management"
python3 << 'EOF'
from src.sheets.oauth_auth import GoogleSheetsOAuth

auth = GoogleSheetsOAuth()
print("브라우저가 열립니다. 로그인하고 권한을 승인하세요...")
service = auth.authenticate()
print("✅ 인증 완료! token.json이 저장되었습니다.")
EOF
```

## 🎯 완료 확인

재인증 후 다음을 확인하세요:

1. **토큰 파일 생성 확인**:
   ```bash
   ls -la config/token.json
   ```

2. **토큰 유효성 확인**:
   ```bash
   python3 -c "
   from google.oauth2.credentials import Credentials
   import json
   token = json.load(open('config/token.json'))
   print('✅ Token 파일 존재')
   print(f'   - Scopes: {token.get(\"scopes\", [])}')
   "
   ```

3. **Cursor 재시작**: 
   - Cursor 완전 종료
   - Cursor 재시작
   - MCP 서버 자동 연결 확인

## 📋 체크리스트

재인증 전:
- [ ] Google Cloud Console에서 API 활성화 확인
- [ ] OAuth 클라이언트 ID 생성 또는 확인
- [ ] OAuth 동의 화면 범위 확인
- [ ] JSON 파일 다운로드
- [ ] `config/oauth_credentials.json`에 저장

재인증 후:
- [ ] 재인증 스크립트 실행 완료
- [ ] `config/token.json` 파일 생성 확인
- [ ] Cursor 재시작
- [ ] MCP 연결 테스트

## 🚨 문제 해결

### "invalid_client" 오류 발생 시
- OAuth 클라이언트 ID가 올바른지 확인
- JSON 파일 형식이 올바른지 확인 (`{"installed": {...}}`)

### "insufficient permissions" 오류 발생 시
- OAuth 동의 화면에서 범위(Scopes) 추가 확인
- Google Sheets API 및 Drive API 활성화 확인

### 브라우저가 열리지 않는 경우
- 방화벽 설정 확인
- 로컬 서버 포트 사용 가능한지 확인

### 토큰 파일이 생성되지 않는 경우
- `config/` 폴더에 쓰기 권한이 있는지 확인
- 파일 경로가 정확한지 확인

## 💡 참고

- **현재 사용 중인 클라이언트 ID**: `487975124917-brr9ii3drgjv34alemopc70u23oa51id.apps.googleusercontent.com`
- **프로젝트 ID**: `ide-mcp`
- **필요한 범위**: 
  - `https://www.googleapis.com/auth/spreadsheets`
  - `https://www.googleapis.com/auth/drive`

