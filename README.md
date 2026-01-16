# 🎭 Agora IA - Débats entre Intelligences Artificielles

Application web permettant de créer et visualiser des débats entre agents IA configurables. Chaque agent possède son propre style de débat, personnalité, stratégie argumentative et génère des réponses en temps réel via streaming.

## 🎯 Fonctionnalités

- ✅ **Débats préconfigurés** - 10 sujets de débat prêts à l'emploi en français
- ✅ **Agents personnalisables** - 4 agents avec des profils distincts (Populiste, Nuancé, Provocateur, Pragmatique)
- ✅ **Streaming en temps réel** - Génération progressive des réponses via SSE
- ✅ **Extraction de sources** - Support HTML/PDF avec crawling automatique
- ✅ **Configuration flexible** - Positions (pour/contre), longueur des réponses (concis/moyen/verbeux), nombre de tours
- ✅ **Interface intuitive** - Sélection par liste déroulante, assignation dynamique des agents
- ✅ **Persistance** - Sauvegarde automatique des débats actifs

## 📁 Structure du projet

```
AI-Debate/
├── backend/                    # API Python (FastAPI)
│   ├── models/
│   │   ├── agent.py           # Modèles d'agents IA (styles, stratégies, paramètres)
│   │   └── debate.py          # Modèles de débats et configuration
│   ├── services/
│   │   ├── ai_service.py      # Intégration OpenAI avec streaming
│   │   ├── prompt_builder.py  # Construction des prompts système
│   │   └── source_fetcher.py  # Extraction de contenu web (HTML/PDF)
│   ├── data/
│   │   ├── agents.json        # 4 agents préconfigurés
│   │   ├── debates.json       # 10 débats template
│   │   └── active_debates.json # Débats en cours/terminés
│   ├── main.py                # API FastAPI avec endpoints
│   └── requirements.txt
├── frontend/                   # Interface client (Vanilla JS)
│   ├── index.html             # Structure de l'interface
│   ├── styles.css             # Styles et mise en page
│   └── app.js                 # Logique client et streaming SSE
└── start_server.ps1           # Script de démarrage Windows
```

## 🚀 Installation & Démarrage

### Prérequis
- Python 3.10+
- Clé API OpenAI

### Installation rapide

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd AI-Debate
```

2. **Créer l'environnement virtuel**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. **Installer les dépendances**
```bash
pip install -r backend/requirements.txt
```

4. **Configurer la clé API OpenAI**
```bash
# Créer un fichier .env à la racine
echo "OPENAI_API_KEY=votre_clé_api" > .env
```

5. **Démarrer l'application**
```powershell
.\start_server.ps1
```

L'application sera accessible sur:
- **Backend API**: http://localhost:8001
- **Documentation API**: http://localhost:8001/docs
- **Frontend**: Ouvrir `frontend/index.html` dans un navigateur

## 📖 Guide d'utilisation

### Démarrer un débat

1. **Sélectionner un débat** dans la liste déroulante (10 sujets préconfigurés)
2. **Choisir les agents** - Assignez un agent à chaque position
3. **Configurer la longueur** - Concis, Moyen ou Verbeux
4. **Cliquer sur "Démarrer le débat"** - Le système prépare le contexte (crawling source si nécessaire)
5. **"Tour suivant"** - Générer les interventions progressivement

### Agents disponibles

| Agent | Style | Ton | Stratégie | Longueur |
|-------|-------|-----|-----------|----------|
| **Agent Populiste** | Populiste | Combatif | Émotionnelle | Moyen |
| **Agent Nuancé** | Nuancé | Académique | Logique | Verbeux |
| **Agent Provocateur** | Provocateur | Combatif | Logique | Moyen |
| **Agent Pragmatique** | Pragmatique | Formel | Pragmatique | Concis |

### Débats préconfigurés

1. Le télétravail devrait-il devenir la norme
2. Les réseaux sociaux sont-ils plus néfastes que bénéfiques
3. Interdire les voitures thermiques d'ici 2030
4. Intégrer l'intelligence émotionnelle dans l'éducation
5. Le revenu universel comme solution à la pauvreté
6. Technologies de surveillance biométrique et libertés
7. Semaine de travail de 4 jours
8. Exploration spatiale vs défis terrestres
9. Régulation des influenceurs
10. Le nucléaire et la transition énergétique

## 🔌 API Endpoints

### Agents
- `GET /agents` - Liste tous les agents
- `POST /agents` - Créer un nouvel agent
- `GET /agents/{id}` - Récupérer un agent spécifique
- `PUT /agents/{id}` - Mettre à jour un agent
- `DELETE /agents/{id}` - Supprimer un agent

### Débats
- `GET /debates` - Liste tous les débats (templates + actifs)
- `POST /debates` - Créer un débat (avec DebateCreateRequest)
- `GET /debates/{id}` - Récupérer un débat
- `POST /debates/{id}/start` - Démarrer un débat (prépare la source)
- `POST /debates/{id}/next-turn` - Générer le tour suivant (JSON)
- `POST /debates/{id}/next-turn/stream` - Générer le tour suivant (SSE streaming)

Documentation interactive: http://localhost:8001/docs

## 🎨 Configuration des Agents

### Attributs principaux

**Identité**
- `name`, `ai_provider`, `model`, `description`

**Style & Personnalité**
- `debate_style`: nuancé | populiste | pragmatique | idéaliste | provocateur | conciliateur
- `tone`: formel | informel | académique | combatif | empathique
- `personality_traits`: Liste de traits (assertif, analytique, etc.)
- `rhetoric_level`: 1-10
- `emotional_intensity`: 1-10

**Stratégies argumentatives**
- `argumentation_strategy`: logique | émotionnelle | éthique | pragmatique
- `fallacy_tolerance`: 0-1 (tolérance aux sophismes)
- `use_examples`: rare | moderate | frequent
- `counter_strategy`: défensive | offensive | esquive

**Biais & Comportement**
- `open_mindedness`: 0-1 (ouverture d'esprit)
- `stubbornness`: 0-1 (entêtement)
- `concession_willingness`: 0-1 (volonté de concéder)

**Paramètres LLM**
- `temperature`: 0-2 (créativité)
- `max_tokens`: 50-4000
- `response_length`: concis | moyen | verbeux

## 🛠️ Technologies

**Backend**
- Python 3.11
- FastAPI 0.1.0 (avec lifespan context manager)
- Pydantic pour la validation
- OpenAI API (streaming)
- BeautifulSoup4 + PyPDF2 (extraction de sources)

**Frontend**
- HTML5 / CSS3
- Vanilla JavaScript
- Server-Sent Events (SSE) pour le streaming
- SweetAlert2 pour les notifications

**Stockage**
- Fichiers JSON (UTF-8-sig)
- Séparation templates (debates.json) / actifs (active_debates.json)

## 🚀 Déploiement sur GCP

### Architecture recommandée

```
Frontend (Cloud Storage + CDN)
    ↓
