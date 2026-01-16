"""Data models for API requests and responses."""

from .nano_banana_models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    GeneratedImage,
    ImageSize,
    AspectRatio,
)
from .kling_models import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoTask,
    TaskStatus,
    VideoMode,
    KlingVersion,
    CameraControl,
)

__all__ = [
    # Nano Banana
    "ImageGenerationRequest",
    "ImageGenerationResponse",
    "GeneratedImage",
    "ImageSize",
    "AspectRatio",
    # Kling
    "VideoGenerationRequest",
    "VideoGenerationResponse",
    "VideoTask",
    "TaskStatus",
    "VideoMode",
    "KlingVersion",
    "CameraControl",
]
