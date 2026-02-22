"""
Quality Check Agent - Validates content quality and compliance.
Acts as a gatekeeper before final assembly.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from ..base_agent import BaseAgent, AgentInput, AgentOutput, AgentStatus


class QCStatus(str, Enum):
    """Quality check status."""
    PASS = "PASS"
    SOFT_FAIL = "SOFT_FAIL"  # Can retry specific step
    HARD_FAIL = "HARD_FAIL"  # Must halt pipeline


@dataclass
class ValidationRule:
    """A quality validation rule."""
    rule_id: str
    name: str
    severity: QCStatus  # What happens if rule fails
    check_function: str  # Name of check function
    threshold: Optional[float] = None
    enabled: bool = True


@dataclass
class QCResult:
    """Result of quality check."""
    status: QCStatus
    score: float  # 0.0 to 1.0
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "score": self.score,
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "warnings": self.warnings,
            "reasons": self.reasons,
            "timestamp": self.timestamp.isoformat()
        }


class QualityCheckAgent(BaseAgent):
    """
    Quality Check Agent - Validates content quality and compliance.
    
    Validates:
    - Content length/duration
    - Tone match
    - Factual consistency
    - Platform compliance
    - Brand safety
    - Technical quality
    
    Returns:
    - PASS: Continue to next step
    - SOFT_FAIL: Regenerate specific step
    - HARD_FAIL: Halt pipeline
    """
    
    def __init__(
        self,
        rules: Optional[List[ValidationRule]] = None,
        timeout_seconds: int = 180
    ):
        super().__init__(agent_name="QualityCheckAgent", timeout_seconds=timeout_seconds)
        self.rules = rules or self._get_default_rules()
    
    def validate_input(self, input_data: AgentInput) -> bool:
        """Validate QC input."""
        # Needs outputs from content generation steps
        return input_data.previous_outputs is not None
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Perform quality checks on generated content.
        
        Args:
            input_data: Contains all previous step outputs
            
        Returns:
            AgentOutput with QC results
        """
        if not self.validate_input(input_data):
            return self._create_output(
                status=AgentStatus.FAILED,
                output_data={},
                error="Invalid input: no content to check"
            )
        
        try:
            config = input_data.pipeline_config
            previous_outputs = input_data.previous_outputs
            context_pack = input_data.context_pack
            
            # Run all validation rules
            qc_result = QCResult(
                status=QCStatus.PASS,
                score=1.0
            )
            
            for rule in self.rules:
                if not rule.enabled:
                    continue
                
                check_result = await self._run_check(
                    rule=rule,
                    config=config,
                    outputs=previous_outputs,
                    context=context_pack
                )
                
                if check_result["passed"]:
                    qc_result.passed_checks.append(rule.rule_id)
                else:
                    qc_result.failed_checks.append({
                        "rule_id": rule.rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity.value,
                        "reason": check_result.get("reason", ""),
                        "details": check_result.get("details", {})
                    })
                    
                    # Update overall status based on severity
                    if rule.severity == QCStatus.HARD_FAIL:
                        qc_result.status = QCStatus.HARD_FAIL
                    elif rule.severity == QCStatus.SOFT_FAIL and qc_result.status == QCStatus.PASS:
                        qc_result.status = QCStatus.SOFT_FAIL
                    
                    qc_result.reasons.append(f"{rule.name}: {check_result.get('reason', 'Failed')}")
            
            # Calculate overall score
            total_rules = len([r for r in self.rules if r.enabled])
            qc_result.score = len(qc_result.passed_checks) / total_rules if total_rules > 0 else 0.0
            
            output_data = {
                "qc_result": qc_result.to_dict(),
                "next_action": self._determine_next_action(qc_result)
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
    
    async def _run_check(
        self,
        rule: ValidationRule,
        config: Dict[str, Any],
        outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run a specific validation check."""
        check_function = getattr(self, f"_check_{rule.check_function}", None)
        
        if not check_function:
            return {
                "passed": False,
                "reason": f"Check function {rule.check_function} not found"
            }
        
        return await check_function(config, outputs, context, rule.threshold)
    
    # ==================== Validation Check Functions ====================
    
    async def _check_length_compliance(
        self,
        config: Dict[str, Any],
        outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> Dict[str, Any]:
        """Check if content length matches requirements."""
        target_duration = config.get("duration_seconds", 60)
        tolerance = threshold or 0.2  # 20% tolerance
        
        script_data = outputs.get("script", {})
        estimated_duration = script_data.get("estimated_duration", 0)
        
        if estimated_duration == 0:
            return {"passed": False, "reason": "No duration estimate available"}
        
        min_duration = target_duration * (1 - tolerance)
        max_duration = target_duration * (1 + tolerance)
        
        if min_duration <= estimated_duration <= max_duration:
            return {"passed": True}
        else:
            return {
                "passed": False,
                "reason": f"Duration {estimated_duration}s outside range [{min_duration:.0f}-{max_duration:.0f}s]",
                "details": {
                    "target": target_duration,
                    "actual": estimated_duration,
                    "tolerance": tolerance
                }
            }
    
    async def _check_tone_match(
        self,
        config: Dict[str, Any],
        outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> Dict[str, Any]:
        """Check if tone matches requirements."""
        target_tone = config.get("tone", "").lower()
        script_data = outputs.get("script", {})
        script_text = script_data.get("script", "")
        
        if not script_text:
            return {"passed": False, "reason": "No script to analyze"}
        
        # TODO: Implement actual tone analysis using LLM
        # Placeholder: simple keyword matching
        tone_keywords = {
            "professional": ["expert", "professional", "industry", "research"],
            "casual": ["hey", "you", "cool", "awesome"],
            "educational": ["learn", "understand", "discover", "explore"],
            "entertaining": ["fun", "amazing", "incredible", "wow"]
        }
        
        keywords = tone_keywords.get(target_tone, [])
        if not keywords:
            return {"passed": True, "reason": "Unknown tone, skipping check"}
        
        script_lower = script_text.lower()
        matches = sum(1 for kw in keywords if kw in script_lower)
        
        if matches >= 2:
            return {"passed": True}
        else:
            return {
                "passed": False,
                "reason": f"Tone '{target_tone}' not well represented",
                "details": {"expected_tone": target_tone, "matches": matches}
            }
    
    async def _check_factual_consistency(
        self,
        config: Dict[str, Any],
        outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> Dict[str, Any]:
        """Check factual consistency against research context."""
        if not context or not context.get("facts"):
            return {"passed": True, "reason": "No research context to verify against"}
        
        script_data = outputs.get("script", {})
        script_text = script_data.get("script", "")
        
        # TODO: Implement actual fact-checking using LLM
        # For now, just check if research facts appear in script
        facts = context.get("facts", [])
        
        if not facts:
            return {"passed": True}
        
        # Simple check: are any facts mentioned in script?
        script_lower = script_text.lower()
        mentioned_facts = 0
        
        for fact in facts[:5]:  # Check top 5 facts
            fact_text = str(fact.get("fact", "")).lower()
            if fact_text and any(word in script_lower for word in fact_text.split()[:3]):
                mentioned_facts += 1
        
        if mentioned_facts >= min(2, len(facts)):
            return {"passed": True}
        else:
            return {
                "passed": False,
                "reason": "Low factual consistency with research",
                "details": {"mentioned_facts": mentioned_facts, "total_facts": len(facts)}
            }
    
    async def _check_platform_compliance(
        self,
        config: Dict[str, Any],
        outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> Dict[str, Any]:
        """Check platform-specific compliance rules."""
        platform = str(config.get("platform", "")).lower()
        content_type = str(config.get("content_type", "")).lower()
        video_data = outputs.get("video", {})
        has_video = bool(video_data.get("video_url") or video_data.get("duration_seconds"))
        
        # Only validate platform rules when video output exists or content type is video
        if content_type not in ["video"] and not has_video:
            return {"passed": True, "reason": "No video output for platform compliance"}
        
        # Platform-specific rules
        platform_rules = {
            "youtube": {
                "min_duration": 10,
                "max_duration": 900,  # 15 minutes for most accounts
                "aspect_ratio": "16:9"
            },
            "tiktok": {
                "min_duration": 3,
                "max_duration": 180,  # 3 minutes
                "aspect_ratio": "9:16"
            },
            "instagram": {
                "min_duration": 3,
                "max_duration": 90,
                "aspect_ratio": "9:16"
            }
        }
        
        rules = platform_rules.get(platform)
        if not rules:
            return {"passed": True, "reason": "Platform not recognized, skipping"}
        
        # Check duration
        duration = video_data.get("duration_seconds", 0)
        
        if duration == 0:
            return {"passed": False, "reason": "No video duration available"}
        
        if duration < rules["min_duration"] or duration > rules["max_duration"]:
            return {
                "passed": False,
                "reason": f"Duration {duration}s outside {platform} limits [{rules['min_duration']}-{rules['max_duration']}s]"
            }
        
        return {"passed": True}
    
    async def _check_brand_safety(
        self,
        config: Dict[str, Any],
        outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> Dict[str, Any]:
        """Check for brand safety issues."""
        script_data = outputs.get("script", {})
        script_text = script_data.get("script", "").lower()
        
        # Basic keyword filtering (would use AI moderation in production)
        unsafe_keywords = [
            "violence", "hate", "explicit", "illegal", "dangerous"
        ]
        
        found_unsafe = [kw for kw in unsafe_keywords if kw in script_text]
        
        if found_unsafe:
            return {
                "passed": False,
                "reason": f"Potential brand safety issues detected",
                "details": {"keywords": found_unsafe}
            }
        
        return {"passed": True}
    
    async def _check_technical_quality(
        self,
        config: Dict[str, Any],
        outputs: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        threshold: Optional[float]
    ) -> Dict[str, Any]:
        """Check technical quality of outputs."""
        content_type = str(config.get("content_type", "text")).lower()
        
        # Required outputs based on content type
        required_outputs = ["script"]
        if content_type in ["image", "carousel", "video"]:
            required_outputs.append("image")
        if content_type in ["audio", "podcast", "video"]:
            required_outputs.append("audio")
        if content_type in ["video"]:
            required_outputs.append("video")
        
        missing = [out for out in required_outputs if out not in outputs]
        
        if missing:
            return {
                "passed": False,
                "reason": f"Missing required outputs: {', '.join(missing)}"
            }
        
        # Check that outputs have required fields
        script_data = outputs.get("script", {})
        if not script_data.get("script"):
            return {"passed": False, "reason": "Script content is empty"}
        
        if "video" in required_outputs:
            video_data = outputs.get("video", {})
            if not video_data.get("video_url"):
                return {"passed": False, "reason": "Video URL is missing"}
        
        return {"passed": True}
    
    # ==================== Helper Methods ====================
    
    def _get_default_rules(self) -> List[ValidationRule]:
        """Get default validation rules."""
        return [
            ValidationRule(
                rule_id="length_compliance",
                name="Length Compliance",
                severity=QCStatus.SOFT_FAIL,
                check_function="length_compliance",
                threshold=0.2  # 20% tolerance
            ),
            ValidationRule(
                rule_id="tone_match",
                name="Tone Match",
                severity=QCStatus.SOFT_FAIL,
                check_function="tone_match"
            ),
            ValidationRule(
                rule_id="factual_consistency",
                name="Factual Consistency",
                severity=QCStatus.SOFT_FAIL,
                check_function="factual_consistency"
            ),
            ValidationRule(
                rule_id="platform_compliance",
                name="Platform Compliance",
                severity=QCStatus.HARD_FAIL,
                check_function="platform_compliance"
            ),
            ValidationRule(
                rule_id="brand_safety",
                name="Brand Safety",
                severity=QCStatus.HARD_FAIL,
                check_function="brand_safety"
            ),
            ValidationRule(
                rule_id="technical_quality",
                name="Technical Quality",
                severity=QCStatus.HARD_FAIL,
                check_function="technical_quality"
            )
        ]
    
    def _determine_next_action(self, qc_result: QCResult) -> str:
        """Determine next action based on QC result."""
        if qc_result.status == QCStatus.PASS:
            return "continue"
        elif qc_result.status == QCStatus.SOFT_FAIL:
            # Identify which step to regenerate
            failed_checks = qc_result.failed_checks
            if any("script" in str(check).lower() for check in failed_checks):
                return "regenerate_script"
            elif any("video" in str(check).lower() for check in failed_checks):
                return "regenerate_video"
            else:
                return "regenerate_script"  # Default
        else:  # HARD_FAIL
            return "halt_pipeline"
