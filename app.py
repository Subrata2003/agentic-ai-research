"""Interactive Web UI for the Intelligent Research Agent"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.research_agent import ResearchAgent
from src.utils.config import Config

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        background-color: #000000;
    }
    .stApp {
        background-color: #000000;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
    }
    [data-testid="stHeader"] {
        background-color: #000000;
    }
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 10px;
        border: none;
        font-size: 16px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(76,175,80,0.4);
    }
    .report-container {
        background-color: #1a1a1a;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(255,255,255,0.1);
        margin-top: 1rem;
        color: #e0e0e0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-card h2, .metric-card p {
        color: white;
    }
    .info-box {
        background-color: #1a2332;
        border-left: 5px solid #2196F3;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #e0e0e0;
    }
    .info-box h2 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        color: #64B5F6;
    }
    .info-box h3 {
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
        color: #64B5F6;
    }
    .info-box p {
        margin-top: 0;
        margin-bottom: 1rem;
        color: #e0e0e0;
    }
    .info-box ul {
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
        padding-left: 1.5rem;
    }
    .info-box li {
        margin-bottom: 0.4rem;
        color: #e0e0e0;
    }
    .success-box {
        background-color: #1a2e1a;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #e0e0e0;
    }
    .success-box h3 {
        color: #81C784;
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
    /* Make all text visible on black background */
    p, span, div, label {
        color: #e0e0e0;
    }
    h2, h3, h4, h5, h6 {
        color: #ffffff;
    }
    /* Style markdown content */
    .stMarkdown {
        color: #e0e0e0;
    }
    /* Horizontal rules */
    hr {
        border-color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_results' not in st.session_state:
    st.session_state.research_results = None
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'research_history' not in st.session_state:
    st.session_state.research_history = []

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 AI Research Assistant")
    st.markdown('<p style="color: #b0b0b0; font-style: italic;">Autonomous research powered by AI - Get comprehensive reports in seconds</p>', unsafe_allow_html=True)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Reset"):
        st.session_state.research_results = None
        st.rerun()

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Research settings
    st.subheader("Research Settings")
    depth = st.selectbox(
        "Research Depth",
        options=["Auto", "Shallow", "Medium", "Deep"],
        help="Auto: AI decides based on topic complexity\nShallow: Quick overview\nMedium: Balanced depth\nDeep: Comprehensive analysis"
    )
    
    save_report = st.checkbox("Save Report to File", value=True)
    
    report_format = st.selectbox(
        "Report Format",
        options=["Markdown", "HTML"],
        help="Choose output format for saved reports"
    )
    
    st.markdown("---")
    
    # About section
    st.subheader("ℹ️ About")
    st.markdown("""
    This AI Research Assistant uses advanced language models to:
    - 📋 Plan research strategy
    - 🌐 Search and gather information
    - 🧠 Synthesize findings
    - 📝 Generate comprehensive reports
    
    Perfect for:
    - Academic research
    - Market analysis
    - Technical documentation
    - Competitive intelligence
    """)
    
    st.markdown("---")
    
    # History
    if st.session_state.research_history:
        st.subheader("📚 Recent Research")
        for i, item in enumerate(reversed(st.session_state.research_history[-5:])):
            with st.expander(f"🔍 {item['topic'][:30]}..."):
                st.caption(f"Date: {item['timestamp']}")
                st.caption(f"Depth: {item['depth']}")
                st.caption(f"Sources: {item['num_sources']}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h3 style="color: #ffffff;">🔍 Enter Your Research Topic</h3>', unsafe_allow_html=True)
    topic = st.text_input(
        "",
        placeholder="e.g., 'Impact of AI on healthcare', 'Climate change solutions', 'Python best practices'",
        label_visibility="collapsed",
        key="topic_input"
    )
    
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    research_button = st.button("🚀 Start Research", type="primary", use_container_width=True)

# Examples
st.markdown('<p style="color: #e0e0e0; font-weight: bold;">💡 Example Topics:</p>', unsafe_allow_html=True)
example_col1, example_col2, example_col3 = st.columns(3)
with example_col1:
    if st.button("🏥 AI in Healthcare", use_container_width=True):
        st.session_state.topic_input = "Impact of artificial intelligence on modern healthcare"
        st.rerun()
with example_col2:
    if st.button("🌍 Climate Solutions", use_container_width=True):
        st.session_state.topic_input = "Innovative solutions for climate change mitigation"
        st.rerun()
with example_col3:
    if st.button("💻 Quantum Computing", use_container_width=True):
        st.session_state.topic_input = "Recent advances in quantum computing technology"
        st.rerun()

st.markdown("---")

# Research execution
if research_button and topic:
    # Initialize agent
    if st.session_state.agent is None:
        with st.spinner("🔧 Initializing AI Research Agent..."):
            try:
                st.session_state.agent = ResearchAgent()
            except Exception as e:
                st.error(f"❌ Error initializing agent: {str(e)}")
                st.info("💡 Make sure you have set up your API keys in the .env file")
                st.stop()
    
    # Progress tracking
    st.markdown('<h3 style="color: #ffffff;">🎯 Research Progress</h3>', unsafe_allow_html=True)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Planning
    status_text.markdown("**📋 Step 1/4:** Planning research strategy...")
    progress_bar.progress(25)
    time.sleep(0.5)
    
    # Step 2: Research
    status_text.markdown("**🌐 Step 2/4:** Conducting web research...")
    progress_bar.progress(50)
    
    # Execute research
    try:
        depth_mapping = {
            "Auto": None,
            "Shallow": "shallow",
            "Medium": "medium",
            "Deep": "deep"
        }
        
        result = st.session_state.agent.research(
            topic=topic,
            depth=depth_mapping[depth],
            save_report=save_report
        )
        
        if "error" in result:
            status_text.empty()
            progress_bar.empty()
            st.error(f"❌ Research Error: {result['error']}")
            st.stop()
        
        # Step 3: Synthesis
        status_text.markdown("**🧠 Step 3/4:** Synthesizing information...")
        progress_bar.progress(75)
        time.sleep(0.5)
        
        # Step 4: Report Generation
        status_text.markdown("**📝 Step 4/4:** Generating report...")
        progress_bar.progress(100)
        time.sleep(0.5)
        
        # Clear progress
        status_text.empty()
        progress_bar.empty()
        
        # Store results
        st.session_state.research_results = result
        
        # Add to history
        st.session_state.research_history.append({
            'topic': topic,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'depth': depth,
            'num_sources': result['num_sources']
        })
        
        # Success message
        st.markdown("""
            <div class="success-box">
                <h3 style="color: #81C784;">✅ Research Completed Successfully!</h3>
                <p style="color: #e0e0e0;">Your comprehensive research report is ready below.</p>
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        status_text.empty()
        progress_bar.empty()
        st.error(f"❌ An error occurred during research: {str(e)}")
        st.exception(e)
        st.stop()

