# Google Sheets MCP 설정 가이드

## 📋 현재 설정 상태

✅ **이미 설정된 항목:**
- `config/oauth_credentials.json` - OAuth 클라이언트 인증 정보 존재
- `config/token.json` - 인증 토큰 파일 존재
- `mcp.json` - MCP 서버 설정 완료

## 🔑 필요한 파일 및 설정

### 1. OAuth 인증 파일 (✅ 이미 있음)

**파일 위치**: `config/oauth_credentials.json`

**내용 구조**:
```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "client_secret": "GOCSPX-your-secret",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["http://localhost"]
  }
}
```

**생성 방법** (필요시 재생성):
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 (또는 새 프로젝트 생성)
3. **API 및 서비스 > 사용 설정된 API**:
   - ✅ Google Sheets API 활성화
   - ✅ Google Drive API 활성화
4. **API 및 서비스 > 사용자 인증 정보**:
   - **+ 사용자 인증 정보 만들기** > **OAuth 클라이언트 ID**
   - 애플리케이션 유형: **데스크톱 앱**
   - 이름 입력 후 생성
   - JSON 다운로드 → `config/oauth_credentials.json`로 저장

### 2. 인증 토큰 파일 (✅ 이미 있음)

**파일 위치**: `config/token.json`

**특징**:
- 첫 인증 시 자동 생성됨
- 토큰 만료 시 자동 갱신됨 (refresh_token 사용)
- 수동 생성 불필요

**토큰 만료 시 재인증 방법**:
```bash
# Python 스크립트로 재인증 (token.json 삭제 후 실행)
python -c "from src.sheets.oauth_auth import GoogleSheetsOAuth; auth = GoogleSheetsOAuth(); auth.authenticate()"
```

### 3. MCP 설정 파일

**파일 위치**: `~/.cursor/mcp.json` (또는 `/Users/jojongho/.cursor/mcp.json`)

**현재 설정**:
```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["mcp-google-sheets@latest"],
      "env": {
        "CREDENTIALS_PATH": "/Users/jojongho/Projects/real estate management/config/oauth_credentials.json",
        "TOKEN_PATH": "/Users/jojongho/Projects/real estate management/config/token.json",
        "DRIVE_FOLDER_ID": "1gbHCZMOKQ9zLIHOLlqxx5aV8I7xnc9sG"
      }
    }
  }
}
```

## 🔧 설정 확인 및 테스트

### 1. 파일 존재 확인

```bash
cd "/Users/jojongho/Projects/real estate management"

# 파일 존재 확인
ls -la config/oauth_credentials.json
ls -la config/token.json

# 파일 내용 확인 (민감 정보 제외)
python3 -c "import json; print('OAuth 파일 존재:', 'oauth_credentials.json' in open('config/oauth_credentials.json').read()[:20])"
python3 -c "import json; print('Token 파일 존재:', 'token' in open('config/token.json').read()[:20])"
```

### 2. 토큰 유효성 확인

```bash
# Python으로 토큰 확인
python3 << 'EOF'
import json
from pathlib import Path

token_path = Path("config/token.json")
if token_path.exists():
    token_data = json.load(open(token_path))
    print("✅ Token 파일 존재")
    print(f"   - Scopes: {token_data.get('scopes', [])}")
    print(f"   - Refresh token 존재: {'refresh_token' in token_data}")
else:
    print("❌ Token 파일 없음 - 재인증 필요")
EOF
```

### 3. MCP 서버 연결 테스트

**Cursor 재시작 후**:
1. Cursor 완전 종료
2. Cursor 재시작
3. MCP 서버 자동 연결 확인

**수동 테스트** (Python):
```python
from src.sheets.oauth_auth import GoogleSheetsOAuth

auth = GoogleSheetsOAuth()
service = auth.authenticate()
print("✅ Google Sheets 연결 성공!")
```

## 🚨 문제 해결

### 문제 1: 토큰이 만료된 경우

**증상**: MCP 서버 연결 실패, 인증 오류

**해결 방법**:
```bash
# 1. token.json 백업 (선택사항)
cp config/token.json config/token.json.backup

# 2. token.json 삭제
rm config/token.json

# 3. 재인증 (브라우저에서 로그인 필요)
python3 << 'EOF'
from src.sheets.oauth_auth import GoogleSheetsOAuth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

credentials_file = "config/oauth_credentials.json"
token_file = "config/token.json"
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

creds = None
if os.path.exists(token_file):
    creds = Credentials.from_authorized_user_file(token_file, scopes)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        print("토큰 갱신 중...")
        creds.refresh(Request())
    else:
        print("새 인증 시작... (브라우저가 열립니다)")
        from google_auth_oauthlib.flow import InstalledAppFlow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, scopes)
        creds = flow.run_local_server(port=0)
    
    with open(token_file, 'w') as token:
        token.write(creds.to_json())
    print("✅ 인증 완료! token.json 저장됨")
else:
    print("✅ 토큰 유효함")
EOF
```

### 문제 2: OAuth 인증 정보가 없는 경우

**증상**: `oauth_credentials.json` 파일 없음 또는 형식 오류

**해결 방법**: 위의 "OAuth 인증 파일 생성 방법" 참조

### 문제 3: MCP 서버가 연결되지 않는 경우

**증상**: Cursor에서 Google Sheets MCP 기능 미작동

**체크리스트**:
- [ ] `uvx` 명령어 설치 여부 확인: `which uvx` 또는 `uvx --version`
- [ ] MCP 서버 패키지 설치 가능 여부: `uvx mcp-google-sheets@latest --help`
- [ ] `mcp.json` 파일 경로 확인 (절대 경로 사용)
- [ ] Cursor 완전 재시작

**uvx 설치** (필요시):
```bash
# uv 설치 (Python 패키지 매니저)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 pip로 설치
pip install uv

# uvx 확인
uvx --version
```

### 문제 4: 권한 오류

**증상**: "insufficient permissions" 오류

**해결 방법**:
1. Google Cloud Console에서 API 활성화 확인:
   - Google Sheets API ✅
   - Google Drive API ✅
2. OAuth 동의 화면 설정 확인:
   - **API 및 서비스 > OAuth 동의 화면**
   - 사용자 유형: 내부 또는 외부
   - 범위: `.../auth/spreadsheets`, `.../auth/drive`

## 📝 사용 예시

MCP 설정 완료 후 Cursor에서:

1. **시트 읽기**: "매물DB 시트의 모든 데이터 보여줘"
2. **데이터 추가**: "매물DB에 새 매물 추가해줘"
3. **데이터 수정**: "매물DB에서 특정 매물 정보 수정해줘"
4. **시트 구조 확인**: "등록검색 시트 구조 알려줘"

## 🔐 보안 주의사항

- ✅ `config/oauth_credentials.json` - `.gitignore`에 포함됨
- ✅ `config/token.json` - `.gitignore`에 포함됨
- ✅ 절대 Git에 커밋하지 않기
- ✅ 파일 권한 설정: `chmod 600 config/*.json`

## 📚 참고 자료

- [Google Sheets API 문서](https://developers.google.com/sheets/api)
- [OAuth 2.0 설정 가이드](https://developers.google.com/identity/protocols/oauth2)
- 프로젝트 내 `src/sheets/oauth_auth.py` - OAuth 인증 구현 참조

