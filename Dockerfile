# Utiliser une image Python légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier requirements.txt
COPY backend/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code backend
COPY backend/ ./backend/

# Exposer le port 8080 (requis par Cloud Run)
EXPOSE 8080

# Variable d'environnement pour le port
ENV PORT=8080

# Commande pour démarrer l'application
CMD uvicorn backend.main:app --host 0.0.0.0 --port $PORT
