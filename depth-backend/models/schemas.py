from pydantic import BaseModel
from typing import Optional, List


class Message(BaseModel):
    role: str  # "user" or "model"
    content: str


class ChatRequest(BaseModel):
    history: List[Message]
    message: str


class TriageData(BaseModel):
    level: str  # "URGENT", "SOON", "HOME"
    explanation: str


class DrugInteraction(BaseModel):
    drug: str
    warning: str
    severity: str  # "HIGH", "MEDIUM", "LOW"


class Clinic(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    distance: Optional[float] = None
    website: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    stage: str  # "INTAKE", "SUMMARY", "TRIAGE", "GUIDANCE", "COMPLETE"
    clinical_summary: Optional[str] = None
    triage: Optional[TriageData] = None
    drug_interactions: Optional[List[DrugInteraction]] = None
    clinics: Optional[List[Clinic]] = None


class InteractionRequest(BaseModel):
    medications: List[str]


class InteractionResponse(BaseModel):
    interactions: List[DrugInteraction]
    summary: str
