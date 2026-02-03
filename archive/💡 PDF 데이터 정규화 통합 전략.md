---
tags: [framing, 부동산, PDF파싱, 데이터정규화, 자동화]
type: note
status: 제안
creation_date: 2025-10-15
index: [["🏷 부동산 프로젝트"]]
---

# 💡 PDF 데이터 정규화 통합 전략

> 기존 수동 방식을 개선하여 PDF → Sheets 자동화 파이프라인 구축

---

## 🔍 기존 방식 분석

### 현재 워크플로우 (비효율적)

```
1. PDF 입수 (입주자모집공고문)
   ↓
2. 수동으로 읽고 CSV 템플릿 생성
   - 동/호/타입 정보 수동 입력
   ↓
3. Python 스크립트로 가격 매핑
   - process_prices_template.py 수정
   - pricing_data 딕셔너리에 PDF 정보 하드코딩
   ↓
4. CSV 파일 생성
   ↓
5. Google Sheets에 수동 업로드
```

### 문제점

1. **반복적인 수동 작업**
   - PDF 읽고 정보 추출 (매번)
   - Python 딕셔너리에 하드코딩 (매번)
   - 단지별 폴더 관리 (복잡)

2. **일관성 부족**
   - 단지마다 다른 구조
   - schema 파일 관리 어려움
   - 결과물 분산 (통합 불가)

3. **매물관리 시스템과 분리**
   - CSV → Sheets 수동 업로드
   - 아파트단지 시트와 별도 관리
   - 중복 데이터 발생

---

## 💡 개선 전략

### 🎯 핵심 아이디어

**"PDF를 AI가 읽어서 바로 Google Sheets에 정규화된 데이터로 입력"**

### 새로운 워크플로우 (자동화)

```
1. PDF 입수
   ↓
2. AI Agent (Gemini Vision + Text)
   - PDF 이미지/텍스트 동시 분석
   - 표 구조 자동 인식
   - 데이터 추출 (분양가, 옵션, 일정 등)
   ↓
3. 데이터 정규화 (Python)
   - JSON 형태로 구조화
   - 층수 범위 → 개별 행으로 확장
   - 데이터 검증
   ↓
4. Google Sheets 자동 업로드
   - 아파트단지 시트: 기본 정보
   - 분양가 시트: 동/호/타입별 가격
   - 옵션 시트: 옵션 항목
   - 단지일정 시트: 분양/납부 일정
   ↓
5. 매물DB와 자동 연동
   - Apps Script가 참조하여 자동 입력
```

---

## 🚀 구현 방안

### Phase 1: AI PDF 파싱 시스템 구축

#### 1.1 Gemini Vision API 활용

**장점:**
- 표 이미지를 직접 분석 가능
- 복잡한 레이아웃 이해 가능
- OCR 불필요

**구현:**
```python
# pdf_parser_ai.py
import google.generativeai as genai
from pdf2image import convert_from_path

def extract_apartment_data(pdf_path):
    """PDF에서 아파트 분양 정보 추출 (AI 기반)"""

    # PDF → 이미지 변환
    images = convert_from_path(pdf_path)

    genai.configure(api_key='YOUR_API_KEY')
    model = genai.GenerativeModel('gemini-1.5-pro-vision')

    # 프롬프트 설계
    prompt = """
    이 입주자 모집공고문 이미지를 분석하여 다음 정보를 JSON 형식으로 추출해주세요:

    1. 기본 정보:
       - 단지명
       - 총 세대수
       - 입주예정일
       - 건설사/시행사

    2. 분양가 정보 (표 형태):
       - 타입 (예: 84A, 102)
       - 동 구분 (예: 103동, 104동)
       - 호 구분 (예: 3호, 4호)
       - 층 구분 (예: 5~9층, 10~19층)
       - 분양가 (원 단위)

    3. 옵션 정보:
       - 옵션 분류 (예: 발코니확장, 시스템에어컨)
       - 타입별 옵션 항목
       - 옵션가

    4. 일정 정보:
       - 청약 접수일
       - 당첨자 발표일
       - 계약일
       - 입주 예정일
       - 중도금/잔금 납부 일정

    JSON 형식:
    {
      "기본정보": {...},
      "분양가": [...],
      "옵션": [...],
      "일정": [...]
    }

    **중요**:
    - 층수 범위는 "5~9층" 형식으로 유지
    - 가격은 숫자만 (예: 538000000)
    - 모든 데이터는 표에서 정확히 읽을 것
    """

    all_data = []
    for image in images:
        response = model.generate_content([prompt, image])
        all_data.append(response.text)

    # JSON 병합 및 정리
    merged_data = merge_extracted_data(all_data)
    return merged_data
```

#### 1.2 데이터 정규화 로직

**기존 문제:**
- "5~9층" → 어떻게 개별 행으로 확장?
- "103동 3,4호" → 어떻게 분리?

