from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class VideoResult:
    provider: str
    status: str
    video_url: Optional[str] = None
    job_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseVideoProvider:
    """Base interface for video generation providers."""

    name: str = "base"

    async def generate_video(
        self,
        prompt: str,
        images: Optional[List[Dict[str, Any]]],
        config: Dict[str, Any]
    ) -> VideoResult:
        raise NotImplementedError
