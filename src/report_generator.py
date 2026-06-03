import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(df, insights, strategic_rec, output_path):
    """
    Generates a professional PDF executive report based on current analytics and insights.
    """
    # Ensure reports directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 0.75 in (54 pt) margins
    doc = SimpleDocTemplate(
        output_path, 
        pagesize=letter,
        rightMargin=54, 
        leftMargin=54, 
        topMargin=54, 
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles matching Netflix palette
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#E50914'),
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=20
    )
    
    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#111111'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        leading=14
    )
    
    bold_body_style = ParagraphStyle(
        'BoldDocBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#E50914'),
        spaceAfter=3
    )
    
    story = []
    
    # Title & Subtitle
    story.append(Paragraph("🎬 CineVision AI", title_style))
    story.append(Paragraph("Netflix Executive Intelligence & Catalog Performance Report", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Data calculations
    total_titles = len(df)
    movies_count = len(df[df['type'] == 'Movie'])
    tv_shows_count = len(df[df['type'] == 'TV Show'])
    
    from collections import Counter
    country_list = []
    for val in df['country'].dropna():
        if val != 'Unknown':
            for c in val.split(','):
                c_clean = c.strip()
                if c_clean:
                    country_list.append(c_clean)
    top_country = Counter(country_list).most_common(1)[0][0] if country_list else 'Unknown'
    
    genre_list = []
    for val in df['listed_in'].dropna():
        for g in val.split(','):
            g_clean = g.strip()
            if g_clean:
                genre_list.append(g_clean)
    top_genre = Counter(genre_list).most_common(1)[0][0] if genre_list else 'Unknown'
    top_rating = df['rating'].mode()[0] if not df['rating'].empty else 'NR'
    top_year = df['release_year'].mode()[0] if not df['release_year'].empty else 'Unknown'
    
    # Header cells for table
    header_metric = Paragraph("Metric", bold_body_style)
    header_metric.style.textColor = colors.white
    header_val = Paragraph("Value", bold_body_style)
    header_val.style.textColor = colors.white
    
    # Stats Table
    table_data = [
        [header_metric, header_val],
        [Paragraph("Total Catalog Titles", body_style), Paragraph(f"{total_titles:,}", body_style)],
        [Paragraph("Movies Count", body_style), Paragraph(f"{movies_count:,} ({movies_count/max(1, total_titles)*100:.1f}%)", body_style)],
        [Paragraph("TV Shows Count", body_style), Paragraph(f"{tv_shows_count:,} ({tv_shows_count/max(1, total_titles)*100:.1f}%)", body_style)],
        [Paragraph("Top Country", body_style), Paragraph(top_country, body_style)],
        [Paragraph("Top Genre", body_style), Paragraph(top_genre, body_style)],
        [Paragraph("Top Age Rating", body_style), Paragraph(top_rating, body_style)],
        [Paragraph("Peak Release Year", body_style), Paragraph(str(top_year), body_style)]
    ]
    
    # Letter width is 612pt. Subtract margins (108pt) -> printable area width is 504pt.
    t = Table(table_data, colWidths=[200, 304])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#221F1F')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F9F9F9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    
    story.append(Paragraph("📊 Executive Platform Summary", section_heading))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # Business Insights Section
    story.append(Paragraph("💡 Strategic Business Insights", section_heading))
    for ins in insights:
        # Strip markdown syntax for PDF display consistency
        title_text = ins['title']
        desc_text = ins['desc'].replace('**', '')
        
        story.append(Paragraph(title_text, card_title_style))
        story.append(Paragraph(desc_text, body_style))
        story.append(Spacer(1, 5))
        
    story.append(Spacer(1, 10))
    
    # Strategic Path Section
    story.append(Paragraph("⚡ Catalog Strategic Path Recommendation", section_heading))
    # Strip markdown syntax for PDF
    rec_desc = strategic_rec['desc'].replace('**', '')
    story.append(Paragraph(rec_desc, body_style))
    
    doc.build(story)
