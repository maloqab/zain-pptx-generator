from flask import Flask, render_template, request, send_file, jsonify
import os
import uuid
import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pptx_renderer import BrandConfig, PPTXRenderer
from ai_planner import create_slide_plan_with_agents, SlidePlanner

app = Flask(__name__)
app_root = Path(__file__).parent.parent
app.config['UPLOAD_FOLDER'] = app_root / 'uploads'
app.config['OUTPUT_FOLDER'] = app_root / 'generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure folders exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

# Track generation status
generation_status = {}


@app.route('/')
def index():
    """Home page with upload form"""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Handle outline submission and generate PPTX with AI planning"""
    try:
        # Get inputs
        outline_text = request.form.get('outline', '')
        title_gradient = request.form.get('title_gradient', 'ultraviolet')
        section_gradient = request.form.get('section_gradient', 'coraldawn')
        use_ai = request.form.get('use_ai', 'true') == 'true'
        
        if 'outline_file' in request.files:
            file = request.files['outline_file']
            if file.filename:
                outline_text = file.read().decode('utf-8')
        
        if not outline_text.strip():
            return jsonify({'error': 'No outline provided'}), 400
        
        # Generate job ID
        job_id = str(uuid.uuid4())[:8]
        output_filename = f"zain_presentation_{job_id}.pptx"
        output_path = Path(app.config['OUTPUT_FOLDER']) / output_filename
        
        # Update status
        generation_status[job_id] = {'status': 'planning', 'progress': 10}
        
        # Step 1: AI Planning (if enabled)
        if use_ai:
            # For now, use the intelligent fallback
            # In future, this will spawn sub-agents
            planner = SlidePlanner()
            slides_data = planner._fallback_plan(outline_text)
            
            # Apply user gradient selections
            for slide in slides_data:
                if slide['type'] == 'title':
                    slide['gradient'] = title_gradient
                elif slide['type'] == 'section':
                    slide['gradient'] = section_gradient
        else:
            # Basic parsing without AI
            from outline_parser import OutlineParser
            parser = OutlineParser()
            slides_data = parser.parse_text(outline_text)
            for slide in slides_data:
                if slide['type'] == 'title':
                    slide['gradient'] = title_gradient
                elif slide['type'] == 'section':
                    slide['gradient'] = section_gradient
                elif slide['type'] == 'content':
                    slide['layout'] = 'bullets'
        
        generation_status[job_id] = {'status': 'rendering', 'progress': 50}
        
        # Step 2: Render to PPTX
        config_path = app_root / "config.json"
        brand = BrandConfig(config_path)
        renderer = PPTXRenderer(brand)
        renderer.render_presentation(slides_data, output_path)
        
        generation_status[job_id] = {'status': 'complete', 'progress': 100}
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'slide_count': len(slides_data),
            'download_url': f'/download/{output_filename}',
            'job_id': job_id
        })
        
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/status/<job_id>')
def get_status(job_id):
    """Get generation status for progress tracking"""
    status = generation_status.get(job_id, {'status': 'unknown', 'progress': 0})
    return jsonify(status)


@app.route('/download/<filename>')
def download(filename):
    """Serve generated PPTX file"""
    file_path = Path(app.config['OUTPUT_FOLDER']) / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404


@app.route('/api/example-outline')
def example_outline():
    """Return example outline"""
    return jsonify({
        'outline': """# Q4 2025 Strategy Review
Driving Growth Through Digital Innovation

## Market Performance

- Revenue increased 15% year-over-year to $1.2B
- Customer base expanded by 2.4M subscribers
- 5G coverage now reaches 85% of population
- Market share grew from 16% to 18%

## Financial Highlights

- Operating profit: $450M (up 12% YoY)
- EBITDA margin improved to 42%
- Free cash flow: $280M
- Dividend payout maintained at 65%

## Product Innovation

- Zain Plus loyalty program: 3M+ members
- AI-powered customer service launched
- Fintech partnership with regional banks
- IoT solutions for enterprise clients

## Looking Ahead to 2026

- Expand 5G to rural and remote areas
- Launch super-app for digital services
- Enter fintech with Zain Pay
- Achieve carbon neutrality by 2030
"""
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
