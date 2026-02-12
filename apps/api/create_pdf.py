from reportlab.pdfgen import canvas
from io import BytesIO

def create_valid_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 750, "Jane Doe")
    c.drawString(100, 730, "Software Engineer")
    c.drawString(100, 710, "Experience: 5 years in Python and AI.")
    c.save()
    buffer.seek(0)
    return buffer.read()

if __name__ == "__main__":
    with open("valid_resume.pdf", "wb") as f:
        f.write(create_valid_pdf())
    print("Created valid_resume.pdf")
