# Intelligent Research & Report Generator Agent

An autonomous AI agent that conducts comprehensive research on any topic and generates detailed, well-structured reports.

## 🎯 Problem Statement

Manual research is time-consuming, inconsistent, and often incomplete. This agent autonomously:
- Researches topics across multiple sources
- Synthesizes information intelligently
- Generates comprehensive, well-structured reports
- Adapts research depth based on query complexity

## 🚀 Features

- **Autonomous Research**: Automatically searches and gathers information from multiple sources
- **Intelligent Synthesis**: Combines findings from different sources into coherent insights
- **Smart Report Generation**: Creates well-formatted reports with citations and structure
- **Multi-step Reasoning**: Plans research strategy and executes systematically
- **Source Tracking**: Maintains references and citations for all information

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
└── main.py                         # CLI entry point
```

## 🛠️ Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. Run the agent:
```bash
python main.py
```

## 📝 Usage

```python
from src.agent.research_agent import ResearchAgent

agent = ResearchAgent()
report = agent.research("Impact of AI on healthcare")
print(report)
```

## 🔧 Technologies

- **LangChain**: Agent framework and orchestration
- **Google Gemini**: LLM for reasoning and generation (free API available)
- **Tavily/DuckDuckGo**: Web search capabilities
- **BeautifulSoup**: Web content extraction
- **Markdown**: Report formatting
