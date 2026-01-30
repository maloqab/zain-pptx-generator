"""
AI Slide Planner
Uses sub-agents to analyze content and plan optimal slide structure
"""

import json
from typing import List, Dict


class SlidePlanner:
    """
    Plans presentation structure using AI reasoning
    """
    
    def __init__(self, sessions_spawn_func=None):
        """
        Args:
            sessions_spawn_func: Function to spawn sub-agents (sessions_spawn)
        """
        self.spawn_agent = sessions_spawn_func
    
    def create_analysis_prompt(self, outline_text: str) -> str:
        """Create prompt for the AI analyst agent"""
        return f"""You are an expert presentation designer and content strategist.

Your task: Analyze the following presentation outline and create an optimal slide plan.

## INPUT OUTLINE:
{outline_text}

## YOUR TASK:

1. **Understand the Content**
   - What is the main message/purpose?
   - Who is the audience?
   - What is the narrative arc? (setup → problem → solution → conclusion)

2. **Design Slide Structure**
   - Break content into logical slides (not too dense, not too sparse)
   - Choose appropriate layout for each slide based on content type:
     * `bullets` - Standard bullet points (most common)
     * `two_column` - When comparing two things or have many points
     * `big_number` - When highlighting a key statistic or achievement
     * `quote` - For testimonials, key insights, or impactful statements
   
3. **Enhance Content**
   - Rewrite bullet points to be punchy and professional
   - Add context where needed
   - Ensure each slide has a clear takeaway

4. **Choose Visual Design**
   - Select appropriate gradient for title/section slides:
     * `ultraviolet` - Professional, corporate (default)
     * `coraldawn` - Energetic, warm
     * `limelagoon` - Fresh, innovative
     * `midnightsky` - Sophisticated, premium
     * `azurewaters` - Calm, trustworthy
     * `magentafade` - Bold, dynamic
     * `twilightmist` - Creative, modern
     * `jadehorizon` - Growth, sustainability

## OUTPUT FORMAT:

Return a JSON object with this exact structure:

```json
{{
  "analysis": {{
    "purpose": "Brief description of presentation purpose",
    "audience": "Target audience",
    "key_message": "The one thing audience should remember"
  }},
  "slides": [
    {{
      "type": "title",
      "title": "Main Presentation Title",
      "subtitle": "Compelling subtitle",
      "gradient": "ultraviolet"
    }},
    {{
      "type": "section",
      "title": "Section Name",
      "gradient": "coraldawn"
    }},
    {{
      "type": "content",
      "title": "Slide Title",
      "layout": "bullets",
      "content": [
        "First bullet point - rewritten to be punchy",
        "Second bullet point - clear and actionable",
        "Third bullet point"
      ]
    }},
    {{
      "type": "content",
      "title": "Key Achievement",
      "layout": "big_number",
      "content": [
        "47% Growth",
        "Exceeded target by 12%",
        "Highest quarterly performance in 5 years"
      ]
    }}
  ]
}}
```

## RULES:
- Maximum 6-8 content slides (not counting title/sections)
- Each slide should have 3-5 bullet points max
- Use `big_number` layout for slides with impressive stats
- Use `quote` layout for customer testimonials or insights
- Use `two_column` when comparing before/after or two categories
- Choose gradients that match the emotional tone of the content
- Rewrite all content to be presentation-ready (not raw notes)

Respond ONLY with the JSON object, no other text.
"""
    
    async def plan_slides(self, outline_text: str) -> List[Dict]:
        """
        Use AI to plan and structure slides
        
        Returns list of slide data dicts ready for rendering
        """
        if self.spawn_agent is None:
            # Fallback: parse outline simply without AI
            return self._fallback_plan(outline_text)
        
        # Spawn AI agent to analyze and plan
        prompt = self.create_analysis_prompt(outline_text)
        
        # For now, return fallback (implement agent spawning when sessions_spawn available)
        return self._fallback_plan(outline_text)
    
    def _fallback_plan(self, outline_text: str) -> List[Dict]:
        """
        Simple fallback that parses outline without AI
        Used when agent spawning is not available
        """
        from outline_parser import OutlineParser
        
        parser = OutlineParser()
        basic_slides = parser.parse_text(outline_text)
        
        # Enhance basic structure with some intelligence
        enhanced_slides = []
        for slide in basic_slides:
            enhanced = slide.copy()
            
            if slide['type'] == 'content':
                # Detect if this should be big_number layout
                content_str = ' '.join(slide.get('content', []))
                if any(c.isdigit() for c in content_str) and len(slide.get('content', [])) <= 3:
                    # Check if it looks like a stat slide
                    if '%' in content_str or '$' in content_str or 'M' in content_str or 'K' in content_str:
                        enhanced['layout'] = 'big_number'
                    else:
                        enhanced['layout'] = 'bullets'
                else:
                    enhanced['layout'] = 'bullets'
                
                # Detect if content is long and should be two_column
                if len(slide.get('content', [])) > 5:
                    enhanced['layout'] = 'two_column'
            
            # Set default gradients
            if slide['type'] == 'title':
                enhanced['gradient'] = 'ultraviolet'
            elif slide['type'] == 'section':
                enhanced['gradient'] = 'coraldawn'
            
            enhanced_slides.append(enhanced)
        
        return enhanced_slides
    
    def analyze_content_depth(self, outline_text: str) -> Dict:
        """
        Analyze how much content needs expansion
        Returns dict with recommendations
        """
        lines = outline_text.strip().split('\n')
        bullets = [l for l in lines if l.strip().startswith('-') or l.strip().startswith('•')]
        
        return {
            'total_lines': len(lines),
            'bullet_count': len(bullets),
            'needs_expansion': len(bullets) < 10,
            'estimated_slides': max(3, len(bullets) // 4 + 1)
        }


class ContentEnricher:
    """
    Enriches sparse content with AI-generated context
    """
    
    def __init__(self, sessions_spawn_func=None):
        self.spawn_agent = sessions_spawn_func
    
    def create_enrichment_prompt(self, topic: str, existing_points: List[str]) -> str:
        """Create prompt to expand on sparse content"""
        points_text = '\n'.join([f'- {p}' for p in existing_points])
        
        return f"""You are a business presentation expert.

Topic: {topic}
Existing points:
{points_text}

Expand these points into 4-5 compelling, professional bullet points suitable for a C-suite presentation.
Each bullet should:
- Start with a strong action verb
- Include specific impact or metric where possible
- Be concise (one sentence max)
- Focus on business value

Respond as a JSON array of strings.
"""
    
    async def enrich_slide_content(self, title: str, existing_points: List[str]) -> List[str]:
        """Use AI to expand sparse bullet points"""
        if not existing_points or len(existing_points) < 2:
            # Spawn agent to generate content
            pass  # Implement when sessions_spawn available
        
        return existing_points


def create_slide_plan_with_agents(outline_text: str, sessions_spawn_func=None) -> List[Dict]:
    """
    Main entry point: Create intelligent slide plan
    
    Uses sub-agents to:
    1. Analyze content and audience
    2. Structure narrative flow
    3. Choose optimal layouts
    4. Enrich sparse content
    5. Select appropriate visual design
    
    Returns slide data ready for PPTX rendering
    """
    planner = SlidePlanner(sessions_spawn_func)
    
    # Analyze content depth first
    analysis = planner.analyze_content_depth(outline_text)
    
    # Plan slides
    slides = planner.plan_slides(outline_text)
    
    return slides
