from typing import Dict, Any
import json
from openai import OpenAI

class BaseAgent:
    def __init__(self,name:str,instructions:str):
        self.name = name
        self.instructions = instructions
        self.ollama_client = OpenAI(
            base_url = "http://localhost:11434/v1",
            api_key = "ollama",     #reqyured but unused
        )

    async def run(self,messages:list)->Dict[str, Any]:
        """Default run method to be overridden by child classes"""
        raise NotImplementedError("Subclasses must implement run()")
    
    def _query_ollama(self,prompt:str)->str:
        """Query Ollama model with the given prompt"""
        try:
            response = self.ollama_client.chat.completions.create(
                model = "llama3.2",
                messages =[
                    {"role":"system","content":self.instructions},
                    {"role": "user", "content":prompt},
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying Ollama: {str(e)}")
            raise

    # def _parse_json_safely(self,text:str)-> Dict[str,Any]:
    #     """Safely parse JSON from text, handling potential errors"""
    #     try:
    #         #Try to find JSON-like content between curly braces
    #         start = text.find("{")
    #         end = text.find("}")
    #         if start != -1 and end != -1:
    #             json_str = text[start:end+1]
    #             return json.loads(json_str)
    #         return {"error":"No JSON content found"}
    #     except json.JSONDecodeError:
    #         return {"error": "Invalid JSON content"}
    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        try:
            # Try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            # Extract JSON object or array from text using regex
            json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            # Return error dict if parsing fails
            return {"error": "Invalid JSON content"}