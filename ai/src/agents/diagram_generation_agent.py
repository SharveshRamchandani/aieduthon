"""
Diagram Generation Agent: Creates educational diagrams using Graphviz, Matplotlib, etc.
"""

import logging
import io
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from ai_db import get_ai_db
# Lazy import to avoid circular dependency
TextGenerationAgent = None

logger = logging.getLogger(__name__)


class DiagramGenerationAgent:
    """Agent that generates educational diagrams"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.diagrams_collection = self.db["diagrams"]
        self.media_collection = self.db["media"]
        self.text_agent = None  # Lazy load to avoid circular import
        self.output_dir = Path("out/generated_diagrams")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_text_agent(self):
        """Lazy load text agent to avoid circular import"""
        global TextGenerationAgent
        if TextGenerationAgent is None:
            from agents.text_generation_agent import TextGenerationAgent as TA
            TextGenerationAgent = TA
        if self.text_agent is None:
            self.text_agent = TextGenerationAgent()
        return self.text_agent
    
    def generate(self,
                 diagram_type: str,
                 description: str,
                 data: Optional[Dict] = None,
                 format: str = "png",
                 style: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate diagram based on type and description
        
        Args:
            diagram_type: Type of diagram (flowchart, process, hierarchy, chart, etc.)
            description: Description of what the diagram should show
            data: Optional data for data-driven diagrams
            format: Output format (png, svg, pdf)
            style: Style preferences
        
        Returns:
            Dict with diagram file path and metadata
        """
        try:
            # Generate diagram based on type
            if diagram_type in ["flowchart", "process"]:
                result = self._generate_flowchart(description, data, format, style)
            elif diagram_type in ["hierarchy", "tree"]:
                result = self._generate_hierarchy(description, data, format, style)
            elif diagram_type in ["chart", "graph", "plot"]:
                result = self._generate_chart(description, data, format, style)
            elif diagram_type == "cycle":
                result = self._generate_cycle(description, data, format, style)
            else:
                result = self._generate_generic(description, data, format, style)
            
            if result["success"]:
                # Store in database
                diagram_doc = {
                    "slideId": None,
                    "diagram_type": diagram_type,
                    "description": description,
                    "file_path": result["file_path"],
                    "format": format,
                    "tags": self._extract_tags(description),
                    "created_at": datetime.utcnow()
                }
                
                diagram_result = self.diagrams_collection.insert_one(diagram_doc)
                result["diagram_id"] = str(diagram_result.inserted_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def _generate_flowchart(self, description: str, data: Optional[Dict], format: str, style: Optional[str]) -> Dict[str, Any]:
        """Generate flowchart diagram using Graphviz"""
        if not GRAPHVIZ_AVAILABLE:
            return {
                "success": False,
                "error": "Graphviz not available",
                "file_path": None
            }
        
        try:
            # Use LLM to structure the flowchart if data not provided
            if data is None:
                structured = self._llm_structure_flowchart(description)
                data = structured.get("data", {})
            
            # Create graph
            dot = graphviz.Digraph(comment=description)
            dot.attr(rankdir='LR' if style == "horizontal" else 'TB')
            dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
            dot.attr('edge', color='gray')
            
            # Add nodes and edges
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            
            for node in nodes:
                node_id = node.get("id", "")
                node_label = node.get("label", node_id)
                dot.node(node_id, node_label)
            
            for edge in edges:
                from_node = edge.get("from", "")
                to_node = edge.get("to", "")
                label = edge.get("label", "")
                if label:
                    dot.edge(from_node, to_node, label=label)
                else:
                    dot.edge(from_node, to_node)
            
            # Save
            filename = f"flowchart_{hashlib.md5(description.encode()).hexdigest()[:8]}.{format}"
            filepath = self.output_dir / filename
            dot.render(str(filepath.with_suffix('')), format=format, cleanup=True)
            
            return {
                "success": True,
                "file_path": str(filepath.with_suffix(f".{format}")),
                "type": "flowchart"
            }
            
        except Exception as e:
            logger.error(f"Flowchart generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def _generate_hierarchy(self, description: str, data: Optional[Dict], format: str, style: Optional[str]) -> Dict[str, Any]:
        """Generate hierarchy/tree diagram"""
        if not GRAPHVIZ_AVAILABLE:
            return {
                "success": False,
                "error": "Graphviz not available",
                "file_path": None
            }
        
        try:
            if data is None:
                structured = self._llm_structure_hierarchy(description)
                data = structured.get("data", {})
            
            dot = graphviz.Digraph(comment=description)
            dot.attr(rankdir='TB')
            dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightgreen')
            
            # Build hierarchy
            root = data.get("root", {})
            if root:
                self._add_hierarchy_node(dot, root, None)
            
            filename = f"hierarchy_{hashlib.md5(description.encode()).hexdigest()[:8]}.{format}"
            filepath = self.output_dir / filename
            dot.render(str(filepath.with_suffix('')), format=format, cleanup=True)
            
            return {
                "success": True,
                "file_path": str(filepath.with_suffix(f".{format}")),
                "type": "hierarchy"
            }
            
        except Exception as e:
            logger.error(f"Hierarchy generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def _generate_chart(self, description: str, data: Optional[Dict], format: str, style: Optional[str]) -> Dict[str, Any]:
        """Generate chart/plot using Matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            return {
                "success": False,
                "error": "Matplotlib not available",
                "file_path": None
            }
        
        try:
            if data is None:
                structured = self._llm_structure_chart(description)
                data = structured.get("data", {})
            
            chart_type = data.get("type", "bar")
            labels = data.get("labels", [])
            values = data.get("values", [])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == "bar":
                ax.bar(labels, values, color='skyblue')
            elif chart_type == "line":
                ax.plot(labels, values, marker='o', color='green')
            elif chart_type == "pie":
                ax.pie(values, labels=labels, autopct='%1.1f%%')
            
            ax.set_title(description)
            ax.set_xlabel(data.get("xlabel", ""))
            ax.set_ylabel(data.get("ylabel", ""))
            plt.tight_layout()
            
            filename = f"chart_{hashlib.md5(description.encode()).hexdigest()[:8]}.{format}"
            filepath = self.output_dir / filename
            plt.savefig(filepath, format=format, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "success": True,
                "file_path": str(filepath),
                "type": "chart"
            }
            
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def _generate_cycle(self, description: str, data: Optional[Dict], format: str, style: Optional[str]) -> Dict[str, Any]:
        """Generate cycle diagram"""
        if not GRAPHVIZ_AVAILABLE:
            return {
                "success": False,
                "error": "Graphviz not available",
                "file_path": None
            }
        
        try:
            if data is None:
                structured = self._llm_structure_cycle(description)
                data = structured.get("data", {})
            
            dot = graphviz.Digraph(comment=description)
            dot.attr(rankdir='TB')
            dot.attr('node', shape='ellipse', style='filled', fillcolor='lightyellow')
            dot.attr('edge', color='blue', dir='forward')
            
            steps = data.get("steps", [])
            for i, step in enumerate(steps):
                step_id = f"step_{i}"
                dot.node(step_id, step)
                if i > 0:
                    dot.edge(f"step_{i-1}", step_id)
            # Close the cycle
            if len(steps) > 1:
                dot.edge(f"step_{len(steps)-1}", "step_0", style="dashed")
            
            filename = f"cycle_{hashlib.md5(description.encode()).hexdigest()[:8]}.{format}"
            filepath = self.output_dir / filename
            dot.render(str(filepath.with_suffix('')), format=format, cleanup=True)
            
            return {
                "success": True,
                "file_path": str(filepath.with_suffix(f".{format}")),
                "type": "cycle"
            }
            
        except Exception as e:
            logger.error(f"Cycle generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }
    
    def _generate_generic(self, description: str, data: Optional[Dict], format: str, style: Optional[str]) -> Dict[str, Any]:
        """Generate generic diagram (fallback to flowchart)"""
        return self._generate_flowchart(description, data, format, style)
    
    def _add_hierarchy_node(self, dot, node: Dict, parent_id: Optional[str]):
        """Recursively add hierarchy nodes"""
        node_id = node.get("id", "")
        node_label = node.get("label", node_id)
        dot.node(node_id, node_label)
        
        if parent_id:
            dot.edge(parent_id, node_id)
        
        children = node.get("children", [])
        for child in children:
            self._add_hierarchy_node(dot, child, node_id)
    
    def _llm_structure_flowchart(self, description: str) -> Dict[str, Any]:
        """Use LLM to structure flowchart data"""
        try:
            text_agent = self._get_text_agent()
            prompt = f"""Convert this description into a flowchart structure:
{description}

Return JSON:
{{
  "data": {{
    "nodes": [{{"id": "start", "label": "Start"}}, {{"id": "step1", "label": "Step 1"}}],
    "edges": [{{"from": "start", "to": "step1", "label": ""}}]
  }}
}}"""
            
            result = text_agent.generate(prompt, max_length=512)
            if result.get("success"):
                try:
                    import json
                    import re
                    json_match = re.search(r'\{.*\}', result["text"], re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                except Exception:
                    pass
        except Exception:
            # If LLM fails, use fallback
            pass
        
        # Fallback structure
        return {
            "data": {
                "nodes": [
                    {"id": "start", "label": "Start"},
                    {"id": "process", "label": description[:50]},
                    {"id": "end", "label": "End"}
                ],
                "edges": [
                    {"from": "start", "to": "process"},
                    {"from": "process", "to": "end"}
                ]
            }
        }
    
    def _llm_structure_hierarchy(self, description: str) -> Dict[str, Any]:
        """Use LLM to structure hierarchy data"""
        # Similar to flowchart but for hierarchy
        return {
            "data": {
                "root": {
                    "id": "root",
                    "label": description[:50],
                    "children": []
                }
            }
        }
    
    def _llm_structure_chart(self, description: str) -> Dict[str, Any]:
        """Use LLM to structure chart data"""
        # Fallback structure
        return {
            "data": {
                "type": "bar",
                "labels": ["A", "B", "C"],
                "values": [10, 20, 30],
                "xlabel": "Category",
                "ylabel": "Value"
            }
        }
    
    def _llm_structure_cycle(self, description: str) -> Dict[str, Any]:
        """Use LLM to structure cycle data"""
        return {
            "data": {
                "steps": ["Step 1", "Step 2", "Step 3", "Step 4"]
            }
        }
    
    def _extract_tags(self, description: str) -> List[str]:
        """Extract tags from description"""
        tags = []
        keywords = ["flowchart", "process", "hierarchy", "cycle", "chart", "diagram"]
        description_lower = description.lower()
        for keyword in keywords:
            if keyword in description_lower:
                tags.append(keyword)
        return tags
    
    def generate_for_slide(self,
                          slide_title: str,
                          slide_content: List[str],
                          diagram_type: str = "process") -> Dict[str, Any]:
        """Generate diagram appropriate for a slide"""
        description = f"{slide_title}: {' '.join(slide_content[:2])}"
        return self.generate(diagram_type, description)

