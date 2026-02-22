"""
Composer Agent - Final media assembly.
Synchronizes script, audio, video, and images into final output.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ..base_agent import BaseAgent, AgentInput, AgentOutput, AgentStatus


class ComposerAgent(BaseAgent):
    """
    Composer Agent - Assembles all content pieces into final video.
    
    Responsibilities:
    - Combine script + audio + video + images
    - Synchronize timing
    - Add transitions
    - Add captions/subtitles
    - Apply branding elements
    - Export final video
    
    This is the final assembly step before posting.
    """
    
    def __init__(
        self,
        video_editor: str = "ffmpeg",
        timeout_seconds: int = 400
    ):
        super().__init__(agent_name="ComposerAgent", timeout_seconds=timeout_seconds)
        self.video_editor = video_editor
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate composer input."""
        if not input_data.previous_outputs:
            return False
        
        content_type = str(input_data.pipeline_config.get("content_type", "video")).lower()
        outputs = input_data.previous_outputs
        
        if content_type == "video":
            required = ["script", "video"]
        elif content_type in ["image", "carousel"]:
            required = ["script", "image"]
        elif content_type in ["audio", "podcast"]:
            required = ["script", "audio"]
        elif content_type == "text":
            required = ["script"]
        else:
            required = ["script"]
        
        return all(key in outputs for key in required)
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Assemble final video from all components.
        
        Args:
            input_data: Contains all previous outputs
            
        Returns:
            AgentOutput with final composed video
        """
        if not self.validate_input(input_data):
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error="Invalid input: missing required components"
            )
        
        try:
            config = input_data.pipeline_config
            outputs = input_data.previous_outputs
            content_type = str(config.get("content_type", "video")).lower()
            
            # Extract components
            script_data = outputs.get("script", {})
            video_data = outputs.get("video", {})
            audio_data = outputs.get("audio", {})
            image_data = outputs.get("image", {})
            
            # Handle non-video compositions
            if content_type == "text":
                output_data = {
                    "final_text": script_data.get("script", ""),
                    "metadata": self._generate_metadata(
                        config=config,
                        script=script_data,
                        composition_spec=None
                    )
                }
                return self._create_output(
                    status=AgentStatus.SUCCESS,
                    output_data=output_data
                )
            
            if content_type in ["image", "carousel"]:
                output_data = {
                    "final_images": image_data.get("images", []),
                    "caption": script_data.get("script", ""),
                    "metadata": self._generate_metadata(
                        config=config,
                        script=script_data,
                        composition_spec=None
                    )
                }
                return self._create_output(
                    status=AgentStatus.SUCCESS,
                    output_data=output_data,
                    artifacts={"images": str(image_data.get("images", []))}
                )
            
            if content_type in ["audio", "podcast"]:
                output_data = {
                    "final_audio_url": audio_data.get("audio_url"),
                    "script": script_data.get("script", ""),
                    "metadata": self._generate_metadata(
                        config=config,
                        script=script_data,
                        composition_spec=None
                    )
                }
                return self._create_output(
                    status=AgentStatus.SUCCESS,
                    output_data=output_data,
                    artifacts={"audio": audio_data.get("audio_url")}
                )
            
            # Build composition specification
            composition_spec = self._build_composition_spec(
                config=config,
                script=script_data,
                video=video_data,
                audio=audio_data,
                images=image_data
            )
            
            # Assemble video
            final_video = await self._assemble_video(composition_spec)
            
            # Add enhancements
            if config.get("add_captions", False):
                final_video = await self._add_captions(
                    final_video,
                    script_data.get("script", "")
                )
            
            if config.get("add_branding", False):
                final_video = await self._add_branding(
                    final_video,
                    config.get("branding_elements", {})
                )
            
            # Generate metadata
            metadata = self._generate_metadata(
                config=config,
                script=script_data,
                composition_spec=composition_spec
            )
            
            output_data = {
                "final_video_url": final_video["url"],
                "duration_seconds": final_video["duration"],
                "resolution": final_video["resolution"],
                "file_size_mb": final_video["file_size"],
                "format": final_video["format"],
                "metadata": metadata,
                "composition_details": {
                    "layers": composition_spec["layers"],
                    "transitions": composition_spec["transitions"],
                    "effects": composition_spec.get("effects", [])
                }
            }
            
            return self._create_output(
                status=AgentStatus.SUCCESS,
                output_data=output_data,
                artifacts={"final_video": final_video["url"]}
            )
            
        except Exception as e:
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error=str(e)
            )
    
    def _build_composition_spec(
        self,
        config: Dict[str, Any],
        script: Dict[str, Any],
        video: Dict[str, Any],
        audio: Dict[str, Any],
        images: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build composition specification for video assembly.
        
        Defines:
        - Timeline structure
        - Layer order
        - Timing synchronization
        - Transitions
        - Effects
        """
        spec = {
            "duration": video.get("duration_seconds", 60),
            "resolution": config.get("resolution", "1080p"),
            "fps": config.get("fps", 30),
            "layers": [],
            "transitions": [],
            "timeline": []
        }
        
        # Layer 1: Base video
        spec["layers"].append({
            "layer_id": "video_base",
            "type": "video",
            "source": video.get("video_url"),
            "start": 0,
            "duration": video.get("duration_seconds", 60),
            "z_index": 0
        })
        
        # Layer 2: Audio/Voiceover
        if audio.get("audio_url"):
            spec["layers"].append({
                "layer_id": "audio_voiceover",
                "type": "audio",
                "source": audio.get("audio_url"),
                "start": 0,
                "duration": audio.get("duration_seconds", 60),
                "volume": 1.0
            })
        
        # Layer 3: Images/Overlays
        if images.get("images"):
            for idx, img in enumerate(images["images"][:3]):  # Max 3 images
                spec["layers"].append({
                    "layer_id": f"image_overlay_{idx}",
                    "type": "image",
                    "source": img.get("url"),
                    "start": idx * 5,  # Stagger images
                    "duration": 5,
                    "z_index": 1,
                    "position": "center"
                })
        
        # Add transitions
        spec["transitions"] = [
            {
                "type": "fade_in",
                "at": 0,
                "duration": 0.5
            },
            {
                "type": "fade_out",
                "at": spec["duration"] - 0.5,
                "duration": 0.5
            }
        ]
        
        # Build timeline from script sections
        script_sections = script.get("sections", {})
        timeline = []
        
        current_time = 0
        for section_name, section_text in script_sections.items():
            estimated_duration = len(section_text.split()) / 2.5  # Words per second
            timeline.append({
                "section": section_name,
                "start": current_time,
                "duration": estimated_duration,
                "text": section_text
            })
            current_time += estimated_duration
        
        spec["timeline"] = timeline
        
        return spec
    
    async def _assemble_video(
        self,
        composition_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assemble video using composition specification.
        
        This would use FFmpeg or similar video editing library.
        """
        # TODO: Implement actual video assembly with FFmpeg
        # Commands would be like:
        # ffmpeg -i video.mp4 -i audio.mp3 -i image.png \
        #   -filter_complex "[0:v][1:a][2:v]..." output.mp4
        
        await asyncio.sleep(2)  # Simulate processing
        
        return {
            "url": "https://example.com/final_video.mp4",
            "duration": composition_spec["duration"],
            "resolution": composition_spec["resolution"],
            "file_size": 15.5,  # MB
            "format": "mp4"
        }
    
    async def _add_captions(
        self,
        video: Dict[str, Any],
        script_text: str
    ) -> Dict[str, Any]:
        """
        Add captions/subtitles to video.
        
        Would use:
        - Speech-to-text for timing
        - FFmpeg for burning subtitles
        - Or generate SRT file
        """
        # TODO: Implement caption generation
        # Generate word-level timestamps
        # Burn captions into video or generate SRT
        
        await asyncio.sleep(0.5)
        
        return video  # Return modified video
    
    async def _add_branding(
        self,
        video: Dict[str, Any],
        branding_elements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add branding elements (logo, watermark, etc.).
        
        Elements:
        - Logo overlay
        - Watermark
        - Intro/outro clips
        - Brand colors
        """
        # TODO: Implement branding overlay
        # Use FFmpeg to overlay images/videos
        
        await asyncio.sleep(0.3)
        
        return video
    
    def _generate_metadata(
        self,
        config: Dict[str, Any],
        script: Dict[str, Any],
        composition_spec: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate metadata for final video."""
        # Extract title from script intro or config
        title = config.get("title", "Untitled Video")
        
        # Generate description from script
        script_text = script.get("script", "")
        description = script_text[:500] if len(script_text) > 500 else script_text
        
        # Extract hashtags
        hashtags = config.get("hashtags", [])
        topic = config.get("topic", "")
        if topic and not hashtags:
            hashtags = [f"#{topic.replace(' ', '')}"]
        
        duration = composition_spec.get("duration") if composition_spec else None

        return {
            "title": title,
            "description": description,
            "hashtags": hashtags,
            "platform": config.get("platform"),
            "content_type": config.get("content_type"),
            "duration": duration,
            "created_at": datetime.utcnow().isoformat(),
            "tags": self._extract_tags(script_text)
        }
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from script text."""
        # TODO: Implement smart tag extraction
        # For now, simple word frequency
        words = text.lower().split()
        
        # Filter common words
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        filtered_words = [w for w in words if w not in common_words and len(w) > 3]
        
        # Get top 5 most frequent
        from collections import Counter
        word_counts = Counter(filtered_words)
        top_words = [word for word, count in word_counts.most_common(5)]
        
        return top_words


class VideoTimingSync:
    """Utility for synchronizing video timing with audio and script."""
    
    @staticmethod
    def sync_audio_to_video(
        video_duration: float,
        audio_duration: float,
        script_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Synchronize audio with video timeline.
        
        Returns timing map for each section.
        """
        timing_map = {}
        
        # Calculate section timings
        total_words = sum(len(text.split()) for text in script_sections.values())
        words_per_second = total_words / audio_duration if audio_duration > 0 else 2.5
        
        current_time = 0.0
        for section_name, section_text in script_sections.items():
            word_count = len(section_text.split())
            duration = word_count / words_per_second
            
            timing_map[section_name] = {
                "start": current_time,
                "end": current_time + duration,
                "duration": duration,
                "words": word_count
            }
            
            current_time += duration
        
        return timing_map
    
    @staticmethod
    def generate_subtitle_timestamps(
        script_text: str,
        audio_duration: float,
        max_words_per_subtitle: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate timestamps for subtitles.
        
        Returns list of subtitle segments with timing.
        """
        words = script_text.split()
        total_words = len(words)
        words_per_second = total_words / audio_duration if audio_duration > 0 else 2.5
        
        subtitles = []
        current_time = 0.0
        
        for i in range(0, total_words, max_words_per_subtitle):
            chunk = words[i:i + max_words_per_subtitle]
            chunk_text = " ".join(chunk)
            duration = len(chunk) / words_per_second
            
            subtitles.append({
                "index": len(subtitles),
                "start": current_time,
                "end": current_time + duration,
                "text": chunk_text
            })
            
            current_time += duration
        
        return subtitles
