# 🚀 빠른 시작 가이드

아파트 매물관리 자동화 시스템을 5분 안에 실행해보세요!

## ⚡ 초고속 설치 (기존 시스템 보유자)

### 1분: 필요한 파일 복사
```powershell
# 기존 스프레드시트와 연결하여 바로 사용
git clone https://github.com/cao25/apartment-automation.git
cd apartment-automation
```

### 2분: 환경 설정
```powershell
# Python 환경 설정
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 환경 변수 설정
copy env.example .env
notepad .env  # Google Sheets ID만 입력하면 OK!
```

### 3분: Apps Script 설정
1. **기존 Google Sheets**에서 Apps Script 열기
2. **통합_최종_스크립트.js** 내용 복사 붙여넣기
3. **실행** 버튼으로 권한 승인

### 4분: 첫 테스트
1. **등록검색 시트**에서 매물 정보 입력
2. **메뉴** → **🏠 매물관리 시스템** → **📝 매물 등록**
3. 성공 메시지 확인!

### 5분: 완료! 🎉
이제 매물 등록이 완전 자동화되었습니다!

---

## 🔧 상세 설치 (처음 시작)

### 단계 1: 환경 준비 (10분)

```bash
# 필요한 도구들 설치 확인
python --> 버전 3.10 이상 ✅
git    --> 최신 버전         ✅
시험용 Google 계정          ✅
```

### 단계 2: 프로젝트 설치 (5분)

```bash
# 저장소 클론
git clone https://github.com/cao25/apartment-automation.git
cd apartment-automation

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate    # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 단계 3: Google 설정 (15분)

#### 3.1 Google Cloud Console 설정
1. **[Google Cloud Console](https://console.cloud.google.com/)** 접속
2. **새 프로젝트 생성**: `매물관리-테스트`
3. **API 활성화**:
   - Google Sheets API ✅
   - Google Drive API ✅

#### 3.2 서비스 계정 생성
```text
1. 좌측 메뉴 → "IAM 및 관리" → "서비스 계정"
2. "만들기" 클릭
3. 이름: "매물관리-자동화"
4. 역할: "편집자" 선택
5. 키 탭에서 "JSON 키 생성" → 파일 다운로드
```

#### 3.3 스프레드시트 설정
1. **[새 Google Sheets](https://sheets.google.com/)** 생성
2. 이름: `테스트_매물DB`
3. **공유 설정**:
   - 서비스 계정 이메일 추가 (편집자 권한)
   - 이메일 형식: `매물관리-자동화@프로젝트ID.iam.gserviceaccount.com`

### 단계 4: 환경 변수 설정 (3분)

```bash
# 환경 변수 템플릿 복사
cp env.example .env

# .env 파일 편집
notepad .env  # 또는 vim .env
```

#### 필수 설정값 입력:
```env
# Google Sheets ID (URL에서 복사)
GOOGLE_SHEETS_ID=1ABC_DEF_실제ID_HERE

# 서비스 계정 키 파일 경로
GOOGLE_CREDENTIALS_FILE=config/credentials.json

# 사용자 정보
USER_NAME=테스트사용자
USER_EMAIL=test@example.com
```

### 단계 5: 첫 매물 등록 테스트 (2분)

#### 시트 구조 생성
다음 시트들을 생성하세요:
- `등록검색` (매물 등록용)
- `매물DB` (매물 저장소)  
- `고객DB` (고객 저장소)
- `아파트단지` (단지 데이터)
- `고정값` (옵션 목록)

#### 테스트 데이터 입력
**등록검색 시트**에 다음 정보 입력:
```text
단지명: 테스트아파트
동: 101  
호: 1401
타입: 34㎡
거래유형: 매매
거래상태: 접수
성: 홍
연락처: 010-1234-5678
```

#### 자동 등록 실행
```python
# Python 셸에서 실행
python
>>> from src.sheets.writer import SheetsWriter
>>> from src.config.settings import Settings
>>> settings = Settings()
>>> writer = SheetsWriter(settings)
>>> print("✅ 연결 성공!" if writer.spreadsheet else "❌ 연결 실패")
```

---

## 🚨 문제 해결

### ❌ 연결 오류
```
AuthenticationError: Invalid credentials
```

**해결방법:**
1. `credentials.json` 파일 경로 확인
2. 서비스 계정 이메일로 시트 공유 확인
3. API 활성화 상태 재확인

### ❌ 권한 오류  
```
PermissionError: The caller does not have permission
```

**해결방법:**
1. Google Cloud Console 권한 재확인
2. 스프레드시트 공유 설정 재확인  
3. Apps Script 권한 재승인

### ❌ 모듈 없음 오류
```
ImportError: No module named 'gspread'
```

**해결방법:**
```bash
# 가상환경 재활성화 후 재설치
source venv/bin/activate  # 또는 venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🎯 다음 단계

설치가 완료되면 다음 기능들을 단계별로 시도해보세요:

### 🔄 정기 작업 자동화
```python
# 매일 데이터 수집 자동화
python src/main.py
```

### 📊 데이터 분석 대시보드  
- Google Sheets의 **추가 기능** → **차트 및 분석** 활용
- 피벗 테이블로 매물 현황 분석

### 🤖 콘텐츠 자동 생성
```python
# 마케팅 문구 자동 생성 (Gemini API 필요)
python -c "from src.generators.marketing import MarketingGenerator; MarketingGenerator().generate_sample_content()"
```

---

## 🆘 도움이 필요하신가요?

문제가 계속 발생하면:

1. **📖 문서 읽기**: [API Reference](API-reference.md)
2. **🛠️ 상세 가이드**: [Setup Guide](setup-guide.md)  
3. **💬 질문하기**: GitHub Issues에 버그 리포트
4. **📧 연락하기**: cao25@example.com

---

**🎉 축하합니다! 매물관리 자동화가 활성화되었습니다!**

이제 매물 등록 시간이 **90% 단축**되고, 데이터 품질이 **99% 이상**으로 향상될 것입니다.
