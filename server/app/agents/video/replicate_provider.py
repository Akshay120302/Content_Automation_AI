from typing import Dict, Any, List, Optional
import os
import httpx

from .provider_base import BaseVideoProvider, VideoResult


class ReplicateProvider(BaseVideoProvider):
    name = "replicate"

    async def generate_video(
        self,
        prompt: str,
        images: Optional[List[Dict[str, Any]]],
        config: Dict[str, Any]
    ) -> VideoResult:
        api_token = os.getenv("REPLICATE_API_TOKEN", "")
        if not api_token or api_token.startswith("example"):
            return VideoResult(
                provider=self.name,
                status="missing_api_key",
                video_url=None,
                metadata={"message": "REPLICATE_API_TOKEN not configured"}
            )

        model = config.get("video_model") or "stability-ai/stable-video-diffusion"
        aspect_ratio = config.get("video_aspect_ratio") or "16:9"
        duration = config.get("video_duration_seconds") or 4

        input_payload: Dict[str, Any] = {
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio
        }

        # Optional image conditioning
        if images:
            first_image = images[0].get("s3_url") or images[0].get("url")
            if first_image:
                input_payload["image"] = first_image

        headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers=headers,
                json={
                    "version": model,
                    "input": input_payload
                }
            )

        if resp.status_code not in [200, 201]:
            return VideoResult(
                provider=self.name,
                status="error",
                metadata={"message": resp.text}
            )

        data = resp.json()
        status = data.get("status", "processing")
        output = data.get("output")
        video_url = output[0] if isinstance(output, list) and output else output

        return VideoResult(
            provider=self.name,
            status=status,
            video_url=video_url,
            job_id=data.get("id"),
            metadata={"raw": data}
        )
