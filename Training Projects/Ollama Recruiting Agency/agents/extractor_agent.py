from typing import Dict,Any
from pdfminer.high_level import extract_text
from .base_agent import BaseAgent

class ExtractorAgent(BaseAgent):
    # Initialize the base class with specific parameters for this agent.
    def __init__(self):
        super().__init__(
            name = "Extractor",
            instructions= """
                Extract and structure information from resumes.
                Focus on: personal info, work experience, education, skills, and certifications.
                Provide output in a clear, structured format.
            """
        )
    
    async def run(self, messages:list)->Dict[str,Any]:
        """Process the resume and extract information"""
        print("Extractor: Processing resume")

        # Extract content from last message; expected to be a dictionary with PDF file path or raw text
        resume_data = eval(messages[-1]["content"])

        #Determine whether we're dealing witha PDF file or plain text.
        if resume_data.get("file_path"):
            #If the key "file_path" exists, extract raw text from the specified PDF using pdfminer's high-level function.
            raw_text = extract_text(resume_data["file_path"])
        else:
            #If no file path is provided, use any available text in the message directly (default to empty string if not present).
            raw_text = resume_data.get("text", "")

        #Query Ollama API with the extrated or inputted text to obtain structured information
        extracted_info = self._query_ollama(raw_text)

        return{
            "raw_text":raw_text,    #Raw extracted or inputted text
            "structured_data":extracted_info,   #Structured data obtained from querying the external service (Ollama)
            "extraction_status": "completed"    #Status indicating that extraction process has completed.
        }