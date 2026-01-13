# Script de démarrage du serveur AI Debate
Write-Host "🚀 Démarrage du serveur AI Debate..." -ForegroundColor Green

# Activer l'environnement virtuel
& ".\.venv\Scripts\Activate.ps1"

# Aller dans le dossier backend
Set-Location backend

# Lancer le serveur
Write-Host "📡 Serveur disponible sur http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentation API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow

python main.py
