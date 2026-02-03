# AppSheet 매물+고객 동시 등록 워크플로우 구현 가이드

## 📋 목표
매물(아파트매물) 입력 시 고객 정보도 함께 등록하고, 양방향 참조가 자동으로 연결되는 통합 입력 시스템 구현

## 🗂️ 데이터베이스 구조

### 1. 아파트단지 (Master DB)
**Spreadsheet ID**: `1tOJWkgAWy6fRCSVbW1dpYT73LBwPVPuo54v8Jjlwlss`
- 상위 마스터 데이터
- 아파트매물과 1:N 관계

### 2. 고객DB (Customer Database)
**Spreadsheet ID**: `1h49R9JBWswPlgqRmcBoitQfZ1v5I2dcAbq0Ksv9_dVw` - Sheet: 고객DB

| 컬럼명 | Type | Required | Description |
|--------|------|----------|-------------|
| 고객ID | Key | ✅ | UNIQUEID() 자동 생성 |
| 고객명 | Text | ✅ | Label column for Ref |
| 연락처 | Phone | ✅ | 010-XXXX-XXXX |
| 고객구분 | Enum | ✅ | 매도인, 임대인, 임차인, 손님, 타부동산, 분양직원 |
| 메모 | LongText | ❌ | Additional notes |

### 3. 아파트매물 (Property Database)
**Spreadsheet ID**: `1h49R9JBWswPlgqRmcBoitQfZ1v5I2dcAbq0Ksv9_dVw` - Sheet: 아파트매물

| 컬럼명 | Type | Required | Description |
|--------|------|----------|-------------|
| 매물ID | Key | ✅ | UNIQUEID() 자동 생성 |
| **고객** | **Ref → 고객DB** | ✅ | **Customer reference (핵심!)** |
| 단지명 | Ref → 아파트단지 | ✅ | Complex reference |
| 동 | Text | ✅ | Building number |
| 호 | Text | ✅ | Unit number |
| 타입 | Text | ✅ | Unit type (84A, 102, etc.) |
| 거래유형 | Enum | ✅ | 매매, 전세, 월세, 임대 |
| 분양가 | Decimal | ❌ | Sale price (만원) |
| 발코니 | Decimal | ❌ | Balcony price (만원) |
| 옵션비 | Decimal | ❌ | Options total (만원) |
| 프리미엄 | Decimal | ❌ | Premium (만원) |
| 합계 | Decimal (Virtual) | ❌ | Auto-calculated sum |

### 4. Virtual Columns in 아파트매물

| 컬럼명 | App Formula | Purpose |
|--------|-------------|---------|
| D_C_ID | `CONCATENATE([단지명].[단지명축약], "-", [동], "동-", [호], "호-", [타입], "타입-", [거래유형], "(", [고객].[고객구분], ")")` | Display identifier |
| 고객연락처 | `[고객].[연락처]` | Dereferenced customer phone |
| 고객구분 | `[고객].[고객구분]` | Dereferenced customer type |
| 합계 | `SUM(LIST([분양가], [발코니], [옵션비], [프리미엄]))` | Total amount |

### 5. Virtual Columns in 고객DB

| 컬럼명 | App Formula | Purpose |
|--------|-------------|---------|
| Related 아파트매물 | `REF_ROWS("아파트매물", "고객")` | List of properties for this customer |

---

## ⚙️ Step-by-Step 구현 가이드

### STEP 1: 고객DB 테이블 설정

#### 1.1 AppSheet에서 고객DB 연결
1. AppSheet → Data → + New table
2. Google Sheets 선택
3. Spreadsheet: `1h49R9JBWswPlgqRmcBoitQfZ1v5I2dcAbq0Ksv9_dVw`
4. Sheet: `고객DB`

#### 1.2 고객DB 컬럼 설정
```
고객ID:
  Type: Key
  Initial value: UNIQUEID()

고객명:
  Type: Text
  Required: Yes

연락처:
  Type: Phone
  Required: Yes

고객구분:
  Type: Enum
  Values: 매도인, 임대인, 임차인, 손님, 타부동산, 분양직원
  Required: Yes

메모:
  Type: LongText
  Required: No
```

#### 1.3 Virtual Column 추가 (Related 아파트매물)
1. Columns → + Add virtual column
2. Settings:
   - Name: `Related 아파트매물`
   - App formula: `REF_ROWS("아파트매물", "고객")`
   - Type: List
   - Description: "이 고객의 모든 매물 목록"

---

### STEP 2: 아파트매물 테이블 설정

#### 2.1 핵심 Ref 컬럼 설정 (고객)

**⚠️ 가장 중요한 설정!**

```
컬럼명: 고객
Type: Ref
Source table: 고객DB
Label column: 고객명
Display name: 의뢰인

✅ Allow other values: ON
✅ Is part of?: ON  ← 이게 핵심! 매물 저장 시 고객도 함께 저장됨
```

