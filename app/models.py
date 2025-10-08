from pydantic import BaseModel
from typing import List

class Offer(BaseModel):
    name: str
    value_props: List[str]
    ideal_use_cases: List[str]

class Lead(BaseModel):
    name: str
    role: str
    company: str
    industry: str
    location: str
    linkedin_bio: str

class ScoredLead(BaseModel):
    name: str
    role: str
    company: str
    intent: str
    score: int
    reasoning: str