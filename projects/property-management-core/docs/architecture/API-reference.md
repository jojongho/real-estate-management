# 📚 API 참조 가이드

아파트 매물관리 자동화 시스템의 모든 API와 함수에 대한 상세한 설명 문서입니다.

## 🏠 클래스 개요

### Settings
시스템 설정을 관리하는 중앙 클래스입니다.

```python
from src.config.settings import Settings

settings = Settings()
```

### CSVImporter
CSV 파일을 Google Sheets로 가져오는 기능을 제공합니다.

```python
from src.collectors.csv_importer import CSVImporter

importer = CSVImporter(settings)
results = importer.process_all_csv_files()
```

### PDFParser
PDF 파일에서 매물 정보를 추출하는 기능을 제공합니다.

```python
from src.collectors.pdf_parser import PDFParser

parser = PDFParser(settings)
parsed_data = parser.process_apartment_notices()
```

### SheetsWriter
Google Sheets에 데이터를 쓰고 읽는 기능을 제공합니다.

```python
from src.sheets.writer import SheetsWriter

writer = SheetsWriter(settings)
success = writer.update_sheet_with_dataframe('매물DB', dataframe)
```

## 🔧 주요 함수 상세

### Settings 클래스

#### `__init__(self)`
설정 객체를 초기화합니다.

```python
def __init__(self):
    """설정 초기화"""
    self.project_name = "아파트 매물관리 자동화 시스템"
    self.version = "1.0.0"
    self.author = "cao25"
```

**매개변수**: 없음  
**반환값**: None  
**예외**: 없음

#### `get_sheet_name(self, sheet_type: str) -> str`
시트 이름을 조회합니다.

```python
sheet_name = settings.get_sheet_name('property_db')
# 반환: "매물DB"
```

**매개변수**:
- `sheet_type` (str): 시트 유형 ('property_db', 'customer_db' 등)

**반환값**:
- `str`: 실제 시트 이름

#### `get_api_key(self, api_name: str) -> Optional[str]`
API 키를 조회합니다.

```python
gemini_key = settings.get_api_key('gemini')
naver_client_id = settings.get_api_key('naver_client_id')
```

**매개변수**:
- `api_name` (str): API 이름 ('gemini', 'naver_client_id' 등)

**반환값**:
- `Optional[str]`: API 키 또는 None

### CSVImporter 클래스

#### `__init__(self, settings: Settings)`
CSV 가져오기를 초기화합니다.

```python
def __init__(self, settings: Settings):
    self.settings = settings
    self.csv_mapping = {
        '통합단지DB - 분양가.csv': '분양가',
        '통합단지DB - 옵션.csv': '옵션',
        # ...
    }
```

**매개변수**:
- `settings` (Settings): 시스템 설정 객체

#### `process_all_csv_files(self) -> Dict[str, bool]`
모든 CSV 파일을 일괄 처리합니다.

```python
results = importer.process_all_csv_files()
# 결과: {'파일1.csv': True, '파일2.csv': False}
```

**반환값**:
- `Dict[str, bool]`: 파일명과 처리 성공 여부의 매핑

**작업 순서**:
1. raw 데이터 디렉토리 스캔
2. 각 CSV 파일 읽기
3. 인코딩 자동 감지
4. Google Sheets 업로드
5. 결과 반환

#### `import_csv_file(self, csv_path: Path) -> bool`
단일 CSV 파일을 가져옵니다.

```python
from pathlib import Path
csv_path = Path('data/raw/매물목록.csv')
success = importer.import_csv_file(csv_path)
```

**매개변수**:
- `csv_path` (Path): CSV 파일 경로

**반환값**:
- `bool`: 처리 성공 여부

#### `validate_csv_structure(self, csv_path: Path) -> bool`
CSV 파일 구조를 검증합니다.

```python
is_valid = importer.validate_csv_structure(csv_path)
if not is_valid:
    logger.warning(f"CSV 구조 검증 실패: {csv_path}")
```

**매개변수**:
- `csv_path` (Path): 검증할 CSV 파일 경로

**반환값**:
- `bool`: 구조 유효성

**검증 규칙**:
- 파일이 비어있지 않음
- 컬럼이 존재함
- 데이터 행이 존재함

### PDFParser 클래스

#### `parse_apartment_notice(self, pdf_path: Path) -> Optional[Dict[str, Any]]`
단일 PDF 파일을 파싱합니다.

