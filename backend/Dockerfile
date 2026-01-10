FROM python:3.12-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application
COPY app.py .

# Créer le dossier pour les résumés
RUN mkdir -p /app/summaries

# Exposer le port
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]
