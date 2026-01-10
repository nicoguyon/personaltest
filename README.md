# YouTube Video Summarizer

Génère automatiquement des résumés de vos vidéos YouTube, peu importe l'appareil utilisé (téléphone, télé, ordinateur).

## Comment ça marche ?

1. Vous créez une playlist YouTube dédiée (ex: "À résumer")
2. Quand vous regardez une vidéo intéressante, vous l'ajoutez à cette playlist
3. Le script surveille la playlist et génère automatiquement un résumé avec Claude

**Avantage** : Fonctionne sur tous vos appareils ! Ajouter une vidéo à une playlist est facile depuis YouTube sur téléphone, télé ou ordinateur.

## Installation rapide

### Prérequis

- Python 3.10+ ou Docker
- Une clé API Anthropic (Claude)
- Une clé API YouTube

### 1. Obtenir les clés API

#### Clé Anthropic (Claude)
1. Allez sur https://console.anthropic.com/
2. Créez un compte ou connectez-vous
3. Allez dans "API Keys" et créez une nouvelle clé

#### Clé YouTube
1. Allez sur https://console.cloud.google.com/
2. Créez un nouveau projet
3. Activez "YouTube Data API v3"
4. Créez une clé API dans "Identifiants"

### 2. Créer votre playlist YouTube

1. Sur YouTube, créez une nouvelle playlist (ex: "À résumer")
2. Configurez-la en "Non répertoriée" ou "Publique"
3. Copiez l'ID de la playlist depuis l'URL :
   - URL : `https://www.youtube.com/playlist?list=PLxxxxxxxxxxxx`
   - ID : `PLxxxxxxxxxxxx`

### 3. Configurer l'application

```bash
cd backend
cp .env.example .env
```

Éditez le fichier `.env` :
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
YOUTUBE_API_KEY=AIzaxxxxx
YOUTUBE_PLAYLIST_ID=PLxxxxx
CHECK_INTERVAL_MINUTES=5
```

### 4. Lancer l'application

#### Option A : Avec Python

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### Option B : Avec Docker

```bash
docker-compose up -d
```

### 5. Accéder à l'interface

Ouvrez http://localhost:5000 dans votre navigateur.

## Utilisation

### Workflow quotidien

1. Regardez une vidéo YouTube (sur n'importe quel appareil)
2. Si elle est intéressante, cliquez sur "Enregistrer" → votre playlist
3. Le résumé sera généré automatiquement dans les 5 minutes !

### Interface web

- **Page d'accueil** : Voir tous vos résumés
- **Bouton "Vérifier maintenant"** : Force une vérification immédiate
- **API JSON** : Accès programmatique aux résumés

### API

```bash
# Vérifier le statut
curl http://localhost:5000/health

# Lister tous les résumés
curl http://localhost:5000/summaries

# Résumer une vidéo manuellement
curl -X POST http://localhost:5000/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=xxxxx"}'
```

## Structure des résumés

Chaque résumé contient :
- **Points clés** : 3-5 idées principales
- **Résumé** : Synthèse de 100-150 mots
- **À retenir** : Actions concrètes
- **Mots-clés** : Pour retrouver facilement

Les résumés sont sauvegardés en :
- JSON (pour l'API)
- Markdown (pour une lecture facile)

## Configuration avancée

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ANTHROPIC_API_KEY` | Clé API Claude | Requis |
| `YOUTUBE_API_KEY` | Clé API YouTube | Requis |
| `YOUTUBE_PLAYLIST_ID` | ID de la playlist | Requis |
| `CHECK_INTERVAL_MINUTES` | Intervalle de vérification | 5 |
| `PORT` | Port du serveur | 5000 |
| `SUMMARIES_DIR` | Dossier des résumés | ./summaries |

### Notifications (optionnel)

Pour recevoir les résumés par email, configurez :
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre_email@gmail.com
SMTP_PASSWORD=mot_de_passe_application
NOTIFICATION_EMAIL=votre_email@gmail.com
```

## Dépannage

### "Aucun transcript disponible"
Certaines vidéos n'ont pas de sous-titres. Le résumé ne peut être généré que pour les vidéos avec sous-titres (automatiques ou manuels).

### "Clé API invalide"
Vérifiez que vos clés API sont correctement configurées dans le fichier `.env`.

### La playlist n'est pas détectée
- Assurez-vous que la playlist est "Non répertoriée" ou "Publique"
- Vérifiez l'ID de la playlist dans l'URL

## Licence

MIT
