from typing import Dict, Any
from swarms import Agent

#Profile Enhancer agent: Enhances the candidate's profile
def profile_enhancer_agent_function(extracted_info: Dict[str, Any])-> Dict[str,Any]:
    # Copy input data to avoid modifying original information
    enhanced_profile = extracted_info.copy()
    #Calculate total years of professional experience from all listed roles in the "experience" list
    total_experience_years = sum(item["years"] for item in extracted_info["experience"])
    #Create a summary string detailing the candidate's overall profile, including name, total years,
    # assumed job roles(Data scientist and Analyst), and listed skills.
    enhanced_profile["summary"] = (
        f"{extracted_info['name']} has {total_experience_years} years of experience in roles including Data Scientist and Analyst, and possesses skills in {', '.join(extracted_info['skills'])}."
    )
    #Return the enhanced profile with new summary
    return enhanced_profile

#Create an agent instance using Swarms Agent class
profile_enhancer_agent = Agent(
    name = "Profile Enhancer Agent",
    model = "llama3.2",
    instructions = "Enhance the candidate's profile based on the extracted information.",
    functions = [profile_enhancer_agent_function],
)