# WordPress + AppSheet 고객 접수 폼 설정 가이드

**목적**: iusell.cheonan-asan.com에 간단한 관심 고객 접수 폼 추가

---

## 🎯 요구사항 정리

### WordPress 페이지: iusell.cheonan-asan.com
### 목적: 관심있는 고객이 간단히 정보 입력
### 타겟 단지: 
- **아산배방1단지우방아이유쉘**
- **아산배방우방아이유쉘2단지**

### 입력 필드:
- **단지명** (2개 중 선택)
- **동** (선택한 단지의 동만 표시)
- **호** (선택한 동의 호만 표시)
- **타입** (선택한 동+호의 타입만 표시)

### 고객 정보:
- **이름** (고객DB.고객성함)
- **연락처** (고객DB.연락처)
- **고객구분** (고객DB.고객구분)
- **고객주소** (고객DB.고객주소)

### 숨길 정보:
- ❌ 분양가 (공개 안 함)
- ❌ 발코니 확장비 (분양가에 포함됨)
- ❌ 옵션 정보 (필요 없음)

---

## 📋 작업 단계

### Phase 1: 별도 고객 접수용 뷰 생성 ⭐⭐⭐⭐⭐

#### 1단계: Slice 생성 (단지 필터링)

**목적**: 2개 단지만 선택 가능하게

```
□ AppSheet → Data → Tables → 고객DB 선택
□ Slices 탭 클릭
□ + New Slice 클릭

□ Slice name: "배방우방아이유쉘_관심고객"

□ Condition 입력:
IN([단지명], ["아산배방1단지우방아이유쉘", "아산배방우방아이유쉘2단지"])

□ Save
```

---

#### 2단계: 별도 Form 뷰 생성 (고객 접수용)

```
□ UX → Views 클릭
□ + Add View 클릭

□ View type: Form 선택
□ Detail table: 고객DB 선택
□ Detail slice: 배방우방아이유쉘_관심고객 (위에서 만든 Slice)
□ Form name: "배방우방아이유쉘_고객접수"

□ Next
```

---

#### 3단계: 폼 필드 배치

**필수 필드만 표시**:

```
□ 왼쪽 필드 목록에서 다음 필드만 추가:

1️⃣ 매물 정보 섹션
   □ 단지명 (Ref → 아파트단지)
   □ 동 (Valid_If 필터링)
   □ 호 (Valid_If 필터링)
   □ 타입 (Valid_If 필터링)

2️⃣ 고객 정보 섹션
   □ 고객성함 (Name)
   □ 연락처 (Phone) - 필수
   □ 고객구분 (Enum)
   □ 고객주소 (Address)

❌ 안 보이게 할 필드들:
   - 고객ID (자동 생성되므로 숨김)
   - 접수일 (자동 생성되므로 숨김)
   - 메모
   - 유입경로 (기본값 설정)
   - 기타 모든 매물 세부 정보
```

---

### Phase 2: Valid_If 조건 설정

#### 동 필드 필터링

```
□ Data → Tables → 고객DB → Columns → 동 필드 클릭

□ Type: Text (또는 Number)

□ Data Validity 섹션으로 스크롤
□ Valid If 필드에 입력:
SELECT(DISTINCT(분양가[동]), [단지명] = [_THISROW].[단지명])

□ Input mode: Dropdown

□ Save
```

⚠️ **주의**: 이 수식은 `분양가` 테이블이 있어야 함. 만약 없으면:
- 방법 1: 아파트단지 테이블의 동 정보 활용
- 방법 2: 직접 입력 (고객이 직접 입력)

---

#### 호 필드 필터링

```
□ Data → Columns → 고객DB → 호 필드 클릭

□ Valid If:
SELECT(DISTINCT(분양가[호]), 
  AND(
    [단지명] = [_THISROW].[단지명],
    [동] = [_THISROW].[동]
  )
)

□ Input mode: Dropdown

□ Save
```

---

#### 타입 필드 필터링

```
□ Data → Columns → 고객DB → 타입 필드 클릭

□ Valid If:
SELECT(DISTINCT(분양가[타입]), 
  AND(
    [단지명] = [_THISROW].[단지명],
    [동] = [_THISROW].[동],
    [호] = [_THISROW].[호]
  )
)

□ Save
```

---

### Phase 3: 자동값 설정

#### 유입경로 기본값

```
□ Data → Columns → 고객DB → 유입경로 클릭

□ Initial Value 섹션:
Value: "온라인광고"

□ Save
```

#### 거래상태 기본값

```
□ Data → Columns → 고객DB → 거래상태 클릭

□ Initial Value:
Value: "관심등록"

□ Save
```

(또는 거래상태 Enum에 "관심등록" 추가 필요)

---

### Phase 4: WordPress에 임베딩

#### AppSheet 공개 폼 링크 생성

