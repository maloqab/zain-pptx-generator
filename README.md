# Zain PPTX Generator

AI-powered presentation generator with authentic Zain branding.

## Features

- **Zain Brand Compliance**: Uses official Zain fonts, colors, and logos
- **Sub-Agent Architecture**: Parallel slide generation for large decks (10+ slides)
- **Multiple Input Formats**: Text, Markdown, or PDF outlines
- **Professional Layouts**: Title, section divider, and content slides

## Brand Assets Included

- **Fonts**: Zain Family (Light, Regular, Bold, Black, Italic variants)
- **Logos**: English and Arabic, black and white variants
- **Colors**: Primary purple (#6E2C91), secondary pink (#E6007E), accent cyan (#00A9CE)
- **Gradients**: 8 official Zain gradient backgrounds

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Generate from text outline
python generate.py outline.txt -o presentation.pptx

# Direct generation (skip sub-agents)
python generate.py outline.txt -o presentation.pptx --direct
```

### Python API

```python
from generate import generate_presentation

outline = """
# Q4 Strategy Review
Quarterly Business Report

## Market Performance
- Revenue up 15%
- New customers: 2,400
- Market share: 18%
"""

generate_presentation(outline, "output.pptx")
```

## Outline Format

```markdown
# Presentation Title
Subtitle goes here

---

## Section Title

- Bullet point one
- Bullet point two
- Bullet point three

---

## Next Section

- More content
- More bullets
```

## Web Interface (Coming Soon)

Upload outlines via web UI, download generated PPTX files.

## Project Structure

```
zain-pptx-generator/
├── config.json           # Brand configuration
├── generate.py           # Main entry point
├── brand-assets/         # Zain logos, fonts, colors
├── templates/            # PPTX templates
├── src/
│   ├── brand_builder.py  # Slide building logic
│   ├── outline_parser.py # Outline parsing
│   └── slide_agents.py   # Sub-agent coordination
└── generated/            # Output files
```

## License

Internal use only. Zain brand assets are proprietary.
