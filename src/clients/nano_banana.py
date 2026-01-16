"""
Nano Banana Pro Client - Google Gemini Image Generation

Supports:
- Text-to-image generation
- Image editing with reference images
- Multiple aspect ratios and sizes
"""

import base64
import httpx
from pathlib import Path
from typing import Optional, Union

from ..config import Config
from ..models.nano_banana_models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    GeneratedImage,
    AspectRatio,
)


class NanoBananaClient:
    """
    Client for Nano Banana Pro (Google Gemini) image generation.

    Usage:
        client = NanoBananaClient()
        response = await client.generate("A sunset over mountains")
        response.images[0].save("sunset.png")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        Initialize the Nano Banana Pro client.

        Args:
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var)
            model: Model to use (defaults to gemini-2.0-flash-exp)
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model or Config.NANO_BANANA_PRO_MODEL
        self.base_url = Config.GEMINI_BASE_URL

        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

    def _build_request_body(
        self,
        request: ImageGenerationRequest,
    ) -> dict:
        """Build the API request body."""
        parts = []

        # Add reference image if provided (for editing)
        if request.reference_image_base64:
            parts.append({
                "inline_data": {
                    "mime_type": request.reference_image_mime or "image/png",
                    "data": request.reference_image_base64,
                }
            })

        # Add text prompt
        parts.append({"text": request.prompt})

        body = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
            },
        }

        return body

    def _parse_response(
        self,
        response_data: dict,
        prompt: str,
    ) -> ImageGenerationResponse:
        """Parse the API response into our model."""
        images = []
        text_response = None

        candidates = response_data.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            for part in parts:
                # Check for inline image data
                if "inlineData" in part:
                    inline_data = part["inlineData"]
                    images.append(
                        GeneratedImage(
                            base64_data=inline_data.get("data", ""),
                            mime_type=inline_data.get("mimeType", "image/png"),
                        )
                    )
                # Check for text response
                elif "text" in part:
                    text_response = part["text"]

        return ImageGenerationResponse(
            images=images,
            text_response=text_response,
            prompt_used=prompt,
        )

    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
        num_images: int = 1,
    ) -> ImageGenerationResponse:
        """
        Generate images from a text prompt.

        Args:
            prompt: Description of the image to generate
            negative_prompt: Elements to avoid (appended to prompt)
            aspect_ratio: Aspect ratio for the image
            num_images: Number of images to generate (1-4)

        Returns:
            ImageGenerationResponse with generated images
        """
        # Build the full prompt
        full_prompt = prompt
        if negative_prompt:
            full_prompt += f". Avoid: {negative_prompt}"

        # Add aspect ratio hint to prompt
        if aspect_ratio != AspectRatio.SQUARE:
            ratio_hints = {
                AspectRatio.LANDSCAPE_16_9: "wide landscape format",
                AspectRatio.PORTRAIT_9_16: "tall portrait format",
                AspectRatio.LANDSCAPE_4_3: "landscape format",
                AspectRatio.PORTRAIT_3_4: "portrait format",
            }
            if aspect_ratio in ratio_hints:
                full_prompt += f". Generate in {ratio_hints[aspect_ratio]}."

        request = ImageGenerationRequest(
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            num_images=num_images,
        )

        url = f"{self.base_url}/models/{self.model}:generateContent"
        body = self._build_request_body(request)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_response(data, full_prompt)

    async def edit(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> ImageGenerationResponse:
        """
        Edit an existing image with a text prompt.

        Args:
            prompt: Instructions for editing the image
            image_path: Path to the image file
            image_base64: Base64 encoded image data
            image_url: URL of the image to edit

        Returns:
            ImageGenerationResponse with edited image
        """
        # Get image data
        if image_path:
            with open(image_path, "rb") as f:
                image_base64 = base64.b64encode(f.read()).decode("utf-8")
            # Detect MIME type from extension
            ext = Path(image_path).suffix.lower()
            mime_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif",
            }.get(ext, "image/png")
        elif image_url:
            # Fetch image from URL
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url)
                resp.raise_for_status()
                image_base64 = base64.b64encode(resp.content).decode("utf-8")
                mime_type = resp.headers.get("content-type", "image/png")
        elif image_base64:
            mime_type = "image/png"
        else:
            raise ValueError("Must provide image_path, image_base64, or image_url")

        request = ImageGenerationRequest(
            prompt=prompt,
            reference_image_base64=image_base64,
            reference_image_mime=mime_type,
        )

        url = f"{self.base_url}/models/{self.model}:generateContent"
        body = self._build_request_body(request)

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_response(data, prompt)

    def generate_sync(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: AspectRatio = AspectRatio.SQUARE,
    ) -> ImageGenerationResponse:
        """
        Synchronous version of generate().

        Args:
            prompt: Description of the image to generate
            negative_prompt: Elements to avoid
            aspect_ratio: Aspect ratio for the image

        Returns:
            ImageGenerationResponse with generated images
        """
        import asyncio
        return asyncio.run(
            self.generate(prompt, negative_prompt, aspect_ratio)
        )

    def edit_sync(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        image_base64: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> ImageGenerationResponse:
        """
        Synchronous version of edit().
        """
        import asyncio
        return asyncio.run(
            self.edit(prompt, image_path, image_base64, image_url)
        )