**Is part of? 옵션 설명**:
- ON으로 설정하면 매물 입력 중 새 고객을 등록하면 매물 저장 시 고객 정보도 함께 저장됨
- 부모-자식 관계에서 "부분(part)" 개념
- 매물이 고객의 "일부"로 간주되어 함께 저장

#### 2.2 Virtual Columns 추가

**D_C_ID (Display ID)**
```
Name: D_C_ID
Type: Text
App formula:
CONCATENATE(
  [단지명].[단지명축약], "-",
  [동], "동-",
  [호], "호-",
  [타입], "타입-",
  [거래유형],
  "(", [고객].[고객구분], ")"
)
```

**고객연락처**
```
Name: 고객연락처
Type: Phone
App formula: [고객].[연락처]
```

**고객구분**
```
Name: 고객구분
Type: Text
App formula: [고객].[고객구분]
```

**합계**
```
Name: 합계
Type: Decimal
App formula: SUM(LIST([분양가], [발코니], [옵션비], [프리미엄]))
```

---

### STEP 3: Form View 설정 (아파트매물)

#### 3.1 Form 생성
1. UX → Views → + New view
2. View type: `form`
3. For this data: `아파트매물`
4. View name: `아파트매물_입력폼`

#### 3.2 Form 필드 순서 설정

**권장 입력 순서**:
```
1. 고객 (Ref to 고객DB) ← 맨 위에 배치
   ↓
2. 단지명 (Ref to 아파트단지)
   ↓
3. 동
   ↓
4. 호
   ↓
5. 타입
   ↓
6. 거래유형
   ↓
7. 분양가
   ↓
8. 발코니
   ↓
9. 옵션비
   ↓
10. 프리미엄
   ↓
11. 합계 (Virtual - auto-calculated, 표시만)
```

#### 3.3 고객 필드 UX 설정

Form view → Column order → `고객` 필드 클릭

**Display**:
```
✅ Show: ON
Display name: 의뢰인
Help text: "기존 고객을 선택하거나 + 버튼으로 새 고객을 등록하세요"
```

**Input**:
```
✅ Editable: ON
✅ Required: ON
✅ Allow adds: ON  ← 중요! 새 고객 등록 버튼 활성화
```

---

### STEP 4: Form View 설정 (고객DB)

#### 4.1 고객 입력 폼 생성
1. UX → Views → + New view
2. View type: `form`
3. For this data: `고객DB`
4. View name: `고객_입력폼`

#### 4.2 Form 필드 최소화 (빠른 입력)

**표시할 필드만**:
```
1. 고객명 (Required)
2. 연락처 (Required)
3. 고객구분 (Required)
4. 메모 (Optional)
```

**숨길 필드**:
```
- 고객ID (자동 생성)
- Related 아파트매물 (나중에 상세 화면에서 표시)
```

---

### STEP 5: 사용자 워크플로우 테스트

#### 시나리오 1: 기존 고객 + 새 매물 등록

**사용자 액션**:
1. 앱 실행 → "아파트매물" 탭
2. `+` 버튼 (새 매물 등록)
3. **의뢰인** 필드 클릭 → 드롭다운에서 기존 고객 선택
4. 단지명, 동, 호, 타입, 거래유형 입력
5. 금액 정보 입력 (분양가, 발코니, 옵션비, 프리미엄)
6. 저장 버튼

**자동 처리**:
- 매물ID 자동 생성
- D_C_ID 자동 생성 (예: "힐스-101동-1201호-84A타입-매매(매도인)")
- 고객연락처 자동 표시
- 고객구분 자동 표시
- 합계 자동 계산
- 고객 상세 화면의 "Related 아파트매물"에 자동 추가

---

#### 시나리오 2: 신규 고객 + 신규 매물 동시 등록

**사용자 액션**:
1. 앱 실행 → "아파트매물" 탭
2. `+` 버튼 (새 매물 등록)
3. **의뢰인** 필드 클릭 → `+ 새 고객 추가` 버튼 클릭
4. **고객 입력 폼 팝업**:
   - 고객명: "홍길동"
   - 연락처: "010-1234-5678"
   - 고객구분: "매도인"
   - 저장 버튼
5. **자동으로 매물 입력 폼으로 복귀** (고객 Ref 자동 연결됨)
6. 단지명, 동, 호, 타입, 거래유형 입력
7. 금액 정보 입력
8. 저장 버튼

**자동 처리**:
- 고객DB에 "홍길동" 저장됨
- 매물의 [고객] Ref가 "홍길동"으로 자동 연결
- D_C_ID에 "...(매도인)" 포함
- 고객연락처: "010-1234-5678" 자동 표시
- 고객 상세 화면에서 이 매물 자동 표시

