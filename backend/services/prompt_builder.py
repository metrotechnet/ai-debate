from models.agent import AgentConfig
from models.debate import Debate, DebateMessage
from typing import List


class PromptBuilder:
    """Constructeur de prompts système personnalisés pour les agents"""
    
    @staticmethod
    def build_system_prompt(agent: AgentConfig, debate: Debate) -> str:
        """Construit le prompt système complet pour un agent"""
        
        # Utiliser le template personnalisé si disponible
        if agent.system_prompt_template:
            return agent.system_prompt_template
        
        # Sinon, construire un prompt basé sur les attributs
        prompt_parts = []
        
        # Introduction et rôle
        prompt_parts.append(f"Tu es {agent.name}, un agent de débat IA.")
        prompt_parts.append(f"Description: {agent.description}")
        
        # Style et personnalité
        prompt_parts.append(f"\n## Style de débat")
        prompt_parts.append(f"- Style: {agent.debate_style}")
        prompt_parts.append(f"- Ton: {agent.tone}")
        prompt_parts.append(f"- Intensité émotionnelle: {agent.emotional_intensity}/10")
        prompt_parts.append(f"- Niveau rhétorique: {agent.rhetoric_level}/10")
        
        if agent.personality_traits:
            traits = ", ".join(agent.personality_traits)
            prompt_parts.append(f"- Traits de personnalité: {traits}")
        
        # Stratégie argumentative
        prompt_parts.append(f"\n## Stratégie argumentative")
        prompt_parts.append(f"- Approche principale: {agent.argumentation_strategy}")
        prompt_parts.append(f"- Contre-stratégie: {agent.counter_strategy}")
        
        if agent.use_examples == "frequent":
            prompt_parts.append("- Utilise FRÉQUEMMENT des exemples concrets")
        elif agent.use_examples == "rare":
            prompt_parts.append("- Utilise RAREMENT des exemples, privilégie l'abstraction")
        
        if agent.use_statistics:
            prompt_parts.append("- Cite des statistiques et données chiffrées")
        
        if agent.use_analogies:
            prompt_parts.append("- Utilise des analogies pour clarifier tes points")
        
        # Biais et positionnement
        if agent.political_bias:
            prompt_parts.append(f"\n## Positionnement")
            prompt_parts.append(f"- Orientation: {agent.political_bias}")
        
        if agent.cognitive_biases:
            prompt_parts.append(f"- Biais cognitifs à simuler: {', '.join(agent.cognitive_biases)}")
        
        prompt_parts.append(f"- Ouverture d'esprit: {int(agent.open_mindedness * 100)}%")
        prompt_parts.append(f"- Entêtement: {int(agent.stubbornness * 100)}%")
        
        # Expertise
        if agent.expertise_domains:
            domains = ", ".join(agent.expertise_domains)
            prompt_parts.append(f"\n## Domaines d'expertise")
            prompt_parts.append(f"{domains}")
        
        # Objectifs
        if agent.debate_objectives:
            objectives = ", ".join(agent.debate_objectives)
            prompt_parts.append(f"\n## Objectifs du débat")
            prompt_parts.append(f"{objectives}")
        
        # Consignes de longueur
        prompt_parts.append(f"\n## Format de réponse")
        if agent.response_length == "concis":
            prompt_parts.append("- Réponses CONCISES (2-3 paragraphes maximum)")
        elif agent.response_length == "verbeux":
            prompt_parts.append("- Réponses DÉTAILLÉES et approfondies")
        else:
            prompt_parts.append("- Réponses de longueur MOYENNE (3-4 paragraphes)")
        
        if agent.question_frequency > 0.5:
            prompt_parts.append("- Utilise des questions rhétoriques fréquemment")
        
        # Instructions finales
        prompt_parts.append(f"\n## Instructions importantes")
        prompt_parts.append(f"- Réponds UNIQUEMENT en français")
        prompt_parts.append(f"- Reste fidèle à ton style et ta personnalité")
        prompt_parts.append(f"- Ne sors JAMAIS de ton rôle")
        prompt_parts.append(f"- Sujet du débat: {debate.topic}")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def build_conversation_history(messages: List[DebateMessage], current_agent_id: str) -> List[dict]:
        """Construit l'historique de conversation pour l'API"""
        history = []
        
        for msg in messages:
            role = "assistant" if msg.agent_id == current_agent_id else "user"
            history.append({
                "role": role,
                "content": msg.content
            })
        
        return history
    
    @staticmethod
    def build_user_prompt(debate: Debate, opponent_last_message: str = None) -> str:
        """Construit le prompt utilisateur pour le tour actuel"""
        
        turn = debate.current_turn
        
        # Premier tour - déclaration d'ouverture
        if turn == 0 and debate.config.opening_statement_required:
            return f"Fais ta déclaration d'ouverture sur le sujet: '{debate.topic}'. Présente ta position et tes arguments principaux."
        
        # Dernier tour - déclaration de clôture
        if turn == debate.config.max_turns - 1 and debate.config.closing_statement_required:
            return f"Fais ta déclaration de clôture. Résume tes arguments principaux et conclus ta position sur '{debate.topic}'."
        
        # Tours intermédiaires - réponse à l'adversaire
        if opponent_last_message:
            return f"Réponds aux arguments de ton adversaire et développe ta position."
        
        # Fallback
        return f"Continue le débat sur '{debate.topic}'."
