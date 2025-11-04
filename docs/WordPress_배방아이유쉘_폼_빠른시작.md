# 배방우방아이유쉘 고객 접수 폼 - 빠른 시작 가이드 ⚡

**대상**: iusell.cheonan-asan.com 워드프레스
**목적**: 관심 고객 간단 접수
**작업 시간**: 20-30분

---

## 🎯 3단계로 끝내기

### ✅ 1단계: 새 Form 뷰 생성 (10분)

```
□ AppSheet 열기
□ UX → Views → + Add View

□ View type: Form
□ Detail table: 고객DB
□ Form name: "배방아이유쉘_고객접수"

□ 다음 필드만 추가:

   매물 선택:
   □ 단지명 (드롭다운)
   □ 동
   □ 호
   □ 타입

   고객 정보:
   □ 고객성함
   □ 연락처 (필수)
   □ 고객구분
   □ 고객주소

□ 나머지는 모두 숨김
```

---

### ✅ 2단계: 단지 필터링 (5분)

**간단한 방법**: 단지명 필드를 Ref가 아닌 Enum으로!

```
□ Data → Tables → 고객DB → Columns → 단지명

□ Type: Enum 선택

□ Values (2개만!):
   아산배방1단지우방아이유쉘
   아산배방우방아이유쉘2단지

□ Allow other values: ❌ 체크 해제

□ Save
```

→ 이제 2개 단지만 선택 가능! ✅

---

### ✅ 3단계: WordPress 임베딩 (5분)

```
□ UX → Views → 배방아이유쉘_고객접수 선택
□ Share 탭
□ Create Form Link 클릭
□ 링크 복사

□ WordPress 페이지 편집
□ HTML/코드 블록 추가:

<iframe 
  src="여기에_복사한_링크_붙여넣기"
  width="100%" 
  height="800px"
  frameborder="0">
</iframe>

□ 저장
```

---

## 🧪 테스트하기

```
□ 워드프레스 페이지 열기
□ 폼이 보이는지 확인
□ 단지명 선택 (2개만!)
□ 동/호/타입 입력 (또는 그냥 텍스트로 입력)
□ 고객 정보 입력
□ 제출
□ AppSheet 고객DB에 데이터 추가 확인
```

---

## 🎨 선택 사항: 더 예쁘게

### 섹션 구분 추가
```
□ Form 편집 → + Add Section
□ "관심 매물"
□ "고객 정보"
□ 각 필드를 섹션으로 드래그
```

### 도움말 추가
```
□ 연락처 필드 클릭
□ Help text: "문자 확인 가능한 번호를 입력해주세요"
□ Save
```

---

## ⚡ 만약 동/호/타입 필터링이 복잡하다면

**해결책**: 그냥 텍스트 입력으로!

```
□ 동, 호, 타입 필드를:
   Type: Text
   Input mode: Text (또는 Numbers for 호)

□ Valid If 제거
□ 고객이 직접 입력하게

→ 간단하고 빠르고 확실함!
```

---

## 🚨 문제 해결

### 폼이 안 열려요
```
□ Share → Permissions
□ "Anyone with the link" 체크
□ "Add rows" YES 체크
```

### 제출이 안 돼요
```
□ 고객DB 테이블 Key 설정 확인
□ 고객ID가 UNIQUEID()로 설정되어 있는지
```

### WordPress iframe이 작아요
```css
/* 테마 CSS에 추가 */
iframe {
  min-height: 800px !important;
}
```

---

## ✨ 완성!

이제 워드프레스 페이지에:
```
[관심 고객 접수 폼]
   ↓
고객이 간단히 입력
   ↓
AppSheet 고객DB에 자동 저장
   ↓
담당자가 확인 및 연락
```

끝! 🎉

---

## 💡 나중에 추가 가능한 기능

1. **자동 메일 알림**: 고객 접수 시 담당자에게 메일
2. **스팸 방지**: reCAPTCHA 추가
3. **분석 연결**: Google Analytics 이벤트 트래킹
4. **SMS 자동 발송**: 고객 확인용

---

**준비됐나요? 시작하세요!** 🚀

