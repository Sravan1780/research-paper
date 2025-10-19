"""
Reusable UI Components
"""

import streamlit as st
from typing import Dict, List
from datetime import datetime

from models import Paper

def render_header():
    """Render main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 ML Research Assistant</h1>
        <p>Final Year Project - Machine Learning Based Academic Research Analysis</p>
        <span class="ml-badge">Powered by NLP & ML</span>
        <span class="ml-badge">TF-IDF Vectorization</span>
        <span class="ml-badge">K-Means Clustering</span>
    </div>
    """, unsafe_allow_html=True)

def render_consensus_meter(consensus_meter: Dict):
    """
    Render consensus meter visualization
    
    Args:
        consensus_meter: Dictionary containing consensus data
    """
    consensus_type = consensus_meter['consensus']
    percentage = consensus_meter['percentage']
    confidence = consensus_meter.get('confidence', 0.0)
    
    if 'positive' in consensus_type:
        meter_class = "consensus-positive"
        meter_text = f"✅ {percentage}% Evidence Supporting"
    elif 'negative' in consensus_type:
        meter_class = "consensus-negative"
        meter_text = f"❌ {100-percentage}% Evidence Against"
    else:
        meter_class = "consensus-mixed"
        meter_text = f"⚖️ Mixed Results ({percentage}% positive)"
    
    st.markdown(f"""
    <div class="consensus-meter {meter_class}">
        <h3>{meter_text}</h3>
        <p><strong>ML Analysis:</strong> {consensus_meter['explanation']}</p>
        <div style="margin-top: 1rem;">
            <span class="ml-badge">ML Confidence: {confidence:.2f}</span>
            <span class="ml-badge">Papers: {consensus_meter['total_papers']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_ml_insights_dashboard(ml_insights: Dict):
    """
    Render ML insights dashboard
    
    Args:
        ml_insights: Dictionary containing ML insights
    """
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg ML Relevance", f"{ml_insights['avg_relevance']:.2f}")
    with col2:
        st.metric("High Confidence Papers", ml_insights['high_confidence_count'])
    with col3:
        st.metric("Recent Papers %", f"{ml_insights['recent_papers_ratio']*100:.0f}%")
    with col4:
        st.metric("Total Clusters", len(ml_insights['paper_clusters']))

def render_research_synthesis(results: Dict, consensus_meter: Dict, ml_insights: Dict):
    """
    Render research synthesis section
    
    Args:
        results: Search results
        consensus_meter: Consensus data
        ml_insights: ML insights
    """
    confidence = consensus_meter.get('confidence', 0.0)
    
    synthesis_text = f"""
    Based on ML analysis of {results['total_found']} academic papers, our algorithms identified 
    key patterns and relationships. The research shows {consensus_meter['consensus'].replace('_', ' ')} 
    consensus with {confidence:.2f} ML confidence score.
    
    **Key ML Findings:**
    - Average relevance score: {ml_insights['avg_relevance']:.2f}/1.0
    - {ml_insights['high_confidence_count']} papers exceed high confidence threshold
    - {ml_insights['recent_papers_ratio']*100:.0f}% of research is from recent years (2020+)
    - Papers clustered into {len(ml_insights['paper_clusters'])} distinct research themes
    """
    
    st.markdown(f"""
    <div class="synthesis-box">
        <h4>🧠 ML-Generated Research Synthesis</h4>
        <p>{synthesis_text}</p>
    </div>
    """, unsafe_allow_html=True)

def render_paper_card(i: int, paper: Paper, summary: Dict):
    """
    Render individual paper card
    
    Args:
        i: Paper index
        paper: Paper object
        summary: Summary dictionary
    """
    st.markdown(f"""
    <div class="paper-card">
        <div class="paper-title">
            {i}. <a href="{paper.url}" target="_blank">{paper.title}</a>
        </div>
        <div class="paper-meta">
            <strong>Authors:</strong> {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}<br>
            <strong>Year:</strong> {paper.year} | 
            <strong>Citations:</strong> {paper.citation_count} | 
            <strong>Venue:</strong> {paper.venue or 'N/A'}
        </div>
        <div class="ml-score">
            🤖 <strong>ML Relevance:</strong> {paper.ml_relevance_score:.3f} | 
            <strong>ML Confidence:</strong> {paper.ml_summary_confidence:.3f} | 
            <strong>Cluster:</strong> {paper.ml_cluster}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if summary:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            evidence_class = f"evidence-{summary.get('evidence_strength', 'limited').lower()}"
            relevance_class = f"relevance-{summary.get('relevance', 'low').lower()}"
            
            st.markdown(f"""
            <span class="evidence-badge {evidence_class}">
                {summary.get('evidence_strength', 'Limited')} Evidence
            </span>
            <span class="evidence-badge {relevance_class}">
                {summary.get('relevance', 'Low')} Relevance
            </span>
            """, unsafe_allow_html=True)
            
            st.write("**🔍 Key Finding:**")
            st.write(summary.get('key_finding', 'Not available'))
            
            st.write("**⚗️ Methodology:**")
            st.write(summary.get('methodology', 'Not specified'))
        
        with col2:
            st.write("**🤖 ML Insights:**")
            st.write(summary.get('ml_insights', 'Not available'))
            
            st.write("**💡 Implications:**")
            st.write(summary.get('implications', 'Not available'))
    
    with st.expander(f"📄 Full Abstract - Paper {i}"):
        st.write(paper.abstract)
        if paper.pdf_url:
            st.markdown(f"[📄 Access PDF]({paper.pdf_url})")

def render_chat_history(chat_history: List[Dict]):
    """
    Render chat conversation history in a conversational format
    
    Args:
        chat_history: List of chat messages
    """
    # Create a container for all messages
    chat_container = st.container()
    
    with chat_container:
        for i, chat in enumerate(chat_history):
            # User message
            st.markdown(f"""
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
                <div style="color: #1976d2; font-weight: bold; margin-bottom: 0.5rem;">
                    👤 You <span style="color: #666; font-size: 0.85em; font-weight: normal;">({chat['timestamp']})</span>
                </div>
                <div style="color: #333;">{chat['question']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Assistant response
            st.markdown(f"""
            <div style="background: white; border-left: 4px solid #28a745; border-radius: 10px; padding: 1rem; margin: 0.5rem 0 1.5rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #28a745; font-weight: bold; margin-bottom: 0.5rem;">
                    🤖 Assistant
                </div>
                <div style="color: #333; line-height: 1.6;">{chat['response']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_session_stats(stats: Dict):
    """
    Render session statistics
    
    Args:
        stats: Statistics dictionary
    """
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{stats.get('total_searches', 0)}</h3>
            <p>Searches</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_papers = stats.get('avg_papers_per_search', 0)
        st.markdown(f"""
        <div class="stats-card">
            <h3>{avg_papers:.1f}</h3>
            <p>Avg Papers</p>
        </div>
        """, unsafe_allow_html=True)

def render_example_questions():
    """Render example research questions"""
    example_questions = [
        "How effective is machine learning in medical image analysis?",
        "What are the applications of deep learning in natural language processing?",
        "How does artificial intelligence improve autonomous vehicle safety?",
        "What machine learning techniques are used in financial fraud detection?",
        "How effective are neural networks for climate change prediction?",
        "What are the ethical implications of AI in healthcare?"
    ]
    
    cols = st.columns(2)
    for i, question in enumerate(example_questions):
        col = cols[i % 2]
        if col.button(f"🔍 {question}", key=f"example_{i}"):
            return question
    return None

def render_footer():
    """Render application footer"""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🤖 <strong>ML Research Assistant</strong> - Final Year Project<br>
        <em>Machine Learning Based Academic Research Analysis System</em><br>
        Technologies: Python • Streamlit • Scikit-learn • TF-IDF • K-Means • NLP • Gemini AI
    </div>
    """, unsafe_allow_html=True)