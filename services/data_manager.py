"""
Data Management Service
"""

import numpy as np
from datetime import datetime
from typing import Dict, List

from utils import logger
from config import DATA_DIR, SESSION_FILE

class DataManager:
    """Manage research session data and history"""
    
    def __init__(self):
        self.session_data = {
            'searches': [],
            'papers': [],
            'chat_history': [],
            'ml_insights': {}
        }
        self.data_file = SESSION_FILE
    
    def save_session(self, search_results: Dict, chat_history: List):
        """
        Save current session data
        
        Args:
            search_results: Results from search
            chat_history: Chat conversation history
        """
        try:
            self.session_data['searches'].append({
                'timestamp': datetime.now().isoformat(),
                'question': search_results.get('question', ''),
                'num_papers': len(search_results.get('papers', [])),
                'consensus': search_results.get('consensus_meter', {}).get('consensus', ''),
                'ml_confidence': search_results.get('consensus_meter', {}).get('confidence', 0.0)
            })
            
            self.session_data['chat_history'] = chat_history
            self.session_data['ml_insights'] = search_results.get('ml_insights', {})
            
            # Save to file (optional - for persistence)
            # import pickle
            # with open(self.data_file, 'wb') as f:
            #     pickle.dump(self.session_data, f)
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
    
    def get_session_stats(self) -> Dict:
        """
        Get session statistics
        
        Returns:
            Dictionary containing session statistics
        """
        searches = self.session_data['searches']
        if not searches:
            return {'total_searches': 0}
        
        return {
            'total_searches': len(searches),
            'avg_papers_per_search': np.mean([s['num_papers'] for s in searches]),
            'recent_searches': searches[-5:],
            'consensus_distribution': {
                search['consensus']: len([s for s in searches if s['consensus'] == search['consensus']])
                for search in searches
            }
        }