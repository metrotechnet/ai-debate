# 🚀 Guide de Déploiement - Agora IA

Ce guide vous explique comment déployer Agora IA sur Google Cloud Platform (GCP).

## Prérequis

### 1. Outils nécessaires

```powershell
# Google Cloud SDK
# Télécharger: https://cloud.google.com/sdk/docs/install

# Firebase CLI
npm install -g firebase-tools

# Docker (optionnel, pour tester localement)
# Télécharger: https://www.docker.com/products/docker-desktop
```

### 2. Compte GCP et Firebase

- Créez un projet sur [Google Cloud Console](https://console.cloud.google.com)
- Notez votre **Project ID** (ex: `agora-ia-12345`)
- Activez la facturation sur le projet
- Créez un projet Firebase sur [Firebase Console](https://console.firebase.google.com)

### 3. Variables d'environnement

Assurez-vous que votre clé API OpenAI est définie :

```powershell
# Définir temporairement
$env:OPENAI_API_KEY = "sk-..."

# Ou de façon permanente (Windows)
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-...', 'User')
```

## Déploiement Automatique

### Option 1: Script PowerShell (Recommandé)

```powershell
# Authentification
gcloud auth login
firebase login

# Déploiement
.\deploy.ps1 -ProjectId votre-project-id
```

Le script effectue automatiquement :
- ✅ Configuration du projet GCP
- ✅ Activation des APIs nécessaires
- ✅ Déploiement du backend sur Cloud Run
- ✅ Mise à jour de l'URL de l'API dans le frontend
- ✅ Déploiement du frontend sur Firebase Hosting

## Déploiement Manuel

### Étape 1: Déployer le Backend sur Cloud Run

```powershell
# Configurer le projet
gcloud config set project votre-project-id

# Activer les APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Déployer
gcloud run deploy ai-debate-api `
  --source . `
  --region europe-west1 `
  --platform managed `
  --allow-unauthenticated `
  --set-env-vars "OPENAI_API_KEY=$env:OPENAI_API_KEY" `
  --min-instances 0 `
  --max-instances 10 `
  --memory 512Mi `
  --cpu 1 `
  --timeout 300
```

Récupérer l'URL du backend :
```powershell
$BackendUrl = gcloud run services describe ai-debate-api --region europe-west1 --format="value(status.url)"
echo $BackendUrl
```

### Étape 2: Mettre à jour le Frontend

Modifier `frontend/app.js` :
```javascript
// Remplacer
const API_BASE_URL = 'http://localhost:8001';

// Par
const API_BASE_URL = 'https://ai-debate-api-xxxxx-ew.a.run.app';
```

### Étape 3: Déployer le Frontend sur Firebase Hosting

```powershell
# Authentification Firebase
firebase login

# Initialiser le projet (première fois seulement)
firebase init hosting
# Choisir: Use an existing project
# Public directory: frontend
# Configure as single-page app: No
# Set up automatic builds: No

# Modifier .firebaserc avec votre Project ID
# {
#   "projects": {
#     "default": "votre-project-id"
#   }
# }

# Déployer
firebase deploy --only hosting
```

## Vérification du Déploiement

### Backend (Cloud Run)

```powershell
# Tester l'API
curl https://votre-backend-url.run.app/

# Vérifier la documentation
# Ouvrir dans le navigateur: https://votre-backend-url.run.app/docs
```

### Frontend (Firebase Hosting)

```powershell
# URL Firebase
# https://votre-project-id.web.app
# ou
# https://votre-project-id.firebaseapp.com
```

## Configuration Cloud Run

### Variables d'environnement

Pour modifier les variables d'environnement après déploiement :

```powershell
gcloud run services update ai-debate-api `
  --region europe-west1 `
  --set-env-vars "OPENAI_API_KEY=nouvelle-clé"
```

### Scaling

```powershell
gcloud run services update ai-debate-api `
  --region europe-west1 `
  --min-instances 0 `
  --max-instances 20 `
  --concurrency 80
```

### Logs

```powershell
# Voir les logs en temps réel
gcloud run services logs tail ai-debate-api --region europe-west1

# Ou dans Cloud Console
# https://console.cloud.google.com/run
```

## Configuration Firebase Hosting

### Domaine personnalisé

```powershell
# Ajouter un domaine
firebase hosting:channel:deploy production
```

Puis suivre les instructions dans [Firebase Console](https://console.firebase.google.com) > Hosting > Add custom domain

### Rollback

```powershell
# Liste des déploiements
firebase hosting:releases:list

# Rollback vers une version précédente
firebase hosting:rollback
```

## Tests Locaux avec Docker

```powershell
# Build de l'image
docker build -t ai-debate-backend .

# Exécution locale
docker run -p 8080:8080 `
  -e OPENAI_API_KEY=$env:OPENAI_API_KEY `
  ai-debate-backend

# Tester
curl http://localhost:8080/
```

## Estimation des Coûts

### Cloud Run (Backend)
- **Gratuit** : 2 millions de requêtes/mois
- **Au-delà** : ~0.40$ par million de requêtes
- **Mémoire** : ~0.0000025$ par GB-seconde
- **CPU** : ~0.00002400$ par vCPU-seconde

### Firebase Hosting (Frontend)
- **Gratuit** : 10 GB stockage + 360 MB/jour de transfert
- **Au-delà** : 0.026$/GB de transfert

**Coût mensuel estimé pour usage modéré** : 2-10€/mois

## Sécurité

### Backend
- Ne jamais commiter `.env` ou les clés API
- Utiliser Secret Manager pour les secrets sensibles :

```powershell
# Créer un secret
gcloud secrets create openai-api-key --data-file=-
# Entrer la clé et CTRL+Z

# Utiliser dans Cloud Run
gcloud run services update ai-debate-api `
  --region europe-west1 `
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```

### Frontend
- CORS configuré pour accepter uniquement l'origine Firebase
- Pas de clés API côté client

## Troubleshooting

### Erreur: Permission denied

```powershell
# Activer les APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Vérifier les permissions IAM
gcloud projects get-iam-policy votre-project-id
```

### Erreur: Container failed to start

```powershell
# Vérifier les logs
gcloud run services logs read ai-debate-api --region europe-west1 --limit 50

# Tester localement avec Docker
docker run -p 8080:8080 -e OPENAI_API_KEY=... ai-debate-backend
```

### Frontend ne se connecte pas au backend

- Vérifier que `API_BASE_URL` dans `frontend/app.js` pointe vers l'URL Cloud Run
- Vérifier les CORS dans `backend/main.py`
- Consulter la console du navigateur (F12)

## Mises à jour

### Backend

```powershell
# Redéployer après modifications
gcloud run deploy ai-debate-api --source . --region europe-west1
```

### Frontend

```powershell
firebase deploy --only hosting
```

## Monitoring

### Cloud Run

```powershell
# Dashboard
# https://console.cloud.google.com/run/detail/europe-west1/ai-debate-api/metrics

# Alertes
gcloud alpha monitoring policies create --notification-channels=...
```

### Firebase Hosting

- Analytics dans Firebase Console
- Performance Monitoring disponible

## Ressources

- [Documentation Cloud Run](https://cloud.google.com/run/docs)
- [Documentation Firebase Hosting](https://firebase.google.com/docs/hosting)
- [Guide des prix GCP](https://cloud.google.com/pricing)
- [Support GCP](https://cloud.google.com/support)
