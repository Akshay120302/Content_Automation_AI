"""
Execution DAG (Directed Acyclic Graph) for pipeline orchestration.
Deterministic execution graph with dependency resolution and parallel execution.
"""

from typing import Dict, List, Set, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime


class NodeType(str, Enum):
    """Types of nodes in the execution graph."""
    RESEARCH = "RESEARCH"
    SCRIPT = "SCRIPT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    QUALITY_CHECK = "QUALITY_CHECK"
    COMPOSER = "COMPOSER"
    POST = "POST"


@dataclass
class DAGNode:
    """A node in the execution DAG."""
    node_id: str
    node_type: NodeType
    agent_name: str
    dependencies: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None
    timeout_seconds: int = 300
    required: bool = True
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def can_execute(self, completed_nodes: Set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep in completed_nodes for dep in self.dependencies)
    
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if node should execute based on condition."""
        if self.condition is None:
            return True
        return self.condition(context)


@dataclass
class ExecutionDAG:
    """
    Directed Acyclic Graph for pipeline execution.
    Manages dependencies and parallel execution.
    """
    dag_id: str
    nodes: Dict[str, DAGNode] = field(default_factory=dict)
    
    def add_node(self, node: DAGNode) -> None:
        """Add a node to the DAG."""
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists")
        self.nodes[node.node_id] = node
    
    def validate(self) -> bool:
        """
        Validate the DAG structure.
        - No cycles
        - All dependencies exist
        - At least one node
        """
        if not self.nodes:
            raise ValueError("DAG must have at least one node")
        
        # Check all dependencies exist
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    raise ValueError(
                        f"Node {node.node_id} depends on non-existent node {dep}"
                    )
        
        # Check for cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            node = self.nodes[node_id]
            for dep in node.dependencies:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    raise ValueError("DAG contains cycles")
        
        return True
    
    def get_ready_nodes(
        self,
        completed_nodes: Set[str],
        running_nodes: Set[str],
        context: Dict[str, Any]
    ) -> List[DAGNode]:
        """
        Get nodes that are ready to execute.
        
        Args:
            completed_nodes: Set of completed node IDs
            running_nodes: Set of currently running node IDs
            context: Execution context for conditional nodes
            
        Returns:
            List of nodes ready to execute
        """
        ready = []
        
        for node_id, node in self.nodes.items():
            # Skip if already completed or running
            if node_id in completed_nodes or node_id in running_nodes:
                continue
            
            # Check dependencies
            if not node.can_execute(completed_nodes):
                continue
            
            # Check condition
            if not node.should_execute(context):
                completed_nodes.add(node_id)  # Mark as skipped
                continue
            
            ready.append(node)
        
        return ready
    
    def get_parallel_groups(
        self,
        ready_nodes: List[DAGNode]
    ) -> Dict[str, List[DAGNode]]:
        """
        Group ready nodes by parallel execution group.
        
        Args:
            ready_nodes: List of nodes ready to execute
            
        Returns:
            Dictionary of group name to nodes
        """
        groups: Dict[str, List[DAGNode]] = {}
        
        for node in ready_nodes:
            group_key = node.parallel_group or node.node_id
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(node)
        
        return groups
    
    def topological_sort(self) -> List[str]:
        """
        Return a topological ordering of nodes.
        Useful for visualizing execution order.
        """
        in_degree = {node_id: 0 for node_id in self.nodes}
        
        # Calculate in-degree for each node
        for node in self.nodes.values():
            for dep in node.dependencies:
                in_degree[dep] += 1
        
        # Queue of nodes with no incoming edges
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            # Reduce in-degree for dependent nodes
            for other_id, other_node in self.nodes.items():
                if node_id in other_node.dependencies:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)
        
        return result
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the DAG structure."""
        return {
            "dag_id": self.dag_id,
            "total_nodes": len(self.nodes),
            "node_types": {
                node_type.value: len([
                    n for n in self.nodes.values() if n.node_type == node_type
                ])
                for node_type in NodeType
            },
            "parallel_groups": len(set(
                n.parallel_group for n in self.nodes.values() if n.parallel_group
            )),
            "topological_order": self.topological_sort()
        }


