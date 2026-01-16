# Script de déploiement pour Agora IA
# Assurez-vous d'avoir configuré gcloud et firebase CLI

param(
    [string]$ProjectId = "",
    [string]$Region = "us-east4",
    [string]$ServiceName = "ai-debate-api"
)

Write-Host "Déploiement d'Agora IA sur GCP" -ForegroundColor Cyan
Write-Host ""

# Vérifier si ProjectId est fourni
if ([string]::IsNullOrEmpty($ProjectId)) {
    Write-Host "Erreur: ProjectId requis" -ForegroundColor Red
    Write-Host "Usage: .\deploy.ps1 -ProjectId votre-project-id" -ForegroundColor Yellow
    exit 1
}

# Configurer le projet GCP
Write-Host "Configuration du projet GCP: $ProjectId" -ForegroundColor Green
gcloud config set project $ProjectId

# Activer les APIs nécessaires
Write-Host "Activation des APIs GCP..." -ForegroundColor Green
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Déployer le backend sur Cloud Run
Write-Host ""
Write-Host "Déploiement du backend sur Cloud Run..." -ForegroundColor Green
Write-Host "   Service: $ServiceName" -ForegroundColor Yellow
Write-Host "   Region: $Region" -ForegroundColor Yellow
Write-Host ""

gcloud run deploy $ServiceName `
    --source . `
    --region $Region `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "OPENAI_API_KEY=$env:OPENAI_API_KEY" `
    --min-instances 0 `
    --max-instances 10 `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors du déploiement du backend" -ForegroundColor Red
    exit 1
}

# Récupérer l'URL du service déployé
Write-Host ""
Write-Host "Récupération de l'URL du backend..." -ForegroundColor Green
$BackendUrl = gcloud run services describe $ServiceName --region $Region --format="value(status.url)"

if ([string]::IsNullOrEmpty($BackendUrl)) {
    Write-Host "Impossible de récupérer l'URL du backend" -ForegroundColor Red
    exit 1
}

Write-Host "Backend déployé: $BackendUrl" -ForegroundColor Green

# Mettre à jour l'URL de l'API dans le frontend
Write-Host ""
Write-Host "Mise à jour de l'URL de l'API dans le frontend..." -ForegroundColor Green

$AppJsPath = "frontend\app.js"
$AppJsContent = Get-Content $AppJsPath -Raw
$AppJsContent = $AppJsContent -replace "const API_BASE_URL = 'http://localhost:8001';", "const API_BASE_URL = '$BackendUrl';"
$AppJsContent | Set-Content $AppJsPath -NoNewline

Write-Host "URL de l'API mise à jour dans app.js" -ForegroundColor Green

# Déployer le frontend sur Firebase Hosting
Write-Host ""
Write-Host "Déploiement du frontend sur Firebase Hosting..." -ForegroundColor Green

# Vérifier si Firebase CLI est installé
$FirebaseInstalled = Get-Command firebase -ErrorAction SilentlyContinue
if (-not $FirebaseInstalled) {
    Write-Host "Firebase CLI non installé" -ForegroundColor Red
    Write-Host "Installez-le avec: npm install -g firebase-tools" -ForegroundColor Yellow
    exit 1
}

# Configurer le projet Firebase
$FirebaseRcPath = ".firebaserc"
$FirebaseRcContent = Get-Content $FirebaseRcPath -Raw | ConvertFrom-Json
$FirebaseRcContent.projects.default = $ProjectId
$FirebaseRcContent | ConvertTo-Json | Set-Content $FirebaseRcPath

# Déployer sur Firebase Hosting
firebase deploy --only hosting

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors du déploiement du frontend" -ForegroundColor Red
    exit 1
}

# Récupérer l'URL Firebase
$FirebaseUrl = "https://$ProjectId.web.app"

# Afficher le résumé
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Déploiement terminé avec succès!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "URLs de votre application:" -ForegroundColor Cyan
Write-Host "   Frontend: $FirebaseUrl" -ForegroundColor Yellow
Write-Host "   Backend:  $BackendUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "Documentation API: $BackendUrl/docs" -ForegroundColor Cyan
Write-Host ""
