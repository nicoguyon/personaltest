"""
Pydantic models for Nano Banana Pro (Google Gemini) image generation.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ImageSize(str, Enum):
    """Available image sizes for generation."""
    SIZE_1K = "1024x1024"
    SIZE_2K = "2048x2048"
    LANDSCAPE_16_9 = "1920x1080"
    PORTRAIT_9_16 = "1080x1920"
    LANDSCAPE_4_3 = "1440x1080"
    PORTRAIT_3_4 = "1080x1440"


class AspectRatio(str, Enum):
    """Aspect ratios for image generation."""
    SQUARE = "1:1"
    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    LANDSCAPE_4_3 = "4:3"
    PORTRAIT_3_4 = "3:4"
    LANDSCAPE_3_2 = "3:2"
    PORTRAIT_2_3 = "2:3"


class ImageGenerationRequest(BaseModel):
    """Request model for Nano Banana Pro image generation."""

    prompt: str = Field(..., description="Text description of the image to generate")
    negative_prompt: Optional[str] = Field(None, description="Elements to avoid in the image")
    aspect_ratio: AspectRatio = Field(default=AspectRatio.SQUARE, description="Aspect ratio")
    num_images: int = Field(default=1, ge=1, le=4, description="Number of images to generate")

    # Optional: reference image for editing
    reference_image_base64: Optional[str] = Field(None, description="Base64 encoded reference image")
    reference_image_mime: Optional[str] = Field(default="image/png", description="MIME type of reference image")


class GeneratedImage(BaseModel):
    """A single generated image."""

    base64_data: str = Field(..., description="Base64 encoded image data")
    mime_type: str = Field(default="image/png", description="MIME type of the image")

    def save(self, path: str) -> None:
        """Save the image to a file."""
        import base64
        with open(path, "wb") as f:
            f.write(base64.b64decode(self.base64_data))


class ImageGenerationResponse(BaseModel):
    """Response from Nano Banana Pro image generation."""

    images: list[GeneratedImage] = Field(default_factory=list, description="Generated images")
    text_response: Optional[str] = Field(None, description="Optional text response from the model")
    prompt_used: str = Field(..., description="The prompt that was used")

    @property
    def success(self) -> bool:
        """Check if generation was successful."""
        return len(self.images) > 0
