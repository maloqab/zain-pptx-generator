"""
AI Agent System for Zain PPTX Generator
Handles chat, tool calls, and sub-agent orchestration
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import uuid
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pptx_renderer import BrandConfig, PPTXRenderer
from ai_planner import SlidePlanner

app = Flask(__name__)
CORS(app)

# Store active conversations
conversations: Dict[str, Dict] = {}

# Tool definitions
TOOLS = {
    "create_slide": {
        "description": "Create a single slide with specific content and layout",
        "parameters": {
            "type": {"type": "string", "enum": ["title", "content", "section"]},
            "title": {"type": "string"},
            "content": {"type": "array", "items": {"type": "string"}},
            "layout": {"type": "string", "enum": ["bullets", "two_column", "big_number", "quote"]},
            "gradient": {"type": "string"}
        }
    },
    "generate_chart": {
        "description": "Generate a chart/visualization for data",
        "parameters": {
            "chart_type": {"type": "string", "enum": ["bar", "line", "pie", "doughnut"]},
            "data": {"type": "object"},
            "title": {"type": "string"},
            "labels": {"type": "array", "items": {"type": "string"}}
        }
    },
    "analyze_content": {
        "description": "Analyze content and suggest optimal slide structure",
        "parameters": {
            "content": {"type": "string"},
            "audience": {"type": "string"},
            "goal": {"type": "string"}
        }
    },
    "render_presentation": {
        "description": "Render all slides into final PPTX file",
        "parameters": {
            "slides": {"type": "array"},
            "title_gradient": {"type": "string"},
            "section_gradient": {"type": "string"}
        }
    }
}


class AgentOrchestrator:
    """Orchestrates sub-agents for presentation design"""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.slides: List[Dict] = []
        self.context: Dict[str, Any] = {}
    
    def process_message(self, message: str) -> Dict:
        """
        Process user message and determine action
        Returns response with optional tool calls
        """
        # Simple intent detection (in production, use LLM)
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["create", "generate", "make", "build"]):
            if "presentation" in message_lower or "slides" in message_lower:
                return self._handle_presentation_request(message)
        
        if any(word in message_lower for word in ["chart", "graph", "visualization", "plot"]):
            return self._handle_chart_request(message)
        
        if any(word in message_lower for word in ["analyze", "structure", "plan"]):
            return self._handle_analysis_request(message)
        
        # General conversation
        return {
            "type": "message",
            "content": "I'm your Zain presentation assistant. I can help you:\n\n• Create presentations from outlines\n• Design individual slides with optimal layouts\n• Generate charts and visualizations\n• Analyze content and suggest structures\n• Apply Zain brand guidelines automatically\n\nWhat would you like to create?"
        }
    
    def _handle_presentation_request(self, message: str) -> Dict:
        """Handle presentation creation request"""
        return {
            "type": "tool_call",
            "tool": "analyze_content",
            "parameters": {
                "content": message,
                "audience": "business",
                "goal": "create_presentation"
            },
            "reasoning": "Analyzing your content to determine optimal slide structure and layouts..."
        }
    
    def _handle_chart_request(self, message: str) -> Dict:
        """Handle chart generation request"""
        # Extract data from message (simplified)
        return {
            "type": "tool_call",
            "tool": "generate_chart",
            "parameters": {
                "chart_type": "bar",
                "data": {"values": [85, 92, 78, 96]},
                "title": "Sample Chart",
                "labels": ["Q1", "Q2", "Q3", "Q4"]
            },
            "reasoning": "Generating chart based on your data..."
        }
    
    def _handle_analysis_request(self, message: str) -> Dict:
        """Handle content analysis request"""
        return {
            "type": "tool_call",
            "tool": "analyze_content",
            "parameters": {
                "content": message,
                "audience": "executive",
                "goal": "inform"
            },
            "reasoning": "Analyzing content structure and audience fit..."
        }
    
    def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute a tool and return results"""
        if tool_name == "create_slide":
            slide = self._create_slide(parameters)
            self.slides.append(slide)
            return {
                "type": "tool_result",
                "tool": tool_name,
                "result": f"Created {parameters['type']} slide: '{parameters.get('title', 'Untitled')}'",
                "slide": slide
            }
        
        elif tool_name == "generate_chart":
            chart_path = self._generate_chart(parameters)
            return {
                "type": "tool_result",
                "tool": tool_name,
                "result": f"Generated {parameters['chart_type']} chart: '{parameters['title']}'",
                "chart_path": chart_path
            }
        
        elif tool_name == "analyze_content":
            analysis = self._analyze_content(parameters)
            return {
                "type": "tool_result",
                "tool": tool_name,
                "result": "Analysis complete",
                "analysis": analysis
            }
        
        elif tool_name == "render_presentation":
            output_path = self._render_presentation(parameters)
            return {
                "type": "tool_result",
                "tool": tool_name,
                "result": "Presentation rendered successfully",
                "download_url": f"/download/{Path(output_path).name}"
            }
        
        return {"type": "error", "message": f"Unknown tool: {tool_name}"}
    
    def _create_slide(self, params: Dict) -> Dict:
        """Create a slide from parameters"""
        return {
            "type": params.get("type", "content"),
            "title": params.get("title", "Slide Title"),
            "content": params.get("content", []),
            "layout": params.get("layout", "bullets"),
            "gradient": params.get("gradient", "ultraviolet" if params.get("type") == "title" else "coraldawn")
        }
    
    def _generate_chart(self, params: Dict) -> str:
        """Generate a chart image (placeholder)"""
        # In production, use matplotlib/plotly to generate chart image
        chart_id = str(uuid.uuid4())[:8]
        return f"/charts/chart_{chart_id}.png"
    
    def _analyze_content(self, params: Dict) -> Dict:
        """Analyze content and suggest structure"""
        content = params.get("content", "")
        
        # Simple analysis (in production, use LLM)
        return {
            "suggested_slides": 5,
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "recommended_layouts": ["title", "big_number", "bullets", "section", "quote"],
            "audience_fit": "executive"
        }
    
    def _render_presentation(self, params: Dict) -> str:
        """Render slides to PPTX"""
        app_root = Path(__file__).parent.parent
        config_path = app_root / "config.json"
        output_path = app_root / "generated" / f"zain_chat_{self.conversation_id}.pptx"
        
        brand = BrandConfig(config_path)
        renderer = PPTXRenderer(brand)
        
        slides = params.get("slides", self.slides)
        for slide in slides:
            if slide["type"] == "title":
                slide["gradient"] = params.get("title_gradient", "ultraviolet")
            elif slide["type"] == "section":
                slide["gradient"] = params.get("section_gradient", "coraldawn")
        
        renderer.render_presentation(slides, output_path)
        return str(output_path)


