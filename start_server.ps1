# Script de démarrage du serveur Agora IA
Write-Host "🚀 Démarrage du serveur Agora IA..." -ForegroundColor Green

# Activer l'environnement virtuel
& ".\.venv\Scripts\Activate.ps1"

# Lancer le serveur avec uvicorn depuis la racine du projet
Write-Host "📡 Serveur disponible sur http://localhost:8001" -ForegroundColor Cyan
Write-Host "📚 Documentation API: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow

uvicorn backend.main:app --host 0.0.0.0 --port 8001
