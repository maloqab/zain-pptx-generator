from flask import Flask, render_template, request, send_file, jsonify
import os
import uuid
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from src.brand_builder import BrandConfig, PPTXAssembler
from src.outline_parser import OutlineParser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'generated'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure folders exist
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

@app.route('/')
def index():
    """Home page with upload form"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handle outline submission and generate PPTX"""
    try:
        # Get outline from form or file
        outline_text = request.form.get('outline', '')
        
        if 'outline_file' in request.files:
            file = request.files['outline_file']
            if file.filename:
                outline_text = file.read().decode('utf-8')
        
        if not outline_text.strip():
            return jsonify({'error': 'No outline provided'}), 400
        
        # Parse outline
        parser = OutlineParser()
        slides_data = parser.parse_text(outline_text)
        parser.validate_structure()
        
        if not slides_data:
            return jsonify({'error': 'Could not parse outline'}), 400
        
        # Generate unique filename
        job_id = str(uuid.uuid4())[:8]
        output_filename = f"zain_presentation_{job_id}.pptx"
        output_path = Path(app.config['OUTPUT_FOLDER']) / output_filename
        
        # Load brand config and generate
        config_path = Path(__file__).parent / "scripts" / "config.json"
        brand = BrandConfig(config_path)
        assembler = PPTXAssembler(brand)
        assembler.create_presentation(slides_data, output_path)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'slide_count': len(slides_data),
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """Serve generated PPTX file"""
    file_path = Path(app.config['OUTPUT_FOLDER']) / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/example-outline')
def example_outline():
    """Return example outline for testing"""
    return jsonify({
        'outline': """# Q4 2025 Strategy Review
Driving Growth Through Digital Innovation

## Market Analysis

- Revenue increased 15% year-over-year to $1.2B
- Customer base expanded by 2.4M subscribers
- 5G coverage now reaches 85% of population
- Market share grew from 16% to 18%

## Financial Performance

- Operating profit: $450M (up 12% YoY)
- EBITDA margin improved to 42%
- Free cash flow: $280M
- Dividend payout maintained at 65%

## Product Innovation

- Zain Plus loyalty program: 3M+ members
- AI-powered customer service launched
- Fintech partnership with regional banks
- IoT solutions for enterprise clients

## 2026 Strategic Priorities

- Expand 5G to rural and remote areas
- Launch super-app for digital services
- Enter fintech with Zain Pay
- Achieve carbon neutrality by 2030
"""
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
