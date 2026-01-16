#!/usr/bin/env python3
"""
Example: Generate images with Nano Banana Pro

This example demonstrates:
- Basic text-to-image generation
- Image editing with a reference image
- Different aspect ratios
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clients.nano_banana import NanoBananaClient
from src.models.nano_banana_models import AspectRatio
from src.config import Config


async def example_basic_generation():
    """Generate a simple image from text."""
    print("=" * 50)
    print("Example 1: Basic Image Generation")
    print("=" * 50)

    client = NanoBananaClient()

    response = await client.generate(
        prompt="A serene Japanese garden with cherry blossoms, "
               "a small wooden bridge over a koi pond, "
               "soft morning light filtering through the trees",
        negative_prompt="people, text, watermark",
    )

    if response.success:
        output_dir = Config.ensure_output_dir()
        output_path = output_dir / "japanese_garden.png"
        response.images[0].save(str(output_path))
        print(f"Image saved to: {output_path}")

        if response.text_response:
            print(f"Model response: {response.text_response}")
    else:
        print("Failed to generate image")


async def example_landscape_generation():
    """Generate a landscape format image."""
    print("\n" + "=" * 50)
    print("Example 2: Landscape Image (16:9)")
    print("=" * 50)

    client = NanoBananaClient()

    response = await client.generate(
        prompt="A dramatic mountain landscape at sunset, "
               "snow-capped peaks reflecting golden light, "
               "a crystal clear lake in the foreground, "
               "cinematic composition",
        aspect_ratio=AspectRatio.LANDSCAPE_16_9,
    )

    if response.success:
        output_dir = Config.ensure_output_dir()
        output_path = output_dir / "mountain_sunset.png"
        response.images[0].save(str(output_path))
        print(f"Image saved to: {output_path}")


async def example_portrait_generation():
    """Generate a portrait format image."""
    print("\n" + "=" * 50)
    print("Example 3: Portrait Image (9:16)")
    print("=" * 50)

    client = NanoBananaClient()

    response = await client.generate(
        prompt="A mystical forest path leading upward, "
               "tall ancient trees with glowing mushrooms, "
               "magical fireflies floating in the air, "
               "fantasy art style",
        aspect_ratio=AspectRatio.PORTRAIT_9_16,
    )

    if response.success:
        output_dir = Config.ensure_output_dir()
        output_path = output_dir / "mystical_forest.png"
        response.images[0].save(str(output_path))
        print(f"Image saved to: {output_path}")


async def example_image_editing():
    """Edit an existing image with a text prompt."""
    print("\n" + "=" * 50)
    print("Example 4: Image Editing")
    print("=" * 50)

    # This example requires an existing image
    # Uncomment and modify the path to test
    """
    client = NanoBananaClient()

    response = await client.edit(
        prompt="Add a beautiful rainbow in the sky and make the colors more vibrant",
        image_path="./output/mountain_sunset.png",
    )

    if response.success:
        output_dir = Config.ensure_output_dir()
        output_path = output_dir / "mountain_sunset_rainbow.png"
        response.images[0].save(str(output_path))
        print(f"Edited image saved to: {output_path}")
    """
    print("(Skipped - requires an existing image)")


async def main():
    """Run all examples."""
    # Check API key
    config = Config.validate()
    if not config["nano_banana"]:
        print("Error: GEMINI_API_KEY not set!")
        print("Please set the GEMINI_API_KEY environment variable or create a .env file.")
        print("\nGet your API key at: https://aistudio.google.com/apikey")
        return

    print("Nano Banana Pro - Image Generation Examples")
    print("API key configured: Yes")
    print()

    try:
        await example_basic_generation()
        await example_landscape_generation()
        await example_portrait_generation()
        await example_image_editing()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print(f"Check the '{Config.OUTPUT_DIR}' directory for generated images.")
        print("=" * 50)

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
