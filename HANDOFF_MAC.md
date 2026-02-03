# 🔄 Mac에서 이어하기 - 스킬 테스트

## 📍 현재 진행 상황

### ✅ 완료된 작업
1. **프로젝트 재구조화** - 51개 문서 분류, 레거시 정리, Obsidian 삭제
2. **스킬 분석** - `pdf`, `xlsx` 스킬이 apartment-normalization에 적용 가능 확인

### 🔜 다음 작업: PDF 스킬 테스트

**목표**: 입주자모집공고 PDF → pdfplumber로 테이블 추출 → Excel 변환

---

## 🚀 Mac에서 시작하기

```bash
# 1. 프로젝트 풀
cd ~/Projects/real-estate-management  # 또는 Mac 경로
git pull origin main

# 2. 테스트용 PDF 준비
# 실제 입주자모집공고 PDF를 아래 경로에 넣기:
# projects/apartment-normalization/data/raw/

# 3. pdfplumber 테스트 실행 (아래 스크립트 실행)
python projects/apartment-normalization/test_pdf_extraction.py
```

---

## 📝 테스트 스크립트 (Mac에서 생성 필요)

```python
# test_pdf_extraction.py
import pdfplumber
import pandas as pd
from pathlib import Path

def extract_tables_from_pdf(pdf_path):
    """PDF에서 테이블 추출 테스트"""
    print(f"📄 PDF 분석: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"📊 총 페이지: {len(pdf.pages)}")
        
        all_tables = []
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables:
                print(f"  - 페이지 {i+1}: {len(tables)}개 테이블 발견")
                for table in tables:
                    if table and len(table) > 1:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        all_tables.append(df)
        
        return all_tables

if __name__ == "__main__":
    raw_dir = Path(__file__).parent / "projects/apartment-normalization/data/raw"
    pdfs = list(raw_dir.glob("*.pdf"))
    
    if not pdfs:
        print("❌ PDF 파일이 없습니다. data/raw/ 폴더에 PDF를 넣어주세요.")
    else:
        for pdf in pdfs:
            tables = extract_tables_from_pdf(pdf)
            print(f"\n✅ 총 {len(tables)}개 테이블 추출")
            for i, df in enumerate(tables):
                print(f"\n테이블 {i+1}:")
                print(df.head())
```

---

## 💡 참고: 설치된 스킬 목록

| 스킬 | 용도 |
|------|------|
| `pdf` | PDF 텍스트/테이블 추출 |
| `xlsx` | Excel 생성/수정 |
| `skill-creator` | 커스텀 스킬 제작 |

스킬 경로: `~/.gemini/antigravity/.agent/skills/`
