# 🪟 Windows PC 환경 설정 가이드

macOS에서 작업하던 프로젝트를 Windows PC(회사 PC)에서도 이어서 작업할 수 있도록 설정하는 가이드입니다.

## 📋 사전 준비사항

### Windows PC에 설치 필요
- ✅ **Python 3.10 이상** ([다운로드](https://www.python.org/downloads/))
- ✅ **Git** ([다운로드](https://git-scm.com/download/win))
- ✅ **Visual Studio Code** 또는 Cursor (선택사항)
- ✅ **Google 계정** (동일 계정 사용 권장)

---

## 🚀 방법 1: Git을 이용한 동기화 (권장)

### Step 1: GitHub/GitLab 저장소 생성

#### macOS에서:
```bash
# 현재 디렉토리로 이동
cd "/Users/jojongho/Projects/real estate management"

# Git 초기화 (아직 안 했다면)
git init

# .gitignore 확인
cat .gitignore

# 초기 커밋
git add .
git commit -m "Initial commit: 아파트 매물관리 시스템"

# GitHub 저장소 생성 후:
# 1. GitHub.com 접속 → New repository
# 2. Repository name: "real-estate-management"
# 3. Private 선택 (민감한 정보 포함)
# 4. 생성 후 표시되는 명령어 실행

git remote add origin https://github.com/YOUR_USERNAME/real-estate-management.git
git branch -M main
git push -u origin main
```

### Step 2: Windows PC에서 클론

```powershell
# 원하는 위치로 이동 (예: D:\Projects)
cd D:\Projects

# 저장소 클론
git clone https://github.com/YOUR_USERNAME/real-estate-management.git

# 프로젝트 폴더로 이동
cd real-estate-management
```

### Step 3: Windows 환경 설정

```powershell
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\Activate.ps1
# 만약 실행 정책 오류가 나면:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 의존성 설치
pip install -r requirements.txt
```

### Step 4: 환경 변수 설정

```powershell
# .env 파일 생성 (macOS와 동일한 내용)
Copy-Item env.example .env

# .env 파일 편집 (메모장 또는 VSCode)
notepad .env
```

**.env 파일 내용** (macOS와 동일):
```env
GOOGLE_SHEETS_ID=1tkDKc7RTCLRgYPM-6e3CFEBOsHckLlNmddfKlVUX2rQ
GOOGLE_CREDENTIALS_FILE=config/credentials.json
GEMINI_API_KEY=your_api_key_here
# ... 기타 설정
```

### Step 5: Google 인증 파일 복사

**⚠️ 중요**: `credentials.json` 파일은 Git에 포함되지 않으므로 수동으로 복사해야 합니다.

**방법 1: USB/네트워크 드라이브 사용**
```
macOS: /Users/jojongho/Projects/real estate management/config/credentials.json
→ 복사 → 
Windows: D:\Projects\real-estate-management\config\credentials.json
```

**방법 2: Google Drive/OneDrive 동기화**
- Google Drive 또는 OneDrive에 `credentials.json` 업로드
- Windows에서 다운로드하여 `config/` 폴더에 배치

**방법 3: 이메일로 전송** (보안 주의)
- 자신의 이메일로 파일 첨부
- Windows에서 다운로드

### Step 6: 연결 테스트

```powershell
# Python 셸에서 테스트
python
>>> from src.config.settings import Settings
>>> settings = Settings()
>>> print("✅ 설정 로드 성공!" if settings.google_sheets.spreadsheet_id else "❌ 실패")
>>> exit()
```

---

## 🔄 작업 흐름 (매일 사용)

### macOS에서 작업 완료 후:

```bash
# 변경사항 커밋
git add .
git commit -m "작업 내용 설명"

# 원격 저장소에 푸시
git push origin main
```

### Windows PC에서 작업 시작 전:

```powershell
# 최신 변경사항 가져오기
git pull origin main

# 가상환경 활성화
.\venv\Scripts\Activate.ps1
```

### Windows PC에서 작업 완료 후:

```powershell
# 변경사항 커밋
git add .
git commit -m "작업 내용 설명"

# 원격 저장소에 푸시
git push origin main
```

---

## 🚀 방법 2: 클라우드 동기화 (간단하지만 주의 필요)

### Google Drive / OneDrive 사용

⚠️ **주의사항**:
- `.git`, `venv/` 폴더는 동기화하지 않기 (용량 문제)
- `credentials.json`은 암호화하거나 별도 관리

**설정 방법:**

1. **프로젝트 폴더를 클라우드 드라이브에 배치**
   ```
   macOS: ~/Google Drive/real-estate-management
   Windows: C:\Users\YourName\Google Drive\real-estate-management
   ```

2. **.git 폴더와 venv 제외**
   - 각 OS에서 별도로 Git 초기화
   - 각 OS에서 별도로 venv 생성

3. **동기화 주의사항**
   - 동시에 같은 파일 편집하지 않기
   - 커밋 전에 항상 최신 파일 확인

---

## 🔧 Windows 전용 설정

### PowerShell 실행 정책 설정

```powershell
# 관리자 권한으로 PowerShell 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 경로 문제 해결

Windows에서 경로에 공백이 있으면 문제가 될 수 있습니다:

```powershell
# PowerShell에서 공백 포함 경로 처리
cd "D:\Projects\real estate management"

# 또는 프로젝트명 변경 (GitHub에서 클론 시)
git clone https://github.com/YOUR_USERNAME/real-estate-management.git real-estate-management
cd real-estate-management
```

### Python 경로 문제

```powershell
# Python이 PATH에 없는 경우
$env:Path += ";C:\Python310;C:\Python310\Scripts"

# 또는 Python Launcher 사용
py -m venv venv
py -m pip install -r requirements.txt
```

---

## ✅ 체크리스트

Windows PC 설정 완료 체크:

- [ ] Git 설치 및 설정 완료
- [ ] Python 3.10+ 설치 완료
- [ ] 프로젝트 클론 완료
- [ ] 가상환경 생성 및 활성화
- [ ] `pip install -r requirements.txt` 성공
- [ ] `.env` 파일 생성 및 설정
- [ ] `config/credentials.json` 파일 복사
- [ ] 연결 테스트 성공
- [ ] `git pull` / `git push` 동작 확인

---

## 🆘 문제 해결

### ❌ "git: command not found"
- Git이 설치되지 않았거나 PATH에 없음
- Git 설치 후 PowerShell 재시작

### ❌ "python: command not found"
- Python 설치 확인: `py --version`
- 또는 `python3` 명령어 시도

### ❌ 가상환경 활성화 실패
```powershell
# 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 또는 직접 실행
.\venv\Scripts\python.exe
```

### ❌ Google Sheets 연결 실패
- `credentials.json` 파일 경로 확인
- 서비스 계정 이메일이 스프레드시트에 공유되어 있는지 확인
- `.env` 파일의 `GOOGLE_SHEETS_ID` 확인

### ❌ Git 충돌 (conflict)
```powershell
# 현재 상태 확인
git status

# 충돌 파일 확인 및 수정 후
git add .
git commit -m "충돌 해결"
git push
```

---

## 💡 팁

### 빠른 작업 전환 스크립트

**Windows용 `start.ps1` 생성:**
```powershell
# start.ps1
Write-Host "🚀 프로젝트 시작..." -ForegroundColor Green
cd "D:\Projects\real-estate-management"
.\venv\Scripts\Activate.ps1
git pull origin main
Write-Host "✅ 준비 완료!" -ForegroundColor Green
```

**사용법:**
```powershell
.\start.ps1
```

### 자동 동기화 (선택사항)

GitHub Actions를 사용하여 자동 백업 설정 가능 (고급)

---

## 📞 도움말

문제가 발생하면:
1. 이 가이드의 문제 해결 섹션 확인
2. Git 상태 확인: `git status`
3. 로그 확인: `logs/` 폴더
4. 설정 확인: `.env` 파일 및 `config/credentials.json`
