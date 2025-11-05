# GhostCommenter-X 🚀

An intelligent automation tool for forum engagement with AI-powered comment generation and self-learning capabilities.

## Features

- **AI Comment Generation**: Generate human-like comments using G4F (free) or OpenAI API
- **Adaptive Learning**: Train the AI by evaluating generated comments to improve quality
- **Smart Automation**: Intelligent post selection and timing randomization
- **Multiple Modes**: Infinite or limited comment sessions
- **Anti-Detection**: Human-like typing simulation and behavior patterns
- **Comment History**: Track commented threads to avoid duplicates

## Installation

### Prerequisites

- Python 3.8+
- Google Chrome (for Playwright)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GhostCommenter-X.git
cd GhostCommenter-X
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

4. Configure credentials:
```bash
cp config/.env.example config/.env
# Edit config/.env with your credentials
```

## Configuration

### Environment Variables

Create `config/.env` file:

```env
# OpenAI API (optional, only if using OpenAI provider)
OPENAI_API_KEY=your_api_key_here

# Saved credentials (optional)
LOGIN_USER_1=YourUsername
LOGIN_PASS_1=YourPassword
```

### AI Prompts

Edit `config/prompts.txt` to customize AI behavior. The file contains three prompt templates:
- `[TITLE_PROMPT]` - For generating thread titles
- `[CONTENT_PROMPT]` - For generating post content
- `[COMMENT_PROMPT]` - For generating comments (main use)

## Usage

### Basic Usage

1. Run the application:
```bash
python src/main.py
```

2. Configure settings in the GUI:
   - Select or enter login credentials
   - Set time intervals between comments
   - Choose AI provider (G4F is free and unlimited)
   - Select mode (Infinite or Limited)

3. Click **Start** to begin automation

### Training Mode

Improve AI quality through evaluation:

1. Load training mode from the menu
2. Import thread samples or generate comments
3. Rate comments (1-5 stars) based on:
   - Human-likeness
   - Relevance
   - Natural language
4. AI automatically learns from your ratings

## AI Providers

### G4F (Recommended for Free Use)
- No API key required
- Unlimited comments
- Uses GPT-4 models
- Install: `pip install g4f`

### OpenAI API
- Requires API key and credits
- More consistent quality
- Models: GPT-4, GPT-3.5-turbo

### Template Mode
- No AI required
- Uses predefined templates
- Good for testing

## Safety Features

- Cloudflare detection handling
- Random timing intervals
- Human-like typing simulation
- Browser fingerprint randomization
- Duplicate comment prevention

## Project Structure

```
GhostCommenter-X/
├── src/
│   ├── main.py                 # GUI application
│   ├── ai_generator.py         # AI comment generation
│   ├── browser_automation.py   # Playwright automation
│   ├── config_manager.py       # Configuration handling
│   ├── text_utils.py          # Text processing
│   └── training/              # Learning module
├── config/
│   ├── .env.example           # Example credentials
│   └── prompts.txt            # AI prompts
├── data/                      # User data (gitignored)
└── requirements.txt
```

## Requirements

See `requirements.txt` for full dependencies. Main packages:
- `patchright` - Browser automation
- `g4f` - Free GPT-4 access (optional)
- `openai` - OpenAI API (optional)
- `beautifulsoup4` - HTML parsing
- `python-dotenv` - Environment management

## Disclaimer

This tool is for educational purposes. Users are responsible for:
- Complying with target forum's Terms of Service
- Respecting rate limits and community guidelines
- Using automation ethically and responsibly

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- Issues: [GitHub Issues](https://github.com/yourusername/GhostCommenter-X/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/GhostCommenter-X/discussions)

## Changelog

### Version 1.0.0
- Initial release
- AI comment generation with G4F and OpenAI
- Self-learning training module
- Minimalist GUI interface
- Comment history tracking