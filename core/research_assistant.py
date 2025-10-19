"""
Main ML Research Assistant Core Logic
"""

import time
import requests
from typing import Dict, Any, List, Tuple
import streamlit as st
import numpy as np

from models import Paper
from services import (
    SemanticScholarAPI,
    MLPaperProcessor,
    MLSummarizationService,
    ChatbotService,
    DataManager
)
from utils import logger

class MLResearchAssistant:
    """Main ML-based research assistant"""
    
    def __init__(self):
        self.api = SemanticScholarAPI()
        self.ml_processor = MLPaperProcessor()
        self.summarizer = MLSummarizationService()
        self.data_manager = DataManager()
        self.current_papers = []
        self.current_summaries = []
        self.chatbot = None
    
    def search_and_analyze_ml(self, research_question: str, num_papers: int = 10) -> Dict[str, Any]:
        """
        Main ML-based search and analysis with robust error handling
        
        Args:
            research_question: Research question to analyze
            num_papers: Number of papers to retrieve
            
        Returns:
            Dictionary containing analysis results
        """
        
        # Input validation
        if not research_question or not research_question.strip():
            st.error("❌ Please provide a valid research question.")
            return {"papers": [], "consensus_meter": None, "ml_insights": {}}
        
        st.write("🔍 **Step 1:** Searching academic databases...")
        
        try:
            # Search papers with error handling
            papers = self.api.search_papers(research_question.strip(), limit=num_papers)
            
            # Debug information
            logger.info(f"API returned: {type(papers)}, Length: {len(papers) if papers else 0}")
            
            # Check for None result
            if papers is None:
                st.error("❌ API connection failed. Please check your internet connection and try again.")
                return {"papers": [], "consensus_meter": None, "ml_insights": {}}
            
            # Check for empty results
            if isinstance(papers, list) and len(papers) == 0:
                st.warning(f"⚠️ No papers found for '{research_question}'. Try different keywords or a broader search.")
                return {"papers": [], "consensus_meter": None, "ml_insights": {}}
            
            # Ensure we have valid papers
            if not isinstance(papers, list) or not papers:
                st.error("❌ Invalid response from search API. Please try again.")
                return {"papers": [], "consensus_meter": None, "ml_insights": {}}
            
            st.success(f"✅ Found {len(papers)} relevant papers!")
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Network error: Unable to connect to academic databases. Please check your connection.")
            logger.error(f"Network error: {e}")
            return {"papers": [], "consensus_meter": None, "ml_insights": {}}
        
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. The academic database is taking too long to respond.")
            return {"papers": [], "consensus_meter": None, "ml_insights": {}}
        
        except Exception as e:
            st.error(f"❌ Search failed: {str(e)}")
            logger.error(f"Unexpected search error: {e}")
            return {"papers": [], "consensus_meter": None, "ml_insights": {}}
        
        # ML Processing
        st.write("🤖 **Step 2:** Applying machine learning analysis...")
        try:
            papers = self.ml_processor.process_papers(papers, research_question)
        except Exception as e:
            st.warning(f"⚠️ ML processing encountered issues: {str(e)}")
            logger.error(f"ML processing error: {e}")
        
        # Generate ML-based consensus
        st.write("📊 **Step 3:** Generating consensus analysis...")
        try:
            consensus_meter = self.summarizer.generate_ml_consensus(papers, research_question)
        except Exception as e:
            st.warning(f"⚠️ Consensus analysis failed: {str(e)}")
            logger.error(f"Consensus error: {e}")
            consensus_meter = {"consensus": "error", "confidence": 0.0, "ml_insights": {}}
        
        # Generate paper summaries
        st.write("📝 **Step 4:** Creating intelligent summaries...")
        progress_bar = st.progress(0)
        
        paper_summaries = []
        for i, paper in enumerate(papers):
            try:
                summary = self.summarizer.summarize_with_ml(paper, research_question)
                paper_summaries.append({
                    'paper': paper,
                    'summary': summary
                })
                progress_bar.progress((i + 1) / len(papers))
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error summarizing paper {i+1}: {e}")
                paper_summaries.append({
                    'paper': paper,
                    'summary': {
                        'key_finding': 'Summary generation failed',
                        'methodology': 'Not available',
                        'evidence_strength': 'Unknown',
                        'relevance': 'Unknown',
                        'ml_insights': f'Error: {str(e)}',
                        'implications': 'Analysis incomplete'
                    }
                })
                continue
        
        progress_bar.empty()
        
        # Ensure we have at least some results
        if not paper_summaries:
            st.error("❌ Failed to process any papers. Please try a different search.")
            return {"papers": [], "consensus_meter": None, "ml_insights": {}}
        
        # Store current data for chatbot
        self.current_papers = papers
        self.current_summaries = [ps['summary'] for ps in paper_summaries]
        
        # Initialize chatbot with current papers
        try:
            self.chatbot = ChatbotService(papers, self.current_summaries)
            if hasattr(self.summarizer, 'gemini_api_key') and self.summarizer.gemini_api_key:
                self.chatbot.set_gemini_api_key(self.summarizer.gemini_api_key)
        except Exception as e:
            logger.error(f"Chatbot initialization error: {e}")
            self.chatbot = None
        
        # ML Insights with error handling
        try:
            ml_insights = {
                'paper_clusters': self.ml_processor.get_paper_clusters(),
                'avg_relevance': np.mean([getattr(p, 'ml_relevance_score', 0.0) for p in papers]),
                'high_confidence_count': len([p for p in papers if getattr(p, 'ml_summary_confidence', 0.0) > 0.7]),
                'recent_papers_ratio': len([p for p in papers if p.year >= 2020]) / len(papers) if papers else 0.0,
            }
        except Exception as e:
            logger.error(f"ML insights error: {e}")
            ml_insights = {
                'paper_clusters': {},
                'avg_relevance': 0.0,
                'high_confidence_count': 0,
                'recent_papers_ratio': 0.0,
            }
        
        results = {
            'question': research_question,
            'papers': paper_summaries,
            'consensus_meter': consensus_meter,
            'ml_insights': ml_insights,
            'total_found': len(papers)
        }
        
        # Save session data
        try:
            self.data_manager.save_session(results, [])
        except Exception as e:
            logger.error(f"Session save error: {e}")
        
        st.success("🎯 **Analysis Complete!** ML-powered insights ready.")
        
        return results
    
    def chat_with_research(self, user_question: str) -> str:
        """
        Chat interface for research papers
        
        Args:
            user_question: User's question
            
        Returns:
            Response string
        """
        if not self.chatbot:
            return "Please search for papers first before asking questions."
        
        return self.chatbot.chat_with_papers(user_question)
    
    def get_similar_papers(self, paper_index: int) -> List[Tuple[Paper, float]]:
        """
        Get ML-based similar papers
        
        Args:
            paper_index: Index of target paper
            
        Returns:
            List of similar papers with scores
        """
        return self.ml_processor.find_similar_papers(paper_index, top_k=3)