---

### STEP 6: 고객 상세 화면 설정 (양방향 참조)

#### 6.1 고객 Detail View 생성
1. UX → Views → + New view
2. View type: `detail`
3. For this data: `고객DB`
4. View name: `고객_상세`

#### 6.2 Related 아파트매물 표시 설정

**Ref Views**:
```
View → Options → Ref views
✅ Show: Related 아파트매물
Display name: 소유/의뢰 매물 목록
View type: Table or Card (선택)
```

**결과**:
- 고객 상세 화면 하단에 이 고객과 연결된 모든 매물이 자동으로 표시됨
- 예시:
  ```
  홍길동 (매도인)
  010-1234-5678

  --- 소유/의뢰 매물 목록 ---
  🏠 힐스-101동-1201호-84A타입-매매(매도인)
  🏠 탕정-205동-801호-102타입-전세(매도인)
  ```

---

## 🎯 구현 완료 체크리스트

### Data Structure
- [ ] 고객DB 테이블 연결 및 컬럼 설정
- [ ] 아파트매물 테이블 연결 및 컬럼 설정
- [ ] 아파트단지 테이블 연결 (Ref 용)
- [ ] 고객 Ref 컬럼 설정 (Is part of? ON)
- [ ] Virtual Columns 모두 생성 (D_C_ID, 고객연락처, 고객구분, 합계, Related 아파트매물)

### Forms
- [ ] 아파트매물_입력폼 생성 및 필드 순서 설정
- [ ] 고객_입력폼 생성 (최소 필드만)
- [ ] 고객 필드에 "Allow adds" 활성화
- [ ] Required 필드 설정

### Views
- [ ] 고객_상세 view 생성
- [ ] Related 아파트매물 표시 설정
- [ ] 매물 목록 view 생성 (선택)

### Testing
- [ ] 기존 고객 선택 → 매물 등록 테스트
- [ ] 신규 고객 등록 → 매물 등록 동시 테스트
- [ ] Virtual Column 자동 계산 검증
- [ ] 고객 상세 화면에서 Related 매물 표시 확인
- [ ] Ref 관계 양방향 동작 확인

---

## 💡 핵심 포인트 요약

### 1. Is part of? 옵션이 핵심
```
[고객] Ref 컬럼에서 "Is part of? = ON"
→ 매물 저장 시 연결된 고객도 함께 저장됨
→ 신규 고객을 폼에서 바로 등록 가능
```

### 2. Virtual Columns로 자동 표시
```
고객연락처 = [고객].[연락처]
고객구분 = [고객].[고객구분]
→ Ref 관계를 통해 자동으로 고객 정보 표시
→ 별도 입력 불필요
```

### 3. 양방향 참조
```
아파트매물 → 고객: Ref 컬럼
고객 → 아파트매물: REF_ROWS() Virtual Column
→ 양쪽에서 서로의 데이터 자동 표시
```

### 4. 사용자 경험
```
매물 입력 중 고객 선택:
  - 기존 고객: 드롭다운 선택
  - 신규 고객: + 버튼 → 팝업 폼 → 저장 → 자동 복귀

→ 한 번의 플로우로 매물+고객 모두 등록 완료
```

---

## 🔧 트러블슈팅

### 문제 1: 고객 필드에 + 버튼이 안 보임
**해결**:
- 고객 컬럼 → UX → Allow adds: ON 확인
- Form view → Column options → 고객 → Allow adds 활성화

### 문제 2: 신규 고객 등록 후 매물로 복귀 안 됨
**해결**:
- Is part of? 옵션이 ON인지 확인
- 고객 폼의 Required 필드가 모두 채워졌는지 확인

### 문제 3: Related 아파트매물이 안 보임
**해결**:
- 고객DB에 Virtual Column "Related 아파트매물" 있는지 확인
- App formula: `REF_ROWS("아파트매물", "고객")` 정확한지 확인
- 고객 Detail view에 Ref views 설정 확인

### 문제 4: Virtual Column이 계산 안 됨
**해결**:
- Ref 관계가 제대로 설정되었는지 확인
- [고객] 컬럼이 Text가 아닌 Ref 타입인지 확인
- AppSheet Sync 후 테스트

---

## 📚 참고 자료

### AppSheet 공식 문서
- Ref columns: https://help.appsheet.com/en/articles/961335
- Virtual columns: https://help.appsheet.com/en/articles/961337
- Is part of?: https://help.appsheet.com/en/articles/961730

### 프로젝트 관련 문서
- [매물관리 앱시트 만들기 내용.md](./매물관리%20앱시트%20만들기%20내용.md) - ChatGPT 대화 내용
- [CLAUDE.md](../CLAUDE.md) - 프로젝트 전체 가이드