Backend (Cloud Run)
    ↓
Firestore/Cloud SQL
    ↓
OpenAI API
```

### Cloud Run (Backend)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
gcloud run deploy ai-debate-api \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key
```

### Cloud Storage (Frontend)

```bash
gsutil mb gs://ai-debate-frontend
gsutil -m cp -r frontend/* gs://ai-debate-frontend
gsutil web set -m index.html gs://ai-debate-frontend
```

**Coût estimé**: 5-20€/mois pour usage modéré

## 📝 Fonctionnalités techniques

### Streaming SSE
- Génération progressive des réponses
- Événements: `token` (segment), `done` (message complet), `error`
- Affichage temps réel avec échappement HTML

### Extraction de sources
- Crawling HTML avec BeautifulSoup4
- Parsing PDF avec PyPDF2
- Validation de pertinence du contenu
- Injection dans le contexte du débat

### Gestion des données
- Templates immuables (debates.json)
- Débats actifs séparés (active_debates.json)
- Sauvegarde uniquement des débats modifiés (status != pending)

## 🔧 Développement

### Environnement de développement

```bash
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1

# Lancer en mode debug
uvicorn backend.main:app --reload --port 8001
```

### Ajouter un nouvel agent

Éditer `backend/data/agents.json`:
```json
{
  "id": "agent-custom-001",
  "name": "Mon Agent",
  "debate_style": "nuancé",
  "tone": "formel",
  // ... autres paramètres
}
```

### Ajouter un débat

Éditer `backend/data/debates.json`:
```json
{
  "id": "debate-custom-001",
  "topic": "Mon sujet de débat",
  "agent1_id": "",
  "agent2_id": "",
  "config": {
    "max_turns": 10,
    "response_length": "moyen"
  }
}
```

## 🐛 Troubleshooting

**Erreur UTF-8 BOM**
- Utiliser `encoding='utf-8-sig'` pour la lecture des JSON

**422 Unprocessable Entity**
- Vérifier que `DebateCreateRequest` est utilisé (pas `Debate` complet)

**Agents non chargés**
- Redémarrer le serveur après modification de `agents.json`

**CORS errors**
- Vérifier que CORS est configuré dans `main.py` (`allow_origins=["*"]`)

## 📄 Licence

MIT

## 👥 Contribuer

Les contributions sont bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
