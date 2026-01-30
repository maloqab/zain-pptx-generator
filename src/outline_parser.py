import re
from pathlib import Path

class OutlineParser:
    """Parses text/PDF outlines into structured slide data"""
    
    def __init__(self):
        self.slides = []
    
    def parse_text(self, text):
        """Parse plain text outline into slide structure"""
        lines = text.strip().split('\n')
        current_slide = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Title slide pattern: # Title or Title: subtitle
            if line.startswith('# ') or line.startswith('## '):
                if current_slide:
                    self.slides.append(current_slide)
                
                title = line.lstrip('#').strip()
                current_slide = {
                    'type': 'title',
                    'title': title,
                    'subtitle': '',
                    'content': []
                }
            
            # Section divider pattern: --- or ## Section Name
            elif line.startswith('---') or (line.startswith('## ') and 'section' in line.lower()):
                if current_slide:
                    self.slides.append(current_slide)
                
                section_title = line.lstrip('#').strip().replace('Section:', '').strip()
                current_slide = {
                    'type': 'section',
                    'title': section_title,
                    'content': []
                }
            
            # Bullet point
            elif line.startswith('-') or line.startswith('•'):
                if current_slide is None:
                    # Start a content slide if no slide active
                    current_slide = {
                        'type': 'content',
                        'title': 'Content',
                        'content': []
                    }
                
                bullet = line.lstrip('-•').strip()
                if current_slide['type'] == 'content':
                    current_slide['content'].append(bullet)
                else:
                    # Convert to content slide if bullets added
                    current_slide['type'] = 'content'
                    current_slide['content'] = [bullet]
            
            # Subtitle or regular text
            else:
                if current_slide and current_slide['type'] == 'title' and not current_slide['subtitle']:
                    current_slide['subtitle'] = line
                elif current_slide and current_slide['type'] == 'content':
                    current_slide['content'].append(line)
        
        # Add final slide
        if current_slide:
            self.slides.append(current_slide)
        
        return self.slides
    
    def parse_markdown(self, md_text):
        """Parse markdown-style outline"""
        return self.parse_text(md_text)  # Similar logic, can extend
    
    def validate_structure(self):
        """Ensure valid slide structure"""
        if not self.slides:
            return False
        
        # Ensure first slide is title
        if self.slides[0]['type'] != 'title':
            self.slides.insert(0, {
                'type': 'title',
                'title': 'Presentation',
                'subtitle': ''
            })
        
        return True
    
    def get_slide_count(self):
        return len(self.slides)
    
    def get_slide(self, index):
        """Get specific slide data"""
        if 0 <= index < len(self.slides):
            return self.slides[index]
        return None
    
    def split_for_agents(self, batch_size=3):
        """Split slides into batches for parallel agent processing"""
        batches = []
        for i in range(0, len(self.slides), batch_size):
            batch = self.slides[i:i + batch_size]
            batches.append({
                'batch_id': i // batch_size,
                'start_index': i,
                'slides': batch
            })
        return batches


def extract_from_pdf(pdf_path):
    """Extract text from PDF outline"""
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        parser = OutlineParser()
        return parser.parse_text(text)
    except ImportError:
        print("PyPDF2 not installed. Install with: pip install PyPDF2")
        return []


# Example usage patterns
EXAMPLE_OUTLINE = """
# Q4 2025 Strategy Review
Driving Growth Through Innovation

---

## Market Analysis

- Revenue up 15% YoY
- New customer acquisition: 2,400
- Market share expanded to 18%

---

## Product Highlights

- Launch of Zain Plus
- 5G coverage now at 85%
- Digital transformation complete

---

## Financial Summary

- Operating profit: $450M
- EBITDA margin: 42%
- Capex investment: $120M

---

## Next Steps

- Expand 5G to rural areas
- Launch AI-powered customer service
- Strategic partnerships in fintech
"""
