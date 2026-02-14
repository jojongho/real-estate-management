# Building Ledger Automation

건축물대장 자동조회 전용 프로젝트입니다.
`n8n`은 트리거/오케스트레이션만 담당하고, 핵심 조회 로직은 이 프로젝트의 Python API가 담당합니다.

## What Is Included

- `src/building_ledger_api/`: FastAPI 서비스 (Vworld → PNU → 건축HUB 조회)
- `scripts/lookup_once.py`: 단건 CLI 테스트
- `n8n-workflows/`: n8n 노드/가이드 자료
- `apps-script/`: 기존 Apps Script 자산
- `docs/reference/`: API 참고 문서
- `notes/`: 기존 시행착오/완료 기록

## Quick Start

```bash
cd projects/building-ledger-automation
cp .env.example .env
# .env에 VWORLD_API_KEY, DATA_GO_KR_SERVICE_KEY 입력

make run
# 또는
./run.sh
```

기본 서버: `http://localhost:8080`

## API

### Health Check

```bash
curl http://localhost:8080/health
```

### Lookup

```bash
curl -X POST http://localhost:8080/lookup \
  -H 'Content-Type: application/json' \
  -d '{"address":"충청남도 천안시 서북구 불당동 1329"}'
```

`LEDGER_API_TOKEN`을 설정한 경우 `X-API-Key` 헤더가 필요합니다.

## n8n Integration Pattern

1. Notion Trigger (`조회상태=대기중`) or Webhook Trigger
2. HTTP Request 노드로 `POST /lookup` 호출
3. 응답값을 Notion/Google Sheets 업데이트 노드에 매핑
4. 성공 시 `조회상태=완료`, 실패 시 `조회상태=실패`

## Commands

- `make install`: 가상환경 + 의존성 설치
- `make run`: API 서버 실행
- `make check`: 컴파일 체크
- `make lookup ADDRESS='...'`: 단건 조회 테스트

## Export As Standalone Repo

현재 워크스페이스에서 분리해 단독 Git 저장소로 만들 때:

```bash
./scripts/bootstrap_standalone_repo.sh ~/dev/building-ledger-automation
```

## Critical Rules

1. 엔드포인트는 `BldRgstHubService/getBrTitleInfo` 사용
2. 파라미터는 `sigungu_code`, `bdong_code`, `plat_code`, `bun`, `ji` 사용
3. PNU는 반드시 19자리 검증
4. 구형 `BldRgstService_v2`와 혼용 금지
