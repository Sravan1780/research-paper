"""
ML-Based Intelligent Research Assistant
Main Streamlit Application

A machine learning powered research assistant that analyzes academic papers 
and provides intelligent insights through natural language processing.

Final Year Project - Computer Science
"""

import streamlit as st
from datetime import datetime

from core import MLResearchAssistant
from ui import (
    CUSTOM_CSS,
    render_header,
    render_consensus_meter,
    render_ml_insights_dashboard,
    render_research_synthesis,
    render_paper_card,
    render_chat_history,
    render_session_stats,
    render_example_questions,
    render_footer
)
from config import PAGE_TITLE, PAGE_ICON, LAYOUT

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Render header
    render_header()
    
    # Initialize session state
    if 'ml_assistant' not in st.session_state:
        st.session_state.ml_assistant = MLResearchAssistant()
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar for history and stats
    with st.sidebar:
        st.header("👤 Research Profile")
        
        # User info section
        with st.expander("📊 Session Statistics"):
            stats = st.session_state.ml_assistant.data_manager.get_session_stats()
            render_session_stats(stats)
        
        # Search History
        st.subheader("📚 Search History")
        
        session_data = st.session_state.ml_assistant.data_manager.session_data
        if session_data['searches']:
            for i, search in enumerate(reversed(session_data['searches'][-5:]), 1):
                with st.expander(f"Search {len(session_data['searches']) - i + 1}"):
                    st.write(f"**Question:** {search['question'][:50]}...")
                    st.write(f"**Papers:** {search['num_papers']}")
                    st.write(f"**Consensus:** {search['consensus'].replace('_', ' ').title()}")
                    st.write(f"**ML Confidence:** {search['ml_confidence']:.2f}")
        else:
            st.info("No search history yet. Start by asking a research question!")
        
        # ML Settings
        st.subheader("⚙️ ML Configuration")
        
        num_papers = st.slider("Papers to Analyze", 5, 20, 20)  # Default set to 20
        
        # Clear history
        if st.button("🗑️ Clear History"):
            st.session_state.ml_assistant.data_manager.session_data = {
                'searches': [], 'papers': [], 'chat_history': [], 'ml_insights': {}
            }
            st.session_state.search_results = None
            st.session_state.chat_history = []
            st.success("History cleared!")
            st.rerun()
    
    # Main content area
    st.header("🔍 Research Question")
    
    research_question = st.text_area(
        "What would you like to research?",
        placeholder="e.g., How does machine learning improve medical diagnosis accuracy?",
        help="Ask specific research questions. Our ML algorithms will find and analyze relevant academic papers.",
        height=150  # Increased height
    )
    
    search_button = st.button("🚀 Analyze with ML", type="primary", use_container_width=True)
    
    # Process search
    if search_button and research_question.strip():
        with st.spinner("🔬 Running ML analysis on academic papers..."):
            results = st.session_state.ml_assistant.search_and_analyze_ml(
                research_question.strip(), 
                num_papers=num_papers
            )
            
            st.session_state.search_results = results
            
            if results['papers']:
                # Display ML Consensus Meter
                consensus_meter = results['consensus_meter']
                if consensus_meter:
                    st.markdown("## 🎯 ML-Powered Research Consensus")
                    render_consensus_meter(consensus_meter)
                
                # ML Insights Dashboard
                ml_insights = results['ml_insights']
                st.markdown("## 📊 ML Insights Dashboard")
                render_ml_insights_dashboard(ml_insights)
                
                # Research Synthesis
                st.markdown("## 📝 Intelligent Research Synthesis")
                render_research_synthesis(results, consensus_meter, ml_insights)
                
                # Individual Papers with ML Scores
                st.markdown("## 📚 ML-Analyzed Papers")
                
                for i, result in enumerate(results['papers'], 1):
                    paper = result['paper']
                    summary = result['summary']
                    render_paper_card(i, paper, summary)
    
    # Chatbot Interface
    if st.session_state.search_results and st.session_state.search_results['papers']:
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("## 💬 Chat with Research Papers")
        with col2:
            if st.button("🗑️ Clear Chat", key="clear_chat"):
                st.session_state.chat_history = []
                st.rerun()
        
        st.markdown("Ask questions about the analyzed papers using natural language!")
        
        # Display chat history FIRST (like ChatGPT)
        if st.session_state.chat_history:
            render_chat_history(st.session_state.chat_history)
        else:
            st.info("👋 Start a conversation! Ask me anything about the papers. Try: 'What does the second paper state about?'")
        
        # Chat input at the bottom
        with st.form(key="chat_form", clear_on_submit=True):
            chat_question = st.text_input(
                "Ask about the research:",
                placeholder="e.g., What methodology did paper 2 use? What are the main findings?",
                key="chat_input_field"
            )
            
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                send_button = st.form_submit_button("💬 Send", type="primary", use_container_width=True)
            with col2:
                help_button = st.form_submit_button("❓ Help", use_container_width=True)
        
        # Process help button
        if help_button:
            st.session_state.chat_history.append({
                'question': 'What can you help me with?',
                'response': """I can help you explore these research papers! Try asking:

📄 **About specific papers:**
- "What is paper 2 about?"
- "Tell me about the second paper"
- "What methodology did paper 3 use?"

🔍 **General queries:**
- "Summarize the findings"
- "What methodologies were used?"
- "Which is the most cited paper?"
- "Show me recent papers"

📊 **Comparisons:**
- "Compare paper 1 and paper 2"
- "What are the key differences?"

Just ask naturally, and I'll help you understand the research!""",
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
            st.rerun()
        
        # Process chat when form is submitted
        if send_button and chat_question:
            with st.spinner("🤖 Processing your question..."):
                try:
                    response = st.session_state.ml_assistant.chat_with_research(chat_question)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        'question': chat_question,
                        'response': response,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
                    
                    # Force refresh to show new message
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Chat error: {str(e)}")
    
    # Example questions for new users
    if not st.session_state.search_results:
        st.markdown("## 💡 Example ML Research Questions")
        selected_question = render_example_questions()
        
        if selected_question:
            st.session_state.example_question = selected_question
            st.rerun()
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()