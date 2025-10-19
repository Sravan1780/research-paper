"""
ML-Enhanced Summarization Service
"""

import re
import numpy as np
from typing import List, Dict, Optional, Any

from models import Paper
from utils import logger, extract_key_terms
from config import (
    GEMINI_API_KEY,
    POSITIVE_INDICATORS,
    NEGATIVE_INDICATORS,
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD,
    RECENT_YEAR_THRESHOLD,
    STRONG_POSITIVE_THRESHOLD,
    MODERATE_POSITIVE_THRESHOLD,
    MODERATE_NEGATIVE_THRESHOLD,
    STRONG_NEGATIVE_THRESHOLD
)

class MLSummarizationService:
    """ML-enhanced summarization service with confidence scoring"""
    
    def __init__(self):
        self.gemini_api_key = GEMINI_API_KEY
    
    def set_gemini_api_key(self, api_key: str):
        """Set Gemini API key"""
        self.gemini_api_key = api_key
    
    def generate_ml_consensus(self, papers: List[Paper], research_question: str) -> Dict[str, Any]:
        """
        Generate ML-based consensus analysis
        
        Args:
            papers: List of papers to analyze
            research_question: Original research question
            
        Returns:
            Dictionary containing consensus analysis
        """
        if not papers:
            return {"consensus": "insufficient_data", "confidence": 0.0, "ml_insights": {}}
        
        try:
            # ML-based sentiment analysis
            positive_scores = []
            negative_scores = []
            
            for paper in papers:
                sentiment_score = self._ml_sentiment_analysis(paper, research_question)
                confidence_weight = paper.ml_summary_confidence
                
                if sentiment_score > 0.1:
                    positive_scores.append(sentiment_score * confidence_weight)
                elif sentiment_score < -0.1:
                    negative_scores.append(abs(sentiment_score) * confidence_weight)
            
            total_weighted_positive = sum(positive_scores)
            total_weighted_negative = sum(negative_scores)
            total_weight = total_weighted_positive + total_weighted_negative
            
            if total_weight > 0:
                positive_percentage = (total_weighted_positive / total_weight) * 100
            else:
                positive_percentage = 50.0  # Neutral
            
            # Determine consensus with ML confidence
            avg_confidence = np.mean([p.ml_summary_confidence for p in papers])
            
            if positive_percentage >= STRONG_POSITIVE_THRESHOLD and avg_confidence > HIGH_CONFIDENCE_THRESHOLD - 0.1:
                consensus = "strong_positive"
                confidence = avg_confidence
            elif positive_percentage >= MODERATE_POSITIVE_THRESHOLD and avg_confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                consensus = "moderate_positive"
                confidence = avg_confidence
            elif positive_percentage <= STRONG_NEGATIVE_THRESHOLD and avg_confidence > HIGH_CONFIDENCE_THRESHOLD - 0.1:
                consensus = "strong_negative"
                confidence = avg_confidence
            elif positive_percentage <= MODERATE_NEGATIVE_THRESHOLD and avg_confidence > MEDIUM_CONFIDENCE_THRESHOLD:
                consensus = "moderate_negative"
                confidence = avg_confidence
            else:
                consensus = "mixed"
                confidence = avg_confidence
            
            # Additional ML insights
            ml_insights = {
                "avg_relevance_score": np.mean([p.ml_relevance_score for p in papers]),
                "high_confidence_papers": len([p for p in papers if p.ml_summary_confidence > HIGH_CONFIDENCE_THRESHOLD]),
                "recent_papers_ratio": len([p for p in papers if p.year >= RECENT_YEAR_THRESHOLD]) / len(papers),
                "avg_citation_impact": np.mean([p.citation_count for p in papers])
            }
            
            explanation = self._generate_ml_explanation(papers, positive_percentage, avg_confidence)
            
            return {
                "consensus": consensus,
                "percentage": round(positive_percentage, 1),
                "confidence": round(confidence, 2),
                "total_papers": len(papers),
                "explanation": explanation,
                "ml_insights": ml_insights
            }
            
        except Exception as e:
            logger.error(f"Error in ML consensus generation: {e}")
            return {"consensus": "error", "confidence": 0.0, "ml_insights": {}}
    
    def _ml_sentiment_analysis(self, paper: Paper, research_question: str) -> float:
        """
        ML-based sentiment analysis for paper relevance
        
        Args:
            paper: Paper to analyze
            research_question: Research question for context
            
        Returns:
            Sentiment score between -1 and 1
        """
        abstract_lower = paper.abstract.lower()
        question_lower = research_question.lower()
        
        # Extract key terms
        question_terms = extract_key_terms(question_lower)
        
        # Calculate weighted sentiment score
        positive_score = sum(2 if indicator in abstract_lower else 0 for indicator in POSITIVE_INDICATORS)
        negative_score = sum(2 if indicator in abstract_lower else 0 for indicator in NEGATIVE_INDICATORS)
        
        # Factor in relevance and citation count
        relevance_boost = paper.ml_relevance_score
        citation_boost = min(paper.citation_count / 100, 1.0)
        
        final_score = (positive_score - negative_score) * relevance_boost * (1 + citation_boost)
        
        # Normalize to [-1, 1] range
        return np.tanh(final_score / 10)
    
    def _generate_ml_explanation(self, papers: List[Paper], positive_pct: float, confidence: float) -> str:
        """
        Generate explanation using ML insights
        
        Args:
            papers: List of papers
            positive_pct: Positive percentage
            confidence: Confidence score
            
        Returns:
            Explanation string
        """
        high_conf_count = len([p for p in papers if p.ml_summary_confidence > HIGH_CONFIDENCE_THRESHOLD])
        avg_relevance = np.mean([p.ml_relevance_score for p in papers])
        
        base_explanation = f"ML analysis of {len(papers)} papers shows "
        
        if positive_pct >= STRONG_POSITIVE_THRESHOLD:
            explanation = base_explanation + f"{positive_pct:.1f}% positive evidence with {confidence:.1f} confidence."
        elif positive_pct <= STRONG_NEGATIVE_THRESHOLD:
            explanation = base_explanation + f"{100-positive_pct:.1f}% negative evidence with {confidence:.1f} confidence."
        else:
            explanation = base_explanation + f"mixed results ({positive_pct:.1f}% positive) with {confidence:.1f} confidence."
        
        if high_conf_count > len(papers) * 0.6:
            explanation += f" {high_conf_count} papers show high ML confidence scores."
        
        if avg_relevance > 0.6:
            explanation += " Strong topical relevance detected by ML analysis."
        
        return explanation
    
    def summarize_with_ml(self, paper: Paper, research_question: str) -> Dict[str, str]:
        """
        Generate ML-enhanced paper summary
        
        Args:
            paper: Paper to summarize
            research_question: Research question for context
            
        Returns:
            Dictionary containing summary sections
        """
        if self.gemini_api_key:
            summary = self._ml_enhanced_gemini_summary(paper, research_question)
            if summary:
                return summary
        
        return self._ml_local_summary(paper, research_question)
    
    def _ml_enhanced_gemini_summary(self, paper: Paper, research_question: str) -> Optional[Dict[str, str]]:
        """
        ML-enhanced Gemini summarization
        
        Args:
            paper: Paper to summarize
            research_question: Research question
            
        Returns:
            Summary dictionary or None if failed
        """
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Enhanced prompt with ML insights
            prompt = f"""
            You are an AI research assistant with machine learning capabilities analyzing academic papers.
            
            Research Question: {research_question}
            
            Paper Analysis:
            - Title: {paper.title}
            - Authors: {', '.join(paper.authors[:5])}
            - Year: {paper.year}
            - Citations: {paper.citation_count}
            - ML Relevance Score: {paper.ml_relevance_score:.2f}
            - ML Confidence: {paper.ml_summary_confidence:.2f}
            - Abstract: {paper.abstract}
            
            Provide a structured analysis:
            
            KEY_FINDING: Main finding relevant to the research question (1 sentence)
            METHODOLOGY: Research methodology used (1 sentence)
            EVIDENCE_STRENGTH: Strong/Moderate/Limited based on citations and ML confidence
            RELEVANCE: High/Medium/Low based on ML relevance score
            ML_INSIGHTS: How ML analysis rates this paper's contribution
            IMPLICATIONS: Practical implications for the research question
            
            Format exactly as shown above with colons.
            """
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse structured response
            sections = {}
            for line in result_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    sections[key.strip()] = value.strip()
            
            return {
                'key_finding': sections.get('KEY_FINDING', ''),
                'methodology': sections.get('METHODOLOGY', ''),
                'evidence_strength': sections.get('EVIDENCE_STRENGTH', ''),
                'relevance': sections.get('RELEVANCE', ''),
                'ml_insights': sections.get('ML_INSIGHTS', ''),
                'implications': sections.get('IMPLICATIONS', '')
            }
            
        except Exception as e:
            logger.error(f"Error with ML-enhanced Gemini: {e}")
            return None
    
    def _ml_local_summary(self, paper: Paper, research_question: str) -> Dict[str, str]:
        """
        ML-enhanced local summarization
        
        Args:
            paper: Paper to summarize
            research_question: Research question
            
        Returns:
            Summary dictionary
        """
        abstract = paper.abstract
        sentences = [s.strip() for s in abstract.split('.') if s.strip()]
        
        # ML-enhanced key finding extraction
        key_finding = sentences[0] if sentences else "Key finding not available."
        
        # ML-based evidence strength assessment
        if paper.ml_summary_confidence > HIGH_CONFIDENCE_THRESHOLD and paper.citation_count > 50:
            evidence_strength = "Strong"
        elif paper.ml_summary_confidence > MEDIUM_CONFIDENCE_THRESHOLD and paper.citation_count > 10:
            evidence_strength = "Moderate"
        else:
            evidence_strength = "Limited"
        
        # ML-based relevance assessment
        if paper.ml_relevance_score > 0.6:
            relevance = "High"
        elif paper.ml_relevance_score > 0.3:
            relevance = "Medium"
        else:
            relevance = "Low"
        
        # ML insights
        ml_insights = f"ML confidence: {paper.ml_summary_confidence:.2f}, Relevance: {paper.ml_relevance_score:.2f}"
        
        return {
            'key_finding': key_finding,
            'methodology': "Methodology details not extracted locally.",
            'evidence_strength': evidence_strength,
            'relevance': relevance,
            'ml_insights': ml_insights,
            'implications': f"This {paper.year} study contributes {evidence_strength.lower()} evidence with {relevance.lower()} relevance."
        }