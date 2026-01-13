# AI Debate

Application permettant à deux intelligences artificielles de débattre sur un sujet donné. Les agents IA peuvent être configurés avec différents styles de débat, personnalités et stratégies argumentatives.

## 🎯 Fonctionnalités

- ✅ Création et configuration d'agents IA avec styles personnalisés
- ✅ Configuration de débats entre deux agents
- ✅ Interface web pour visualiser les débats
- 🚧 Intégration avec OpenAI, Google Gemini, Anthropic Claude
- 🚧 Système de tours de parole
- 🚧 Analyse et évaluation des arguments

## 📁 Structure du projet

```
AI-Debate/
├── backend/           # API Python (FastAPI)
│   ├── models/        # Modèles de données (Pydantic)
│   │   ├── agent.py   # Configuration des agents
│   │   └── debate.py  # Configuration des débats
│   ├── main.py        # Point d'entrée de l'API
│   ├── requirements.txt
│   └── .env.example
└── frontend/          # Interface client (HTML/CSS/JS)
    ├── index.html
    ├── styles.css
    └── app.js
```

## 🚀 Installation

### Backend (Python)

1. Créer un environnement virtuel:
```bash
cd backend
python -m venv venv
```

2. Activer l'environnement:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances:
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement:
```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

5. Lancer le serveur:
```bash
python main.py
```

L'API sera disponible sur http://localhost:8000

### Frontend (JavaScript)

1. Ouvrir `frontend/index.html` dans un navigateur web

Ou utiliser un serveur local:
```bash
cd frontend
python -m http.server 8080
```

Puis accéder à http://localhost:8080

## 📋 Taxonomie des Agents

Chaque agent IA est défini par les attributs suivants:

### Identité
- **name**: Nom de l'agent
- **ai_provider**: Fournisseur (openai, google, anthropic, mistral)
- **model**: Modèle spécifique
- **description**: Description de l'agent

### Style & Personnalité
- **debate_style**: nuancé, populiste, pragmatique, idéaliste, provocateur, conciliateur
- **tone**: formel, informel, académique, combatif, empathique
- **personality_traits**: Liste de traits de personnalité
- **rhetoric_level**: Niveau rhétorique (1-10)
- **emotional_intensity**: Intensité émotionnelle (1-10)

### Stratégies
- **argumentation_strategy**: logique, émotionnelle, éthique, pragmatique
- **fallacy_tolerance**: Tolérance aux sophismes (0-1)
- **use_examples**: Fréquence d'utilisation d'exemples
- **counter_strategy**: défensive, offensive, esquive

### Biais & Comportement
- **political_bias**: Orientation politique
- **open_mindedness**: Ouverture d'esprit (0-1)
- **stubbornness**: Entêtement (0-1)
- **concession_willingness**: Volonté de faire des concessions

### Paramètres Techniques
- **temperature**: Créativité (0-2)
- **max_tokens**: Longueur maximale
- **top_p**, **presence_penalty**, **frequency_penalty**

## 🔌 API Endpoints

### Agents
- `GET /agents` - Liste tous les agents
- `POST /agents` - Créer un agent
- `GET /agents/{id}` - Récupérer un agent
- `PUT /agents/{id}` - Mettre à jour un agent
- `DELETE /agents/{id}` - Supprimer un agent

### Débats
- `GET /debates` - Liste tous les débats
- `POST /debates` - Créer un débat
- `GET /debates/{id}` - Récupérer un débat

Documentation complète: http://localhost:8000/docs

## 🛠️ Technologies

- **Backend**: Python 3.10+, FastAPI, Pydantic
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **IA**: OpenAI GPT, Google Gemini, Anthropic Claude, Mistral

## 📝 Prochaines étapes

1. Implémenter l'intégration avec les API des fournisseurs d'IA
2. Créer le système de tours de parole
3. Ajouter la génération de prompts système personnalisés
4. Implémenter le système de modération
5. Ajouter l'analyse et notation des arguments
6. Créer un historique des débats
7. Ajouter l'export des débats (PDF, JSON)

## 📄 Licence

MIT
