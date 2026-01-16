#!/usr/bin/env python3
"""
Example: Generate videos with Kling 2.6

This example demonstrates:
- Basic text-to-video generation
- Image-to-video generation
- Camera controls
- Different modes and durations
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clients.kling import KlingClient
from src.models.kling_models import (
    VideoMode,
    KlingVersion,
    VideoAspectRatio,
    CameraControl,
    CameraControlType,
)
from src.config import Config


def progress_callback(response):
    """Print progress updates during video generation."""
    status = response.task.status.value
    print(f"  Status: {status}")


async def example_basic_video():
    """Generate a simple video from text."""
    print("=" * 50)
    print("Example 1: Basic Text-to-Video")
    print("=" * 50)

    client = KlingClient()

    print("Starting video generation...")
    response = await client.generate(
        prompt="A golden retriever puppy playing with a red ball "
               "in a sunny backyard, slow motion, cinematic lighting",
        duration=5,
        mode=VideoMode.STANDARD,
    )

    print(f"Task created: {response.task.task_id}")
    print("Waiting for completion (this may take a few minutes)...")

    result = await client.wait_for_completion(
        response.task.task_id,
        poll_interval=15.0,
        callback=progress_callback,
    )

    if result.is_completed and result.task.video_url:
        output_dir = Config.ensure_output_dir()
        output_path = output_dir / "puppy_playing.mp4"
        await client.download_video(result.task.video_url, str(output_path))
        print(f"Video saved to: {output_path}")
    else:
        print(f"Generation status: {result.task.status}")


async def example_pro_mode():
    """Generate a high-quality video with Pro mode."""
    print("\n" + "=" * 50)
    print("Example 2: Pro Mode Video (Higher Quality)")
    print("=" * 50)

    client = KlingClient()

    print("Starting pro mode generation...")
    result = await client.generate_and_wait(
        prompt="A majestic eagle soaring through mountain peaks "
               "at golden hour, dramatic clouds, epic cinematic shot",
        duration=5,
        mode=VideoMode.PRO,
        version=KlingVersion.V2_6,
        output_path=str(Config.ensure_output_dir() / "eagle_flight.mp4"),
    )

    if result.is_completed:
        print(f"Video saved to: {Config.OUTPUT_DIR}/eagle_flight.mp4")


async def example_with_camera_control():
    """Generate a video with camera movements."""
    print("\n" + "=" * 50)
    print("Example 3: Video with Camera Control")
    print("=" * 50)

    client = KlingClient()

    camera = CameraControl(
        type=CameraControlType.FORWARD_UP,
        zoom=3.0,
        tilt=-2.0,
    )

    print("Starting generation with camera control...")
    result = await client.generate_and_wait(
        prompt="A futuristic city skyline at night, "
               "neon lights reflecting on wet streets, "
               "cyberpunk atmosphere",
        duration=5,
        camera_control=camera,
        output_path=str(Config.ensure_output_dir() / "cyberpunk_city.mp4"),
    )

    if result.is_completed:
        print(f"Video saved to: {Config.OUTPUT_DIR}/cyberpunk_city.mp4")


async def example_portrait_video():
    """Generate a vertical video (for social media)."""
    print("\n" + "=" * 50)
    print("Example 4: Portrait Video (9:16 for social media)")
    print("=" * 50)

    client = KlingClient()

    print("Starting portrait video generation...")
    result = await client.generate_and_wait(
        prompt="A beautiful waterfall in a tropical rainforest, "
               "mist rising, lush green vegetation, "
               "peaceful nature scene",
        duration=5,
        aspect_ratio=VideoAspectRatio.PORTRAIT,
        output_path=str(Config.ensure_output_dir() / "waterfall_portrait.mp4"),
    )

    if result.is_completed:
        print(f"Video saved to: {Config.OUTPUT_DIR}/waterfall_portrait.mp4")


async def example_10_second_video():
    """Generate a longer 10-second video."""
    print("\n" + "=" * 50)
    print("Example 5: Extended Duration (10 seconds)")
    print("=" * 50)

    client = KlingClient()

    print("Starting 10-second video generation...")
    result = await client.generate_and_wait(
        prompt="Ocean waves gently rolling onto a sandy beach "
               "at sunset, seagulls flying, peaceful atmosphere, "
               "ambient sounds of nature",
        duration=10,
        enable_audio=True,
        output_path=str(Config.ensure_output_dir() / "beach_sunset.mp4"),
    )

    if result.is_completed:
        print(f"Video saved to: {Config.OUTPUT_DIR}/beach_sunset.mp4")


async def example_image_to_video():
    """Generate a video from an existing image."""
    print("\n" + "=" * 50)
    print("Example 6: Image-to-Video")
    print("=" * 50)

    # This requires an existing image URL
    # Uncomment and modify to test
    """
    client = KlingClient()

    result = await client.generate_and_wait(
        prompt="Add gentle animation, subtle movement in the leaves, "
               "soft breeze effect",
        image_url="https://example.com/your-image.jpg",  # Replace with your image URL
        duration=5,
        output_path=str(Config.ensure_output_dir() / "animated_image.mp4"),
    )

    if result.is_completed:
        print(f"Video saved to: {Config.OUTPUT_DIR}/animated_image.mp4")
    """
    print("(Skipped - requires an image URL)")


async def main():
    """Run all examples."""
    # Check API key
    config = Config.validate()
    if not config["kling_piapi"]:
        print("Error: PIAPI_API_KEY not set!")
        print("Please set the PIAPI_API_KEY environment variable or create a .env file.")
        print("\nGet your API key at: https://piapi.ai")
        return

    print("Kling 2.6 - Video Generation Examples")
    print("API key configured: Yes")
    print()
    print("Note: Video generation can take several minutes per video.")
    print("The examples will wait for completion automatically.")
    print()

    try:
        # Run only the basic example by default
        # Uncomment others to run them
        await example_basic_video()
        # await example_pro_mode()
        # await example_with_camera_control()
        # await example_portrait_video()
        # await example_10_second_video()
        # await example_image_to_video()

        print("\n" + "=" * 50)
        print("Examples completed!")
        print(f"Check the '{Config.OUTPUT_DIR}' directory for generated videos.")
        print("=" * 50)

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
