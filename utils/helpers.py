"""
Helper utility functions
"""

import re
from typing import List

def clean_query(query: str) -> str:
    """
    Clean and optimize query for academic search
    
    Args:
        query: Raw search query
        
    Returns:
        Cleaned query string
    """
    query = re.sub(
        r'\b(does|do|is|are|what|how|why|when|where|can|will|should)\b', 
        '', 
        query.lower()
    )
    query = re.sub(r'[^\w\s-]', ' ', query)
    query = re.sub(r'\s+', ' ', query).strip()
    return query

def extract_key_terms(text: str, min_length: int = 3) -> List[str]:
    """
    Extract key terms from text
    
    Args:
        text: Input text
        min_length: Minimum term length
        
    Returns:
        List of key terms
    """
    terms = re.findall(r'\b\w+\b', text.lower())
    return [term for term in terms if len(term) > min_length]

def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Input text
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + '...'