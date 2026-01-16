from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.models.agent import AgentConfig
from backend.models.debate import Debate, DebateConfig, DebateMessage, MessageRole, DebateStatus, DebateCreateRequest
from typing import List
import uvicorn
import json
from pathlib import Path
from datetime import datetime
from backend.services.ai_service import AIService
from backend.services.prompt_builder import PromptBuilder
from backend.services.source_fetcher import fetch_source_text,topic_related_to_text
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    print("🚀 Démarrage de l'application Agora IA...")
    load_agents()
    load_debates()
    print(f"📊 Statut: {len(agents_db)} agents, {len(debates_db)} débats")
    yield
    # Shutdown (si nécessaire)
    print("👋 Arrêt de l'application...")


app = FastAPI(
    title="Agora IA API",
    description="API pour gérer des débats entre agents IA",
    version="0.1.0",
    lifespan=lifespan
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Middleware pour bypass l'authentification Cloud Run
@app.middleware("http")
async def bypass_auth(request, call_next):
    response = await call_next(request)
    return response

# Stockage temporaire en mémoire (à remplacer par une base de données)
agents_db = {}
debates_db = {}
debates_config_db = {}

# Chemins des fichiers de données
DATA_DIR = Path(__file__).parent / "data"
AGENTS_FILE = DATA_DIR / "agents.json"
DEBATES_FILE = DATA_DIR / "debates.json"
ACTIVE_DEBATES_FILE = DATA_DIR / "active_debates.json"

# Créer le dossier data s'il n'existe pas
DATA_DIR.mkdir(exist_ok=True)

# Service IA
ai_service = AIService()
prompt_builder = PromptBuilder()


def load_agents():
    """Charger les agents depuis le fichier JSON"""
    if AGENTS_FILE.exists():
        try:
            with open(AGENTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for agent_data in data.get('agents', []):
                    agent = AgentConfig(**agent_data)
                    agents_db[agent.id] = agent
            print(f"✅ {len(agents_db)} agents chargés depuis {AGENTS_FILE}")
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des agents: {e}")
    else:
        print(f"ℹ️ Aucun fichier d'agents trouvé à {AGENTS_FILE}")


def save_agents():
    """Sauvegarder les agents dans le fichier JSON"""
    try:
        agents_data = {
            "agents": [agent.model_dump(mode='json') for agent in agents_db.values()]
        }
        with open(AGENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(agents_data, f, indent=2, ensure_ascii=False)
        print(f"💾 {len(agents_db)} agents sauvegardés dans {AGENTS_FILE}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde des agents: {e}")


def load_debates():
    """Charger les débats préconfigurés et actifs depuis les fichiers JSON"""
    # Charger les débats préconfigurés (templates)
    if DEBATES_FILE.exists():
        try:
            with open(DEBATES_FILE, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
                for debate_data in data.get('debates', []):
                    debate = Debate(**debate_data)
                    debates_config_db[debate.id] = debate
            print(f"✅ {len(debates_config_db)} débats préconfigurés chargés depuis {DEBATES_FILE}")
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des débats préconfigurés: {e}")
    


def save_debates():
    """Sauvegarder uniquement les débats actifs/modifiés dans active_debates.json"""
    try:
        # Ne sauvegarder que les débats qui ne sont plus "pending" (ont été démarrés/modifiés)
        active_debates = [
            debate for debate in debates_db.values() 
            if debate.status != 'pending' or len(debate.messages) > 0 or debate.started_at is not None
        ]
        
        debates_data = {
            "debates": [debate.model_dump(mode='json') for debate in active_debates]
        }
        with open(ACTIVE_DEBATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(debates_data, f, indent=2, ensure_ascii=False)
        print(f"💾 {len(active_debates)} débats actifs sauvegardés dans {ACTIVE_DEBATES_FILE}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde des débats: {e}")


@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API AI Debate",
        "version": "0.1.0",
        "stats": {
            "agents": len(agents_db),
            "debates": len(debates_config_db)
        },
        "endpoints": {
            "agents": "/agents",
            "debates": "/debates",
            "docs": "/docs"
        }
    }


# ===== ENDPOINTS AGENTS =====

@app.post("/agents", response_model=AgentConfig)
async def create_agent(agent: AgentConfig):
    """Créer un nouveau agent"""
    import uuid
    agent.id = str(uuid.uuid4())
    agents_db[agent.id] = agent
    save_agents()
    return agent


@app.get("/agents", response_model=List[AgentConfig])
async def list_agents():
    """Lister tous les agents"""
    return list(agents_db.values())


@app.get("/agents/{agent_id}", response_model=AgentConfig)
async def get_agent(agent_id: str):
    """Récupérer un agent spécifique"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    return agents_db[agent_id]


@app.put("/agents/{agent_id}", response_model=AgentConfig)
async def update_agent(agent_id: str, agent: AgentConfig):
    """Mettre à jour un agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    agent.id = agent_id
    from datetime import datetime
    agent.updated_at = datetime.now()
    agents_db[agent_id] = agent
    save_agents()
    return agent


@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Supprimer un agent"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent non trouvé")
    del agents_db[agent_id]
    save_agents()
    return {"message": "Agent supprimé avec succès"}


# ===== ENDPOINTS DÉBATS =====

@app.post("/debates", response_model=Debate)
async def create_debate(request: DebateCreateRequest):
    """Créer un nouveau débat"""
    import uuid
    
    # Vérifier que les agents existent
    if request.agent1_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Agent 1 non trouvé: {request.agent1_id}")
    if request.agent2_id not in agents_db:
        raise HTTPException(status_code=404, detail=f"Agent 2 non trouvé: {request.agent2_id}")
    
    # Créer la configuration avec les valeurs par défaut
    config_data = request.config or {}
    debate_config = DebateConfig(
        topic=request.topic,
        max_turns=config_data.get('max_turns', 10),
        agent1_position=config_data.get('agent1_position', 'pour'),
        agent2_position=config_data.get('agent2_position', 'contre'),
        source_url=config_data.get('source_url'),
        response_length=config_data.get('response_length', 'moyen')
    )
    
    # Créer le débat
    debate = Debate(
        id=str(uuid.uuid4()),
        topic=request.topic,
        agent1_id=request.agent1_id,
        agent2_id=request.agent2_id,
        config=debate_config,
        status=DebateStatus.PENDING,
        messages=[],
        current_turn=0,
        created_at=datetime.now()
    )
    
    debates_db[debate.id] = debate
    save_debates()
    return debate


@app.get("/debates")
async def list_debates():
    """Lister tous les débats"""
    print(f"ℹ️ Récupération de la liste des débats ({len(debates_config_db)} au total)")
    return {"debates": list(debates_config_db.values())}


@app.get("/debates/{debate_id}", response_model=Debate)
async def get_debate(debate_id: str):
    """Récupérer un débat spécifique"""
    if debate_id not in debates_db:
        raise HTTPException(status_code=404, detail="Débat non trouvé")
    return debates_db[debate_id]


@app.post("/debates/{debate_id}/next-turn")
async def next_turn(debate_id: str):
    """Faire progresser le débat d'un tour"""
    
    # Vérifier que le débat existe
    if debate_id not in debates_db:
        raise HTTPException(status_code=404, detail="Débat non trouvé")
    
    debate = debates_db[debate_id]
    
    # Vérifier que le débat n'est pas terminé
    if debate.status == DebateStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Le débat est déjà terminé")
    
    # Vérifier qu'on n'a pas atteint le max de tours
    if debate.current_turn >= debate.config.max_turns:
        debate.status = DebateStatus.COMPLETED
        debate.completed_at = datetime.now()
        save_debates()
        raise HTTPException(status_code=400, detail="Nombre maximum de tours atteint")
    
    # Récupérer les agents
    agent1 = agents_db.get(debate.agent1_id)
    agent2 = agents_db.get(debate.agent2_id)
    
    if not agent1 or not agent2:
        raise HTTPException(status_code=500, detail="Agents non trouvés")
    
    # Marquer le début du débat si c'est le premier tour
    if debate.current_turn == 0 and not debate.started_at:
        debate.status = DebateStatus.IN_PROGRESS
        debate.started_at = datetime.now()
    
    try:
        # Déterminer quel agent parle (alternance)
        is_agent1_turn = len(debate.messages) % 2 == 0
        current_agent = agent1 if is_agent1_turn else agent2
        current_role = MessageRole.AGENT1 if is_agent1_turn else MessageRole.AGENT2
        
        # Construire le prompt système
        system_prompt = prompt_builder.build_system_prompt(current_agent, debate)
        
        # Obtenir le dernier message de l'adversaire
        opponent_last_message = None
        if debate.messages:
            opponent_last_message = debate.messages[-1].content
        
        # Construire le prompt utilisateur
        user_prompt = prompt_builder.build_user_prompt(debate, opponent_last_message)
        
        # Construire l'historique de conversation pour l'agent actuel
        conversation_history = prompt_builder.build_conversation_history(
            debate.messages,
            current_agent.id
        )
        
        # Générer la réponse
        response = await ai_service.generate_response(
            current_agent,
            system_prompt,
            user_prompt,
            conversation_history
        ) 
        
        # Créer le message
        import uuid
        message = DebateMessage(
            id=str(uuid.uuid4()),
            debate_id=debate_id,
            role=current_role,
            agent_id=current_agent.id,
            content=response["content"],
            timestamp=datetime.now(),
            turn_number=debate.current_turn,
            tokens_used=response.get("tokens_used", 0)
        )
        
        # Ajouter le message au débat
        debate.messages.append(message)
        
        # Incrémenter le tour après que les deux agents aient parlé
        if not is_agent1_turn:
            debate.current_turn += 1
        
        # Vérifier si le débat est terminé
        if debate.current_turn >= debate.config.max_turns:
            debate.status = DebateStatus.COMPLETED
            debate.completed_at = datetime.now()
        
        # Sauvegarder
        save_debates()
        
        return {
            "success": True,
            "message": message,
            "debate": debate,
            "next_speaker": "agent2" if is_agent1_turn else "agent1"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@app.post("/debates/{debate_id}/next-turn/stream")
async def next_turn_stream(debate_id: str):
    """Endpoint streaming (SSE) pour le tour suivant.
    Envoie des segments de texte au client au fur et à mesure.
    """
    # Vérifier que le débat existe
    if debate_id not in debates_db:
        raise HTTPException(status_code=404, detail="Débat non trouvé")

    debate = debates_db[debate_id]

    # Vérifier que le débat n'est pas terminé
    if debate.status == DebateStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Le débat est déjà terminé")

    # Vérifier qu'on n'a pas atteint le max de tours
    if debate.current_turn >= debate.config.max_turns:
        debate.status = DebateStatus.COMPLETED
        debate.completed_at = datetime.now()
        save_debates()
        raise HTTPException(status_code=400, detail="Nombre maximum de tours atteint")

    # Récupérer les agents
    agent1 = agents_db.get(debate.agent1_id)
    agent2 = agents_db.get(debate.agent2_id)

    if not agent1 or not agent2:
        raise HTTPException(status_code=500, detail="Agents non trouvés")

    # Déterminer quel agent parle (alternance)
    is_agent1_turn = len(debate.messages) % 2 == 0
    current_agent = agent1 if is_agent1_turn else agent2
    current_role = MessageRole.AGENT1 if is_agent1_turn else MessageRole.AGENT2

    # Construire le prompt système
    system_prompt = prompt_builder.build_system_prompt(current_agent, debate)

    # Obtenir le dernier message de l'adversaire
    opponent_last_message = None
    if debate.messages:
        opponent_last_message = debate.messages[-1].content

    # Construire le prompt utilisateur
    user_prompt = prompt_builder.build_user_prompt(debate, opponent_last_message)

    # Construire l'historique de conversation pour l'agent actuel
    conversation_history = prompt_builder.build_conversation_history(
        debate.messages,
        current_agent.id
    )

    async def event_generator():
        try:
            full_content = ""
            chunk_count = 0
            async for chunk in ai_service.generate_response_stream(
                current_agent,
                system_prompt,
                user_prompt,
                conversation_history,
                debate
            ):
                chunk_count += 1
                full_content += chunk
                payload = {"type": "token", "text": chunk}
                yield f"data: {json.dumps(payload)}\n\n"

            # Après la fin du streaming, créer le message final et sauvegarder
            import uuid
            message = DebateMessage(
                id=str(uuid.uuid4()),
                debate_id=debate_id,
                role=current_role,
                agent_id=current_agent.id,
                content=full_content,
                timestamp=datetime.now(),
                turn_number=debate.current_turn,
                tokens_used=0
            )

            debate.messages.append(message)

            # Incrémenter le tour après que les deux agents aient parlé
            if not is_agent1_turn:
                debate.current_turn += 1

            # Vérifier si le débat est terminé
            if debate.current_turn >= debate.config.max_turns:
                debate.status = DebateStatus.COMPLETED
                debate.completed_at = datetime.now()

            save_debates()

            message_dict = {
                'id': message.id,
                'debate_id': message.debate_id,
                'role': message.role,
                'agent_id': message.agent_id,
                'content': message.content,
                'timestamp': message.timestamp.isoformat() if message.timestamp else None,
                'turn_number': message.turn_number,
                'tokens_used': message.tokens_used
            }

            final_payload = {
                'type': 'done',
                'message': message_dict,
                'debate': {
                    'id': debate.id,
                    'current_turn': debate.current_turn,
                    'status': debate.status
                }
            }

            yield f"data: {json.dumps(final_payload)}\n\n"

        except Exception as e:
            err = {"type": "error", "detail": str(e)}
            yield f"data: {json.dumps(err)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/debates/{debate_id}/start")
async def start_debate(debate_id: str):
    """Démarrer un débat (déclarations d'ouverture des deux agents)"""
    
    if debate_id not in debates_db:
        raise HTTPException(status_code=404, detail="Débat non trouvé")
    
    debate = debates_db[debate_id]
    
    if debate.status != DebateStatus.PENDING:
        raise HTTPException(status_code=400, detail="Le débat a déjà commencé")
    
    debate.status = DebateStatus.IN_PROGRESS
    debate.started_at = datetime.now()
    # Si une source URL est fournie, déléguer l'extraction au module `source_fetcher`
    source_url = getattr(debate.config, 'source_url', None)
    if source_url:
        try:
            extracted = fetch_source_text(source_url)
            if extracted:
                # Valider que le sujet du débat est en lien avec le texte extrait
                if not topic_related_to_text(debate.topic, extracted):
                    # Ne pas démarrer le débat si la source n'est pas pertinente
                    raise HTTPException(status_code=400, detail="Le sujet du débat ne semble pas lié au contenu de la source fournie.")

                debate.source_text = extracted
                import uuid
                snippet = extracted[:8000]
                sys_msg = DebateMessage(
                    id=str(uuid.uuid4()),
                    debate_id=debate.id,
                    role=MessageRole.SYSTEM,
                    agent_id=None,
                    content=f"Contexte provenant de {source_url}:\n\n{snippet}",
                    timestamp=datetime.now(),
                    turn_number=0,
                    tokens_used=None
                )
                debate.messages.insert(0, sys_msg)
        except Exception as e:
            print(f"⚠️ Impossible de récupérer la source {source_url}: {e}")

    save_debates()
    
    return {"success": True, "debate": debate}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
