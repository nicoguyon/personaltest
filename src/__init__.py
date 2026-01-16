"""
AI Media Generation SDK
Supports Nano Banana Pro (images) and Kling 2.6 (videos)
"""

from .clients.nano_banana import NanoBananaClient
from .clients.kling import KlingClient

__all__ = ["NanoBananaClient", "KlingClient"]
__version__ = "1.0.0"
