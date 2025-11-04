#!/bin/bash
#
# PDF 일괄 처리 스크립트
# 여러 아파트 단지의 입주자모집공고문을 한번에 처리
#

set -e  # 오류 발생 시 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 프로젝트 루트 디렉터리
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PDF_PROCESSOR="$PROJECT_ROOT/src/collectors/pdf_to_data.py"

# PDF 폴더 경로 (사용자 환경에 맞게 수정)
PDF_BASE_DIR="d:/Flow System/- Flow/01. Framing/Project/아파트 입주자 모집공고문 데이터 정규화 및 마이그레이션"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  입주자모집공고문 일괄 처리 시작${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 처리 통계
TOTAL_COUNT=0
SUCCESS_COUNT=0
FAIL_COUNT=0

# PDF 파일 찾기 및 처리
find "$PDF_BASE_DIR" -type f \( -name "*.pdf" -o -name "*.PDF" \) | while read -r pdf_file; do
    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}[$TOTAL_COUNT] 처리 중: $(basename "$pdf_file")${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Python 스크립트 실행
    if python "$PDF_PROCESSOR" "$pdf_file"; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        echo -e "${GREEN}✅ 성공${NC}"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        echo -e "${RED}❌ 실패${NC}"
    fi

    echo ""
done

# 최종 결과
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  처리 완료${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "총 처리: ${TOTAL_COUNT}개"
echo -e "${GREEN}성공: ${SUCCESS_COUNT}개${NC}"
echo -e "${RED}실패: ${FAIL_COUNT}개${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}�� 모든 PDF 처리 완료!${NC}"
else
    echo -e "${YELLOW}⚠️  일부 PDF 처리 실패. 로그를 확인하세요.${NC}"
fi