```python
pdf_path = Path('data/raw/입주자모집공고.pdf')
data = parser.parse_apartment_notice(pdf_path)
if data:
    print(f"단지명: {data['단지명']}")
    print(f"총세대수: {data['총세대수']}")
```

**매개변수**:
- `pdf_path` (Path): PDF 파일 경로

**반환값**:
- `Optional[Dict[str, Any]]`: 파싱된 데이터 또는 None

**추출되는 데이터**:
- 단지명
- 총세대수
- 입주예정일
- 민원실 연락처
- 공급면적
- 분양가 정보

#### `process_apartment_notices(self, pdf_dir: Optional[Path] = None) -> List[Dict[str, Any]]`
여러 PDF 파일을 일괄 처리합니다.

```python
pdf_dir = Path('data/raw')
results = parser.process_apartment_notices(pdf_dir)
for data in results:
    print(f"처리된 파일: {data['source_file']}")
```

**매개변수**:
- `pdf_dir` (Optional[Path]): PDF 파일 디렉토리 (기본값: data/raw)

**반환값**:
- `List[Dict[str, Any]]`: 파싱된 데이터 목록

#### `save_parsed_data(self, parsed_data: List[Dict[str, Any]], output_path: Optional[Path] = None)`
파싱된 데이터를 저장합니다.

```python
parser.save_parsed_data(results, Path('data/processed/parsed_result.json'))
```

**매개변수**:
- `parsed_data` (List[Dict[str, Any]]): 저장할 데이터
- `output_path` (Optional[Path]): 출력 파일 경로

### SheetsWriter 클래스

#### `__init__(self, settings)`
Google Sheets에 연결합니다.

```python
def __init__(self, settings):
    self.settings = settings
    self._connect_to_sheets()
```

**연결 과정**:
1. credentials.json 파일 로드
2. 스코프 설정 (Sheets, Drive)
3. 인증 수행
4. 스프레드시트 열기

#### `update_sheet_with_dataframe(self, sheet_name: str, dataframe: pd.DataFrame, clear_existing: bool = True) -> bool`
DataFrame으로 시트를 업데이트합니다.

```python
import pandas as pd

df = pd.DataFrame({
    '상품명': ['아파트A', '아파트B'],
    '가격': [100000, 150000]
})

success = writer.update_sheet_with_dataframe('매물DB', df)
```

**매개변수**:
- `sheet_name` (str): 시트 이름
- `dataframe` (pd.DataFrame): 업데이트할 데이터
- `clear_existing` (bool): 기존 데이터 삭제 여부 (기본값: True)

**반환값**:
- `bool`: 성공 여부

#### `sync_property_data(self, property_data: Dict[str, Any], mode: str = 'append') -> bool`
매물 데이터를 동기화합니다.

```python
property_data = {
    '매물ID': 'HIL240101-001',
    '단지명': '히르스테이트두정역',
    '동': 101,
    '호': 1401,
    '타입': '3BR/2BA',
    '거래유형': '매매',
    '매매가': 45000,
    '거래상태': '계약가능'
}

success = writer.sync_property_data(property_data, 'append')
```

**매개변수**:
- `property_data` (Dict[str, Any]): 매물 데이터
- `mode` (str): 동기화 모드 ('append', 'update')

**반환값**:
- `bool`: 성공 여부

#### `get_sheet_info(self) -> Dict[str, Any]`
시트 정보를 조회합니다.

```python
info = writer.get_sheet_info()
print(f"스프레드시트: {info['spreadsheet_title']}")
print(f"시트 수: {info['sheets_count']}")
for sheet in info['sheets']:
    print(f"- {sheet['title']}: {sheet['rows']}행 × {sheet['cols']}열")
```

**반환값**:
- `Dict[str, Any]`: 시트 정보 사전

## 🎯 Apps Script 함수

### Google Apps Script 메인 함수

#### `registerPropertyAndClient()`
매물 및 고객 정보를 동시에 등록하는 메인 함수입니다.

```javascript
function registerPropertyAndClient() {
  // 1. 입력 데이터 읽기
  // 2. 필수 필드 검증  
  // 3. 자동 값 설정
  // 4. 매물ID 자동 생성
  // 5. 중복 체크
  // 6. DB 업데이트
  // 7. 폰더 생성
  // 8. 입력 필드 초기화
}
```

**사용법**:
1. '등록검색' 시트에서 데이터 입력
2. '메뉴' → '🏠 매물관리 시스템' → '📝 매물 등록' 클릭
3. 또는 시트에서 버튼 클릭

