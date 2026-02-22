from typing import Dict, Any, List, Optional
import os
import httpx

from .provider_base import BaseVideoProvider, VideoResult


class RunwayProvider(BaseVideoProvider):
    name = "runway"

    async def generate_video(
        self,
        prompt: str,
        images: Optional[List[Dict[str, Any]]],
        config: Dict[str, Any]
    ) -> VideoResult:
        api_key = os.getenv("RUNWAY_API_KEY", "")
        api_url = os.getenv("RUNWAY_API_URL", "")
        if not api_key or api_key.startswith("example") or not api_url:
            return VideoResult(
                provider=self.name,
                status="missing_api_key",
                metadata={"message": "RUNWAY_API_KEY or RUNWAY_API_URL not configured"}
            )

        payload: Dict[str, Any] = {
            "prompt": prompt,
            "duration": config.get("video_duration_seconds") or 4,
            "aspect_ratio": config.get("video_aspect_ratio") or "16:9"
        }

        if images:
            payload["image"] = images[0].get("s3_url") or images[0].get("url")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(api_url, headers=headers, json=payload)

        if resp.status_code not in [200, 201, 202]:
            return VideoResult(
                provider=self.name,
                status="error",
                metadata={"message": resp.text}
            )

        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        return VideoResult(
            provider=self.name,
            status=data.get("status", "processing"),
            video_url=data.get("video_url"),
            job_id=data.get("id"),
            metadata={"raw": data}
        )
