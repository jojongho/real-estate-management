# AppSheet 고정값 드롭다운 설정 가이드

## 📊 고정값 테이블 정보
**Spreadsheet ID**: `1cFePAgehODmcTiPoWoDKOg2kIZSd2Zu2ZaiFL36ucVE`

**목적**: 일관된 데이터 입력을 위한 드롭다운 참조 테이블

---

## 🎯 AppSheet에서 드롭다운 만드는 3가지 방법

### 방법 비교표

| 방법 | 데이터 위치 | 변경 용이성 | 설정 난이도 | 추천 케이스 |
|------|------------|------------|------------|------------|
| **Enum** | AppSheet 앱 내부 | 낮음 (수동) | ⭐ 쉬움 | 고정값, 변경 적음 |
| **Ref** | 스프레드시트 | 높음 (자동) | ⭐⭐ 중간 | 자주 변경, 추가 정보 필요 |
| **Valid_If** | 수식/스프레드시트 | 높음 (조건부) | ⭐⭐⭐ 어려움 | 조건부 필터링 |

---

## 방법 1: Enum 타입 (정적 리스트) ⭐ 추천

### 언제 사용?
- **고정값**이 거의 변하지 않을 때
- 빠른 성능이 필요할 때
- 간단한 드롭다운

### 예시: 고객구분, 거래유형

#### STEP 1: 컬럼 타입 설정
```
Data → Columns → 아파트매물 → 거래유형 (또는 해당 컬럼)

Type: Enum

Type Details:
  Values:
    매매
    전세
    월세
    임대
```

#### STEP 2: 값 입력 방법

**직접 입력**:
```
Values 필드에 한 줄씩 입력:
매매
전세
월세
임대
```

**또는 쉼표 구분**:
```
매매, 전세, 월세, 임대
```

#### STEP 3: 기타 설정
```
Base type: Text (기본값)
Input mode: Dropdown
Allow other values: ❌ (정해진 값만 입력)
```

### 장점
- ✅ 설정 간단
- ✅ 빠른 성능
- ✅ 오프라인 작동

### 단점
- ❌ 값 변경 시 앱에서 수동 수정 필요
- ❌ 스프레드시트와 분리 관리

---

## 방법 2: Ref 타입 (동적 참조) ⭐⭐ 중앙 관리

### 언제 사용?
- 값이 **자주 변경**될 때
- **스프레드시트에서 중앙 관리**하고 싶을 때
- 추가 정보(설명, 순서 등)가 필요할 때

### 예시: 단지명 목록

#### STEP 1: 참조 테이블 준비 (스프레드시트)

**고정값 시트 구조**:
| 단지명 | 단지명축약 | 순서 |
|--------|-----------|------|
| 힐스테이트두정역 | 힐스 | 1 |
| 탕정더샵퍼스트파크 | 탕샵 | 2 |
| 아산성팍리슈빌 | 성팍 | 3 |

#### STEP 2: AppSheet에 데이터 추가
```
Data → + New table
→ Google Sheets 선택
→ Spreadsheet: 1cFePAgehODmcTiPoWoDKOg2kIZSd2Zu2ZaiFL36ucVE
→ Sheet: 단지명목록 (또는 해당 시트명)
```

#### STEP 3: 참조 테이블 설정
```
Data → Columns → 단지명목록

단지명:
  Type: Text
  Label: ✅ (체크) ← 중요! 이게 드롭다운에 표시됨

단지명축약:
  Type: Text

순서:
  Type: Number
```

#### STEP 4: Ref 컬럼 설정
```
Data → Columns → 아파트매물 → 단지명

Type: Ref

Type Details:
  Source table: 단지명목록
  Label column: 단지명 (자동 선택됨)

Input mode: Dropdown
```

#### STEP 5: 정렬 설정 (선택사항)
```
UX → Views → 아파트매물_Form
→ Column order → 단지명 클릭
→ Dropdown options:
    Sort by: 순서
    Sort order: Ascending
```

