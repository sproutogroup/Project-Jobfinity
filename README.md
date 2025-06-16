

A Python-based LinkedIn automation tool that combines web scraping with intelligent profile analysis using LLMs.

## Features

- **Profile Scraping**: Automated scraping of LinkedIn profiles based on search criteria
- **Intelligent Analysis**: LLM-powered analysis of profiles for lead qualification
- **Human-in-the-Loop**: Review and approve suggested actions before execution
- **Action Automation**: Support for sending connection requests and messages
- **Analytics**: Summary reports of actions taken and results

## Project Structure

```
LinkedIn_Leadgen_Agent/
├── src/
│   ├── linkedin_agent/
│   │   ├── browser/
│   │   │   └── selenium_manager.py    # Chrome WebDriver management
│   │   ├── config/
│   │   │   └── settings.py            # Configuration and selectors
│   │   ├── models/
│   │   │   └── types.py              # Data structures
│   │   ├── tools/
│   │   │   └── linkedin_tools.py     # Core scraping functions
│   │   └── workflow/
│   │       ├── states.py             # Workflow state definitions
│   │       ├── prompts.py            # LLM prompt templates
│   │       ├── nodes.py              # Workflow nodes
│   │       └── graph.py              # LangGraph workflow
│   ├── main.py                       # Profile scraping entry point
│   └── analyze_profiles.py           # Profile analysis entry point
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.9+
- Chrome browser with remote debugging enabled
- Google Gemini API key for LLM functionality
- LinkedIn account

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LinkedIn_Leadgen_Agent.git
cd LinkedIn_Leadgen_Agent
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings:
GEMINI_API_KEY=your_api_key_here
CHROME_DEBUG_PORT=9222
LINKEDIN_USERNAME=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
```

## Usage

### 1. Start Chrome with Remote Debugging

```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data"

# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="~/ChromeProfile"

# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir=~/ChromeProfile
```

### 2. Run Profile Scraping

```bash
python src/main.py
```

This will:
- Connect to your Chrome instance
- Search LinkedIn for profiles based on your criteria
- Save profile data to `linkedin_profiles.json`

### 3. Run Profile Analysis

```bash
python src/analyze_profiles.py
```

This will:
- Load scraped profiles
- Analyze each profile using LLM
- Suggest actions (message/connect/skip)
- Ask for your approval before taking action
- Generate a summary report

## Docker Support

1. Build the image:
```bash
docker-compose build
```

2. Run the container:
```bash
docker-compose up
```

## Security Notes

- Never commit your `.env` file or API keys
- Use LinkedIn automation responsibly and within their terms of service
- Implement appropriate delays between actions to avoid rate limiting

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.