from typing import Dict, Any, List, Optional

from .provider_base import BaseVideoProvider, VideoResult
from .replicate_provider import ReplicateProvider
from .runway_provider import RunwayProvider
from .comfyui_provider import ComfyUIProvider


class VideoProviderSelector:
    def __init__(self):
        self.providers = {
            "replicate": ReplicateProvider(),
            "runway": RunwayProvider(),
            "comfyui": ComfyUIProvider()
        }

    async def generate_video(
        self,
        provider_name: str,
        prompt: str,
        images: Optional[List[Dict[str, Any]]],
        config: Dict[str, Any]
    ) -> VideoResult:
        provider_key = (provider_name or "replicate").lower()
        provider = self.providers.get(provider_key, self.providers["replicate"])
        return await provider.generate_video(prompt=prompt, images=images, config=config)
