#!/usr/bin/env python3
"""
Zain PPTX Generator
AI-powered presentation generator with Zain branding
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from brand_builder import BrandConfig, PPTXAssembler
from outline_parser import OutlineParser, extract_from_pdf
from slide_agents import SlideAgentSpawner, SlideAgentCoordinator


def generate_presentation(outline_text, output_path, use_agents=True):
    """
    Main generation function
    
    Args:
        outline_text: Raw outline text
        output_path: Where to save the PPTX
        use_agents: Whether to use sub-agents for parallel generation
    """
    # Parse outline
    parser = OutlineParser()
    slides_data = parser.parse_text(outline_text)
    parser.validate_structure()
    
    print(f"Parsed {len(slides_data)} slides from outline")
    
    # Load brand config
    config_path = Path(__file__).parent / "config.json"
    brand = BrandConfig(config_path)
    
    if use_agents and len(slides_data) > 5:
        # Use sub-agent architecture for large decks
        print(f"Using sub-agent architecture for {len(slides_data)} slides...")
        
        output_dir = Path(output_path).parent / "generated_slides"
        output_dir.mkdir(exist_ok=True)
        
        spawner = SlideAgentSpawner(config_path)
        coordinator = SlideAgentCoordinator(spawner)
        
        plan = coordinator.coordinate_generation(parser, output_dir, batch_size=3)
        print(f"Spawned {len(plan['jobs'])} jobs across {plan['batches']} batches")
        
        # NOTE: Actual agent spawning requires Clawd integration
        # For now, we process directly
        print("(Direct mode - agent integration pending)")
        assembler = PPTXAssembler(brand)
        result_path = assembler.create_presentation(slides_data, output_path)
        
    else:
        # Direct generation for small decks
        print("Using direct generation...")
        assembler = PPTXAssembler(brand)
        result_path = assembler.create_presentation(slides_data, output_path)
    
    print(f"Presentation saved to: {result_path}")
    return result_path


def main():
    parser = argparse.ArgumentParser(description='Generate Zain-branded PowerPoint presentations')
    parser.add_argument('outline', help='Path to outline file (.txt or .md)')
    parser.add_argument('-o', '--output', default='output.pptx', help='Output PPTX file')
    parser.add_argument('--direct', action='store_true', help='Skip agents, generate directly')
    
    args = parser.parse_args()
    
    # Read outline
    outline_path = Path(args.outline)
    if not outline_path.exists():
        print(f"Error: Outline file not found: {outline_path}")
        sys.exit(1)
    
    with open(outline_path, 'r', encoding='utf-8') as f:
        outline_text = f.read()
    
    # Generate
    try:
        generate_presentation(
            outline_text, 
            args.output, 
            use_agents=not args.direct
        )
    except Exception as e:
        print(f"Error generating presentation: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
