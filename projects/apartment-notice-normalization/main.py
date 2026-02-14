import sys
from pathlib import Path
from src.extractor import PDFDataExtractor

def main():
    print("🏢 입주자모집공고 정규화 도구 실행")
    
    # 기본 경로 설정
    base_dir = Path(__file__).parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    
    # PDF 파일 검색
    pdfs = list(raw_dir.glob("*.pdf"))
    
    if not pdfs:
        print(f"\n❌ 처리할 PDF 파일이 없습니다.")
        print(f"📂 '{raw_dir}' 폴더에 입주자모집공고 PDF 파일을 넣어주세요.")
        return

    print(f"📊 총 {len(pdfs)}개의 파일을 발견했습니다.\n")
    
    for pdf in pdfs:
        try:
            extractor = PDFDataExtractor(pdf, processed_dir)
            extractor.process()
        except Exception as e:
            print(f"❌ '{pdf.name}' 처리 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
