# AppSheet Related 리스트 접근 가이드

## 📋 문제 상황

`Related 토지s`와 같은 Related 리스트 컬럼에서 `INDEX()` 함수를 사용할 때 다음 에러 발생:
```
Column 'Related 토지s' is used in a SELECT or list dereference expression 
and should be a List/EnumList of Refs
```

## 🔍 원인 분석

### 1. Related 컬럼 타입 확인

**올바른 설정**:
- Type: **List** (또는 **List of Refs**)
- Is Virtual Column: ✅ 체크
- App Formula: `REF_ROWS("토지", "고객")` 또는 자동 생성됨

**잘못된 설정**:
- Type: Text, Number 등
- Related 리스트를 일반 컬럼처럼 사용

### 2. Related 리스트에서 값 가져오기

**잘못된 방법**:
```
INDEX([Related 토지s][D_L_ID], 1)  // ❌ 에러 발생
```

**올바른 방법**:
```
IF(
  COUNT([Related 토지s]) > 0,
  INDEX([Related 토지s][D_L_ID], 1),
  ""
)
```

## ✅ 해결 방법

### 방법 1: COUNT 체크 + INDEX (안전한 방법)

여러 Related 리스트 중 첫 번째로 있는 값만 선택:

```
IF(
  COUNT([Related 아파트매물s]) > 0,
  INDEX([Related 아파트매물s][D_AD_ID], 1),
  IF(
    COUNT([Related 상가s]) > 0,
    INDEX([Related 상가s][D_S_ID], 1),
    IF(
      COUNT([Related 원투룸s]) > 0,
      INDEX([Related 원투룸s][D_O_ID], 1),
      IF(
        COUNT([Related 공장창고s]) > 0,
        INDEX([Related 공장창고s][D_F_ID], 1),
        IF(
          COUNT([Related 토지s]) > 0,
          INDEX([Related 토지s][D_L_ID], 1),
          IF(
            COUNT([Related 주택타운s]) > 0,
            INDEX([Related 주택타운s][D_H_ID], 1),
            IF(
              COUNT([Related 건물s]) > 0,
              INDEX([Related 건물s][D_B_ID], 1),
              ""
            )
          )
        )
      )
    )
  )
)
```

### 방법 2: CONCATENATE 사용 (모든 매물 ID 합치기)

여러 매물 ID를 모두 연결하려면:

```
CONCATENATE(
  IF(COUNT([Related 아파트매물s]) > 0, INDEX([Related 아파트매물s][D_AD_ID], 1), ""),
  IF(COUNT([Related 상가s]) > 0, INDEX([Related 상가s][D_S_ID], 1), ""),
  IF(COUNT([Related 원투룸s]) > 0, INDEX([Related 원투룸s][D_O_ID], 1), ""),
  IF(COUNT([Related 공장창고s]) > 0, INDEX([Related 공장창고s][D_F_ID], 1), ""),
  IF(COUNT([Related 토지s]) > 0, INDEX([Related 토지s][D_L_ID], 1), ""),
  IF(COUNT([Related 주택타운s]) > 0, INDEX([Related 주택타운s][D_H_ID], 1), ""),
  IF(COUNT([Related 건물s]) > 0, INDEX([Related 건물s][D_B_ID], 1), "")
)
```

### 방법 3: SELECT + ANY 사용 (조건부 선택)

특정 조건에 맞는 매물만 선택:

```
ANY(
  SELECT([Related 아파트매물s][D_AD_ID], TRUE),
  SELECT([Related 상가s][D_S_ID], TRUE),
  SELECT([Related 원투룸s][D_O_ID], TRUE),
  ""
)
```

## 🔧 고객DB D_C_ID 최종 공식

### 시나리오 1: 대행사/부동산은 이름+직급, 나머지는 첫 번째 매물 ID

```
IF(
  OR([고객구분] = "대행사", [고객구분] = "부동산"),
  CONCATENATE([이름], " ", [직급]),
  CONCATENATE(
    IF(
      COUNT([Related 아파트매물s]) > 0,
      INDEX([Related 아파트매물s][D_AD_ID], 1),
      IF(
        COUNT([Related 상가s]) > 0,
        INDEX([Related 상가s][D_S_ID], 1),
        IF(
          COUNT([Related 원투룸s]) > 0,
          INDEX([Related 원투룸s][D_O_ID], 1),
          IF(
            COUNT([Related 공장창고s]) > 0,
            INDEX([Related 공장창고s][D_F_ID], 1),
            IF(
              COUNT([Related 토지s]) > 0,
              INDEX([Related 토지s][D_L_ID], 1),
              IF(
                COUNT([Related 주택타운s]) > 0,
                INDEX([Related 주택타운s][D_H_ID], 1),
                IF(
                  COUNT([Related 건물s]) > 0,
                  INDEX([Related 건물s][D_B_ID], 1),
                  ""
                )
              )
            )
          )
        )
      )
    ),
    "_",
    [고객구분],
    "_",
    RIGHT([연락처], 4)
  )
)
```

### 시나리오 2: 단순화 버전 (첫 번째 매물만, 없으면 고객정보만)

```
IF(
  OR([고객구분] = "대행사", [고객구분] = "부동산"),
  CONCATENATE([이름], " ", [직급]),
  CONCATENATE(
    COALESCE(
      IF(COUNT([Related 아파트매물s]) > 0, INDEX([Related 아파트매물s][D_AD_ID], 1), ""),
      IF(COUNT([Related 상가s]) > 0, INDEX([Related 상가s][D_S_ID], 1), ""),
      IF(COUNT([Related 원투룸s]) > 0, INDEX([Related 원투룸s][D_O_ID], 1), ""),
      ""
    ),
    "_",
    [고객구분],
    "_",
    RIGHT([연락처], 4)
  )
)
```

## 📝 체크리스트

### Related 컬럼 설정 확인

- [ ] `Related 아파트매물s` 컬럼 존재 여부
- [ ] Type이 **List** 또는 **List of Refs**인지 확인
- [ ] Is Virtual Column: ✅ 체크
- [ ] App Formula: `REF_ROWS("아파트매물", "고객")` (또는 자동 생성)
- [ ] 다른 Related 컬럼들도 동일하게 확인

### D_C_ID 공식 수정

- [ ] COUNT 체크 추가 (빈 리스트 처리)
- [ ] INDEX 함수 올바르게 사용
- [ ] IF 체인으로 여러 리스트 처리
- [ ] 테스트: 매물이 없는 고객도 에러 없이 처리되는지 확인

## 💡 참고

### AppSheet 리스트 함수 정리

| 함수 | 설명 | 예시 |
|------|------|------|
| `COUNT()` | 리스트 요소 개수 | `COUNT([Related 아파트매물s])` |
| `INDEX()` | 리스트의 N번째 요소 | `INDEX([Related 아파트매물s][D_AD_ID], 1)` |
| `FIRST()` | 첫 번째 요소 | `FIRST([Related 아파트매물s][D_AD_ID])` |
| `ANY()` | 리스트 중 하나 선택 | `ANY(SELECT(...), "")` |
| `SELECT()` | 조건에 맞는 요소 선택 | `SELECT([Related ...][D_AD_ID], TRUE)` |

### 주의사항

1. **COUNT 체크 필수**: 리스트가 비어있을 수 있으므로 항상 `COUNT() > 0` 확인
2. **Type 확인**: Related 컬럼은 반드시 List 타입이어야 함
3. **Virtual Column**: Related 컬럼은 Virtual Column으로 생성되어야 함
4. **REF_ROWS 수식**: `REF_ROWS("테이블명", "Ref컬럼명")` 형식 사용

