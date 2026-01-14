from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    AGENT1 = "agent1"
    AGENT2 = "agent2"
    MODERATOR = "moderator"
    SYSTEM = "system"


class DebateStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DebateMessage(BaseModel):
    """Message dans un débat"""
    id: Optional[str] = None
    debate_id: str
    role: MessageRole
    agent_id: Optional[str] = None
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    turn_number: int
    tokens_used: Optional[int] = None
    
    class Config:
        use_enum_values = True


class DebateConfig(BaseModel):
    """Configuration d'un débat"""
    topic: str = Field(..., description="Sujet du débat")
    max_turns: int = Field(default=10, ge=1, le=100, description="Nombre maximum de tours")
    turn_time_limit: Optional[int] = Field(default=None, description="Limite de temps par tour en secondes")
    opening_statement_required: bool = Field(default=True, description="Déclaration d'ouverture obligatoire")
    closing_statement_required: bool = Field(default=True, description="Déclaration de clôture obligatoire")
    allow_questions: bool = Field(default=True, description="Permettre les questions")
    moderated: bool = Field(default=False, description="Débat modéré")
    short_responses: bool = Field(default=True, description="Forcer les réponses courtes (2-3 phrases max)")


class Debate(BaseModel):
    """Débat entre deux agents"""
    id: Optional[str] = None
    topic: str
    agent1_id: str
    agent2_id: str
    config: DebateConfig
    status: DebateStatus = Field(default=DebateStatus.PENDING)
    messages: List[DebateMessage] = Field(default_factory=list)
    current_turn: int = Field(default=0)
    winner_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
