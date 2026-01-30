"""
Sub-agent spawner for parallel slide generation
Each slide gets its own agent to avoid context overload on long decks
"""

import json
import uuid
from pathlib import Path

class SlideAgentSpawner:
    """Spawns sub-agents to generate slides in parallel"""
    
    def __init__(self, brand_config_path="config.json"):
        self.brand_config_path = brand_config_path
        self.jobs = {}
    
    def create_slide_generation_prompt(self, slide_data, slide_index, total_slides):
        """Create prompt for a single slide agent"""
        
        slide_type = slide_data.get('type', 'content')
        title = slide_data.get('title', '')
        content = slide_data.get('content', [])
        
        prompt = f"""You are a presentation designer for Zain, a telecommunications company.

Generate slide {slide_index + 1} of {total_slides} for a PowerPoint presentation.

SLIDE TYPE: {slide_type}
TITLE: {title}

"""
        
        if slide_type == 'title':
            subtitle = slide_data.get('subtitle', '')
            prompt += f"SUBTITLE: {subtitle}\n\n"
            prompt += """INSTRUCTIONS:
1. Create a compelling title slide
2. Use professional, confident language
3. The subtitle should expand on the main title
4. Keep it concise and impactful

OUTPUT FORMAT (JSON):
{
  "type": "title",
  "title": "Main Title Text",
  "subtitle": "Subtitle Text"
}
"""
        
        elif slide_type == 'section':
            prompt += """INSTRUCTIONS:
1. This is a section divider slide
2. Create a clear, bold section title
3. Keep it short - 2-4 words maximum

OUTPUT FORMAT (JSON):
{
  "type": "section",
  "title": "Section Name"
}
"""
        
        else:  # content slide
            content_text = "\n".join([f"- {c}" for c in content]) if isinstance(content, list) else content
            prompt += f"CONTENT POINTS:\n{content_text}\n\n"
            prompt += """INSTRUCTIONS:
1. Transform these points into clear, professional bullet points
2. Each bullet should be one concise sentence
3. Use action verbs and specific metrics where possible
4. Maximum 5 bullet points per slide
5. If content is sparse, expand with relevant context

OUTPUT FORMAT (JSON):
{
  "type": "content",
  "title": "Slide Title",
  "content": [
    "First bullet point",
    "Second bullet point",
    "Third bullet point"
  ]
}
"""
        
        prompt += """
BRAND GUIDELINES:
- Tone: Professional, innovative, confident
- Language: Clear, concise, action-oriented
- Avoid: Jargon, passive voice, overly long sentences

Respond ONLY with the JSON object, no other text.
"""
        
        return prompt
    
    def spawn_slide_agent(self, slide_data, slide_index, total_slides, output_dir):
        """
        Spawn a sub-agent to generate a single slide
        
        Returns job_id for tracking
        """
        job_id = str(uuid.uuid4())[:8]
        prompt = self.create_slide_generation_prompt(slide_data, slide_index, total_slides)
        
        output_file = Path(output_dir) / f"slide_{slide_index:03d}.json"
        
        # Store job info
        self.jobs[job_id] = {
            'slide_index': slide_index,
            'status': 'pending',
            'output_file': output_file
        }
        
        # The actual spawning would happen here via sessions_spawn
        # For now, we prepare the structure
        return job_id, prompt, output_file
    
    def spawn_batch(self, slides_batch, start_index, total_slides, output_dir):
        """Spawn agents for a batch of slides"""
        batch_jobs = []
        
        for i, slide in enumerate(slides_batch):
            slide_index = start_index + i
            job_id, prompt, output_file = self.spawn_slide_agent(
                slide, slide_index, total_slides, output_dir
            )
            batch_jobs.append({
                'job_id': job_id,
                'slide_index': slide_index,
                'prompt': prompt,
                'output_file': output_file
            })
        
        return batch_jobs


class SlideAgentCoordinator:
    """Coordinates multiple slide agents and assembles results"""
    
    def __init__(self, spawner):
        self.spawner = spawner
        self.results = {}
    
    def coordinate_generation(self, outline_parser, output_dir, batch_size=3):
        """
        Main coordination logic
        
        1. Split outline into batches
        2. Spawn agents for each batch
        3. Collect results
        4. Assemble final presentation
        """
        batches = outline_parser.split_for_agents(batch_size)
        total_slides = outline_parser.get_slide_count()
        
        all_jobs = []
        
        for batch in batches:
            jobs = self.spawner.spawn_batch(
                batch['slides'], 
                batch['start_index'], 
                total_slides, 
                output_dir
            )
            all_jobs.extend(jobs)
        
        return {
            'total_slides': total_slides,
            'batches': len(batches),
            'jobs': all_jobs,
            'output_dir': output_dir
        }
    
    def collect_results(self, job_results):
        """Collect and order slide results from agents"""
        slides = []
        
        # Sort by slide index
        sorted_results = sorted(job_results, key=lambda x: x['slide_index'])
        
        for result in sorted_results:
            if 'generated_slide' in result:
                slides.append(result['generated_slide'])
        
        return slides
