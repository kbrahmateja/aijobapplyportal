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

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    
    # 1. Parse PDF
    try:
        text = parser.extract_text_from_pdf(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 2. Analyze Resume (Structured Data)
    structured_data = await analyst.analyze(text)
    
    # 3. Generate Embedding
    vector = embedding_service.generate_embedding(text)
    
    # 4. Save to DB
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
        "message": "Resume uploaded successfully", 
        "data": structured_data
    }
