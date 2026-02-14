# 심볼릭 링크 생성 스크립트
# 이 스크립트를 PowerShell 관리자 권한으로 실행하세요

$linkPath = "d:\Flow System\- Flow\01. Framing\Project\구글 스프레드시트 자동화 매물관리 시스템구축\code"
$targetPath = "d:\Projects\apartment-automation"

# 기존 링크가 있는지 확인
if (Test-Path $linkPath) {
    Write-Host "⚠️  기존 'code' 폴더/링크가 이미 존재합니다." -ForegroundColor Yellow
    $response = Read-Host "삭제하고 다시 생성하시겠습니까? (Y/N)"

    if ($response -eq 'Y' -or $response -eq 'y') {
        Remove-Item $linkPath -Force -Recurse
        Write-Host "✅ 기존 항목 삭제 완료" -ForegroundColor Green
    } else {
        Write-Host "❌ 작업 취소됨" -ForegroundColor Red
        exit
    }
}

# 타겟 폴더 존재 확인
if (-not (Test-Path $targetPath)) {
    Write-Host "❌ 타겟 폴더를 찾을 수 없습니다: $targetPath" -ForegroundColor Red
    exit
}

# 심볼릭 링크 생성
try {
    New-Item -ItemType SymbolicLink -Path $linkPath -Target $targetPath -ErrorAction Stop
    Write-Host ""
    Write-Host "✅ 심볼릭 링크 생성 완료!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📂 링크 위치: $linkPath" -ForegroundColor Cyan
    Write-Host "🎯 타겟 위치: $targetPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "이제 Obsidian의 'code' 폴더를 통해 Git 저장소에 접근할 수 있습니다!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ 심볼릭 링크 생성 실패!" -ForegroundColor Red
    Write-Host ""
    Write-Host "오류 메시지: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "해결 방법:" -ForegroundColor Cyan
    Write-Host "1. PowerShell을 관리자 권한으로 다시 실행하세요" -ForegroundColor White
    Write-Host "2. 시작 메뉴 → PowerShell 우클릭 → '관리자 권한으로 실행'" -ForegroundColor White
    Write-Host "3. 다음 명령어 실행:" -ForegroundColor White
    Write-Host "   cd 'd:\Flow System\- Flow\01. Framing\Project\구글 스프레드시트 자동화 매물관리 시스템구축'" -ForegroundColor Gray
    Write-Host "   .\create_symlink.ps1" -ForegroundColor Gray
}
