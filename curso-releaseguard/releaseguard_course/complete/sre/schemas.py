from pydantic import BaseModel, Field
from typing import Literal
class Incident(BaseModel):
    service:str
    symptom:str
    window_minutes:int=Field(default=10,ge=1,le=60)
class Evidence(BaseModel):
    source:Literal['metrics','traces','health','changes','errors']
    summary:str
    raw:object|None=None
class InvestigationResult(BaseModel):
    symptom:str
    evidence:list[Evidence]
    probable_cause:str
    confidence:float=Field(ge=0,le=1)
    active_incident:bool
    unsupported_claims:list[str]=[]
    remediation_options:list[str]=[]
    requires_human:bool=True
