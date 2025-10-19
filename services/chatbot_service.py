"""
Chatbot Service for Research Paper Interaction
"""

import re
from typing import List, Dict

from models import Paper
from utils import logger
from config import GEMINI_API_KEY

class ChatbotService:
    """Chatbot service for conversational interaction with research papers"""
    
    def __init__(self, papers: List[Paper], summaries: List[Dict]):
        self.papers = papers
        self.summaries = summaries
        self.chat_history = []
        self.gemini_api_key = GEMINI_API_KEY
    
    def set_gemini_api_key(self, api_key: str):
        """Set Gemini API key"""
        self.gemini_api_key = api_key
    
    def chat_with_papers(self, user_question: str) -> str:
        """
        Process user questions about the research papers
        
        Args:
            user_question: User's question
            
        Returns:
            Response string
        """
        if not self.papers:
            return "No papers are currently loaded. Please search for papers first."
        
        # Add to chat history
        self.chat_history.append({"role": "user", "content": user_question})
        
        if self.gemini_api_key:
            response = self._chat_with_gemini(user_question)
        else:
            response = self._chat_locally(user_question)
        
        # Add response to history
        self.chat_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _chat_with_gemini(self, question: str) -> str:
        """
        Chat using Gemini with paper context
        
        Args:
            question: User question
            
        Returns:
            Response string
        """
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare context from papers
            context = "Available Research Papers:\n\n"
            for i, (paper, summary) in enumerate(zip(self.papers[:5], self.summaries[:5]), 1):
                context += f"{i}. {paper.title} ({paper.year})\n"
                context += f"   Authors: {', '.join(paper.authors[:3])}\n"
                context += f"   Key Finding: {summary.get('key_finding', 'Not available')}\n"
                context += f"   Citations: {paper.citation_count}\n\n"
            
            prompt = f"""
            You are an AI research assistant helping analyze academic papers. 
            Answer the user's question based on the provided research papers.
            
            {context}
            
            Chat History:
            {self._format_chat_history()}
            
            User Question: {question}
            
            Provide a helpful response based on the research papers. If the question
            is about a specific paper, reference it by number. Be concise but informative.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            return self._chat_locally(question)
    
    def _chat_locally(self, question: str) -> str:
        """
        Simple local chatbot responses with improved context awareness
        
        Args:
            question: User question
            
        Returns:
            Response string
        """
        question_lower = question.lower()
        
        # Check for paper number references
        paper_num_match = re.search(r'(?:paper\s+)?(\d+)|(?:second|third|fourth|fifth|first)\s+paper', question_lower)
        
        if paper_num_match:
            # Extract paper number
            number_word_map = {
                'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
                'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10
            }
            
            paper_num = None
            # Check for word numbers
            for word, num in number_word_map.items():
                if word in question_lower:
                    paper_num = num
                    break
            
            # Check for digit numbers
            if not paper_num and paper_num_match.group(1):
                try:
                    paper_num = int(paper_num_match.group(1))
                except:
                    pass
            
            if paper_num:
                idx = paper_num - 1
                if 0 <= idx < len(self.papers):
                    paper = self.papers[idx]
                    summary = self.summaries[idx] if idx < len(self.summaries) else {}
                    
                    # Check what specifically they're asking about
                    if any(word in question_lower for word in ['about', 'state', 'finding', 'result', 'conclude', 'show']):
                        response = f"**Paper {paper_num}: {paper.title}**\n\n"
                        
                        if summary.get('key_finding'):
                            response += f"**Key Finding:** {summary['key_finding']}\n\n"
                        
                        if summary.get('implications'):
                            response += f"**Implications:** {summary['implications']}\n\n"
                        
                        response += f"**Authors:** {', '.join(paper.authors[:3])}\n"
                        response += f"**Year:** {paper.year} | **Citations:** {paper.citation_count}\n\n"
                        
                        if paper.abstract:
                            response += f"**Abstract Summary:** {paper.abstract[:300]}..."
                        
                        return response
                    
                    elif any(word in question_lower for word in ['method', 'methodology', 'approach', 'how']):
                        response = f"**Paper {paper_num} Methodology:**\n\n"
                        
                        if summary.get('methodology'):
                            response += f"{summary['methodology']}\n\n"
                        else:
                            response += "Methodology details are not explicitly extracted. Here's what the abstract mentions:\n\n"
                            response += f"{paper.abstract[:400]}..."
                        
                        return response
                    
                    elif any(word in question_lower for word in ['author', 'who wrote', 'researcher']):
                        return f"**Paper {paper_num}** was written by: {', '.join(paper.authors)}\n\nPublished in {paper.year}" + (f" at {paper.venue}" if paper.venue else "")
                    
                    elif any(word in question_lower for word in ['citation', 'impact', 'influential']):
                        return f"**Paper {paper_num}** has **{paper.citation_count} citations** and **{paper.influential_citation_count} influential citations**. " + \
                               f"ML Relevance Score: {paper.ml_relevance_score:.2f} | ML Confidence: {paper.ml_summary_confidence:.2f}"
                    
                    else:
                        # General info about the paper
                        return f"**Paper {paper_num}: {paper.title}**\n\n" + \
                               f"**Authors:** {', '.join(paper.authors[:3])}\n" + \
                               f"**Year:** {paper.year}\n" + \
                               f"**Citations:** {paper.citation_count}\n\n" + \
                               f"**Key Finding:** {summary.get('key_finding', 'Not available')}\n\n" + \
                               f"You can ask me about the methodology, findings, or specific aspects of this paper!"
                else:
                    return f"I only have information about {len(self.papers)} papers. Paper {paper_num} is not in the results."
        
        # General questions
        if any(word in question_lower for word in ['summary', 'summarize', 'overview']):
            response = f"📚 **Research Overview:**\n\nI've analyzed {len(self.papers)} papers on your research topic.\n\n"
            response += "**Top 3 Papers:**\n"
            for i in range(min(3, len(self.papers))):
                paper = self.papers[i]
                response += f"\n{i+1}. **{paper.title}** ({paper.year})\n"
                response += f"   - {paper.citation_count} citations\n"
                if i < len(self.summaries) and self.summaries[i].get('key_finding'):
                    response += f"   - {self.summaries[i]['key_finding']}\n"
            return response
        
        elif any(word in question_lower for word in ['method', 'methodology', 'approach']):
            response = "**Research Methodologies Used:**\n\n"
            count = 0
            for i, summary in enumerate(self.summaries[:5], 1):
                if summary.get('methodology') and 'not extracted' not in summary['methodology'].lower():
                    response += f"**Paper {i}:** {summary['methodology']}\n\n"
                    count += 1
            
            if count == 0:
                response += "Detailed methodology information is limited in the summaries. Would you like me to elaborate on a specific paper's approach?"
            
            return response
        
        elif any(word in question_lower for word in ['finding', 'result', 'discover', 'conclude']):
            response = "**Key Findings from the Research:**\n\n"
            for i, summary in enumerate(self.summaries[:5], 1):
                if summary.get('key_finding'):
                    response += f"**Paper {i}:** {summary['key_finding']}\n\n"
            return response
        
        elif any(word in question_lower for word in ['compare', 'comparison', 'difference', 'similar']):
            return f"I can help you compare papers! Please specify which papers you'd like to compare. For example: 'Compare paper 1 and paper 2' or 'What are the differences between the first and second papers?'"
        
        elif any(word in question_lower for word in ['best', 'top', 'most important', 'recommend']):
            paper = self.papers[0] if self.papers else None
            if paper:
                return f"Based on ML relevance scores and citations, **{paper.title}** ({paper.year}) appears most significant with:\n" + \
                       f"- **{paper.citation_count} citations**\n" + \
                       f"- **ML Relevance: {paper.ml_relevance_score:.2f}**\n" + \
                       f"- **ML Confidence: {paper.ml_summary_confidence:.2f}**\n\n" + \
                       f"This paper is ranked #1 in the results."
        
        elif any(word in question_lower for word in ['recent', 'latest', 'new']):
            recent_papers = sorted([p for p in self.papers], key=lambda x: x.year, reverse=True)[:3]
            response = "**Most Recent Papers:**\n\n"
            for i, paper in enumerate(recent_papers, 1):
                response += f"{i}. **{paper.title}** ({paper.year})\n"
                response += f"   - {paper.citation_count} citations\n\n"
            return response
        
        elif any(word in question_lower for word in ['help', 'what can you', 'how to']):
            return """I can help you explore these research papers! Try asking:

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

Just ask naturally, and I'll help you understand the research!"""
        
        else:
            # Default helpful response
            return f"I have {len(self.papers)} research papers loaded. You can ask me about:\n\n" + \
                   "• Specific papers (e.g., 'What does paper 2 say?')\n" + \
                   "• Methodologies used\n" + \
                   "• Key findings and results\n" + \
                   "• Citations and impact\n" + \
                   "• Comparisons between papers\n\n" + \
                   "Try asking a specific question about the papers!"
    
    def _format_chat_history(self) -> str:
        """
        Format chat history for context
        
        Returns:
            Formatted history string
        """
        if not self.chat_history:
            return "No previous conversation."
        
        formatted = ""
        for msg in self.chat_history[-4:]:  # Last 4 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        
        return formatted