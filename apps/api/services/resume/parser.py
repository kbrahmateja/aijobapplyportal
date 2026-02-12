from pdfminer.high_level import extract_text
from io import BytesIO

class ResumeParser:
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        Extracts text from a PDF file.
        """
        try:
            text = extract_text(BytesIO(file_content))
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
