# Setup Gmail OAuth2 - Mac Mini

## Étape 1 : Google Cloud Console

1. Va sur [console.cloud.google.com](https://console.cloud.google.com)
2. Crée un nouveau projet (ou sélectionne un existant)
3. Active l'**API Gmail** :
   - Menu > APIs & Services > Library
   - Cherche "Gmail API" > Enable

## Étape 2 : Créer les identifiants OAuth 2.0

1. Va dans **APIs & Services > Credentials**
2. Clique **+ Create Credentials > OAuth client ID**
3. Si demandé, configure l'écran de consentement OAuth :
   - Type : External (ou Internal si Google Workspace)
   - Nom de l'app : ce que tu veux (ex: "Mac Mini Gmail")
   - Ajoute ton email comme utilisateur test
4. Type d'application : **Desktop app**
5. Télécharge le fichier JSON
6. Renomme-le **`credentials.json`** et place-le dans ce répertoire

## Étape 3 : Installer les dépendances

```bash
pip3 install -r requirements.txt
```

## Étape 4 : Lancer l'authentification

```bash
# Première connexion (ouvre le navigateur)
python3 gmail_auth.py

# Lister les derniers emails
python3 gmail_auth.py --list

# Envoyer un email de test (à soi-même)
python3 gmail_auth.py --send

# Envoyer un email à quelqu'un
python3 gmail_auth.py --send --to destinataire@gmail.com
```

Au premier lancement, un navigateur s'ouvre pour l'authentification Google.
Un fichier `token.json` est créé localement pour les connexions suivantes.

## Fichiers

| Fichier | Description |
|---------|-------------|
| `gmail_auth.py` | Script principal d'authentification et d'utilisation |
| `credentials.json` | Identifiants OAuth (à télécharger depuis Google Cloud) |
| `token.json` | Token d'accès généré automatiquement (ne pas committer) |
| `requirements.txt` | Dépendances Python |

## Sécurité

- **Ne jamais committer** `credentials.json` ni `token.json`
- Ces fichiers sont dans le `.gitignore`
- En cas de compromission, révoquer les tokens dans Google Cloud Console
