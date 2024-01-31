from pydantic import BaseModel

class Candidate(BaseModel):
    resume: str
    name: str
    rawText: str
    data: dict
