"""
Individual agent tasks for Celery.
Granular tasks for specific agent operations.
"""

import asyncio
from typing import Dict, Any, Optional
import logging

from .celery_app import celery_app, agent_task, research_task, background_task
from ..agents.research.deep_research_agent import DeepResearchAgent, ResearchDepth
from ..agents.content.content_agents import ScriptAgent, ImageAgent, AudioAgent, VideoAgent
from ..agents.quality.quality_check_agent import QualityCheckAgent
from ..agents.composer.composer_agent import ComposerAgent
from ..agents.base_agent import AgentInput

logger = logging.getLogger(__name__)


# ==================== Research Tasks ====================

@research_task(name='research.deep_research')
def deep_research_task(
    self,
    topic: str,
    depth: str = "MEDIUM",
    region: Optional[str] = None,
    language: str = "en",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Execute deep research on a topic.
    
    Args:
        topic: Research topic
        depth: Research depth (SHALLOW, MEDIUM, DEEP)
        region: Geographic region
        language: Language for results
        context: Additional context
        
    Returns:
        ContextPack as dictionary
    """
    logger.info(f"Starting deep research: {topic}")
    
    try:
        agent = DeepResearchAgent()
        
        # Convert depth string to enum
        research_depth = ResearchDepth[depth.upper()]
        
        # Execute research
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        context_pack = loop.run_until_complete(
            agent.research(
                topic=topic,
                depth=research_depth,
                region=region,
                language=language,
                context=context
            )
        )
        
        logger.info(f"Research completed: {topic} - Score: {context_pack.confidence_score}")
        
        return {
            "success": True,
            "context_pack": context_pack.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Research failed: {topic} - {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== Content Generation Tasks ====================

@agent_task(name='agent.generate_script')
def generate_script_task(
    self,
    pipeline_config: Dict[str, Any],
    context_pack: Optional[Dict[str, Any]] = None,
    user_assets: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate script content."""
    logger.info("Starting script generation")
    
    try:
        agent = ScriptAgent()
        
        agent_input = AgentInput(
            pipeline_config=pipeline_config,
            context_pack=context_pack,
            user_assets=user_assets
        )
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        output = loop.run_until_complete(agent.execute(agent_input))
        
        logger.info(f"Script generation completed - Status: {output.status.value}")
        
        return {
            "success": output.status.value == "SUCCESS",
            "output": output.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Script generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@agent_task(name='agent.generate_image')
def generate_image_task(
    self,
    pipeline_config: Dict[str, Any],
    context_pack: Optional[Dict[str, Any]] = None,
    user_assets: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate images."""
    logger.info("Starting image generation")
    
    try:
        agent = ImageAgent()
        
        agent_input = AgentInput(
            pipeline_config=pipeline_config,
            context_pack=context_pack,
            user_assets=user_assets
        )
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        output = loop.run_until_complete(agent.execute(agent_input))
        
        logger.info(f"Image generation completed - Status: {output.status.value}")
        
        return {
            "success": output.status.value == "SUCCESS",
            "output": output.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Image generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@agent_task(name='agent.generate_audio')
def generate_audio_task(
    self,
    pipeline_config: Dict[str, Any],
    previous_outputs: Dict[str, Any],
    context_pack: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate audio/voiceover."""
    logger.info("Starting audio generation")
    
    try:
        agent = AudioAgent()
        
        agent_input = AgentInput(
            pipeline_config=pipeline_config,
            context_pack=context_pack,
            previous_outputs=previous_outputs
        )
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        output = loop.run_until_complete(agent.execute(agent_input))
        
        logger.info(f"Audio generation completed - Status: {output.status.value}")
        
        return {
            "success": output.status.value == "SUCCESS",
            "output": output.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Audio generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@agent_task(name='agent.generate_video')
def generate_video_task(
    self,
    pipeline_config: Dict[str, Any],
    previous_outputs: Dict[str, Any],
    context_pack: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate video content."""
    logger.info("Starting video generation")
    
    try:
        agent = VideoAgent()
        
        agent_input = AgentInput(
            pipeline_config=pipeline_config,
            context_pack=context_pack,
            previous_outputs=previous_outputs
        )
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        output = loop.run_until_complete(agent.execute(agent_input))
        
        logger.info(f"Video generation completed - Status: {output.status.value}")
        
        return {
            "success": output.status.value == "SUCCESS",
            "output": output.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== Quality Check Tasks ====================

@agent_task(name='agent.quality_check')
def quality_check_task(
    self,
    pipeline_config: Dict[str, Any],
    previous_outputs: Dict[str, Any],
    context_pack: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Perform quality check on generated content."""
    logger.info("Starting quality check")
    
    try:
        agent = QualityCheckAgent()
        
        agent_input = AgentInput(
            pipeline_config=pipeline_config,
            context_pack=context_pack,
            previous_outputs=previous_outputs
        )
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        output = loop.run_until_complete(agent.execute(agent_input))
        
        qc_result = output.output_data.get("qc_result", {})
        logger.info(
            f"Quality check completed - Status: {qc_result.get('status')} - "
            f"Score: {qc_result.get('score')}"
        )
        
        return {
            "success": output.status.value == "SUCCESS",
            "output": output.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Quality check failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== Composition Tasks ====================

@agent_task(name='agent.compose_final_video')
def compose_final_video_task(
    self,
    pipeline_config: Dict[str, Any],
    previous_outputs: Dict[str, Any]
) -> Dict[str, Any]:
    """Compose final video from all components."""
    logger.info("Starting final video composition")
    
    try:
        agent = ComposerAgent()
        
        agent_input = AgentInput(
            pipeline_config=pipeline_config,
            previous_outputs=previous_outputs
        )
        
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        output = loop.run_until_complete(agent.execute(agent_input))
        
        logger.info(f"Video composition completed - Status: {output.status.value}")
        
        return {
            "success": output.status.value == "SUCCESS",
            "output": output.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Video composition failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== Utility Tasks ====================

@background_task(name='utility.cleanup_temp_files')
def cleanup_temp_files_task(self, pipeline_run_id: str) -> Dict[str, Any]:
    """Clean up temporary files from pipeline execution."""
    logger.info(f"Cleaning up temp files for: {pipeline_run_id}")
    
    try:
        # TODO: Implement cleanup logic
        # Remove temporary files, cache entries, etc.
        
        return {
            "success": True,
            "pipeline_run_id": pipeline_run_id,
            "message": "Temp files cleaned"
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@background_task(name='utility.cache_research')
def cache_research_task(
    self,
    topic: str,
    context_pack: Dict[str, Any]
) -> Dict[str, Any]:
    """Cache research results for reuse."""
    logger.info(f"Caching research for: {topic}")
    
    try:
        # TODO: Store in Redis/database
        # This would save the context_pack for future use
        
        return {
            "success": True,
            "topic": topic,
            "message": "Research cached"
        }
        
    except Exception as e:
        logger.error(f"Cache failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
