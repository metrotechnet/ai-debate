# Charger les variables d'environnement
import os
from typing import Dict, Any, AsyncIterator
import asyncio
from pathlib import Path
from backend.models.agent import AgentConfig, AIProvider
from backend.models.debate import Debate
from backend.services.prompt_builder import PromptBuilder
from dotenv import load_dotenv

# Charger les variables d'environnement depuis backend/.env si présent
env_path = Path(__file__).resolve().parents[1] / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"ℹ️ Chargé .env depuis {env_path}")
else:
    # fallback to default search locations
    load_dotenv()


class AIService:
    """Service pour gérer les appels aux différentes API d'IA"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        
        # Initialiser le générateur de prompts
        self.prompt_builder = PromptBuilder()
        
        # Initialiser les clients uniquement si les clés sont disponibles
        self._init_clients()
    
    def _init_clients(self):
        """Initialiser les clients API"""
        
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your_openai_key_here":
            try:
                import openai
                # Première tentative: nouvel API client
                try:
                    self.openai_client = openai.OpenAI(api_key=openai_key)
                    print("✅ Client OpenAI initialisé (openai.OpenAI)")
                except Exception:
                    # Fallback: affecter la clé au module historique
                    try:
                        openai.api_key = openai_key 
                        self.openai_client = openai
                        print("✅ Client OpenAI initialisé (openai.api_key fallback)")
                    except Exception as e:
                        raise e
            except Exception as e:
                print(f"⚠️ Erreur initialisation OpenAI: {e}")
        else:
            print("ℹ️ OPENAI_API_KEY non défini — initialisation OpenAI ignorée")
        
        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_key_here":
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                print("✅ Client Anthropic initialisé")
            except Exception as e:
                print(f"⚠️ Erreur initialisation Anthropic: {e}")
        
        # Google
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key and google_key != "your_google_key_here":
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_key)
                self.google_client = genai
                print("✅ Client Google initialisé")
            except Exception as e:
                print(f"⚠️ Erreur initialisation Google: {e}")
    
    async def generate_response(
        self,
        agent: AgentConfig,
        system_prompt: str,
        user_prompt: str,
        conversation_history: list = None
    ) -> Dict[str, Any]:
        """
        Génère une réponse en utilisant l'API appropriée
        
        Returns:
            Dict avec 'content' (str) et 'tokens_used' (int)
        """
        
        if conversation_history is None:
            conversation_history = []
        
        # Dispatcher vers le bon provider
        if agent.ai_provider == AIProvider.OPENAI:
            return await self._generate_openai(agent, system_prompt, user_prompt, conversation_history)
        elif agent.ai_provider == AIProvider.ANTHROPIC:
            return await self._generate_anthropic(agent, system_prompt, user_prompt, conversation_history)
        elif agent.ai_provider == AIProvider.GOOGLE:
            return await self._generate_google(agent, system_prompt, user_prompt, conversation_history)
        else:
            # Fallback - réponse simulée
            return await self._generate_mock(agent, user_prompt)
    
    async def _generate_openai(
        self,
        agent: AgentConfig,
        system_prompt: str,
        user_prompt: str,
        conversation_history: list
    ) -> Dict[str, Any]:
        """Génère une réponse avec OpenAI"""
        
        if not self.openai_client:
            raise Exception("Client OpenAI non initialisé. Vérifiez votre clé API.")
        
        # Construire les messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self.openai_client.chat.completions.create(
                model=agent.model,
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                top_p=agent.top_p,
                presence_penalty=agent.presence_penalty,
                frequency_penalty=agent.frequency_penalty,
            )
            
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens
            }
        except Exception as e:
            raise Exception(f"Erreur OpenAI: {str(e)}")
    
    async def _generate_anthropic(
        self,
        agent: AgentConfig,
        system_prompt: str,
        user_prompt: str,
        conversation_history: list
    ) -> Dict[str, Any]:
        """Génère une réponse avec Anthropic Claude"""
        
        if not self.anthropic_client:
            raise Exception("Client Anthropic non initialisé. Vérifiez votre clé API.")
        
        # Anthropic utilise un format différent
        messages = []
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            response = self.anthropic_client.messages.create(
                model=agent.model,
                system=system_prompt,
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                top_p=agent.top_p
            )
            
            return {
                "content": response.content[0].text,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
        except Exception as e:
            raise Exception(f"Erreur Anthropic: {str(e)}")
    
    async def _generate_google(
        self,
        agent: AgentConfig,
        system_prompt: str,
        user_prompt: str,
        conversation_history: list
    ) -> Dict[str, Any]:
        """Génère une réponse avec Google Gemini"""
        
        if not self.google_client:
            raise Exception("Client Google non initialisé. Vérifiez votre clé API.")
        
        try:
            # Configurer le modèle
            model = self.google_client.GenerativeModel(
                model_name=agent.model,
                generation_config={
                    "temperature": agent.temperature,
                    "top_p": agent.top_p,
                    "max_output_tokens": agent.max_tokens,
                }
            )
            
            # Construire le prompt complet (Google ne supporte pas system prompt séparé pour tous les modèles)
            full_prompt = f"{system_prompt}\n\n---\n\n"
            
            # Ajouter l'historique
            for msg in conversation_history:
                role = "Assistant" if msg["role"] == "assistant" else "Adversaire"
                full_prompt += f"{role}: {msg['content']}\n\n"
            
            full_prompt += f"Question: {user_prompt}\n\nRéponse:"
            
            response = model.generate_content(full_prompt)
            
            return {
                "content": response.text,
                "tokens_used": 0  # Google ne fournit pas toujours le compte de tokens
            }
        except Exception as e:
            raise Exception(f"Erreur Google: {str(e)}")
    
    async def _generate_mock(
        self,
        agent: AgentConfig,
        user_prompt: str
    ) -> Dict[str, Any]:
        """Génère une réponse simulée (pour test sans API)"""
        
        mock_responses = {
            "populiste": f"[SIMULÉ] En tant qu'{agent.name}, je dois dire que c'est une question importante qui touche directement les gens ordinaires ! Il faut être pragmatique et direct sur ce sujet. Les élites ne comprennent pas la réalité du terrain.",
            "nuancé": f"[SIMULÉ] En tant qu'{agent.name}, il convient d'examiner cette question sous plusieurs angles. D'une part, nous devons considérer les implications éthiques, et d'autre part, les aspects pratiques. La vérité se situe souvent dans la nuance et le contexte.",
            "pragmatique": f"[SIMULÉ] En tant qu'{agent.name}, regardons les faits concrets. Qu'est-ce qui fonctionne dans la pratique ? Quels sont les résultats mesurables ? C'est cela qui doit guider notre réflexion.",
        }
        
        default_response = f"[SIMULÉ] En tant qu'{agent.name}, je réponds à cette question avec mon style {agent.debate_style} et mon ton {agent.tone}."
        
        return {
            "content": mock_responses.get(agent.debate_style, default_response),
            "tokens_used": 50
        }

    async def generate_response_stream(
        self,
        agent: AgentConfig,
        system_prompt: str,
        user_prompt: str,
        conversation_history: list = None,
        debate: Debate = None
    ) -> AsyncIterator[str]:
        """
        Génère une réponse en mode streaming (yield des tokens/segments)
        Retourne un async iterator de segments de texte.
        """
        if conversation_history is None:
            conversation_history = []

        # Option de debug: forcer le streaming simulé
        force_mock = os.getenv("FORCE_MOCK_STREAM", "false").lower() in ("1", "true", "yes")
        
        if force_mock:
            async for chunk in self._generate_mock_stream(agent, user_prompt):
                yield chunk
            return

        # Construire le prompt système pour les providers qui en ont besoin
        system_prompt = self.prompt_builder.build_agent_prompt(agent, user_prompt, debate)
        
        if agent.ai_provider == AIProvider.OPENAI:
            if not self.openai_client:
                # Fallback simulé lorsque le client OpenAI n'est pas initialisé
                async for chunk in self._generate_mock_stream(agent, user_prompt):
                    yield chunk
            else:
                async for chunk in self._generate_openai_stream(agent, system_prompt, user_prompt, conversation_history):
                    yield chunk
        elif agent.ai_provider == AIProvider.ANTHROPIC:
            async for chunk in self._generate_anthropic_stream(agent, system_prompt, user_prompt, conversation_history):
                yield chunk
        elif agent.ai_provider == AIProvider.GOOGLE:
            async for chunk in self._generate_google_stream(agent, system_prompt, user_prompt, conversation_history):
                yield chunk
        else:
            async for chunk in self._generate_mock_stream(agent, user_prompt):
                yield chunk

    async def _generate_mock_stream(self, agent: AgentConfig, user_prompt: str) -> AsyncIterator[str]:
        """Streaming simulé: génère du contenu de test par chunks"""
        # Contenu de test significatif pour le streaming
        test_content = f"En tant qu'{agent.name}, je réponds à votre question sur le débat. " \
                      f"Mon style est {agent.debate_style} avec un ton {agent.tone}. " \
                      "Voici mes arguments principaux: premièrement, il faut considérer les aspects sociaux. " \
                      "Deuxièmement, les implications économiques sont importantes. " \
                      "Troisièmement, nous devons examiner les conséquences à long terme. " \
                      "En conclusion, cette question mérite une analyse approfondie et nuancée."
        
        # Découper en petits morceaux de 3-5 mots pour simuler le streaming
        words = test_content.split(' ')
        
        for i in range(0, len(words), 4):
            chunk = ' '.join(words[i:i+4])
            if i + 4 < len(words):
                chunk += ' '  # Ajouter un espace sauf pour le dernier chunk
            yield chunk
            await asyncio.sleep(0.1)  # Pause pour simuler le streaming

    async def _generate_openai_stream(
        self,
        agent: AgentConfig,
        system_prompt: str,
        user_prompt: str,
        conversation_history: list
    ) -> AsyncIterator[str]:
        """Utilise le streaming OpenAI si disponible."""
        if not self.openai_client:
            raise Exception("Client OpenAI non initialisé. Vérifiez votre clé API.")

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_prompt})

        try:
            # Demande en mode stream
            response = self.openai_client.chat.completions.create(
                model=agent.model,
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                top_p=agent.top_p,
                presence_penalty=agent.presence_penalty,
                frequency_penalty=agent.frequency_penalty,
                stream=True
            )

            # L'itération retourne des morceaux (delta)
            for event in response:
                try:
                    # Plusieurs formes possibles selon la lib
                    chunk = ''
                    if hasattr(event, 'choices') and event.choices:
                        choice = event.choices[0]
                        if hasattr(choice, 'delta') and isinstance(choice.delta, dict):
                            chunk = choice.delta.get('content', '')
                        elif hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                            chunk = choice.delta.content or ''
                        elif hasattr(choice, 'message') and choice.message:
                            # fallback
                            chunk = getattr(choice.message, 'content', '')
                    # Si chunk vide, ignorer
                    if chunk:
                        yield chunk
                        # Petit délai pour rendre le streaming visible
                        await asyncio.sleep(0.05)
                except Exception:
                    continue

        except Exception as e:
            raise Exception(f"Erreur OpenAI streaming: {str(e)}")

    async def _generate_anthropic_stream(self, *args, **kwargs) -> AsyncIterator[str]:
        # Anthropic streaming non implémenté ici; fallback au mock
        async for chunk in self._generate_mock_stream(args[0], kwargs.get('user_prompt', '')):
            yield chunk

    async def _generate_google_stream(self, *args, **kwargs) -> AsyncIterator[str]:
        # Google streaming non implémenté ici; fallback au mock
        async for chunk in self._generate_mock_stream(args[0], kwargs.get('user_prompt', '')):
            yield chunk
