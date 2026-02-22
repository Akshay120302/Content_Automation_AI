"""
Content generation agents (Script, Image, Audio, Video).
Pure execution workers - stateless, idempotent, retryable.
"""

from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import os
import tempfile
import urllib.request

from app.utils.s3_storage import S3Client
from app.agents.video.selector import VideoProviderSelector

from ..base_agent import BaseAgent, AgentInput, AgentOutput, AgentStatus


class ScriptAgent(BaseAgent):
    """
    Script generation agent.
    Creates written content/scripts for videos based on context and requirements.
    """
    
    def __init__(
        self,
        timeout_seconds: int = 300
    ):
        super().__init__(agent_name="ScriptAgent", timeout_seconds=timeout_seconds)
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate script generation input."""
        required_fields = ["content_type", "platform"]
        config = input_data.pipeline_config
        
        return all(field in config for field in required_fields)
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Generate script content.
        
        Args:
            input_data: Contains pipeline_config, context_pack, user_assets
            
        Returns:
            AgentOutput with generated script
        """
        if not self.validate_input(input_data):
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error="Invalid input: missing required fields (content_type, platform)"
            )
        
        try:
            config = input_data.pipeline_config
            context_pack = input_data.context_pack
            
            # Extract parameters from user config
            content_type = config.get("content_type", "text")
            platform = config.get("platform", "general")
            tone = config.get("tone", "professional")
            topic = config.get("topic", "")
            duration_seconds = config.get("duration_seconds", 60)
            additional_prompt = config.get("additional_prompt", "")
            llm_model = config.get("llm_model", "gpt-4")  # User's chosen model
            llm_provider = config.get("llm_provider", "openai")  # openai or anthropic
            
            # Build prompt with user inputs
            prompt = self._build_prompt(
                topic=topic,
                content_type=content_type,
                platform=platform,
                tone=tone,
                duration=duration_seconds,
                additional_prompt=additional_prompt,
                context_pack=context_pack
            )
            
            # Generate script using selected LLM
            script = await self._generate_script(
                prompt=prompt,
                provider=llm_provider,
                model=llm_model
            )
            
            # Structure output
            output_data = {
                "script": script,
                "word_count": len(script.split()),
                "estimated_duration": self._estimate_duration(script),
                "sections": self._parse_sections(script),
                "metadata": {
                    "tone": tone,
                    "platform": platform,
                    "content_type": content_type,
                    "model_used": llm_model
                }
            }
            
            return self._create_output(
                status=AgentStatus.SUCCESS,
                output_data=output_data
            )
            
        except Exception as e:
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error=str(e)
            )
    
    def _build_prompt(
        self,
        topic: str,
        content_type: str,
        platform: str,
        tone: str,
        duration: int,
        additional_prompt: str,
        context_pack: Optional[Dict[str, Any]]
    ) -> str:
        """Build LLM prompt for script generation with user inputs."""
        prompt_parts = [
            f"Create a {content_type} script for {platform}.",
            f"Topic: {topic}",
            f"Tone: {tone}",
        ]
        
        # Add duration for video/audio content
        if content_type in ["video", "audio", "podcast"]:
            prompt_parts.append(f"Target duration: {duration} seconds")
        
        # Add context from research if available
        if context_pack:
            facts = context_pack.get("facts", [])
            if facts:
                prompt_parts.append(f"\nKey facts to include: {', '.join(str(f) for f in facts[:3])}")
            
            trends = context_pack.get("trends", [])
            if trends:
                prompt_parts.append(f"Current trends: {', '.join(str(t) for t in trends[:2])}")
        
        # Add user's additional prompt/requirements
        if additional_prompt:
            prompt_parts.append(f"\nAdditional requirements: {additional_prompt}")
        
        # Platform-specific guidelines
        platform_guidelines = {
            "linkedin": "Professional tone, industry insights, value-driven content",
            "youtube": "Engaging hook, storytelling, call-to-action",
            "instagram": "Visual-first, concise, trendy language",
            "twitter": "Concise, punchy, thread-friendly",
            "tiktok": "Fast-paced, trending sounds, hook in first 3 seconds",
            "facebook": "Community-focused, shareable, conversational"
        }
        
        if platform.lower() in platform_guidelines:
            prompt_parts.append(f"\nPlatform guidelines: {platform_guidelines[platform.lower()]}")
        
        prompt_parts.append("\nMake it engaging, authentic, and platform-appropriate.")
        
        return "\n".join(prompt_parts)
    
    async def _generate_script(self, prompt: str, provider: str, model: str) -> str:
        """Generate script using selected LLM provider."""
        try:
            if provider.lower() == "openai":
                return await self._call_openai(prompt, model)
            elif provider.lower() == "anthropic":
                return await self._call_anthropic(prompt, model)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        except Exception as e:
            # Fallback to mock if API fails
            print(f"LLM API call failed: {e}. Using fallback.")
            return await self._generate_fallback_script(prompt)
    
    async def _call_openai(self, prompt: str, model: str) -> str:
        """Call OpenAI API for script generation."""
        try:
            from openai import AsyncOpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key or api_key == "your-openai-api-key-here":
                raise ValueError("OPENAI_API_KEY not configured")
            
            client = AsyncOpenAI(api_key=api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional content creator and scriptwriter. Create engaging, platform-optimized content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            raise ValueError("OpenAI library not installed. Run: pip install openai")
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    async def _call_anthropic(self, prompt: str, model: str) -> str:
        """Call Anthropic Claude API for script generation."""
        try:
            from anthropic import AsyncAnthropic
            
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")
            
            client = AsyncAnthropic(api_key=api_key)
            
            response = await client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except ImportError:
            raise ValueError("Anthropic library not installed. Run: pip install anthropic")
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")
    
    async def _generate_fallback_script(self, prompt: str) -> str:
        """Fallback mock script when API unavailable."""
        await asyncio.sleep(0.5)
        
        return f"""[INTRO]
Welcome! Today we're exploring an exciting topic.

[MAIN CONTENT]
Here's where we dive deep into the subject matter, providing valuable insights and engaging storytelling that resonates with our audience.

[CALL TO ACTION]
If you found this valuable, engage with the content!

[OUTRO]
Thanks for your time! Stay tuned for more."""
    
    def _estimate_duration(self, script: str) -> int:
        """Estimate duration based on word count (assumes 150 words/min)."""
        word_count = len(script.split())
        return int((word_count / 150) * 60)
    
    def _parse_sections(self, script: str) -> Dict[str, str]:
        """Parse script into sections."""
        sections = {}
        current_section = "main"
        current_text = []
        
        for line in script.split("\n"):
            if line.strip().startswith("[") and line.strip().endswith("]"):
                if current_text:
                    sections[current_section] = "\n".join(current_text)
                current_section = line.strip()[1:-1].lower().replace(" ", "_")
                current_text = []
            else:
                current_text.append(line)
        
        if current_text:
            sections[current_section] = "\n".join(current_text)
        
        return sections


class ImageAgent(BaseAgent):
    """
    Image generation agent.
    Creates images/thumbnails for content.
    """
    
    def __init__(
        self,
        image_provider: str = "dalle",
        timeout_seconds: int = 400
    ):
        super().__init__(agent_name="ImageAgent", timeout_seconds=timeout_seconds)
        self.image_provider = image_provider
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate image generation input."""
        return "content_type" in input_data.pipeline_config
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Generate images."""
        if not self.validate_input(input_data):
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error="Invalid input"
            )
        
        try:
            config = input_data.pipeline_config
            context_pack = input_data.context_pack
            
            # Extract parameters
            topic = config.get("topic", "")
            style = config.get("image_style", "realistic")
            count = config.get("image_count", 1)
            
            # Generate images
            images = await self._generate_images(
                topic=topic,
                style=style,
                count=count,
                context=context_pack
            )

            # Upload to S3 if configured
            images = await self._upload_images_to_s3(images, config)
            
            output_data = {
                "images": images,
                "count": len(images),
                "style": style
            }
            
            return self._create_output(
                status=AgentStatus.SUCCESS,
                output_data=output_data,
                artifacts={"images": str(images)}
            )
            
        except Exception as e:
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error=str(e)
            )
    
    async def _generate_images(
        self,
        topic: str,
        style: str,
        count: int,
        context: Optional[Dict[str, Any]]
    ) -> list:
        """Generate images using AI."""
        prompt = f"{topic} in {style} style".strip()
        api_key = os.getenv("OPENAI_API_KEY")

        if api_key and api_key != "your-openai-api-key-here":
            try:
                from openai import AsyncOpenAI

                client = AsyncOpenAI(api_key=api_key)
                response = await client.images.generate(
                    model="gpt-image-1",
                    prompt=prompt,
                    size="1024x1024",
                    n=max(1, count)
                )

                images = []
                for idx, item in enumerate(response.data):
                    images.append({
                        "url": item.url,
                        "prompt": prompt,
                        "index": idx
                    })

                return images
            except Exception:
                pass

        # Fallback mock output
        await asyncio.sleep(0.5)

        return [
            {
                "url": f"https://example.com/image_{i}.png",
                "prompt": prompt,
                "index": i
            }
            for i in range(count)
        ]

    async def _upload_images_to_s3(self, images: list, config: Dict[str, Any]) -> list:
        s3 = S3Client()
        if not s3.is_available():
            return images

        user_id = str(config.get("user_id", ""))
        pipeline_id = config.get("pipeline_id")
        run_id = config.get("run_id", "")
        if not user_id or not pipeline_id or not run_id:
            return images

        updated = []
        for img in images:
            url = img.get("url")
            if not url:
                updated.append(img)
                continue

            try:
                data = await asyncio.to_thread(lambda: urllib.request.urlopen(url).read())
                filename = f"image_{img.get('index', 0)}.png"
                s3_key = s3.generate_run_s3_key(
                    user_id=user_id,
                    pipeline_id=int(pipeline_id),
                    run_id=run_id,
                    filename=filename,
                    role="images"
                )
                s3_url = s3.upload_bytes(data, s3_key, "image/png")
                updated.append({
                    **img,
                    "s3_key": s3_key,
                    "s3_url": s3_url or img.get("url")
                })
            except Exception:
                updated.append(img)

        return updated


