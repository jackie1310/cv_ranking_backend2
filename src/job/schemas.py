from pydantic import BaseModel

class JobSchema(BaseModel):
    job_name: str
    job_description: str