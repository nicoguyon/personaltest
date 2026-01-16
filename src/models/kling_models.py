"""
Pydantic models for Kling 2.6 video generation.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class TaskStatus(str, Enum):
    """Status of a video generation task."""
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    STAGED = "Staged"


class VideoMode(str, Enum):
    """Video generation mode."""
    STANDARD = "std"
    PRO = "pro"


class KlingVersion(str, Enum):
    """Kling model versions."""
    V1_5 = "1.5"
    V1_6 = "1.6"
    V2_1 = "2.1"
    V2_1_MASTER = "2.1-master"
    V2_5 = "2.5"
    V2_6 = "2.6"


class VideoAspectRatio(str, Enum):
    """Aspect ratios for video generation."""
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    SQUARE = "1:1"


class CameraControlType(str, Enum):
    """Types of camera movements."""
    SIMPLE = "simple"
    DOWN_BACK = "down_back"
    FORWARD_UP = "forward_up"
    RIGHT_TURN_FORWARD = "right_turn_forward"
    LEFT_TURN_FORWARD = "left_turn_forward"


class CameraControl(BaseModel):
    """Camera control settings for video generation."""

    type: CameraControlType = Field(default=CameraControlType.SIMPLE)
    horizontal: Optional[float] = Field(None, ge=-10, le=10, description="Horizontal movement")
    vertical: Optional[float] = Field(None, ge=-10, le=10, description="Vertical movement")
    pan: Optional[float] = Field(None, ge=-10, le=10, description="Pan angle")
    tilt: Optional[float] = Field(None, ge=-10, le=10, description="Tilt angle")
    roll: Optional[float] = Field(None, ge=-10, le=10, description="Roll angle")
    zoom: Optional[float] = Field(None, ge=-10, le=10, description="Zoom level")


class VideoGenerationRequest(BaseModel):
    """Request model for Kling video generation."""

    prompt: str = Field(..., max_length=2500, description="Text description of the video")
    negative_prompt: Optional[str] = Field(None, max_length=2500, description="Elements to avoid")

    # Video settings
    duration: int = Field(default=5, description="Duration in seconds (5 or 10)")
    aspect_ratio: VideoAspectRatio = Field(default=VideoAspectRatio.LANDSCAPE)
    mode: VideoMode = Field(default=VideoMode.STANDARD)
    version: KlingVersion = Field(default=KlingVersion.V2_6)

    # Generation settings
    cfg_scale: float = Field(default=0.5, ge=0, le=1, description="Creativity scale")
    enable_audio: bool = Field(default=False, description="Generate audio with video")

    # Image-to-video settings
    image_url: Optional[str] = Field(None, description="URL of initial frame image")
    image_tail_url: Optional[str] = Field(None, description="URL of end frame image")

    # Camera control
    camera_control: Optional[CameraControl] = Field(None, description="Camera movement settings")

    # Webhook
    webhook_url: Optional[str] = Field(None, description="URL for task completion webhook")


class TaskMeta(BaseModel):
    """Metadata for a video generation task."""

    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class TaskUsage(BaseModel):
    """Usage information for billing."""

    type: Optional[str] = None
    frozen: Optional[float] = None
    consume: Optional[float] = None


class VideoTask(BaseModel):
    """A video generation task."""

    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    video_url: Optional[str] = Field(None, description="URL of generated video")
    meta: Optional[TaskMeta] = None
    usage: Optional[TaskUsage] = None
    error_message: Optional[str] = None


class VideoGenerationResponse(BaseModel):
    """Response from Kling video generation."""

    task: VideoTask
    success: bool = Field(default=True)
    message: Optional[str] = None

    @property
    def is_completed(self) -> bool:
        """Check if the task is completed."""
        return self.task.status == TaskStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if the task failed."""
        return self.task.status == TaskStatus.FAILED

    @property
    def is_processing(self) -> bool:
        """Check if the task is still processing."""
        return self.task.status in [TaskStatus.PENDING, TaskStatus.PROCESSING, TaskStatus.STAGED]