class AudioAgent(BaseAgent):
    """
    Audio generation agent.
    Creates voiceovers and audio for content.
    """
    
    def __init__(
        self,
        tts_provider: str = "elevenlabs",
        timeout_seconds: int = 300
    ):
        super().__init__(agent_name="AudioAgent", timeout_seconds=timeout_seconds)
        self.tts_provider = tts_provider
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate audio generation input."""
        # Needs script from previous step
        if not input_data.previous_outputs:
            return False
        return "script" in input_data.previous_outputs.get("script", {})
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Generate audio/voiceover."""
        if not self.validate_input(input_data):
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error="Invalid input: script required"
            )
        
        try:
            config = input_data.pipeline_config
            script_data = input_data.previous_outputs.get("script", {})
            script_text = script_data.get("script", "")
            self._current_config = config
            
            # Extract parameters
            voice = config.get("voice", "default")
            language = config.get("language", "en")
            
            # Generate audio
            audio = await self._generate_audio(
                text=script_text,
                voice=voice,
                language=language
            )
            
            output_data = {
                "audio_url": audio["url"],
                "duration_seconds": audio["duration"],
                "voice": voice,
                "language": language
            }
            
            return self._create_output(
                status=AgentStatus.SUCCESS,
                output_data=output_data,
                artifacts={"audio": audio["url"]}
            )
            
        except Exception as e:
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error=str(e)
            )
    
    async def _generate_audio(
        self,
        text: str,
        voice: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate audio using TTS."""
        try:
            from gtts import gTTS
        except Exception:
            await asyncio.sleep(0.5)
            return {
                "url": "https://example.com/audio.mp3",
                "duration": len(text.split()) / 2.5,
                "format": "mp3"
            }

        s3 = S3Client()
        if not s3.is_available():
            await asyncio.sleep(0.5)
            return {
                "url": "https://example.com/audio.mp3",
                "duration": len(text.split()) / 2.5,
                "format": "mp3"
            }

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            tts = gTTS(text=text, lang=language or "en")
            tts.save(temp_audio.name)

        user_id = str(self._config_get("user_id"))
        pipeline_id = self._config_get("pipeline_id")
        run_id = str(self._config_get("run_id"))
        s3_key = s3.generate_run_s3_key(
            user_id=user_id,
            pipeline_id=int(pipeline_id),
            run_id=run_id,
            filename="voiceover.mp3",
            role="audio"
        )
        s3_url = s3.upload_file(temp_audio.name, s3_key, "audio/mpeg")

        return {
            "url": s3_url or "https://example.com/audio.mp3",
            "duration": len(text.split()) / 2.5,
            "format": "mp3",
            "s3_key": s3_key
        }

    def _config_get(self, key: str):
        return getattr(self, "_current_config", {}).get(key)


class VideoAgent(BaseAgent):
    """
    Video generation agent.
    Creates video clips from images, text, and specifications.
    """
    
    def __init__(
        self,
        video_provider: str = "runway",
        timeout_seconds: int = 600
    ):
        super().__init__(agent_name="VideoAgent", timeout_seconds=timeout_seconds)
        self.video_provider = video_provider
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate video generation input."""
        # Needs script at minimum
        if not input_data.previous_outputs:
            return False
        return "script" in input_data.previous_outputs
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """Generate video content."""
        if not self.validate_input(input_data):
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error="Invalid input: script required"
            )
        
        try:
            config = input_data.pipeline_config
            script_data = input_data.previous_outputs.get("script", {})
            image_data = input_data.previous_outputs.get("image", {})
            audio_data = input_data.previous_outputs.get("audio", {})

            self._current_config = config
            
            # Extract parameters
            duration = config.get("duration_seconds", 60)
            resolution = config.get("resolution", "1080p")
            fps = config.get("fps", 30)
            
            # Generate video
            video = await self._generate_video(
                script=script_data,
                images=image_data.get("images", []),
                duration=duration,
                resolution=resolution,
                fps=fps,
                audio=audio_data,
                config=config
            )
            
            output_data = {
                "video_url": video["url"],
                "duration_seconds": video["duration"],
                "resolution": resolution,
                "fps": fps,
                "scenes": video["scenes"]
            }
            
            return self._create_output(
                status=AgentStatus.SUCCESS,
                output_data=output_data,
                artifacts={"video": video["url"]}
            )
            
        except Exception as e:
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error=str(e)
            )
    
    async def _generate_video(
        self,
        script: Dict[str, Any],
        images: list,
        duration: int,
        resolution: str,
        fps: int,
        audio: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video using AI."""
        provider_name = config.get("video_provider") or "replicate"
        selector = VideoProviderSelector()
        prompt = self._build_video_prompt(script, config)

        result = await selector.generate_video(
            provider_name=provider_name,
            prompt=prompt,
            images=images,
            config=config
        )

        video_url = result.video_url
        if not video_url:
            await asyncio.sleep(0.5)
            return {
                "url": "https://example.com/video.mp4",
                "duration": duration,
                "format": "mp4",
                "scenes": [],
                "provider": result.provider,
                "status": result.status,
                "job_id": result.job_id
            }

        s3 = S3Client()
        if not s3.is_available():
            return {
                "url": video_url,
                "duration": duration,
                "format": "mp4",
                "scenes": [],
                "provider": result.provider,
                "status": result.status,
                "job_id": result.job_id
            }

        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = os.path.join(temp_dir, "video.mp4")
            await asyncio.to_thread(lambda: urllib.request.urlretrieve(video_url, local_path))

            user_id = str(self._config_get("user_id"))
            pipeline_id = self._config_get("pipeline_id")
            run_id = str(self._config_get("run_id"))
            s3_key = s3.generate_run_s3_key(
                user_id=user_id,
                pipeline_id=int(pipeline_id),
                run_id=run_id,
                filename="final.mp4",
                role="video"
            )
            s3_url = s3.upload_file(local_path, s3_key, "video/mp4")

        return {
            "url": s3_url or video_url,
            "duration": duration,
            "format": "mp4",
            "scenes": [],
            "provider": result.provider,
            "status": result.status,
            "job_id": result.job_id,
            "s3_key": s3_key
        }

    def _build_video_prompt(self, script: Dict[str, Any], config: Dict[str, Any]) -> str:
        base_prompt = config.get("additional_prompt") or ""
        script_text = script.get("script", "")
        topic = config.get("topic", "")

        parts = [
            f"Topic: {topic}" if topic else "",
            base_prompt,
            script_text
        ]

        return "\n".join([p for p in parts if p]).strip()

    def _config_get(self, key: str):
        return getattr(self, "_current_config", {}).get(key)
