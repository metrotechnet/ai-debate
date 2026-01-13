from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class DebateStyle(str, Enum):
    NUANCE = "nuancé"
    POPULISTE = "populiste"
    PRAGMATIQUE = "pragmatique"
    IDEALISTE = "idéaliste"
    PROVOCATEUR = "provocateur"
    CONCILIATEUR = "conciliateur"


class Tone(str, Enum):
    FORMEL = "formel"
    INFORMEL = "informel"
    ACADEMIQUE = "académique"
    COMBATIF = "combatif"
    EMPATHIQUE = "empathique"


class ArgumentationStrategy(str, Enum):
    LOGIQUE = "logique"
    EMOTIONNELLE = "émotionnelle"
    ETHIQUE = "éthique"
    PRAGMATIQUE = "pragmatique"


class ResponseLength(str, Enum):
    CONCIS = "concis"
    MOYEN = "moyen"
    VERBEUX = "verbeux"


class AIProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"


class AgentConfig(BaseModel):
    """Configuration complète d'un agent de débat IA"""
    
    # Identité & Configuration de Base
    id: Optional[str] = None
    name: str = Field(..., description="Nom de l'agent")
    ai_provider: AIProvider = Field(..., description="Fournisseur de l'IA")
    model: str = Field(..., description="Modèle spécifique (ex: gpt-4, gemini-pro)")
    description: str = Field(..., description="Description courte de l'agent")
    
    # Style & Personnalité
    debate_style: DebateStyle = Field(..., description="Style principal de débat")
    tone: Tone = Field(default=Tone.FORMEL, description="Tonalité du discours")
    personality_traits: List[str] = Field(default_factory=list, description="Traits de personnalité")
    rhetoric_level: int = Field(default=5, ge=1, le=10, description="Niveau rhétorique")
    emotional_intensity: int = Field(default=5, ge=1, le=10, description="Intensité émotionnelle")
    
    # Stratégies Argumentatives
    argumentation_strategy: ArgumentationStrategy = Field(..., description="Approche argumentative principale")
    fallacy_tolerance: float = Field(default=0.5, ge=0, le=1, description="Tolérance aux sophismes")
    use_examples: Literal["rare", "moderate", "frequent"] = Field(default="moderate")
    use_statistics: bool = Field(default=True, description="Utiliser des statistiques")
    use_analogies: bool = Field(default=True, description="Utiliser des analogies")
    counter_strategy: Literal["défensive", "offensive", "esquive"] = Field(default="défensive")
    
    # Biais & Positionnement
    political_bias: Optional[str] = Field(default=None, description="Orientation politique")
    cognitive_biases: List[str] = Field(default_factory=list, description="Biais cognitifs à simuler")
    open_mindedness: float = Field(default=0.5, ge=0, le=1, description="Ouverture d'esprit")
    stubbornness: float = Field(default=0.5, ge=0, le=1, description="Entêtement")
    
    # Paramètres Techniques (LLM)
    temperature: float = Field(default=0.7, ge=0, le=2, description="Créativité/aléatoire")
    max_tokens: int = Field(default=500, ge=50, le=4000, description="Longueur max de réponse")
    top_p: float = Field(default=1.0, ge=0, le=1, description="Échantillonnage nucleus")
    presence_penalty: float = Field(default=0.0, ge=-2, le=2)
    frequency_penalty: float = Field(default=0.0, ge=-2, le=2)
    
    # Contexte & Connaissances
    expertise_domains: List[str] = Field(default_factory=list, description="Domaines d'expertise")
    knowledge_cutoff: Optional[str] = Field(default=None, description="Date limite de connaissances")
    allowed_sources: List[str] = Field(default_factory=list, description="Sources autorisées")
    language: str = Field(default="fr", description="Langue principale")
    
    # Comportement de Débat
    response_length: ResponseLength = Field(default=ResponseLength.MOYEN)
    interrupt_tendency: float = Field(default=0.3, ge=0, le=1, description="Tendance à interrompre")
    concession_willingness: float = Field(default=0.5, ge=0, le=1, description="Volonté de concéder")
    question_frequency: float = Field(default=0.3, ge=0, le=1, description="Fréquence de questions rhétoriques")
    
    # Méta-configuration
    system_prompt_template: Optional[str] = Field(default=None, description="Template du prompt système")
    debate_objectives: List[str] = Field(default_factory=lambda: ["convaincre"], description="Objectifs du débat")
    active: bool = Field(default=True, description="Agent actif")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "Agent Populiste",
                "ai_provider": "openai",
                "model": "gpt-4",
                "description": "Un agent au style populiste et direct",
                "debate_style": "populiste",
                "tone": "combatif",
                "argumentation_strategy": "émotionnelle",
                "personality_traits": ["assertif", "passionné", "simplificateur"],
                "expertise_domains": ["politique", "économie"],
                "rhetoric_level": 7,
                "emotional_intensity": 8
            }
        }
