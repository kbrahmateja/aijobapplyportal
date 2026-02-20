import logging
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from config import settings
from .analyst import ResumeData

class ResumeTailor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=settings.OPENAI_API_KEY)
        else:
            self.llm = None

    async def tailor(self, base_resume_data: dict, job_description: str) -> dict:
        """
        Tailors a resume's content to match a specific job description.
        Returns a new dictionary in the shape of ResumeData.
        """
        if not self.llm:
            self.logger.warning("OPENAI_API_KEY missing. Returning original resume data.")
            return base_resume_data
            
        try:
            parser = PydanticOutputParser(pydantic_object=ResumeData)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert Executive Resume Writer and Career Coach. 
Your task is to tailor the candidate's existing resume data to perfectly match the provided job description.

Rules:
1. DO NOT invent new experiences, companies, or degrees that the candidate does not have.
2. DO rewrite the 'description' bullet points in the work experience to emphasize skills and achievements that align with the job description.
3. DO reorder and filter the 'skills' list to prioritize those mentioned in the job description.
4. DO write a compelling 'summary' that positions the candidate as the ideal fit for THIS specific role.
5. Maintain a professional, impact-driven tone (use strong action verbs).
"""),
                ("user", """
Job Description:
{job_description}

Candidate's Current Resume Data (JSON):
{resume_data}

{format_instructions}
""")
            ])
            
            chain = prompt | self.llm | parser
            
            import json
            result = await chain.ainvoke({
                "job_description": job_description,
                "resume_data": json.dumps(base_resume_data),
                "format_instructions": parser.get_format_instructions()
            })
            
            return result.model_dump()
            
        except Exception as e:
            self.logger.error(f"Error tailoring resume: {e}")
            # Fallback to the original data if LLM fails
            return base_resume_data