#### `generatePropertyId(data)`
매물ID를 자동 생성합니다.

```javascript
function generatePropertyId(data) {
  // 단지명축약 + 날짜(240101) + 순번(001)
  // 예: "HIL두정 240101-001"
}
```

**매개변수**:
- `data`: 입력 데이터 객체

**반환**:
- `string`: 생성된 매물ID

**형식**:
- `{단지명축약} {YYMMDD}-{순번}`

#### `generateCustomerId(data)`
고객ID를 자동 생성합니다.

```javascript
function generateCustomerId(data) {
  // C + 날짜(240101) + 순번(001)  
  // 예: "C240101-001"
}
```

#### `checkPropertyDuplication(data)`
매물 중복을 체크합니다.

```javascript
function checkPropertyDuplication(data) {
  // 단지명 + 동 + 호 + 타입으로 중복 체크
  return isDuplicated;
}
```

## 🔧 유틸리티 함수

### `getPropertySummary()`
매물 현황 요약 정보를 조회합니다.

```javascript
function getPropertySummary() {
  return {
    total: 61,
    new_today: 3,
    available: 45
  };
}
```

### `createDailyBriefing()`
일일 브리핑을 생성합니다.

```javascript
function generateDailyBriefing() {
  const doc = DocumentApp.create('일일 브리핑 ' + today);
  // 브리핑 내용 작성
  // 이메일 발송
  return doc.getUrl();
}
```

### `setupTriggers()`
자동 트리거를 설정합니다.

```javascript
function setupTriggers() {
  // 매일 오전 9시 브리핑 생서 트리거
  ScriptApp.newTrigger('generateDailyBriefing')
    .timeBased()
    .everyDays(1)  
    .atHour(9)
    .create();
}
```

## 🚀 실행 예제

### Python 예제

```python
from src.config.settings import Settings
from src.collectors.csv_importer import CSVImporter
from src.sheets.writer import SheetsWriter

# 1. 설정 로드
settings = Settings()

# 2. CSV 파일 일괄 처리
importer = CSVImporter(settings)
results = importer.process_all_csv_files()

# 3. 성공한 파일들 확인
for filename, success in results.items():
    if success:
        print(f"✅ {filename} 처리 완료")
    else:
        print(f"❌ {filename} 처리 실패")

# 4. Sheets 연결 확인
writer = SheetsWriter(settings)
sheet_info = writer.get_sheet_info()
print(f"연결된 스프레드시트: {sheet_info['spreadsheet_title']}")
```

### JavaScript 예제 (Apps Script)

```javascript
// 매물 등록 테스트 함수
function testPropertyRegistration() {
  const testData = {
    '단지명': '히르스테이트두정역',
    '동': 101,
    '호': 1401,
    '타입': '3BR/2BA',
    '거래유형': '매매',
    '거래상태': '접수',
    '성': '홍',
    '연락처': '010-1234-5678',
    '매매가': 45000
  };
  
  // 테스트 데이터를 시트에 입력
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('등록검색');
  Object.keys(testData).forEach((key, index) => {
    sheet.getRange(`B${4 + index}`).setValue(key);
    sheet.getRange(`C${4 + index}`).setValue(testData[key]);
  });
  
  // 등록 실행
  registerPropertyAndClient();
  
  Logger.log('테스트 매물 등록 완료');
}
```

## 🔍 디버깅 가이드

### 로그 확인

```python
from loguru import logger

logger.debug("디버그 메시지")
logger.info("정보 메시지")  
logger.warning("경고 메시지")
logger.error("오류 메시지")
```

### Apps Script 로그 확인

1. Apps Script 에디터에서 **실행** → **실행**
2. **보기** → **로그** 클릭
3. Logger.log() 메시지 확인

### 오류 처리

```python
try:
    # 실행할 코드
    importer.process_all_csv_files()
except Exception as e:
    logger.error(f"처리 실패: {e}")
    # 대안 처리
```

## 📞 지원 및 개문

API 사용 중 문제가 발생하면:

1. **GitHub Issues**에 버그 리포트 등록
2. **로그 파일** 첨부 (`logs/apartment_automation_YYYY-MM-DD.log`)
3. **재현 단계** 상세히 기술
4. **예상 동작**과 **실제 동작** 비교

---

이 문서는 시스템 업데이트에 따라 계속 업데이트됩니다. 최신 정보는 GitHub 저장소를 확인하세요.
