@echo off
REM PDF 일괄 처리 스크립트 (Windows)
REM 여러 아파트 단지의 입주자모집공고문을 한번에 처리

setlocal enabledelayedexpansion

echo ========================================
echo   입주자모집공고문 일괄 처리 시작
echo ========================================
echo.

REM 프로젝트 루트 디렉터리
set "PROJECT_ROOT=%~dp0.."
set "PDF_PROCESSOR=%PROJECT_ROOT%\src\collectors\pdf_to_data.py"

REM PDF 폴더 경로
set "PDF_BASE_DIR=d:\Flow System\- Flow\01. Framing\Project\아파트 입주자 모집공고문 데이터 정규화 및 마이그레이션"

REM 처리 통계
set /a TOTAL_COUNT=0
set /a SUCCESS_COUNT=0
set /a FAIL_COUNT=0

REM PDF 파일 찾기 및 처리
for /r "%PDF_BASE_DIR%" %%f in (*.pdf *.PDF) do (
    set /a TOTAL_COUNT+=1

    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    echo [!TOTAL_COUNT!] 처리 중: %%~nxf
    echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    REM Python 스크립트 실행
    python "%PDF_PROCESSOR%" "%%f"

    if !errorlevel! equ 0 (
        set /a SUCCESS_COUNT+=1
        echo ✅ 성공
    ) else (
        set /a FAIL_COUNT+=1
        echo ❌ 실패
    )

    echo.
)

REM 최종 결과
echo ========================================
echo   처리 완료
echo ========================================
echo 총 처리: %TOTAL_COUNT%개
echo 성공: %SUCCESS_COUNT%개
echo 실패: %FAIL_COUNT%개
echo.

if %FAIL_COUNT% equ 0 (
    echo 🎉 모든 PDF 처리 완료!
) else (
    echo ⚠️  일부 PDF 처리 실패. 로그를 확인하세요.
)

pause