```
□ UX → Views → 배방우방아이유쉘_고객접수 선택

□ Form view 편집 모드

□ Share 탭 클릭
□ Create Form Link 클릭
□ 링크 복사: https://app.appsheet.com/form/[앱ID]/[뷰ID]

□ Permissions:
   - Anyone with the link
   - Read access: YES
   - Add rows: YES
   - Edit rows: NO
   - Delete rows: NO

□ Save
```

---

#### WordPress 페이지에 임베딩

**방법 A: iframe 임베딩 (추천)**

WordPress 페이지나 게시물에 추가:

```html
<iframe 
  src="https://app.appsheet.com/form/[앱ID]/[뷰ID]"
  width="100%" 
  height="800px"
  frameborder="0"
  allowfullscreen>
</iframe>
```

**방법 B: 직접 링크**

```
□ WordPress 버튼 추가
□ 버튼 텍스트: "관심 고객 접수하기"
□ 링크: AppSheet Form URL
□ 새 창에서 열기: YES
```

**방법 C: AppSheet Embed 플러그인**

```
□ WordPress에 "AppSheet Embed" 플러그인 설치
□ 단축코드 사용: [appsheet form="뷰ID"]
```

---

## 🎨 폼 UI 커스터마이징

### 섹션 구분

```
□ Form 편집 모드
□ + Add Section 클릭
□ Section name: "🏠 관심 매물 선택"

□ + Add Section 클릭
□ Section name: "👤 고객 정보"

□ 각 필드를 적절한 섹션으로 드래그
```

---

### 필수 필드 표시

```
□ 연락처 필드 클릭
□ Required 체크 ✅

□ 고객성함 필드 클릭
□ Required 체크 ✅
```

---

### 설명 텍스트 추가

```
□ 각 필드 클릭
□ "Help text" 섹션에 안내 문구 입력

예시:
- 단지명: "관심있는 단지를 선택해주세요"
- 동: "매물의 동호수를 선택해주세요"
- 연락처: "연락 가능한 번호를 입력해주세요"
```

---

## ✅ 검증 체크리스트

### Phase 1 완료
```
✅ 단지 2개만 선택 가능
✅ 동/호/타입 계층 구조 작동
✅ 고객 기본 정보만 입력
✅ 분양가/발코니/옵션 숨김
```

### Phase 2 완료
```
✅ 폼 링크 생성
✅ 공개 설정 완료
✅ WordPress에 임베딩 완료
```

### 전체 테스트
```
□ WordPress 페이지 열기
□ "관심 고객 접수" 버튼/폼 클릭
□ AppSheet 폼이 새 창 또는 iframe에서 열림
□ 단지명 선택 → 동 목록 확인
□ 동 선택 → 호 목록 확인
□ 호 선택 → 타입 목록 확인
□ 고객 정보 입력
□ 제출
□ 고객DB에 데이터 추가 확인 ✅
```

---

## 🚨 문제 해결

### 문제 1: Valid_If가 작동 안 함

**원인**: 분양가 테이블이 없거나 연결 안 됨

**해결**:
```
□ Data → Tables에서 "분양가" 테이블이 있는지 확인
□ 없으면 외부 스프레드시트에서 추가:
   + New Table → Data source: Google Sheets
   Spreadsheet ID 입력 → Sheet: "분양가"
```

---

### 문제 2: 링크가 작동 안 함

**원인**: 권한 설정 문제

**해결**:
```
□ UX → Views → 해당 Form 뷰
□ Share 탭 → Permissions 확인
□ "Anyone with the link" 선택
□ "Add rows" YES 설정
```

---

### 문제 3: WordPress에 표시가 이상함

**원인**: iframe 크기나 플러그인 충돌

**해결**:
```css
/* WordPress 테마 CSS에 추가 */
.appsheet-form {
  width: 100%;
  min-height: 800px;
  border: none;
}

@media (max-width: 768px) {
  .appsheet-form {
    min-height: 600px;
  }
}
```

---

## 🎯 최종 구조

```
WordPress 페이지
   ↓ 클릭
AppSheet 공개 Form
   ↓ 입력
   단지명 (2개 중 선택)
   동 (필터링)
   호 (필터링)
   타입 (필터링)
   고객성함
   연락처
   고객구분
   고객주소
   ↓ 저장
고객DB 테이블
   - 자동 생성: 고객ID
   - 자동 생성: 접수일
   - 자동 입력: 유입경로 = "온라인광고"
   - 자동 입력: 거래상태 = "관심등록"
```

---

## 📞 다음 단계

### 즉시 적용
```
□ AppSheet에서 별도 Form 뷰 생성
□ 필터링 조건 설정
□ 공개 링크 생성
□ WordPress에 임베딩
```

### 추가 개선 (나중에)
```
□ Automation 추가 (접수 시 메일 알림)
□ 스팸 방지 (reCAPTCHA)
□ 다국어 지원 (한글/영어)
□ 모바일 최적화
□ 분석 연결 (Google Analytics)
```

---

**작성일**: 2025-01-XX
**버전**: 1.0
**상태**: ✅ WordPress + AppSheet 통합 준비 완료