### 장점
- ✅ 스프레드시트에서 중앙 관리
- ✅ 값 변경 시 자동 반영 (앱 Sync만 하면 됨)
- ✅ 추가 정보 활용 가능 (축약명, 순서 등)

### 단점
- ❌ 설정 복잡
- ❌ 약간 느린 성능 (큰 차이 없음)

---

## 방법 3: Valid_If 표현식 (조건부 필터링) ⭐⭐⭐ 고급

### 언제 사용?
- **다른 필드 값에 따라** 드롭다운 목록이 달라질 때
- 계층 구조 (단지 → 동 → 호)

### 예시 1: 단지별 동 목록 필터링

#### 전제 조건
```
"동목록" 테이블 구조:
| 단지명 | 동 |
|--------|-----|
| 힐스테이트두정역 | 101 |
| 힐스테이트두정역 | 102 |
| 탕정더샵퍼스트파크 | 103 |
```

#### STEP 1: 동목록 테이블 추가
```
Data → + New table
→ 고정값 시트에서 "동목록" 선택
```

#### STEP 2: Valid_If 설정
```
Data → Columns → 아파트매물 → 동

Type: Text (또는 Number)

Data Validity:
  Valid If:
    SELECT(동목록[동], [단지명] = [_THISROW].[단지명])
```

**수식 설명**:
- `SELECT(동목록[동], ...)`: 동목록 테이블에서 동 값 가져오기
- `[단지명] = [_THISROW].[단지명]`: 현재 선택한 단지명과 일치하는 것만

#### STEP 3: 테스트
```
1. 단지명에서 "힐스테이트두정역" 선택
2. 동 필드 클릭
3. 드롭다운에 "101", "102"만 표시됨 (해당 단지 동만)
```

### 예시 2: 스프레드시트 범위에서 직접 가져오기

#### STEP 1: Suggested values 사용
```
Data → Columns → 아파트매물 → 거래유형

Type: Text

Auto Compute:
  Suggested values:
    IMPORTRANGE("1cFePAgehODmcTiPoWoDKOg2kIZSd2Zu2ZaiFL36ucVE", "고정값!A2:A10")
```

**참고**: AppSheet는 IMPORTRANGE 직접 지원 안 함. 대신:

#### STEP 2: 스프레드시트에 Named Range 만들기
```
Google Sheets:
1. 고정값 시트에서 범위 선택 (예: A2:A10)
2. Data → Named ranges → Add range
3. Name: 거래유형목록
```

#### STEP 3: AppSheet에서 참조
```
Data → Columns → 거래유형

Type: Enum

Type Details:
  Values: (수동 복사 붙여넣기)
  또는
  Suggested values:
    LOOKUP(...) 수식 활용
```

### 장점
- ✅ 동적 필터링
- ✅ 계층 구조 지원
- ✅ 유연성 높음

### 단점
- ❌ 수식 복잡
- ❌ 디버깅 어려움

---

## 🎯 권장 설정 (실무 기준)

### 고객구분
```
Type: Enum
Values: 매도인, 임대인, 임차인, 손님, 타부동산, 분양직원
이유: 변경 빈도 낮음, 고정값
```

### 거래유형
```
Type: Enum
Values: 매매, 전세, 월세, 임대
이유: 변경 빈도 낮음, 고정값
```

### 단지명
```
Type: Ref
Source table: 아파트단지 (1tOJWkgAWy6fRCSVbW1dpYT73LBwPVPuo54v8Jjlwlss)
이유: 단지 추가/변경 가능, 추가 정보 필요 (단지명축약 등)
```

### 동
```
방법 A (단순): Type: Text, 사용자 직접 입력
방법 B (고급): Valid_If로 단지별 동 필터링
```

### 호
```
방법 A (단순): Type: Text, 사용자 직접 입력
방법 B (고급): Valid_If로 동별 호 필터링
```

### 타입
```
방법 A (단순): Type: Text, 사용자 직접 입력
방법 B (고급): Valid_If로 단지별 타입 필터링
```

