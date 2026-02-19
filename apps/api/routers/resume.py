from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, User
from services.resume.parser import ResumeParser
from services.resume.embedding import EmbeddingService
from services.resume.analyst import ResumeAnalyst
from auth import get_current_user

router = APIRouter()
parser = ResumeParser()
embedding_service = EmbeddingService()
analyst = ResumeAnalyst()

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
