from typing import Dict, Any
from .base_agent import BaseAgent
from datetime import datetime

class AnalyzerAgent(BaseAgent):
    #Initialize the base class with specific parameters for this agent.
    def __init__(self):
        super().__init__(
            name = "Analyzer",
            instructions = """
            Analyze candidate profiles and extract:
            1. Technical skills (as a list)
            2. Years of experience (numeric)
            3. Education level
            4. Experience level (junior/mid-level/Senior)
            5. Key achievements
            6. Domain expertise

            Format the output as structured data.
            """
        )

    async def run(self, messages: list) -> Dict[str,Any]:
        """Analyze the exttracted resume data"""
        print("Analyzer: Analyzing candidate profile")

        #Extracting content from last message in input
        extracted_data = eval(messages[-1]["content"])

        #Construct analysis prompt to send to Ollama API
        analysis_prompt = f"""
            Analyze this resume data and return a JSON object with the following structures:
            - "years_of_experience": number of years of professional work experience (exclude schooling).
            - "experience_level": one of "Junior", "Mid-level", or "Senior" based strictly on years of professional experience:
                - Junior: 0-2 years
                - Mid-level: 3-5 years
                - Senior: 6+ years
            {{
                "technical_skills":["skill1", "skill2"],
                "years_of_experience": number,
                "education": {{
                    "level": "Diploma/Bachelors/Masters/PhD",
                    "field": "field of study"
                }},
                "experience_level": "Junior/Mid-level/Senior",
                "key_achievements": ["achievement1", "achievement2"],
                "domain_expertise": ["domain1", "domain2"]
            }}

            Resume data:
            {extracted_data["structured_data"]}

            Return ONLY the JSON object, no other text.
            """

        #Query Ollama API with analysis prompt
        analysis_result = self._query_ollama(analysis_prompt)

        #Parse returned result safely to handle errors in JSON format
        parsed_result = self._parse_json_safely(analysis_result)

        #Ensure we have valid data even if parsing fails, set default values for error handling.
        if "error" in parsed_result:
            parsed_result = {
                "technical_skills": [],
                "years_of_experience":0,
                "education": {"level": "Unknown", "field": "Unknown"},
                "experience_level": "Junior",
                "key_achievements":[],
                "domain_expertise":[],
            }
        # Return the structured analysis result along with timestamp, and confidence score
        return{
            "skills_analysis": parsed_result,
            "analysis_timestamp": datetime.now().isoformat(),
            #Higher confidence if there is no error in parsing, other wise lower it.
            "confidence_score": 0.85 if "error" not in parsed_result else 0.5,
        }