"""
PDF 스킬 테스트: 샘플 분양가 PDF 생성 및 추출 테스트
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 폰트 등록 (한글 지원)
try:
    pdfmetrics.registerFont(TTFont('Malgun', 'C:/Windows/Fonts/malgun.ttf'))
    FONT = 'Malgun'
except:
    FONT = 'Helvetica'

def create_sample_pdf():
    output_path = "data/raw/sample_pricing.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # 제목
    title = Paragraph("<b>아파트 분양가 안내</b>", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # 분양가 테이블 데이터
    data = [
        ['타입', '층구분', '대지비', '건축비', '부가세', '분양가'],
        ['84A', '3층', '150,000,000', '300,000,000', '30,000,000', '480,000,000'],
        ['84A', '4층', '153,000,000', '305,000,000', '30,500,000', '488,500,000'],
        ['84A', '5~9층', '155,000,000', '310,000,000', '31,000,000', '496,000,000'],
        ['84B', '3층', '145,000,000', '290,000,000', '29,000,000', '464,000,000'],
        ['84B', '4층', '148,000,000', '295,000,000', '29,500,000', '472,500,000'],
        ['101A', '3층', '180,000,000', '360,000,000', '36,000,000', '576,000,000'],
        ['101A', '4층', '183,000,000', '365,000,000', '36,500,000', '584,500,000'],
    ]
    
    table = Table(data, colWidths=[60, 60, 90, 90, 80, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTNAME', (0, 1), (-1, -1), FONT),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(table)
    doc.build(story)
    print(f"✅ 샘플 PDF 생성 완료: {output_path}")
    return output_path

if __name__ == "__main__":
    create_sample_pdf()
