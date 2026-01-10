#!/usr/bin/env python3
"""
YouTube Video Summarizer - Backend
Surveille une playlist YouTube et génère des résumés automatiques.
Fonctionne peu importe l'appareil utilisé (téléphone, télé, ordinateur).
"""

import os
import json
import re
import time
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import anthropic
from dotenv import load_dotenv
import schedule
from googleapiclient.discovery import build

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_MINUTES", 5))
SUMMARIES_DIR = Path(os.getenv("SUMMARIES_DIR", "./summaries"))
PROCESSED_FILE = Path(os.getenv("PROCESSED_FILE", "./processed_videos.json"))

SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)


def load_processed_videos() -> set:
    """Charge la liste des vidéos déjà traitées."""
    if PROCESSED_FILE.exists():
        with open(PROCESSED_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("processed", []))
    return set()


def save_processed_video(video_id: str):
    """Ajoute une vidéo à la liste des vidéos traitées."""
    processed = load_processed_videos()
    processed.add(video_id)
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump({"processed": list(processed), "updated_at": datetime.now().isoformat()}, f)


def get_playlist_videos() -> list[dict]:
    """Récupère les vidéos d'une playlist YouTube."""
    if not YOUTUBE_API_KEY or not YOUTUBE_PLAYLIST_ID:
        raise Exception("Configuration YouTube manquante (API_KEY ou PLAYLIST_ID)")

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    videos = []
    next_page_token = None

    while True:
        request_yt = youtube.playlistItems().list(
            part="snippet,contentDetails",
            playlistId=YOUTUBE_PLAYLIST_ID,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request_yt.execute()

        for item in response.get("items", []):
            video_id = item["contentDetails"]["videoId"]
            snippet = item["snippet"]
            videos.append({
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:200],
                "channel": snippet.get("videoOwnerChannelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


def extract_video_id(url: str) -> str | None:
    """Extrait l'ID de la vidéo depuis une URL YouTube."""
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript(video_id: str) -> tuple[str, str]:
    """Récupère le transcript d'une vidéo YouTube."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        lang = "unknown"

        # Priorité: français > anglais > auto-généré > première langue disponible
        for lang_code in ["fr", "en"]:
            try:
                transcript = transcript_list.find_transcript([lang_code])
                lang = lang_code
                break
            except NoTranscriptFound:
                continue

        if transcript is None:
            # Essayer les transcripts auto-générés
            try:
                transcript = transcript_list.find_generated_transcript(["fr", "en"])
                lang = transcript.language_code
            except NoTranscriptFound:
                # Prendre n'importe quel transcript disponible
                for t in transcript_list:
                    transcript = t
                    lang = t.language_code
                    break

        if transcript is None:
            raise NoTranscriptFound(video_id, ["fr", "en"], None)

        transcript_data = transcript.fetch()
        full_text = " ".join([entry["text"] for entry in transcript_data])
        return full_text, lang

    except TranscriptsDisabled:
        raise Exception("Les sous-titres sont désactivés pour cette vidéo")
    except VideoUnavailable:
        raise Exception("Cette vidéo n'est pas disponible")
    except NoTranscriptFound:
        raise Exception("Aucun transcript disponible pour cette vidéo")


def generate_summary(transcript: str, video_title: str = "", language: str = "fr") -> str:
    """Génère un résumé du transcript avec Claude."""
    if not ANTHROPIC_API_KEY:
        raise Exception("Clé API Anthropic non configurée")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Tu es un assistant spécialisé dans la création de résumés de vidéos YouTube.

Voici le transcript d'une vidéo YouTube{f' intitulée "{video_title}"' if video_title else ''}.

Génère un résumé structuré et utile de cette vidéo. Le résumé doit être en français et inclure:

## Points clés
- Liste les 3 à 5 idées principales de la vidéo

## Résumé
Un paragraphe de synthèse de 100-150 mots qui capture l'essence de la vidéo.

## À retenir
- 2-3 points essentiels ou actions concrètes à retenir

## Mots-clés
Liste de 5-7 mots-clés pertinents pour retrouver ce résumé facilement.

---

Transcript:
{transcript[:15000]}"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


def save_summary(video_id: str, video_info: dict, summary: str) -> dict:
    """Sauvegarde le résumé dans un fichier JSON et Markdown."""
    timestamp = datetime.now()
    base_filename = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{video_id}"

    # Sauvegarder en JSON
    json_filepath = SUMMARIES_DIR / f"{base_filename}.json"
    data = {
        "video_id": video_id,
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "title": video_info.get("title", ""),
        "channel": video_info.get("channel", ""),
        "thumbnail": video_info.get("thumbnail", ""),
        "summary": summary,
        "created_at": timestamp.isoformat(),
    }
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Sauvegarder en Markdown pour une lecture facile
    md_filepath = SUMMARIES_DIR / f"{base_filename}.md"
    md_content = f"""# {video_info.get('title', 'Sans titre')}

**Chaîne:** {video_info.get('channel', 'Inconnue')}
**Lien:** https://www.youtube.com/watch?v={video_id}
**Résumé généré le:** {timestamp.strftime('%d/%m/%Y à %H:%M')}

---

{summary}
"""
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    return data


def process_video(video_info: dict) -> dict | None:
    """Traite une vidéo: récupère le transcript et génère un résumé."""
    video_id = video_info["video_id"]
    title = video_info.get("title", "")

    print(f"📹 Traitement de: {title}")

    try:
        # Récupérer le transcript
        transcript, lang = get_transcript(video_id)
        print(f"  ✓ Transcript récupéré ({lang})")

        # Générer le résumé
        summary = generate_summary(transcript, title, lang)
        print(f"  ✓ Résumé généré")

        # Sauvegarder
        data = save_summary(video_id, video_info, summary)
        print(f"  ✓ Sauvegardé")

        # Marquer comme traité
        save_processed_video(video_id)

        return data

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        return None


def check_new_videos():
    """Vérifie s'il y a de nouvelles vidéos dans la playlist."""
    print(f"\n🔍 Vérification de la playlist... ({datetime.now().strftime('%H:%M:%S')})")

    try:
        videos = get_playlist_videos()
        processed = load_processed_videos()

        new_videos = [v for v in videos if v["video_id"] not in processed]

        if new_videos:
            print(f"📌 {len(new_videos)} nouvelle(s) vidéo(s) trouvée(s)")
            for video in new_videos:
                process_video(video)
        else:
            print("  Aucune nouvelle vidéo")

    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")


def run_scheduler():
    """Lance le scheduler en arrière-plan."""
    schedule.every(CHECK_INTERVAL).minutes.do(check_new_videos)

    while True:
        schedule.run_pending()
        time.sleep(1)


# ============================================
# Routes API
# ============================================

@app.route("/")
def home():
    """Page d'accueil avec les résumés."""
    summaries = []
    for filepath in sorted(SUMMARIES_DIR.glob("*.json"), reverse=True)[:20]:
        with open(filepath, encoding="utf-8") as f:
            summaries.append(json.load(f))

    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Video Summarizer</title>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 900px; margin: 0 auto; padding: 20px;
                background: #f5f5f5; color: #333;
            }
            h1 { color: #c00; }
            .status {
                background: #e8f5e9; padding: 15px; border-radius: 8px;
                margin-bottom: 20px; border-left: 4px solid #4caf50;
            }
            .video-card {
                background: white; padding: 20px; border-radius: 8px;
                margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .video-card h3 { margin-top: 0; }
            .video-card .meta { color: #666; font-size: 0.9em; margin-bottom: 10px; }
            .video-card .summary {
                background: #fafafa; padding: 15px; border-radius: 4px;
                white-space: pre-wrap; font-size: 0.95em;
            }
            .video-card a { color: #c00; }
            .thumbnail { max-width: 200px; border-radius: 4px; }
            .actions { margin-top: 20px; }
            .btn {
                background: #c00; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; cursor: pointer;
                text-decoration: none; display: inline-block;
            }
            .btn:hover { background: #a00; }
            .btn-secondary { background: #666; }
            .btn-secondary:hover { background: #444; }
        </style>
    </head>
    <body>
        <h1>🎬 YouTube Video Summarizer</h1>

        <div class="status">
            <strong>Status:</strong> Surveillance active<br>
            <strong>Playlist:</strong> {{ playlist_id }}<br>
            <strong>Intervalle:</strong> Toutes les {{ interval }} minutes<br>
            <strong>Résumés générés:</strong> {{ count }}
        </div>

        <div class="actions">
            <a href="/check" class="btn">🔄 Vérifier maintenant</a>
            <a href="/summaries" class="btn btn-secondary">📋 API JSON</a>
        </div>

        <h2>Derniers résumés</h2>

        {% for s in summaries %}
        <div class="video-card">
            <h3>{{ s.title }}</h3>
            <div class="meta">
                <strong>{{ s.channel }}</strong> •
                <a href="{{ s.video_url }}" target="_blank">Voir la vidéo</a> •
                {{ s.created_at[:10] }}
            </div>
            {% if s.thumbnail %}
            <img src="{{ s.thumbnail }}" alt="Thumbnail" class="thumbnail">
            {% endif %}
            <div class="summary">{{ s.summary }}</div>
        </div>
        {% endfor %}

        {% if not summaries %}
        <p>Aucun résumé pour le moment. Ajoutez des vidéos à votre playlist!</p>
        {% endif %}
    </body>
    </html>
    """
    from jinja2 import Template
    template = Template(html)
    return template.render(
        summaries=summaries,
        playlist_id=YOUTUBE_PLAYLIST_ID or "Non configuré",
        interval=CHECK_INTERVAL,
        count=len(list(SUMMARIES_DIR.glob("*.json"))),
    )


@app.route("/health")
def health():
    """Endpoint de santé."""
    return jsonify({
        "status": "ok",
        "playlist_configured": bool(YOUTUBE_PLAYLIST_ID),
        "anthropic_configured": bool(ANTHROPIC_API_KEY),
        "youtube_configured": bool(YOUTUBE_API_KEY),
    })


@app.route("/check")
def check():
    """Force une vérification de la playlist."""
    check_new_videos()
    return jsonify({"status": "ok", "message": "Vérification effectuée"})


@app.route("/summarize", methods=["POST"])
def summarize():
    """Endpoint pour résumer une vidéo spécifique (par URL)."""
    try:
        data = request.get_json()
        if not data or "url" not in data:
            return jsonify({"error": "URL de vidéo manquante"}), 400

        video_url = data["url"]
        video_id = extract_video_id(video_url)
        if not video_id:
            return jsonify({"error": "URL YouTube invalide"}), 400

        video_info = {
            "video_id": video_id,
            "title": data.get("title", ""),
            "channel": "",
        }

        result = process_video(video_info)
        if result:
            return jsonify({"success": True, **result})
        else:
            return jsonify({"error": "Impossible de traiter cette vidéo"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/summaries")
def list_summaries():
    """Liste tous les résumés."""
    summaries = []
    for filepath in sorted(SUMMARIES_DIR.glob("*.json"), reverse=True):
        with open(filepath, encoding="utf-8") as f:
            summaries.append(json.load(f))
    return jsonify(summaries)


@app.route("/summaries/<video_id>")
def get_summary(video_id: str):
    """Récupère le résumé d'une vidéo."""
    for filepath in SUMMARIES_DIR.glob(f"*_{video_id}.json"):
        with open(filepath, encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Résumé non trouvé"}), 404


# ============================================
# Point d'entrée
# ============================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))

    print("=" * 50)
    print("🎬 YouTube Video Summarizer")
    print("=" * 50)
    print(f"📺 Playlist: {YOUTUBE_PLAYLIST_ID or 'Non configurée!'}")
    print(f"⏱️  Intervalle: {CHECK_INTERVAL} minutes")
    print(f"📁 Résumés: {SUMMARIES_DIR.absolute()}")
    print(f"🌐 Interface: http://localhost:{port}")
    print("=" * 50)

    # Vérification initiale
    if YOUTUBE_PLAYLIST_ID and YOUTUBE_API_KEY:
        check_new_videos()

        # Lancer le scheduler en arrière-plan
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    else:
        print("⚠️  Configuration incomplète - Mode API uniquement")

    app.run(host="0.0.0.0", port=port, debug=False)
