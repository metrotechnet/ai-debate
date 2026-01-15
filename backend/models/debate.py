from pydantic import BaseModel, Field
from typing import List, Optional
from backend.models.agent import ResponseLength
from datetime import datetime
from enum import Enum
from typing import Dict


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
    response_length: ResponseLength = Field(default=ResponseLength.MOYEN, description="Longueur des réponses: concis/moyen/verbeux")
    short_responses: Optional[bool] = Field(default=None, description="Compatibilité: anciennes données utilisant short_responses")
    # Position des agents dans le débat: valeurs possibles 'pour'|'contre'|'neutre'
    agent1_position: Optional[str] = Field(default="pour", description="Position de l'agent1: pour/contre/neutre")
    agent2_position: Optional[str] = Field(default="contre", description="Position de l'agent2: pour/contre/neutre")
    # Optionnel: URL d'une page HTML ou d'un PDF dont le texte sera ajouté au contexte du débat
    source_url: Optional[str] = Field(default=None, description="URL d'une page HTML ou d'un PDF à inclure dans le contexte du débat")


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
    # Texte extrait de la source (si fournie) et ajouté au contexte
    source_text: Optional[str] = None
    
    class Config:
        use_enum_values = True