@app.route('/api/chat/new', methods=['POST'])
def new_conversation():
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    conversations[conversation_id] = {
        "id": conversation_id,
        "orchestrator": AgentOrchestrator(conversation_id),
        "messages": [],
        "created_at": time.time()
    }
    return jsonify({
        "conversation_id": conversation_id,
        "message": "New conversation started. How can I help you create your presentation?"
    })


@app.route('/api/chat/<conversation_id>/message', methods=['POST'])
def send_message(conversation_id: str):
    """Send a message to the AI"""
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    data = request.json
    message = data.get("message", "")
    
    conv = conversations[conversation_id]
    orchestrator = conv["orchestrator"]
    
    # Store user message
    conv["messages"].append({"role": "user", "content": message})
    
    # Process message
    response = orchestrator.process_message(message)
    
    # Store assistant response
    conv["messages"].append({"role": "assistant", "content": response})
    
    return jsonify({
        "conversation_id": conversation_id,
        "response": response
    })


@app.route('/api/chat/<conversation_id>/tool', methods=['POST'])
def execute_tool(conversation_id: str):
    """Execute a tool call"""
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    data = request.json
    tool_name = data.get("tool")
    parameters = data.get("parameters", {})
    
    conv = conversations[conversation_id]
    orchestrator = conv["orchestrator"]
    
    result = orchestrator.execute_tool(tool_name, parameters)
    
    conv["messages"].append({"role": "tool", "content": result})
    
    return jsonify(result)


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get available tools"""
    return jsonify({"tools": TOOLS})


@app.route('/api/chat/<conversation_id>/slides', methods=['GET'])
def get_slides(conversation_id: str):
    """Get current slides in conversation"""
    if conversation_id not in conversations:
        return jsonify({"error": "Conversation not found"}), 404
    
    orchestrator = conversations[conversation_id]["orchestrator"]
    return jsonify({"slides": orchestrator.slides})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
