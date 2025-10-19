"""
Semantic Scholar API Service
"""

import requests
import time
from typing import List, Dict, Optional

from models import Paper
from utils import logger, clean_query
from config import (
    SEMANTIC_SCHOLAR_BASE_URL,
    SEMANTIC_SCHOLAR_API_KEY,
    REQUEST_DELAY,
    TIMEOUT,
    FIELDS,
    MAX_PAPER_LIMIT
)

class SemanticScholarAPI:
    """Handler for Semantic Scholar API interactions"""
    
    def __init__(self, api_key: str = None):
        self.base_url = SEMANTIC_SCHOLAR_BASE_URL
        self.session = requests.Session()
        
        headers = {'User-Agent': 'MLResearchAssistant/1.0 (academic-research)'}
        if api_key or SEMANTIC_SCHOLAR_API_KEY:
            headers['X-API-KEY'] = api_key or SEMANTIC_SCHOLAR_API_KEY
        
        self.session.headers.update(headers)
        self.last_request_time = 0
        self.request_delay = REQUEST_DELAY
    
    def _rate_limit(self):
        """Rate limiting to avoid API restrictions"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    def search_papers(self, query: str, limit: int = 10) -> List[Paper]:
        """
        Search for papers using Semantic Scholar API
        
        Args:
            query: Search query string
            limit: Maximum number of papers to retrieve
            
        Returns:
            List of Paper objects
        """
        try:
            self._rate_limit()
            
            clean_query_str = clean_query(query)
            
            params = {
                'query': clean_query_str,
                'limit': min(limit, MAX_PAPER_LIMIT),
                'fields': FIELDS,
                'sort': 'citationCount:desc'
            }
            
            url = f"{self.base_url}/paper/search"
            logger.info(f"Searching Semantic Scholar: {clean_query_str}")
            
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            
            if response.status_code == 429:
                logger.warning("Rate limited, waiting...")
                time.sleep(10)
                response = self.session.get(url, params=params, timeout=TIMEOUT)
            
            response.raise_for_status()
            data = response.json()
            
            papers = []
            for paper_data in data.get('data', []):
                paper = self._parse_paper_data(paper_data)
                if paper and paper.abstract:
                    papers.append(paper)
            
            logger.info(f"Retrieved {len(papers)} papers from Semantic Scholar")
            return papers
            
        except Exception as e:
            logger.error(f"Semantic Scholar API error: {e}")
            return []
    
    def _parse_paper_data(self, paper_data: Dict) -> Optional[Paper]:
        """
        Parse Semantic Scholar response into Paper object
        
        Args:
            paper_data: Raw paper data from API
            
        Returns:
            Paper object or None if parsing fails
        """
        try:
            title = paper_data.get('title', '').strip()
            if not title:
                return None
            
            authors = [
                author.get('name') 
                for author in paper_data.get('authors', []) 
                if author.get('name')
            ]
            year = paper_data.get('year') or 0
            abstract = paper_data.get('abstract', '').strip()
            
            if not abstract:
                return None
            
            url = paper_data.get('url', '')
            paper_id = paper_data.get('paperId', '')
            
            external_ids = paper_data.get('externalIds', {})
            doi = external_ids.get('DOI') if external_ids else None
            
            venue = paper_data.get('venue', {})
            venue_name = venue.get('name') if isinstance(venue, dict) else venue
            
            citation_count = paper_data.get('citationCount', 0)
            influential_citation_count = paper_data.get('influentialCitationCount', 0)
            
            tldr_data = paper_data.get('tldr')
            tldr = tldr_data.get('text') if tldr_data else None
            
            fields_of_study = []
            for field in paper_data.get('fieldsOfStudy', []):
                if isinstance(field, dict):
                    fields_of_study.append(field.get('name', ''))
                else:
                    fields_of_study.append(str(field))
            
            pdf_url = None
            open_access_pdf = paper_data.get('openAccessPdf')
            if open_access_pdf and open_access_pdf.get('url'):
                pdf_url = open_access_pdf['url']
            
            return Paper(
                title=title,
                authors=authors,
                year=year,
                abstract=abstract,
                url=url,
                doi=doi,
                venue=venue_name,
                citation_count=citation_count,
                paper_id=paper_id,
                pdf_url=pdf_url,
                tldr=tldr,
                fields_of_study=fields_of_study,
                influential_citation_count=influential_citation_count
            )
            
        except Exception as e:
            logger.error(f"Error parsing paper data: {e}")
            return None