**해결:**
```python
# normalizer.py
import pandas as pd

def normalize_pricing_data(raw_data):
    """추출된 원시 데이터를 정규화"""

    normalized_rows = []

    for entry in raw_data['분양가']:
        # 1. 타입 추출
        unit_type = entry['타입']

        # 2. 동/호 확장 (예: "103동 3,4호" → [(103, 3), (103, 4)])
        dong_ho_list = expand_dong_ho(entry['동구분'], entry['호구분'])

        # 3. 층/가격 확장 (예: "5~9층" → [(5, 9, 538000000)])
        floor_price_list = expand_floor_range(entry['층구분'], entry['분양가'])

        # 4. 교차 곱 (Cartesian Product)
        for dong, ho in dong_ho_list:
            for min_floor, max_floor, price in floor_price_list:
                # 실제 층수 계산 (호수에서 추출)
                actual_floor = int(str(ho)[:-2]) if len(str(ho)) >= 3 else 1

                # 층수 범위 검증
                if min_floor <= actual_floor <= max_floor:
                    normalized_rows.append({
                        '단지명': raw_data['기본정보']['단지명'],
                        '동': dong,
                        '호': ho,
                        '타입': unit_type,
                        '최저층': min_floor,
                        '최고층': max_floor,
                        '분양가': price
                    })

    return pd.DataFrame(normalized_rows)

def expand_dong_ho(dong_str, ho_str):
    """'103동 3,4호' → [(103, 3), (103, 4)]"""
    # 동 추출 (예: "103동" → 103)
    dong = int(dong_str.replace('동', '').strip())

    # 호 추출 (예: "3,4호" → [3, 4])
    ho_list = [int(h.strip()) for h in ho_str.replace('호', '').split(',')]

    return [(dong, ho) for ho in ho_list]

def expand_floor_range(floor_str, price):
    """'5~9층' → (5, 9, 538000000)"""
    if '~' in floor_str:
        parts = floor_str.replace('층', '').split('~')
        min_floor = int(parts[0].strip())
        max_floor = int(parts[1].strip())
        return [(min_floor, max_floor, price)]
    else:
        # 단일 층 (예: "5층")
        floor = int(floor_str.replace('층', '').strip())
        return [(floor, floor, price)]
```

#### 1.3 Google Sheets 자동 업로드

```python
# sheets_uploader.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def upload_to_sheets(normalized_data, spreadsheet_id):
    """정규화된 데이터를 Google Sheets에 업로드"""

    # 인증
    scope = ['https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope
    )
    client = gspread.authorize(creds)

    # 스프레드시트 열기
    spreadsheet = client.open_by_key(spreadsheet_id)

    # 1. 아파트단지 시트 업데이트
    apartment_sheet = spreadsheet.worksheet('아파트단지')
    basic_info = normalized_data['기본정보']

    # 기존 데이터 확인 (중복 방지)
    existing_data = apartment_sheet.get_all_values()
    if not any(row[0] == basic_info['단지명'] for row in existing_data):
        apartment_sheet.append_row([
            basic_info['단지명'],
            basic_info['단지코드'],
            basic_info['총세대수'],
            basic_info['입주예정일'],
            # ... 나머지 필드
        ])

    # 2. 분양가 시트 업데이트
    price_sheet = spreadsheet.worksheet('분양가')
    price_df = normalized_data['분양가_정규화']

    # DataFrame → List of Lists
    price_data = [price_df.columns.tolist()] + price_df.values.tolist()
    price_sheet.append_rows(price_data[1:])  # 헤더 제외

    # 3. 옵션 시트 업데이트
    option_sheet = spreadsheet.worksheet('옵션')
    for option in normalized_data['옵션']:
        option_sheet.append_row([
            basic_info['단지명'],
            option['타입'],
            option['옵션분류'],
            option['옵션항목'],
            option['옵션가']
        ])

    # 4. 단지일정 시트 업데이트
    schedule_sheet = spreadsheet.worksheet('단지일정')
    for schedule in normalized_data['일정']:
        schedule_sheet.append_row([
            basic_info['단지명'],
            schedule['일정명'],
            schedule['시작일'],
            schedule['종료일']
        ])

    print(f"✅ {basic_info['단지명']} 데이터 업로드 완료!")
```

---

### Phase 2: 통합 아키텍처

#### 새로운 Google Sheets 구조

**기존 시트:**
- 등록검색 (UI)
- 매물DB (매물 정보)
- 고객DB (고객 정보)
- 아파트단지 (단지 마스터)
- 고정값 (설정)

**추가 시트:**
```
📊 분양가 (신규)
└── 단지명 | 동 | 호 | 타입 | 최저층 | 최고층 | 분양가

📊 옵션 (신규)
└── 단지명 | 타입 | 옵션분류 | 옵션항목 | 옵션가

📊 단지일정 (신규)
└── 단지명 | 일정명 | 시작일 | 종료일

📊 발코니 (신규)
└── 단지명 | 타입 | 발코니확장비
```

#### Apps Script 자동 연동

**시나리오: 매물 등록 시 자동 입력**

