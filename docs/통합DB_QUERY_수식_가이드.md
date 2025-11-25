# 통합DB QUERY 수식 가이드

통합DB를 시트 포뮬러로 자동 생성하는 방법입니다.

## 📊 통합DB 구조

```
A열: ID
B열: 관련파일
C열: 폴더ID
D열: D_ID
E열: 주소
F열: 매물유형
```

## 🔧 QUERY 수식 구현

### 방법 1: 각 시트별 QUERY + 배열 합치기

통합DB 시트의 A1 셀에 다음 수식을 입력:

```excel
={
  QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != ''", 0);
  QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != ''", 0);
  QUERY(건물!A2:F, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND M = TRUE", 0);
  QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != ''", 0);
  QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != ''", 0);
  QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != ''", 0);
  QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != ''", 0)
}
```

### 방법 2: 개선된 버전 (빈 값 제거)

```excel
={
  QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(건물!A2:F, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL AND M = TRUE", 0);
  QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0)
}
```

## 📝 수식 설명

### QUERY 구문
- `SELECT A, B, C, D, E, '아파트'`: A~E열 선택 + 매물유형 고정값
- `WHERE D IS NOT NULL AND D != ''`: D_ID가 비어있지 않은 행만
- `AND M = TRUE`: 건물 시트의 경우 M열 통매매 체크박스가 체크된 것만
- `0`: 헤더 없이 데이터만 반환

### 배열 합치기
- `{ ...; ...; ... }`: 세미콜론으로 배열을 세로로 합치기
- 각 QUERY 결과를 하나로 합쳐서 통합DB 생성

## ⚠️ 주의사항

1. **건물 시트의 M열**: 통매매 체크박스가 TRUE인 것만 포함
2. **D_ID 필터링**: D_ID가 비어있지 않은 행만 포함
3. **헤더 행**: 수식은 A1에 넣고, 헤더는 별도로 설정하거나 QUERY의 `1` 옵션 사용

## 🔄 자동 업데이트

- 각 매물 시트에 데이터가 추가/수정/삭제되면 자동으로 통합DB에 반영
- 실시간 동기화 (수식 재계산 시)
- 서버 리소스 사용 없음
- 실행 시간 제한 없음

## 📋 헤더 설정

통합DB 시트의 헤더 행 (1행)은 수동으로 설정:

```
A1: ID
B1: 관련파일
C1: 폴더ID
D1: D_ID
E1: 주소
F1: 매물유형
```

또는 QUERY에 `1` 옵션을 추가하여 헤더 포함:

```excel
={
  QUERY(아파트매물!A1:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != ''", 1);
  ...
}
```

하지만 이 경우 각 QUERY의 헤더가 중복되므로, 첫 번째 QUERY만 헤더를 포함하고 나머지는 제외하는 것이 좋습니다.

## 🎯 최종 권장 수식

### 방법 1: 헤더 포함 (첫 번째 QUERY만)

통합DB 시트의 A1 셀에 다음 수식 입력:

```excel
={
  QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' LABEL '아파트' '매물유형' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 1);
  QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(건물!A2:F, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL AND M = TRUE", 0);
  QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0)
}
```

**문제**: 첫 번째 QUERY의 헤더가 표시되지 않음 (LABEL 사용 필요)

### 방법 2: 헤더 수동 설정 (권장)

**1단계: 헤더 행 수동 입력**
```
A1: ID
B1: 관련파일
C1: 폴더ID
D1: D_ID
E1: 주소
F1: 매물유형
```

**2단계: A2 셀에 데이터 수식 입력**

빈 행 제거 및 매물유형 정리 버전 (최종 - 수정):

```excel
=FILTER({
  QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(건물!A2:M, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL AND M = TRUE", 0);
  QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0)
}, INDEX({QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(건물!A2:M, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL AND M = TRUE", 0); QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0)}, 0, 1) <> "" AND INDEX({QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(건물!A2:M, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL AND M = TRUE", 0); QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0); QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0)}, 0, 4) <> "")
```

이 수식은 너무 복잡합니다. 더 간단한 방법을 사용하세요:

### ✅ 간단하고 안정적인 버전 (권장)

```excel
={
  QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(건물!A2:M, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL AND M = TRUE", 0);
  QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0)
}
```

**설명**:
- 각 QUERY의 WHERE 조건에서 이미 빈 행을 필터링하므로 FILTER 불필요
- `WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL` 조건으로 빈 행 자동 제거
- 수식이 간단하고 안정적
- 매물유형 컬럼에 정확한 값만 표시 ("아파트", "주택타운" 등)

### 방법 3: 최종 완성 버전 (빈 행 완전 제거)

빈 행과 불필요한 데이터를 완전히 제거하는 버전:

```excel
=FILTER({
  QUERY(아파트매물!A2:F, "SELECT A, B, C, D, E, '아파트' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(주택타운!A2:F, "SELECT A, B, C, D, E, '주택타운' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(건물!A2:M, "SELECT A, B, C, D, E, '건물' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL AND M = TRUE", 0);
  QUERY(상가!A2:F, "SELECT A, B, C, D, E, '상가' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(원투룸!A2:F, "SELECT A, B, C, D, E, '원투룸' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(공장창고!A2:F, "SELECT A, B, C, D, E, '공장창고' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0);
  QUERY(토지!A2:F, "SELECT A, B, C, D, E, '토지' WHERE D IS NOT NULL AND D != '' AND A IS NOT NULL", 0)
}, A:A <> "" AND D:D <> "")
```

이 수식은:
- A열(ID)이 비어있지 않은 행만 표시
- D열(D_ID)이 비어있지 않은 행만 표시
- 각 매물유형 사이의 빈 행 자동 제거

## ⚠️ 주의사항

1. **건물 시트의 M열**: QUERY에서 M열을 참조하려면 범위에 M열까지 포함해야 함 (`A2:M`)
2. **체크박스 값**: TRUE/FALSE 값으로 저장되므로 `M = TRUE`로 필터링
3. **빈 값 처리**: `D IS NOT NULL AND D != ''`로 D_ID가 비어있지 않은 행만 선택
4. **헤더 처리**: 첫 번째 행은 헤더로 수동 설정하거나, 모든 QUERY에서 `0` 옵션 사용

## 🔄 자동 업데이트

- 각 매물 시트에 데이터가 추가/수정/삭제되면 자동으로 통합DB에 반영
- 실시간 동기화 (수식 재계산 시)
- 서버 리소스 사용 없음
- 실행 시간 제한 없음
- 일일 쿼터 제한 없음