# Display results
if st.session_state.research_results:
    result = st.session_state.research_results
    
    # Metrics
    st.markdown('<h3 style="color: #ffffff;">📊 Research Metrics</h3>', unsafe_allow_html=True)
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.markdown(f"""
            <div class="metric-card">
                <h2>📚 {result['num_sources']}</h2>
                <p>Sources Analyzed</p>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_col2:
        depth_display = result['plan'].get('depth', 'medium').capitalize()
        st.markdown(f"""
            <div class="metric-card">
                <h2>🎯 {depth_display}</h2>
                <p>Research Depth</p>
            </div>
        """, unsafe_allow_html=True)
    
    with metric_col3:
        word_count = len(result['report'].split())
        st.markdown(f"""
            <div class="metric-card">
                <h2>📝 {word_count}</h2>
                <p>Words Generated</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Report display
    st.markdown('<h3 style="color: #ffffff;">📄 Research Report</h3>', unsafe_allow_html=True)
    
    # Download buttons
    col1, col2 = st.columns([1, 5])
    with col1:
        st.download_button(
            label="⬇️ Download MD",
            data=result['report'],
            file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    with col2:
        if result.get('report_path'):
            st.info(f"💾 Report saved to: `{result['report_path']}`")
    
    # Display report
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown(result['report'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sources detail
    with st.expander("🔗 View Source Details"):
        sources = result['synthesis'].get('sources', [])
        for i, source in enumerate(sources, 1):
            st.markdown(f"**{i}. [{source.get('title', 'Untitled')}]({source.get('url', '#')})**")
            if source.get('snippet'):
                st.caption(source['snippet'])
            st.markdown("---")

elif not research_button:
    # Welcome screen
    st.markdown("""
        <div class="info-box">
            <h2>👋 Welcome to AI Research Assistant!</h2>
            <p>Get started by entering a research topic above and clicking "Start Research".</p>
            <h3>🎯 What This Tool Does:</h3>
            <ul>
                <li><strong>Intelligent Planning:</strong> AI analyzes your topic and creates an optimal research strategy</li>
                <li><strong>Comprehensive Research:</strong> Searches multiple sources across the web</li>
                <li><strong>Smart Synthesis:</strong> Combines information from all sources into coherent insights</li>
                <li><strong>Professional Reports:</strong> Generates well-structured, publication-ready reports</li>
            </ul>
            <h3>⚡ Features:</h3>
            <ul>
                <li>Real-time progress tracking</li>
                <li>Adjustable research depth</li>
                <li>Multiple output formats</li>
                <li>Source citations and references</li>
                <li>Download and save capabilities</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    # Feature showcase
    st.markdown('<h3 style="color: #ffffff;">🌟 Key Features</h3>', unsafe_allow_html=True)
    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
    
    with feat_col1:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1>🎯</h1>
                <h4 style="color: #ffffff;">Smart Planning</h4>
                <p style="color: #b0b0b0;">AI-powered research strategy</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1>⚡</h1>
                <h4 style="color: #ffffff;">Fast Results</h4>
                <p style="color: #b0b0b0;">Get reports in seconds</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1>📚</h1>
                <h4 style="color: #ffffff;">Multiple Sources</h4>
                <p style="color: #b0b0b0;">Comprehensive data gathering</p>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col4:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1>✨</h1>
                <h4 style="color: #ffffff;">Pro Reports</h4>
                <p style="color: #b0b0b0;">Publication-ready output</p>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem;">
        <p style="color: #888;">🤖 Powered by Advanced AI | Built with ❤️ using Streamlit</p>
        <p style="font-size: 0.8rem; color: #666;">© 2026 AI Research Assistant - All rights reserved</p>
    </div>
""", unsafe_allow_html=True)
