from typing import Dict, Any, List, Optional
import os
import httpx

from .provider_base import BaseVideoProvider, VideoResult


class ComfyUIProvider(BaseVideoProvider):
    name = "comfyui"

    async def generate_video(
        self,
        prompt: str,
        images: Optional[List[Dict[str, Any]]],
        config: Dict[str, Any]
    ) -> VideoResult:
        base_url = os.getenv("COMFYUI_URL", "http://localhost:8188")
        if not base_url:
            return VideoResult(
                provider=self.name,
                status="missing_config",
                metadata={"message": "COMFYUI_URL not configured"}
            )

        workflow = config.get("comfyui_workflow")
        if not workflow:
            # Minimal fallback workflow stub (expects ComfyUI custom nodes to handle prompt)
            workflow = {
                "prompt": prompt,
                "images": [img.get("s3_url") or img.get("url") for img in (images or []) if img.get("s3_url") or img.get("url")]
            }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{base_url}/prompt", json=workflow)

        if resp.status_code not in [200, 201]:
            return VideoResult(
                provider=self.name,
                status="error",
                metadata={"message": resp.text}
            )

        data = resp.json()
        return VideoResult(
            provider=self.name,
            status="processing",
            video_url=None,
            job_id=data.get("prompt_id") or data.get("id"),
            metadata={"raw": data}
        )
