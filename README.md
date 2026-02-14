# Real Estate Workspace

이 저장소는 기능별로 분리된 멀티 프로젝트 워크스페이스입니다.
루트에서는 공통 문서만 관리하고, 실제 개발은 각 프로젝트 폴더에서 진행합니다.

## Projects

| 프로젝트 | 경로 | 목적 |
|---|---|---|
| Property Management Core | `projects/property-management-core` | 매물/고객 관리, AppSheet/Google Sheets/Excel 연동 중심 백엔드 |
| Building Ledger Automation | `projects/building-ledger-automation` | 건축물대장 API + n8n + Apps Script + Notion/Sheets 자동화 |
| Apartment Notice Normalization | `projects/apartment-notice-normalization` | 입주자모집공고 PDF 정규화/추출 파이프라인 |
| Legacy Archive | `projects/legacy-archive` | 과거 실험/마이그레이션/레거시 코드 보관 |

## Recommended Focus Workflow

1. 오늘 집중할 프로젝트 하나만 선택
2. 해당 폴더로 이동해서 작업
3. 해당 프로젝트 README 기준으로 실행/테스트

```bash
cd projects/building-ledger-automation
# 또는
cd projects/property-management-core
```

## Workspace Shortcuts

루트에서 바로 실행할 때:

```bash
make ledger-run
make pm-run
make notice-run
```

## Notes

- 루트의 `AGENTS.md`, `CLAUDE.md`는 워크스페이스 공통 컨텍스트입니다.
- 루트 `.env`는 공통값이 필요할 때만 사용하고, 프로젝트별 `.env`를 별도로 두는 것을 권장합니다.
