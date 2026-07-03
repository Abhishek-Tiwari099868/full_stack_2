import os
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

class ResumeAnalysisSchema(BaseModel):
    score: int = Field(description="Evaluation score between 0 and 100 assessing structure, depth, and formatting.")
    summary: str = Field(description="2-3 sentence overall review and critique of the resume.")
    strengths: List[str] = Field(description="List of 2 to 4 core strengths identified.")
    improvements: List[str] = Field(description="List of 2 to 4 concrete, actionable improvement recommendations.")
    suggested_roles: List[str] = Field(description="List of 1 to 3 job role recommendations.")

class ResumeDataSchema(BaseModel):
    name: Optional[str] = Field(description="Candidate's full name extracted from the resume.")
    role: Optional[str] = Field(description="Candidate's target role or current professional designation.")
    skills: List[str] = Field(description="List of technical skills, frameworks, and programming languages identified.")
    analysis: ResumeAnalysisSchema = Field(description="Structured AI evaluation critique analysis.")

class GeminiResumeService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                # Initialize using the new google-genai SDK format
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize google-genai Client: {str(e)}")

    def analyze_resume(self, resume_text):
        """
        Sends extracted PDF resume text to Gemini API using structured response outputs.
        Utilizes the latest google-genai SDK.
        """
        if not self.client:
            raise ValueError(
                "Gemini API client is not configured. "
                "Please add GEMINI_API_KEY to your environment variables."
            )

        prompt = f"""
        You are a senior technical recruiter and professional resume reviewer.
        Analyze the following candidate resume text and extract candidate profile details and feedback analysis.

        Resume Text:
        ---
        {resume_text}
        ---
        """

        try:
            # Execute generate_content with structured response configurations
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ResumeDataSchema,
                }
            )

            # Access SDK automatically parsed response matching Pydantic model structure
            if hasattr(response, 'parsed') and response.parsed:
                try:
                    return response.parsed.model_dump()
                except AttributeError:
                    return response.parsed.dict()
            else:
                raise ValueError("Response object is missing parsed structured output data.")

        except Exception as e:
            # Robust error handling: Log the raw response if parsing/evaluation fails
            raw_response_text = "N/A"
            try:
                if 'response' in locals() and hasattr(response, 'text'):
                    raw_response_text = response.text
            except Exception as read_err:
                raw_response_text = f"Error reading raw text: {str(read_err)}"

            print(f"ERROR: Gemini API structured analysis or client invocation failed: {str(e)}")
            print(f"RAW API RESPONSE FROM GEMINI:\n{raw_response_text}")

            raise RuntimeError(
                f"Gemini API structured analysis failed: {str(e)}. "
                f"Raw response output was logged to standard output."
            )