```javascript
// apps-script/auto_populate.gs
function onApartmentSelected() {
  const regSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('등록검색');
  const apartmentName = regSheet.getRange('C4').getValue(); // 단지명
  const dong = regSheet.getRange('C5').getValue();
  const ho = regSheet.getRange('C6').getValue();
  const type = regSheet.getRange('C7').getValue();

  // 1. 층수 계산
  const floor = Math.floor(ho / 100);

  // 2. 분양가 시트에서 가격 조회
  const priceSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('분양가');
  const priceData = priceSheet.getDataRange().getValues();

  let foundPrice = null;
  for (let i = 1; i < priceData.length; i++) {
    const row = priceData[i];
    if (row[0] === apartmentName &&
        row[1] === dong &&
        row[3] === type &&
        floor >= row[4] && floor <= row[5]) {
      foundPrice = row[6];
      break;
    }
  }

  // 3. 분양가 자동 입력
  if (foundPrice) {
    regSheet.getRange('C10').setValue(foundPrice); // 분양가 셀
  }

  // 4. 옵션 목록 불러오기
  const optionSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('옵션');
  const optionData = optionSheet.getDataRange().getValues();

  const availableOptions = optionData.filter(row =>
    row[0] === apartmentName && row[1] === type
  );

  // 5. 옵션 드롭다운 생성
  // ... (코드 생략)
}
```

---

## 🎯 실행 계획

### Step 1: AI PDF 파싱 테스트 (3일)

**대상:** 기존 PDF 1개 (힐스테이트두정역)

- [ ] Gemini Vision API 설정
- [ ] PDF → 이미지 변환
- [ ] 프롬프트 엔지니어링
- [ ] JSON 추출 테스트
- [ ] 정확도 검증 (수동 비교)

**성공 기준:**
- 분양가 정확도 95% 이상
- 옵션 정보 90% 이상 추출

### Step 2: 정규화 로직 구현 (2일)

- [ ] `normalizer.py` 작성
- [ ] 동/호 확장 로직
- [ ] 층/가격 확장 로직
- [ ] 테스트 (기존 CSV와 비교)

### Step 3: Sheets 연동 (2일)

- [ ] `sheets_uploader.py` 작성
- [ ] 새 시트 4개 추가 (분양가, 옵션, 단지일정, 발코니)
- [ ] 데이터 업로드 테스트

### Step 4: Apps Script 자동화 (3일)

- [ ] `onApartmentSelected()` 함수 작성
- [ ] 분양가 자동 입력 기능
- [ ] 옵션 자동 불러오기 기능
- [ ] 통합 테스트

### Step 5: 전체 파이프라인 테스트 (2일)

- [ ] 새 PDF로 E2E 테스트
- [ ] 성능 측정 (처리 시간)
- [ ] 문서화

**총 예상 기간:** 2주

---

## 💰 비용 및 효과 분석

### 기존 방식 vs 신규 방식

| 항목 | 기존 (수동) | 신규 (AI 자동화) | 개선율 |
|------|------------|-----------------|--------|
| 단지 1개 처리 시간 | 4시간 | 10분 | ▼96% |
| 오류 발생 가능성 | 높음 | 매우 낮음 | ▼90% |
| 확장성 | 어려움 | 쉬움 | - |
| Sheets 연동 | 수동 | 자동 | 100% |

### 비용

**Gemini API:**
- 이미지 처리: $0.00025/이미지
- PDF 평균 20페이지 = $0.005/단지
- 월 100개 단지 처리 = $0.50/월

**결론:** 거의 무료 수준! 🎉

---

## 🔗 통합 후 전체 시스템

```
[입주자 모집공고 PDF]
         ↓
   [AI PDF 파싱]
   (Gemini Vision)
         ↓
   [데이터 정규화]
   (Python)
         ↓
   [Google Sheets 업로드]
   (분양가/옵션/일정/발코니 시트)
         ↓
   [Apps Script 자동화]
   (등록검색 시트에서 자동 입력)
         ↓
   [매물DB 저장]
         ↓
   [일일 브리핑 자동 생성]
         ↓
   [마케팅 콘텐츠 발행]
```

**완전 자동화 완성!** 🚀

---

## 📝 다음 단계

### 즉시 시작 가능:

1. **Gemini API 키 발급** (무료)
2. **테스트 PDF 1개 선택** (힐스테이트두정역)
3. **AI 프롬프트 작성 & 테스트**

### 장기 계획:

1. **다른 단지 확장** (천안신부더샵센트라, 아산탕정 등)
2. **OCR 고도화** (손글씨, 스캔 품질 낮은 PDF 대응)
3. **실시간 모니터링** (새 PDF 업로드 시 자동 처리)

---

## 🔗 관련 문서

- [[📝 프로젝트 허브]]
- [[📋 통합 마스터플랜 - 기존 시스템 개선 + 확장]]
- [[아파트_분양정보_정규화_에이전트_지침]] (기존)
- [[분양가 옵션가 DB구축 플랜]] (기존)

---

**🚀 "AI로 4시간 작업을 10분으로!"**
