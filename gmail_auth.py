#!/usr/bin/env python3
"""
Gmail OAuth2 Authentication - Mac Mini Setup

Ce script gère l'authentification OAuth2 avec l'API Gmail de Google.
Il permet de lire et envoyer des emails programmatiquement.

Prérequis :
1. Créer un projet sur Google Cloud Console (console.cloud.google.com)
2. Activer l'API Gmail
3. Créer des identifiants OAuth 2.0 (type "Application de bureau")
4. Télécharger le fichier credentials.json dans ce répertoire

Usage :
    python3 gmail_auth.py          # Authentification + test de connexion
    python3 gmail_auth.py --send   # Envoyer un email de test
"""

import os
import sys
import base64
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes Gmail - modifier selon les besoins
# https://developers.google.com/gmail/api/auth/scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.labels",
]

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")


def authenticate():
    """
    Lance le flow OAuth2 et retourne les credentials.
    - Si un token.json existe et est valide, il est réutilisé.
    - Sinon, ouvre un navigateur pour l'authentification Google.
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Token expiré, rafraîchissement en cours...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(
                    "ERREUR : fichier credentials.json introuvable.\n"
                    "\n"
                    "Pour l'obtenir :\n"
                    "1. Va sur https://console.cloud.google.com\n"
                    "2. Crée un projet (ou sélectionne un existant)\n"
                    "3. Active l'API Gmail (APIs & Services > Enable APIs)\n"
                    "4. Va dans APIs & Services > Credentials\n"
                    "5. Crée un OAuth 2.0 Client ID (type: Desktop app)\n"
                    "6. Télécharge le JSON et renomme-le credentials.json\n"
                    "7. Place-le dans ce répertoire\n"
                )
                sys.exit(1)

            print("Ouverture du navigateur pour l'authentification Google...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Sauvegarde du token pour les prochaines utilisations
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print(f"Token sauvegardé dans {TOKEN_FILE}")

    return creds


def get_gmail_service(creds):
    """Construit et retourne le service Gmail API."""
    return build("gmail", "v1", credentials=creds)


def get_profile(service):
    """Récupère le profil de l'utilisateur connecté."""
    profile = service.users().getProfile(userId="me").execute()
    return profile


def list_labels(service):
    """Liste tous les labels du compte Gmail."""
    results = service.users().labels().list(userId="me").execute()
    return results.get("labels", [])


def list_recent_messages(service, max_results=5):
    """Liste les messages récents de la boîte de réception."""
    results = (
        service.users()
        .messages()
        .list(userId="me", maxResults=max_results, labelIds=["INBOX"])
        .execute()
    )
    messages = results.get("messages", [])

    detailed = []
    for msg in messages:
        msg_data = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="metadata")
            .execute()
        )
        headers = {
            h["name"]: h["value"]
            for h in msg_data.get("payload", {}).get("headers", [])
        }
        detailed.append(
            {
                "id": msg["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", "(sans objet)"),
                "date": headers.get("Date", ""),
            }
        )
    return detailed


def send_email(service, to, subject, body):
    """Envoie un email via l'API Gmail."""
    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(MIMEText(body, "plain"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = (
        service.users()
        .messages()
        .send(userId="me", body={"raw": raw})
        .execute()
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="Gmail OAuth2 Auth - Mac Mini")
    parser.add_argument(
        "--send", action="store_true", help="Envoyer un email de test"
    )
    parser.add_argument("--to", type=str, help="Destinataire de l'email de test")
    parser.add_argument(
        "--list", action="store_true", help="Lister les 5 derniers emails"
    )
    args = parser.parse_args()

    # Authentification
    print("=== Gmail OAuth2 Authentication ===\n")
    creds = authenticate()

    # Connexion au service Gmail
    service = get_gmail_service(creds)

    # Afficher le profil
    profile = get_profile(service)
    print(f"\nConnecté en tant que : {profile['emailAddress']}")
    print(f"Messages totaux : {profile.get('messagesTotal', 'N/A')}")
    print(f"Threads totaux : {profile.get('threadsTotal', 'N/A')}")

    # Labels
    labels = list_labels(service)
    print(f"\nLabels ({len(labels)}) :")
    for label in labels[:10]:
        print(f"  - {label['name']}")
    if len(labels) > 10:
        print(f"  ... et {len(labels) - 10} autres")

    # Lister les emails récents
    if args.list:
        print("\n--- 5 derniers emails ---")
        messages = list_recent_messages(service)
        for msg in messages:
            print(f"  De: {msg['from']}")
            print(f"  Objet: {msg['subject']}")
            print(f"  Date: {msg['date']}")
            print()

    # Envoyer un email de test
    if args.send:
        if not args.to:
            # Envoie à soi-même par défaut
            to = profile["emailAddress"]
            print(f"\nPas de destinataire spécifié, envoi à soi-même ({to})")
        else:
            to = args.to

        result = send_email(
            service,
            to=to,
            subject="Test Gmail OAuth2 - Mac Mini",
            body=(
                "Cet email a été envoyé via l'API Gmail OAuth2 "
                "depuis le Mac Mini.\n\n"
                "L'authentification fonctionne correctement !"
            ),
        )
        print(f"\nEmail envoyé ! Message ID: {result['id']}")

    print("\nAuthentification OK !")


if __name__ == "__main__":
    main()
