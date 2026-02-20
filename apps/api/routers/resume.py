import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import Response, FileResponse, JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, User, Job
from services.resume.parser import ResumeParser
from services.resume.embedding import EmbeddingService
from services.resume.analyst import ResumeAnalyst
from services.resume.tailor import ResumeTailor
from services.resume.pdf_generator import PDFGenerator
from auth import get_current_user

router = APIRouter()
parser = ResumeParser()
embedding_service = EmbeddingService()
analyst = ResumeAnalyst()
tailor_service = ResumeTailor()
pdf_generator = PDFGenerator()

# Set up temporary directory for downloads
TEMP_DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "temp_downloads")
os.makedirs(TEMP_DOWNLOADS_DIR, exist_ok=True)

# Accepted MIME types → mapped to common extensions for display
ACCEPTED_MIME_TYPES = {
    "application/pdf":                                                    "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword":                                                 "doc",
    "text/plain":                                                         "txt",
    "application/rtf":                                                    "rtf",
    "text/rtf":                                                           "rtf",
}

ACCEPTED_EXTENSIONS = {"pdf", "docx", "doc", "txt", "rtf"}


def _get_extension(file: UploadFile) -> str:
    """
    Determine file extension from filename or content_type.
    Returns lowercase extension without the leading dot.
    """
    if file.filename and "." in file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext in ACCEPTED_EXTENSIONS:
            return ext

    # Fallback to MIME type
    if file.content_type in ACCEPTED_MIME_TYPES:
        return ACCEPTED_MIME_TYPES[file.content_type]

    return ""


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a resume. Supported formats: PDF, DOCX, DOC, TXT, RTF.
    """
    ext = _get_extension(file)
    if not ext:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                "Please upload a PDF, DOCX, DOC, TXT, or RTF file."
            )
        )

    content = await file.read()

    # Guard: 10 MB max
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")

    # 1. Parse → plain text
    filename = file.filename or f"resume.{ext}"
    try:
        text = parser.extract_text(content, filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text or len(text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract meaningful text from the file. Please check the file is not empty or image-only."
        )

    # 2. Analyze (structured data via GPT)
    structured_data = await analyst.analyze(text)

    # 3. Generate embedding for job matching
    vector = embedding_service.generate_embedding(text)

    # 4. Save to DB (mark as default)
    resume = Resume(
        user_id=current_user.id,
        content=text,
        structured_data=structured_data,
        embedding=vector,
        is_default=True
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "id": resume.id,
        "message": f"Resume uploaded successfully ({ext.upper()})",
        "data": structured_data
    }


@router.get("")
@router.get("/")
async def get_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all resumes for the current user.
    """
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    
    # We don't want to return the massive embedding vector
    return [
        {
            "id": r.id,
            "is_default": r.is_default,
            "created_at": r.created_at,
            "has_structured_data": r.structured_data is not None
        }
        for r in resumes
    ]


from pydantic import BaseModel

class TailorRequest(BaseModel):
    job_id: int


@router.post("/{resume_id}/tailor")
async def tailor_resume(
    resume_id: int,
    request: TailorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Tailors a resume to a specific job description and returns a generated PDF.
    """
    # 1. Fetch Resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if not resume.structured_data:
        raise HTTPException(status_code=400, detail="Resume has no structured data to tailor")

    # 2. Fetch Job
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_description = f"{job.title} at {job.company}\n\n{job.description}"

    # 3. Tailor Resume Data
    tailored_data = await tailor_service.tailor(
        base_resume_data=resume.structured_data, 
        job_description=job_description
    )

    # 4. Generate PDF
    try:
        pdf_bytes = pdf_generator.generate_pdf(tailored_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")

    # 5. Return PDF directly as raw bytes
    # Clean company name for filename
    clean_company = "".join([c for c in job.company if c.isalnum() or c in (" ", "_")]).strip()
    filename = f"Tailored_Resume_{clean_company.replace(' ', '_')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )



