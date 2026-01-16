"""
Kling 2.6 Client - Video Generation

Supports:
- Text-to-video generation
- Image-to-video generation
- Camera controls
- Audio generation
- Multiple aspect ratios and durations
"""

import asyncio
import httpx
from typing import Optional
from datetime import datetime

from ..config import Config
from ..models.kling_models import (
    VideoGenerationRequest,
    VideoGenerationResponse,
    VideoTask,
    TaskStatus,
    VideoMode,
    KlingVersion,
    VideoAspectRatio,
    CameraControl,
    TaskMeta,
)


class KlingClient:
    """
    Client for Kling 2.6 video generation via PiAPI.

    Usage:
        client = KlingClient()

        # Start generation
        response = await client.generate("A cat playing piano")

        # Wait for completion
        result = await client.wait_for_completion(response.task.task_id)

        # Download video
        await client.download_video(result.task.video_url, "cat_piano.mp4")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_direct_api: bool = False,
    ):
        """
        Initialize the Kling client.

        Args:
            api_key: API key (defaults to PIAPI_API_KEY or KLING_API_KEY env var)
            use_direct_api: Use direct Kling API instead of PiAPI
        """
        if use_direct_api:
            self.api_key = api_key or Config.KLING_API_KEY
            self.base_url = Config.KLING_BASE_URL
        else:
            self.api_key = api_key or Config.PIAPI_API_KEY
            self.base_url = Config.PIAPI_BASE_URL

        self.use_direct_api = use_direct_api

        if not self.api_key:
            raise ValueError(
                "API key required. Set PIAPI_API_KEY (or KLING_API_KEY) environment variable "
                "or pass api_key parameter."
            )

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }

    def _build_request_body(
        self,
        request: VideoGenerationRequest,
    ) -> dict:
        """Build the API request body for PiAPI."""
        input_data = {
            "prompt": request.prompt,
            "duration": request.duration,
            "aspect_ratio": request.aspect_ratio.value,
            "mode": request.mode.value,
            "version": request.version.value,
            "cfg_scale": request.cfg_scale,
        }

        if request.negative_prompt:
            input_data["negative_prompt"] = request.negative_prompt

        if request.enable_audio:
            input_data["enable_audio"] = True

        # Image-to-video
        if request.image_url:
            input_data["image_url"] = request.image_url

        if request.image_tail_url:
            input_data["image_tail_url"] = request.image_tail_url

        # Camera control
        if request.camera_control:
            camera_config = {"type": request.camera_control.type.value}
            if request.camera_control.horizontal is not None:
                camera_config["horizontal"] = request.camera_control.horizontal
            if request.camera_control.vertical is not None:
                camera_config["vertical"] = request.camera_control.vertical
            if request.camera_control.pan is not None:
                camera_config["pan"] = request.camera_control.pan
            if request.camera_control.tilt is not None:
                camera_config["tilt"] = request.camera_control.tilt
            if request.camera_control.roll is not None:
                camera_config["roll"] = request.camera_control.roll
            if request.camera_control.zoom is not None:
                camera_config["zoom"] = request.camera_control.zoom
            input_data["camera_control"] = camera_config

        body = {
            "model": "kling",
            "task_type": "video_generation",
            "input": input_data,
        }

        # Webhook configuration
        if request.webhook_url:
            body["config"] = {
                "webhook_config": {
                    "endpoint": request.webhook_url,
                }
            }

        return body

    def _parse_response(self, response_data: dict) -> VideoGenerationResponse:
        """Parse the API response."""
        data = response_data.get("data", response_data)

        # Extract task info
        task_id = data.get("task_id", "")
        status_str = data.get("status", "Pending")

        # Parse status
        try:
            status = TaskStatus(status_str)
        except ValueError:
            status = TaskStatus.PENDING

        # Extract video URL from output
        output = data.get("output", {})
        video_url = output.get("video_url") if isinstance(output, dict) else None

        # Parse metadata
        meta_data = data.get("meta", {})
        meta = None
        if meta_data:
            meta = TaskMeta(
                created_at=meta_data.get("created_at"),
                started_at=meta_data.get("started_at"),
                ended_at=meta_data.get("ended_at"),
            )

        # Parse error
        error_data = data.get("error", {})
        error_message = error_data.get("message") if isinstance(error_data, dict) else None

        task = VideoTask(
            task_id=task_id,
            status=status,
            video_url=video_url,
            meta=meta,
            error_message=error_message,
        )

        return VideoGenerationResponse(
            task=task,
            success=response_data.get("code", 200) == 200,
            message=response_data.get("message"),
        )

    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        duration: int = 5,
        aspect_ratio: VideoAspectRatio = VideoAspectRatio.LANDSCAPE,
        mode: VideoMode = VideoMode.STANDARD,
        version: KlingVersion = KlingVersion.V2_6,
        cfg_scale: float = 0.5,
        enable_audio: bool = False,
        image_url: Optional[str] = None,
        camera_control: Optional[CameraControl] = None,
        webhook_url: Optional[str] = None,
    ) -> VideoGenerationResponse:
        """
        Start a video generation task.

        Args:
            prompt: Description of the video to generate
            negative_prompt: Elements to avoid
            duration: Duration in seconds (5 or 10)
            aspect_ratio: Video aspect ratio
            mode: Generation mode (std or pro)
            version: Kling model version
            cfg_scale: Creativity scale (0-1)
            enable_audio: Generate audio with video
            image_url: URL of initial frame (for image-to-video)
            camera_control: Camera movement settings
            webhook_url: URL for completion webhook

        Returns:
            VideoGenerationResponse with task info
        """
        request = VideoGenerationRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            mode=mode,
            version=version,
            cfg_scale=cfg_scale,
            enable_audio=enable_audio,
            image_url=image_url,
            camera_control=camera_control,
            webhook_url=webhook_url,
        )

        url = f"{self.base_url}/task"
        body = self._build_request_body(request)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_response(data)

    async def get_task_status(self, task_id: str) -> VideoGenerationResponse:
        """
        Get the status of a video generation task.

        Args:
            task_id: The task ID to check

        Returns:
            VideoGenerationResponse with current status
        """
        url = f"{self.base_url}/task/{task_id}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            data = response.json()

        return self._parse_response(data)

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 10.0,
        max_wait: float = 600.0,
        callback: Optional[callable] = None,
    ) -> VideoGenerationResponse:
        """
        Wait for a video generation task to complete.

        Args:
            task_id: The task ID to wait for
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait
            callback: Optional callback function called on each poll

        Returns:
            VideoGenerationResponse with final status

        Raises:
            TimeoutError: If max_wait is exceeded
            RuntimeError: If the task fails
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            response = await self.get_task_status(task_id)

            if callback:
                callback(response)

            if response.is_completed:
                return response

            if response.is_failed:
                raise RuntimeError(
                    f"Video generation failed: {response.task.error_message}"
                )

            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait:
                raise TimeoutError(
                    f"Video generation timed out after {max_wait} seconds"
                )

            await asyncio.sleep(poll_interval)

    async def download_video(
        self,
        video_url: str,
        output_path: str,
    ) -> str:
        """
        Download a generated video.

        Args:
            video_url: URL of the video to download
            output_path: Path to save the video

        Returns:
            Path to the saved video
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(video_url)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(response.content)

        return output_path

    async def generate_and_wait(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> VideoGenerationResponse:
        """
        Generate a video and wait for completion.

        This is a convenience method that combines generate(),
        wait_for_completion(), and optionally download_video().

        Args:
            prompt: Description of the video to generate
            output_path: Optional path to save the video
            **kwargs: Additional arguments passed to generate()

        Returns:
            VideoGenerationResponse with completed task
        """
        response = await self.generate(prompt, **kwargs)
        result = await self.wait_for_completion(response.task.task_id)

        if output_path and result.task.video_url:
            await self.download_video(result.task.video_url, output_path)

        return result

    # Synchronous convenience methods

    def generate_sync(
        self,
        prompt: str,
        **kwargs,
    ) -> VideoGenerationResponse:
        """Synchronous version of generate()."""
        return asyncio.run(self.generate(prompt, **kwargs))

    def get_task_status_sync(self, task_id: str) -> VideoGenerationResponse:
        """Synchronous version of get_task_status()."""
        return asyncio.run(self.get_task_status(task_id))

    def wait_for_completion_sync(
        self,
        task_id: str,
        **kwargs,
    ) -> VideoGenerationResponse:
        """Synchronous version of wait_for_completion()."""
        return asyncio.run(self.wait_for_completion(task_id, **kwargs))

    def generate_and_wait_sync(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> VideoGenerationResponse:
        """Synchronous version of generate_and_wait()."""
        return asyncio.run(
            self.generate_and_wait(prompt, output_path, **kwargs)
        )
