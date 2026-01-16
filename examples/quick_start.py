#!/usr/bin/env python3
"""
Quick Start Guide - AI Media Generation

This script provides a simple interface to generate images and videos.
Run it interactively or use the functions directly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clients.nano_banana import NanoBananaClient
from src.clients.kling import KlingClient
from src.config import Config


async def generate_image(prompt: str, output_name: str = "generated_image.png"):
    """
    Generate an image with Nano Banana Pro.

    Args:
        prompt: Description of the image
        output_name: Filename for the output

    Returns:
        Path to the generated image
    """
    print(f"Generating image: {prompt[:50]}...")

    client = NanoBananaClient()
    response = await client.generate(prompt)

    if response.success:
        output_dir = Config.ensure_output_dir()
        output_path = output_dir / output_name
        response.images[0].save(str(output_path))
        print(f"Image saved: {output_path}")
        return str(output_path)
    else:
        print("Image generation failed")
        return None


async def generate_video(
    prompt: str,
    output_name: str = "generated_video.mp4",
    duration: int = 5,
):
    """
    Generate a video with Kling 2.6.

    Args:
        prompt: Description of the video
        output_name: Filename for the output
        duration: Video duration (5 or 10 seconds)

    Returns:
        Path to the generated video
    """
    print(f"Generating video: {prompt[:50]}...")
    print("This may take a few minutes...")

    client = KlingClient()

    def on_progress(response):
        print(f"  Status: {response.task.status.value}")

    output_dir = Config.ensure_output_dir()
    output_path = output_dir / output_name

    response = await client.generate(prompt, duration=duration)
    result = await client.wait_for_completion(
        response.task.task_id,
        callback=on_progress,
    )

    if result.is_completed and result.task.video_url:
        await client.download_video(result.task.video_url, str(output_path))
        print(f"Video saved: {output_path}")
        return str(output_path)
    else:
        print(f"Video generation failed: {result.task.error_message}")
        return None


async def interactive_mode():
    """Run in interactive mode."""
    config = Config.validate()

    print("=" * 50)
    print("AI Media Generation - Interactive Mode")
    print("=" * 50)
    print()
    print("Available APIs:")
    print(f"  - Nano Banana Pro (images): {'Ready' if config['nano_banana'] else 'Not configured'}")
    print(f"  - Kling 2.6 (videos): {'Ready' if config['kling_piapi'] else 'Not configured'}")
    print()

    while True:
        print("\nOptions:")
        print("  1. Generate an image")
        print("  2. Generate a video")
        print("  3. Exit")
        print()

        choice = input("Choose an option (1-3): ").strip()

        if choice == "1":
            if not config["nano_banana"]:
                print("Error: GEMINI_API_KEY not set")
                continue

            prompt = input("Enter image prompt: ").strip()
            if prompt:
                name = input("Output filename (default: image.png): ").strip() or "image.png"
                await generate_image(prompt, name)

        elif choice == "2":
            if not config["kling_piapi"]:
                print("Error: PIAPI_API_KEY not set")
                continue

            prompt = input("Enter video prompt: ").strip()
            if prompt:
                name = input("Output filename (default: video.mp4): ").strip() or "video.mp4"
                duration = input("Duration in seconds (5 or 10, default: 5): ").strip()
                duration = int(duration) if duration in ["5", "10"] else 5
                await generate_video(prompt, name, duration)

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid option")


# Synchronous convenience functions for simple usage
def image(prompt: str, output_name: str = "generated_image.png"):
    """Generate an image (synchronous)."""
    return asyncio.run(generate_image(prompt, output_name))


def video(prompt: str, output_name: str = "generated_video.mp4", duration: int = 5):
    """Generate a video (synchronous)."""
    return asyncio.run(generate_video(prompt, output_name, duration))


if __name__ == "__main__":
    asyncio.run(interactive_mode())
