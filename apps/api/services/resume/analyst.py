from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config import settings
import logging
import json

# --- Data Models ---
class WorkExperience(BaseModel):
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    start_date: Optional[str] = Field(description="Start date (YYYY-MM or Present)")
    end_date: Optional[str] = Field(description="End date (YYYY-MM or Present)")
    description: Optional[str] = Field(description="Short summary of responsibilities")

class Education(BaseModel):
    degree: str = Field(description="Degree obtained")
    school: str = Field(description="School/University name")
    year: Optional[str] = Field(description="Year of graduation")

class ResumeData(BaseModel):
    full_name: Optional[str] = Field(description="Candidate's full name")
    email: Optional[str] = Field(description="Candidate's email")
    skills: List[str] = Field(description="List of technical and soft skills")
    experience: List[WorkExperience] = Field(description="List of work experiences")
    education: List[Education] = Field(description="List of educational background")
    summary: Optional[str] = Field(description="Brief professional summary")

# --- Service ---
class ResumeAnalyst:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, openai_api_key=settings.OPENAI_API_KEY)
        else:
            self.llm = None
            
    async def analyze(self, text: str) -> dict:
        """
        Analyzes resume text and returns structured data.
        """
        if not self.llm:
            self.logger.warning("OPENAI_API_KEY missing. Returning mock structured data.")
            return self._get_mock_data()
            
        try:
            parser = PydanticOutputParser(pydantic_object=ResumeData)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert AI Resume Parser. Extract the following information from the resume text provided."),
                ("user", "{format_instructions}\n\nResume Text:\n{text}")
            ])
            
            chain = prompt | self.llm | parser
            
            result = chain.invoke({
                "format_instructions": parser.get_format_instructions(),
                "text": text
            })
            
            return result.model_dump()
            
        except Exception as e:
            self.logger.error(f"Error analyzing resume: {e}")
            return self._get_mock_data() # Fallback

    def _get_mock_data(self) -> dict:
        return {
            "full_name": "Unknown Candidate",
            "skills": ["Python (Mock)", "FastAPI (Mock)", "React (Mock)"],
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Mock Company",
                    "start_date": "2023-01",
                    "end_date": "Present",
                    "description": "Implemented features."
                }
            ],
            "education": [],
            "summary": "This is a mock summary because OpenAI API Key is missing."
        }
