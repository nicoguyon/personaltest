# AI Media Generation SDK

SDK Python pour la génération d'images et de vidéos avec **Nano Banana Pro** (Google Gemini) et **Kling 2.6**.

## Fonctionnalités

### Nano Banana Pro (Images)
- Génération text-to-image
- Édition d'images avec prompts
- Multiples formats et ratios d'aspect
- Support async/sync

### Kling 2.6 (Vidéos)
- Génération text-to-video
- Génération image-to-video
- Contrôles de caméra (zoom, pan, tilt)
- Génération audio intégrée
- Durées 5s et 10s
- Modes Standard et Pro

## Installation

```bash
# Cloner le repo
git clone <repo-url>
cd personaltest

# Installer les dépendances
pip install -r requirements.txt

# Configurer les clés API
cp .env.example .env
# Éditer .env avec vos clés
```

## Configuration

Créer un fichier `.env` avec vos clés API :

```env
# Google Gemini / Nano Banana Pro
GEMINI_API_KEY=your_key_here

# Kling via PiAPI
PIAPI_API_KEY=your_key_here
```

**Obtenir les clés :**
- Gemini : https://aistudio.google.com/apikey
- PiAPI (Kling) : https://piapi.ai

## Usage Rapide

### Génération d'image

```python
from src.clients.nano_banana import NanoBananaClient

client = NanoBananaClient()

# Async
response = await client.generate("A sunset over mountains")
response.images[0].save("sunset.png")

# Sync
response = client.generate_sync("A sunset over mountains")
response.images[0].save("sunset.png")
```

### Génération de vidéo

```python
from src.clients.kling import KlingClient

client = KlingClient()

# Méthode simple (attend automatiquement)
result = await client.generate_and_wait(
    "A cat playing piano",
    output_path="cat_piano.mp4"
)

# Contrôle fin
response = await client.generate("A cat playing piano", duration=5)
result = await client.wait_for_completion(response.task.task_id)
await client.download_video(result.task.video_url, "video.mp4")
```

### Mode interactif

```bash
python examples/quick_start.py
```

## Exemples

```bash
# Génération d'images
python examples/generate_image.py

# Génération de vidéos
python examples/generate_video.py

# Mode interactif
python examples/quick_start.py
```

## Structure du Projet

```
.
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration et env vars
│   ├── clients/
│   │   ├── nano_banana.py     # Client Nano Banana Pro
│   │   └── kling.py           # Client Kling 2.6
│   └── models/
│       ├── nano_banana_models.py  # Modèles Pydantic (images)
│       └── kling_models.py        # Modèles Pydantic (vidéos)
├── examples/
│   ├── generate_image.py      # Exemples images
│   ├── generate_video.py      # Exemples vidéos
│   └── quick_start.py         # Guide rapide
├── output/                    # Fichiers générés
├── requirements.txt
├── .env.example
└── README.md
```

## API Reference

### NanoBananaClient

| Méthode | Description |
|---------|-------------|
| `generate(prompt, ...)` | Génère une image (async) |
| `generate_sync(prompt, ...)` | Génère une image (sync) |
| `edit(prompt, image_path, ...)` | Édite une image (async) |
| `edit_sync(prompt, image_path, ...)` | Édite une image (sync) |

**Paramètres de génération :**
- `prompt` : Description de l'image
- `negative_prompt` : Éléments à éviter
- `aspect_ratio` : Ratio (1:1, 16:9, 9:16, etc.)

### KlingClient

| Méthode | Description |
|---------|-------------|
| `generate(prompt, ...)` | Démarre une génération |
| `get_task_status(task_id)` | Vérifie le statut |
| `wait_for_completion(task_id)` | Attend la fin |
| `download_video(url, path)` | Télécharge la vidéo |
| `generate_and_wait(prompt, ...)` | Tout-en-un |

**Paramètres de génération :**
- `prompt` : Description de la vidéo
- `duration` : 5 ou 10 secondes
- `mode` : `std` ou `pro`
- `aspect_ratio` : 16:9, 9:16, 1:1
- `enable_audio` : Générer l'audio
- `camera_control` : Mouvements de caméra
- `image_url` : Image source (image-to-video)

## Tarification

### Nano Banana Pro
- Gratuit avec compte Google AI Studio (quotas)

### Kling 2.6 (via PiAPI)
| Mode | 5 secondes | 10 secondes |
|------|------------|-------------|
| Standard | ~$0.20 | ~$0.40 |
| Pro | ~$0.33 | ~$0.66 |

## Licence

MIT
