# AI Recruiter Agency

## Overview
AI Recruiter Agency is an intelligent recruiting platform that orchestrates multiple AI agents to streamline the candidate evaluation process. Our system leverages an Applicant Tracking System (ATS) integrated with AI-driven components to cross-compare a candidate's resume against a curated subset of synthetic job postings. This enables efficient, insightful matching and shortlisting within a controlled testing environment.

## Features
- **Multi-agent orchestration:** Coordinates several AI agents specializing in resume parsing, job posting analysis, and candidate-job matching.
- **ATS Integration:** Utilizes a simulated ATS system to manage candidate data and job listings.
- **Synthetic job postings:** Works with a small dataset of fabricated job opportunities to ensure privacy and support prototype testing.
- **Resume matching:** Compares candidate resumes against job criteria to generate relevance scores and highlight competencies.
- **Extensible architecture:** Modular AI agents can be extended or replaced to improve performance or support additional use cases.

## Installation
Clone this repository:

git clone https://github.com/DamienHu/Small-Projects/tree/main/Training%20Projects/Ollama%20Recruiting%20Agency

Install dependencies:

pip install -r requirements.txt

Configure ATS and dataset paths in `config.yaml`.

## Usage
1. Prepare your resume file(s) in supported formats (e.g., PDF, DOCX).
2. Run the agent orchestrator:

streamlit run app.py

3. View the matching results and recommendations in the console or output report.

## Project Structure
- `agents/` — AI agent modules for parsing, matching, and analysis  
- `data/` — Synthetic job postings and example resumes  
- `app.py` — Main program coordinating AI agents  
- `config.yaml` — Configuration for system parameters and data paths  
- `requirements.txt` — Python dependencies  

## Contributing
Contributions are welcome! Please submit issues or pull requests for bug fixes, new features, or performance improvements.
