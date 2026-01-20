# 🤖 Intelligent Research & Report Generator Agent

An autonomous AI agent that conducts comprehensive research on any topic and generates detailed, well-structured reports.

## 🎯 Problem Statement

Manual research is time-consuming, inconsistent, and often incomplete. This agent autonomously:
- Researches topics across multiple sources
- Synthesizes information intelligently
- Generates comprehensive, well-structured reports
- Adapts research depth based on query complexity

## 🚀 Features

- **🖥️ Interactive Web UI**: Beautiful, modern interface with real-time progress tracking
- **Autonomous Research**: Automatically searches and gathers information from multiple sources
- **Intelligent Synthesis**: Combines findings from different sources into coherent insights
- **Smart Report Generation**: Creates well-formatted reports with citations and structure
- **Multi-step Reasoning**: Plans research strategy and executes systematically
- **Source Tracking**: Maintains references and citations for all information
- **Multiple Interfaces**: Choose between Web UI or CLI based on your preference

## 📁 Project Structure

```
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── research_agent.py      # Main agent orchestrator
│   │   └── planner.py             # Research planning logic
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── web_researcher.py      # Web search and content extraction
│   │   ├── synthesizer.py         # Information synthesis
│   │   └── report_generator.py    # Report creation
│   └── utils/
│       ├── __init__.py
│       └── config.py              # Configuration management
├── outputs/                        # Generated reports
├── .env.example                    # Environment variables template
├── requirements.txt                # Python dependencies
├── app.py                          # Web UI (Streamlit)
├── main.py                         # CLI entry point
├── run_ui.bat                      # Windows launcher for UI
└── run_ui.sh                       # Linux/Mac launcher for UI
```

## 🛠️ Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GOOGLE_API_KEY (for Gemini)
# - TAVILY_API_KEY (for web search)
```

3. **Run the application:**

### Option 1: Web UI (Recommended) 🌐
```bash
# Windows
run_ui.bat

# Linux/Mac
chmod +x run_ui.sh
./run_ui.sh

# Or directly:
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Option 2: Command Line Interface 💻
```bash
python main.py "Your research topic here"

# With options:
python main.py "Impact of AI on healthcare" --depth deep --format html
```

## 📝 Usage Examples

### Web UI
1. Open the application in your browser
2. Enter your research topic
3. Select research depth (Auto/Shallow/Medium/Deep)
4. Click "Start Research"
5. View results and download reports

### CLI
```bash
# Basic research
python main.py "Impact of AI on healthcare"

# Deep research with HTML output
python main.py "Climate change solutions" --depth deep --format html

# Quick research without saving
python main.py "Python best practices" --depth shallow --no-save
```

### Python API
```python
from src.agent.research_agent import ResearchAgent

agent = ResearchAgent()
result = agent.research("Impact of AI on healthcare", depth="medium")
print(result['report'])
print(f"Report saved to: {result['report_path']}")
```

## 🔧 Technologies

- **LangChain**: Agent framework and orchestration
- **Google Gemini**: LLM for reasoning and generation (free API available)
- **Tavily/DuckDuckGo**: Web search capabilities
- **BeautifulSoup**: Web content extraction
- **Markdown**: Report formatting
