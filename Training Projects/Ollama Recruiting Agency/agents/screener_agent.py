from typing import Dict,Any
from .base_agent import BaseAgent
import datetime

#Define ScreenerAgent class inheriting from BaseAgent
class ScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            #Init base agent properties
            name = "Screener",
            instructions = """
                Screen candidates based on:
                - Qualification alignment
                - Experience relevance
                - Skill match percentage
                - Cultural fit indicators
                - Red flags or concerns
                Provide comprehensive screening reports.
                """,
            )
        
    async def run(self,messages:list)-> Dict[str,Any]:
        """Screen the candidate"""
        print("Screener: Conducting initial screening")

        # Retrieve and parse context information from last message content:
        workflow_context = eval(messages[-1]["content"],{"datetime":datetime})    #Evaluate string representation to dictionary
        
        #Perform actual querying/analysis of candidates based on parsed context.
        screening_results = self._query_ollama(str(workflow_context))

        return {
            "screening_report": screening_results,  #Report containing the results of candidate's analysis/screening
            "screening_timestamp": datetime.datetime.now(),  #Current time stamp
            "screening_score": 85,                  #Example score to indicate overall suitability or a numerical rating.
        }