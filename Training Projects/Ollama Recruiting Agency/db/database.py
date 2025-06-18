import sqlite3
from pathlib import Path
from typing import Dict,List,Any
import json
import os

class JobDatabase:
    def __init__(self):
        #Determine the directory where this script (JobDatabase class)
        current_dir = Path(__file__).parent

        #Define paths to database file and schema SQL file based on the location of the current script.
        self.db_path = current_dir / "jobs.sqllite"
        self.schema_path = current_dir / "schema.sql"

        #Initialize the database with its predefined schema.
        self._init_db()

    def _init_db(self):
        """Initialize the database with schema"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found at {self.schema_path}")
        
        #Read in the SQL script from the schema file to create tables and initial settings.
        with open(self.schema_path) as f:
            schema = f.read()

        #Connect to the SQLite database, executre the schema, and commit it (if necessary).
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)

    def add_job(self, job_data: Dict[str,Any])->int:
        """Add a new job to the database"""
        query = """
            INSERT INTO jobs(
                title, company, location, type, experience_level,
                salary_range, description, requirements, benefits
            ) VALUES (?,?,?,?,?,?,?,?,?)
            """
        
        # Connnect to the SQLite database and execute an insert statement with the provided job data.
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                query,(
                    job_data["title"],
                    job_data["company"],
                    job_data["location"],
                    job_data["type"],
                    job_data["experience_level"],
                    job_data.get("salary_range"),
                    job_data["description"],
                    json.dumps(job_data["requirements"]),
                    json.dumps(job_data.get("benefits",[])),
                ),
            )
            #Return the ID of the newly inserted row
            return cursor.lastrowid
        
    def get_all_jobs(self)-> List[Dict[str,Any]]:
        """Retrieve all jobs from the database"""
        query = "SELECT * FROM jobs ORDER BY created_at DESC"

        #Connnect to the SQLite database and execute a select statement that retrieves all job data.
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            #Process each row into a dictionary format, convert JSON fields back to Python objects.
            return [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "company": row["company"],
                    "location": row["location"],
                    "type": row["type"],
                    "experience_level": row["experience_level"],
                    "salary_range": row["salary_range"],
                    "description": row["description"],
                    "requirements": json.loads(row["requirements"]),
                    "benefits": json.loads(row["benefits"]) if row["benefits"] else [],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
        
    def search_jobs(self, skills: List[str],experience_level: str) -> List[Dict[str,Any]]:
        """Search jobs based on skills and experience level"""
        query = """
            SELECT * FROM jobs
            WHERE experience_level = ?
            AND (
            """
        
        # Initialize the list for SQL conditions and parameters to be used in the SQL statement.
        query_conditions = []
        params = [experience_level]

        #Create LIKE conditions for each skill provided in the search criteria.
        for skill in skills:
            query_conditions.append("requirements LIKE ?")
            params.append(f"%{skill}%")

        #Append all generated conditions to the main SQL query with 'OR' logic between them.
        query += " OR ".join(query_conditions) + ")"

        try:
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query,params)
                rows = cursor.fetchall()

                #Process each row into a dictionary format and convert JSON fields back to Python objects.
                return[
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "company": row["company"],
                        "location": row["location"],
                        "type": row["type"],
                        "experience_level": row["experience_level"],
                        "salary_range": row["salary_range"],
                        "description": row["description"],
                        "requirements": json.loads(row["requirements"]),
                        "benefits": (
                            json.loads(row["benefits"]) if row["benefits"] else[]
                        ),
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []