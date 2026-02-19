import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem

class PDFGenerator:
    """
    Generates a clean, professional PDF from structured resume data.
    """
    def __init__(self):
        self.doc_style = getSampleStyleSheet()
        
        # Define Custom Styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.doc_style['Heading1'],
            fontSize=24,
            spaceAfter=6,
            textColor=colors.HexColor("#1f2937"),
            alignment=1 # Center
        )
        
        self.contact_style = ParagraphStyle(
            'ContactInfo',
            parent=self.doc_style['Normal'],
            fontSize=10,
            textColor=colors.HexColor("#4b5563"),
            alignment=1 # Center
        )
        
        self.heading_style = ParagraphStyle(
            'SectionHeading',
            parent=self.doc_style['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#111827"),
            borderPadding=(0,0,2,0),
        )
        
        self.normal_style = ParagraphStyle(
            'NormalStyle',
            parent=self.doc_style['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=colors.HexColor("#374151")
        )
        
        self.bold_style = ParagraphStyle(
            'BoldStyle',
            parent=self.doc_style['Normal'],
            fontSize=11,
            spaceAfter=2,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor("#111827")
        )
        
        self.italic_style = ParagraphStyle(
            'ItalicStyle',
            parent=self.doc_style['Normal'],
            fontSize=10,
            spaceAfter=2,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor("#4b5563")
        )

    def generate_pdf(self, resume_data: dict) -> bytes:
        """
        Takes structured JSON data (matching ResumeData schema) and returns PDF bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )
        
        story = []

        # --- Header ---
        name = resume_data.get("full_name", "Candidate Name")
        story.append(Paragraph(name, self.title_style))
        
        email = resume_data.get("email", "")
        if email:
            story.append(Paragraph(email, self.contact_style))
        story.append(Spacer(1, 10))
        
        # --- Summary ---
        summary = resume_data.get("summary", "")
        if summary:
            story.append(Paragraph("Professional Summary", self.heading_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceBefore=0, spaceAfter=8))
            story.append(Paragraph(summary, self.normal_style))
            story.append(Spacer(1, 10))

        # --- Skills ---
        skills = resume_data.get("skills", [])
        if skills:
            story.append(Paragraph("Skills", self.heading_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceBefore=0, spaceAfter=8))
            skills_text = " • ".join(skills)
            story.append(Paragraph(skills_text, self.normal_style))
            story.append(Spacer(1, 10))

        # --- Experience ---
        experience = resume_data.get("experience", [])
        if experience:
            story.append(Paragraph("Experience", self.heading_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceBefore=0, spaceAfter=8))
            
            for exp in experience:
                title = exp.get("title", "")
                company = exp.get("company", "")
                start = exp.get("start_date", "")
                end = exp.get("end_date", "Present")
                
                # Title and Company
                story.append(Paragraph(f"{title} | {company}", self.bold_style))
                # Dates
                if start or end:
                    story.append(Paragraph(f"{start} — {end}", self.italic_style))
                
                # Description
                desc = exp.get("description", "")
                if desc:
                    # Split into bullets (assuming Claude/GPT might return newlines or bullet points)
                    # We'll just do simple paragraphs for now, or split by newline if there are multiple.
                    bullets = [d.strip() for d in desc.split("\n") if d.strip()]
                    list_items = [ListItem(Paragraph(b.lstrip("•- "), self.normal_style)) for b in bullets]
                    
                    if list_items:
                        story.append(ListFlowable(
                            list_items,
                            bulletType='bullet',
                            start='•',
                            leftIndent=15,
                            bulletSpace=5
                        ))
                    else:
                        story.append(Paragraph(desc, self.normal_style))
                story.append(Spacer(1, 8))

        # --- Education ---
        education = resume_data.get("education", [])
        if education:
            story.append(Paragraph("Education", self.heading_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceBefore=0, spaceAfter=8))
            
            for edu in education:
                degree = edu.get("degree", "")
                school = edu.get("school", "")
                year = edu.get("year", "")
                
                story.append(Paragraph(f"{degree} — {school}", self.bold_style))
                if year:
                    story.append(Paragraph(year, self.italic_style))
                story.append(Spacer(1, 6))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