---

## 🛠️ 실전 구현 가이드

### STEP 1: 고정값 시트 구조 파악

**먼저 확인할 사항**:
1. 고정값 시트에 어떤 데이터가 있나요?
2. 각 컬럼명은 무엇인가요?
3. 데이터 예시는?

**스크린샷이나 구조를 공유해주시면 정확한 설정 방법을 알려드릴 수 있습니다!**

### STEP 2: 활용 계획 수립

**질문**:
1. 어떤 필드에 드롭다운을 적용하고 싶으신가요?
2. 값이 자주 변경되나요?
3. 조건부 필터링이 필요한가요? (예: 단지 선택 시 동 목록 변경)

### STEP 3: 단계별 구현

**우선순위**:
1. 간단한 Enum부터 (고객구분, 거래유형)
2. Ref 설정 (단지명)
3. 고급 Valid_If (필요시)

---

## 💡 팁

### Enum vs Ref 선택 기준
```
Q: 1년에 몇 번이나 값이 바뀌나요?
A: 0-2번 → Enum 추천
A: 3번 이상 → Ref 추천
```

### 성능 고려
```
드롭다운 항목 100개 미만: Enum, Ref 모두 OK
드롭다운 항목 100개 이상: Ref + 검색 기능 활용
```

### 사용자 경험
```
Input mode:
- Dropdown: 항목 30개 이하
- Auto: 항목 30개 이상 (검색 가능)
- Buttons: 항목 5개 이하 (시각적으로 선택)
```

---

## 🚀 실제 고정값 시트 분석 완료!

### 📊 확인된 시트 구조

**Spreadsheet ID**: `1cFePAgehODmcTiPoWoDKOg2kIZSd2Zu2ZaiFL36ucVE`
**제목**: Dev. 목록원본 앱시트

### 시트 탭 목록
1. **데이터확인_list** - 다양한 속성 통합 리스트
2. **시도** - 시/도 행정구역
3. **시군구** - 시/군/구 행정구역
4. **동읍면** - 동/읍/면 행정구역
5. **통반리** - 통/반/리 행정구역
6. **아파트단지목록** - 아파트 단지명

### 데이터확인_list 시트 컬럼
| 컬럼 | 용도 | AppSheet 설정 권장 |
|------|------|-------------------|
| 담당자 | 사용자명 | Text 또는 Ref (사용자 테이블) |
| 성별 | 성별 구분 | Enum: 남, 여 |
| 용도지역 | 토지 용도 | Ref (별도 시트 정리 필요) |
| 지목 | 토지 지목 | Ref (별도 시트 정리 필요) |
| 건축물명 | 건물 타입 | Ref (별도 시트 정리 필요) |
| 주택유형 | 주택 분류 | Ref (별도 시트 정리 필요) |
| 건축물주용도 | 건물 용도 | Ref (별도 시트 정리 필요) |
| 난방방식 | 난방 타입 | Enum: 개별난방, 중앙난방, 지역난방 |
| 건축물구조 | 구조 타입 | Ref (별도 시트 정리 필요) |
| 거래유형 | 거래 방식 | Enum: 매매, 전세, 월세, 임대 |
| 월부담(월구조) | 방 구조 | Text (자유 입력) |

---

## 🎯 매물 관리 앱을 위한 실전 가이드

### STEP 1: 간단한 고정값부터 (Enum 방식)

#### 거래유형 설정
```
Data → Columns → 아파트매물 → 거래유형

Type: Enum
Values:
  매매
  전세
  월세
  임대

Base type: Text
Allow other values: ❌
```

#### 난방방식 설정
```
Data → Columns → 아파트매물 → 난방방식

Type: Enum
Values:
  개별난방
  중앙난방
  지역난방
  기타

Allow other values: ❌
```

---

### STEP 2: 행정구역 계층 구조 (Valid_If)

#### 전제 조건
고정값 시트에 **시도, 시군구, 동읍면, 통반리** 시트가 있으므로 이를 AppSheet에 추가