class DAGBuilder:
    """Builder for creating standard pipeline DAGs."""
    
    @staticmethod
    def build_standard_dag(
        pipeline_config: Dict[str, Any],
        user_assets: Dict[str, Any]
    ) -> ExecutionDAG:
        """
        Build a standard content generation DAG based on configuration.
        Conditionally includes nodes based on content_type.
        
        Args:
            pipeline_config: Pipeline configuration
            user_assets: User-provided assets
            
        Returns:
            ExecutionDAG ready for execution
        """
        dag = ExecutionDAG(dag_id=f"dag_{pipeline_config.get('pipeline_id')}")
        
        content_type = pipeline_config.get("content_type", "text").lower()
        
        # Research node (conditional - only if needed)
        def needs_research(ctx: Dict[str, Any]) -> bool:
            topic_type = pipeline_config.get("topic_type", "")
            factual_mode = pipeline_config.get("factual_mode", False)
            
            return (
                topic_type in ["trending", "news"] or
                factual_mode or
                content_type in ["educational", "long-form"]
            )
        
        research_node = DAGNode(
            node_id="research",
            node_type=NodeType.RESEARCH,
            agent_name="DeepResearchAgent",
            dependencies=[],
            condition=needs_research,
            required=False,
            timeout_seconds=600
        )
        dag.add_node(research_node)
        
        # Content generation based on content_type
        parallel_group = "content_generation"
        
        # Script/Text node - ALWAYS needed
        script_node = DAGNode(
            node_id="script",
            node_type=NodeType.SCRIPT,
            agent_name="ScriptAgent",
            dependencies=["research"],
            parallel_group=parallel_group if content_type != "text" else None,
            timeout_seconds=300
        )
        dag.add_node(script_node)
        
        # For text-only content, skip all other agents
        if content_type == "text":
            # No quality check or composer needed for simple text
            dag.validate()
            return dag
        
        # Image generation (for image, carousel, video content)
        if content_type in ["image", "carousel", "video"]:
            image_node = DAGNode(
                node_id="image",
                node_type=NodeType.IMAGE,
                agent_name="ImageAgent",
                dependencies=["research", "script"],  # Script provides context
                parallel_group=parallel_group if content_type != "image" else None,
                timeout_seconds=400
            )
            dag.add_node(image_node)
        
        # Audio generation (for audio, video content)
        if content_type in ["audio", "video", "podcast"]:
            audio_node = DAGNode(
                node_id="audio",
                node_type=NodeType.AUDIO,
                agent_name="AudioAgent",
                dependencies=["research", "script"],  # Script provides narration
                parallel_group=parallel_group if content_type == "video" else None,
                timeout_seconds=300
            )
            dag.add_node(audio_node)
        
        # Video generation (only for video content)
        if content_type == "video":
            video_deps = ["script"]
            if "image" in dag.nodes:
                video_deps.append("image")
            if "audio" in dag.nodes:
                video_deps.append("audio")
            
            video_node = DAGNode(
                node_id="video",
                node_type=NodeType.VIDEO,
                agent_name="VideoAgent",
                dependencies=video_deps,
                timeout_seconds=600
            )
            dag.add_node(video_node)
        
        # Quality check (depends on all generated content)
        qc_deps = ["script"]
        if "image" in dag.nodes:
            qc_deps.append("image")
        if "audio" in dag.nodes:
            qc_deps.append("audio")
        if "video" in dag.nodes:
            qc_deps.append("video")
        
        qc_node = DAGNode(
            node_id="quality_check",
            node_type=NodeType.QUALITY_CHECK,
            agent_name="QualityCheckAgent",
            dependencies=qc_deps,
            timeout_seconds=180
        )
        dag.add_node(qc_node)
        
        # Composer (final assembly - combines all outputs)
        composer_deps = ["quality_check", "script"]
        if "audio" in dag.nodes:
            composer_deps.append("audio")
        if "image" in dag.nodes:
            composer_deps.append("image")
        if "video" in dag.nodes:
            composer_deps.append("video")
        
        composer_node = DAGNode(
            node_id="composer",
            node_type=NodeType.COMPOSER,
            agent_name="ComposerAgent",
            dependencies=composer_deps,
            timeout_seconds=400
        )
        dag.add_node(composer_node)
        
        # Post (optional)
        if pipeline_config.get("auto_post", False):
            post_node = DAGNode(
                node_id="post",
                node_type=NodeType.POST,
                agent_name="PostingAgent",
                dependencies=["composer"],
                required=False,
                timeout_seconds=120
            )
            dag.add_node(post_node)
        
        # Validate DAG
        dag.validate()
        
        return dag
