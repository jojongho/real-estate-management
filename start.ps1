# Windows 프로젝트 시작 스크립트
# 사용법: .\start.ps1

Write-Host "🚀 아파트 매물관리 프로젝트 시작..." -ForegroundColor Green
Write-Host ""

# 현재 스크립트 위치 확인
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Git 상태 확인
if (Test-Path ".git") {
    Write-Host "📥 최신 변경사항 가져오는 중..." -ForegroundColor Yellow
    git pull origin main 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 최신 코드 동기화 완료" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Git pull 실패 (무시 가능)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Git 저장소가 아닙니다" -ForegroundColor Yellow
}

# 가상환경 확인 및 활성화
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🐍 가상환경 활성화 중..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "✅ 가상환경 활성화 완료" -ForegroundColor Green
} else {
    Write-Host "⚠️  가상환경이 없습니다. 다음 명령어로 생성하세요:" -ForegroundColor Yellow
    Write-Host "   python -m venv venv" -ForegroundColor Cyan
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "   pip install -r requirements.txt" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "✅ 준비 완료! 작업을 시작하세요." -ForegroundColor Green
Write-Host ""
Write-Host "💡 유용한 명령어:" -ForegroundColor Cyan
Write-Host "   python src/main.py              # 메인 실행" -ForegroundColor White
Write-Host "   git status                      # 변경사항 확인" -ForegroundColor White
Write-Host "   git add . && git commit -m '메시지' && git push  # 작업 저장" -ForegroundColor White
Write-Host ""