#### 2-1. AppSheet에 참조 테이블 추가
```
Data → + New table (4개 시트 모두 추가)
→ Spreadsheet: 1cFePAgehODmcTiPoWoDKOg2kIZSd2Zu2ZaiFL36ucVE
→ Sheets: 시도, 시군구, 동읍면, 통반리
```

#### 2-2. 시도 설정 (Ref)
```
Data → Columns → 아파트매물 → 시도

Type: Ref
Source table: 시도
Label column: 시도명 (또는 해당 컬럼명)
```

#### 2-3. 시군구 설정 (Valid_If)
```
Data → Columns → 아파트매물 → 시군구

Type: Text

Data Validity → Valid If:
SELECT(시군구[시군구명], [시도] = [_THISROW].[시도])

설명: 선택한 시도에 속한 시군구만 드롭다운에 표시
```

#### 2-4. 동읍면 설정 (Valid_If)
```
Data → Columns → 아파트매물 → 동읍면

Type: Text

Valid If:
SELECT(동읍면[동읍면명], [시군구] = [_THISROW].[시군구])
```

#### 2-5. 통반리 설정 (Valid_If)
```
Data → Columns → 아파트매물 → 통반리

Type: Text

Valid If:
SELECT(통반리[통반리명], [동읍면] = [_THISROW].[동읍면])
```

**사용자 경험**:
1. 시도 선택: "충청남도"
2. 시군구 드롭다운: 천안시, 아산시 등 (충청남도 소속만 표시)
3. 동읍면 드롭다운: 탕정면, 음봉면 등 (선택한 시군구 소속만)
4. 통반리 드롭다운: 해당 동읍면 소속만

---

### STEP 3: 복잡한 참조 데이터 정리

#### 문제점
현재 **데이터확인_list** 시트에 여러 속성이 섞여 있음

#### 권장 조치

**새로운 시트 생성** (고정값 스프레드시트에):
1. **용도지역** 시트
   - A열: 코드 (예: UZ01)
   - B열: 용도지역명 (예: 제1종전용주거지역)

2. **지목** 시트
   - A열: 코드
   - B열: 지목명 (전, 답, 과수원, 임야 등)

3. **주택유형** 시트
   - A열: 코드
   - B열: 유형명 (아파트, 오피스텔, 단독주택 등)

4. **건축물구조** 시트
   - A열: 코드
   - B열: 구조명 (철근콘크리트, 경량철골 등)

#### AppSheet 적용
```
Data → + New table (각 시트 추가)

각 필드 설정:
Type: Ref
Source table: 해당 참조 테이블
Label column: 명칭 컬럼
```

---

## 💡 빠른 시작 가이드

### 지금 바로 적용 가능한 것

#### 1. 거래유형 (5분)
```
Data → Columns → 아파트매물 → 거래유형
Type: Enum
Values: 매매, 전세, 월세, 임대
Done!
```

#### 2. 단지명 (이미 있음)
```
이미 아파트단지 Ref로 설정되어 있음 ✅
Source: 1tOJWkgAWy6fRCSVbW1dpYT73LBwPVPuo54v8Jjlwlss
```

#### 3. 행정구역 (10분)
```
1. Data → + New table → 시도 추가
2. Data → + New table → 시군구 추가
3. 시도 필드: Type = Ref, Source = 시도
4. 시군구 필드: Valid_If = SELECT(시군구[명], [시도] = [_THISROW].[시도])
```

---

## 🔧 다음 작업 우선순위

### 우선순위 1 (바로 적용)
- ✅ 거래유형: Enum
- ✅ 고객구분: Enum (매도인, 임대인, 임차인, 손님)

### 우선순위 2 (데이터 정리 후)
- 용도지역, 지목, 주택유형 등 참조 테이블 생성
- AppSheet Ref 설정

### 우선순위 3 (고급 기능)
- 행정구역 계층 구조 Valid_If
- 조건부 필터링

---

어떤 필드부터 드롭다운으로 만들어볼까요? 🚀
