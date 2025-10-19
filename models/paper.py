"""
Paper data model
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Paper:
    """Data class to represent an academic paper with ML features"""
    title: str
    authors: List[str]
    year: int
    abstract: str
    url: str
    doi: Optional[str] = None
    venue: Optional[str] = None
    citation_count: int = 0
    paper_id: Optional[str] = None
    pdf_url: Optional[str] = None
    tldr: Optional[str] = None
    fields_of_study: List[str] = field(default_factory=list)
    influential_citation_count: int = 0
    ml_relevance_score: float = 0.0
    ml_cluster: int = -1
    ml_summary_confidence: float = 0.0
    
    def __post_init__(self):
        """Validate and process fields after initialization"""
        if self.fields_of_study is None:
            self.fields_of_study = []
        
        # Ensure scores are within valid ranges
        self.ml_relevance_score = max(0.0, min(1.0, self.ml_relevance_score))
        self.ml_summary_confidence = max(0.0, min(1.0, self.ml_summary_confidence))
    
    def to_dict(self):
        """Convert paper to dictionary"""
        return {
            'title': self.title,
            'authors': self.authors,
            'year': self.year,
            'abstract': self.abstract,
            'url': self.url,
            'doi': self.doi,
            'venue': self.venue,
            'citation_count': self.citation_count,
            'paper_id': self.paper_id,
            'pdf_url': self.pdf_url,
            'tldr': self.tldr,
            'fields_of_study': self.fields_of_study,
            'influential_citation_count': self.influential_citation_count,
            'ml_relevance_score': self.ml_relevance_score,
            'ml_cluster': self.ml_cluster,
            'ml_summary_confidence': self.ml_summary_confidence
        }