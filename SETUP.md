# Setup Guide

## Step-by-Step Setup Instructions

### Step 1: Install Python Dependencies

Make sure you have Python 3.8+ installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

### Step 2: Get API Keys

#### Google Gemini API Key (Required - FREE!)
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy the API key (starts with "AIza...")

**Note:** Gemini API is free to use with generous rate limits - perfect for this project!

#### Tavily API Key (Recommended for better search)
1. Go to https://tavily.com
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes generous usage limits

### Step 3: Configure Environment Variables

1. Copy the example environment file:
```bash
copy env.example .env
```

2. Edit `.env` and add your API keys:
```
GEMINI_API_KEY=AIza-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

**Note:** The agent requires Gemini API key. Tavily is optional but provides better web search results (DuckDuckGo will be used as fallback).

### Step 4: Test the Installation

Run a quick test:
```bash
python example.py
```

Or use the CLI:
```bash
python main.py "Introduction to machine learning" --depth shallow
```

## Usage Examples

### Basic Usage (CLI)
```bash
# Simple research
python main.py "Impact of AI on healthcare"

# Deep research
python main.py "Climate change solutions" --depth deep

# Quick research without saving
python main.py "Python best practices" --depth shallow --no-save
```

### Programmatic Usage
```python
from src.agent.research_agent import ResearchAgent

agent = ResearchAgent()
result = agent.research("Your research topic here")
print(result['report'])
```

## Troubleshooting

### Issue: "GEMINI_API_KEY is required"
- Make sure you created a `.env` file
- Check that the Gemini API key is correctly set in `.env`
- Ensure `.env` is in the project root directory
- Get your free API key from https://makersuite.google.com/app/apikey

### Issue: "No research results found"
- Check your internet connection
- Verify Tavily API key is set (or DuckDuckGo will be used as fallback)
- Try a different search query

### Issue: Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

## Project Structure

```
├── src/
│   ├── agent/              # Agent orchestration
│   │   ├── research_agent.py    # Main agent
│   │   └── planner.py           # Research planning
│   ├── modules/            # Core modules
│   │   ├── web_researcher.py    # Web search
│   │   ├── synthesizer.py       # Information synthesis
│   │   └── report_generator.py  # Report creation
│   └── utils/              # Utilities
│       └── config.py            # Configuration
├── outputs/                # Generated reports
├── main.py                 # CLI interface
├── example.py              # Usage example
└── requirements.txt        # Dependencies
```

## Next Steps

1. ✅ Complete setup
2. ✅ Run your first research query
3. ✅ Explore different research depths
4. ✅ Customize the agent for your needs
5. ✅ Add additional features (PDF export, email reports, etc.)
