"""
Machine Learning Paper Processing Service
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
from collections import defaultdict

from models import Paper
from utils import logger
from config import (
    MAX_TF_IDF_FEATURES,
    NGRAM_RANGE,
    MAX_CLUSTERS,
    MIN_PAPERS_FOR_CLUSTERING
)

class MLPaperProcessor:
    """Machine Learning component for paper analysis and clustering"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=MAX_TF_IDF_FEATURES, 
            stop_words='english',
            ngram_range=NGRAM_RANGE
        )
        self.paper_vectors = None
        self.papers_data = []
        self.clusters = None
    
    def process_papers(self, papers: List[Paper], query: str) -> List[Paper]:
        """
        Apply ML processing to papers for relevance scoring and clustering
        
        Args:
            papers: List of papers to process
            query: Original search query
            
        Returns:
            Processed and ranked list of papers
        """
        if not papers:
            return papers
        
        try:
            # Extract text features for ML processing
            paper_texts = []
            for paper in papers:
                # Combine title, abstract, and fields for feature extraction
                text = f"{paper.title} {paper.abstract}"
                if paper.fields_of_study:
                    text += " " + " ".join(paper.fields_of_study)
                paper_texts.append(text)
            
            # Add query to the corpus for similarity calculation
            paper_texts.append(query)
            
            # Vectorize papers using TF-IDF
            self.paper_vectors = self.vectorizer.fit_transform(paper_texts)
            
            # Calculate relevance scores using cosine similarity
            query_vector = self.paper_vectors[-1]  # Last vector is the query
            paper_vectors_only = self.paper_vectors[:-1]  # All except query
            
            similarities = cosine_similarity(paper_vectors_only, query_vector).flatten()
            
            # Apply clustering if we have enough papers
            if len(papers) > MIN_PAPERS_FOR_CLUSTERING:
                n_clusters = min(MAX_CLUSTERS, len(papers))
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                clusters = kmeans.fit_predict(paper_vectors_only)
            else:
                clusters = np.zeros(len(papers))
            
            # Update papers with ML-derived features
            for i, paper in enumerate(papers):
                paper.ml_relevance_score = float(similarities[i])
                paper.ml_cluster = int(clusters[i])
                
                # Calculate summary confidence based on multiple factors
                confidence_factors = [
                    similarities[i],  # Relevance to query
                    min(paper.citation_count / 100, 1.0),  # Citation count (normalized)
                    1.0 if paper.abstract and len(paper.abstract) > 100 else 0.5,  # Abstract quality
                    1.0 if paper.year >= 2015 else 0.7  # Recency factor
                ]
                paper.ml_summary_confidence = np.mean(confidence_factors)
            
            # Sort papers by ML relevance score
            papers.sort(key=lambda x: x.ml_relevance_score, reverse=True)
            
            self.papers_data = papers
            logger.info(f"ML processing complete: {len(papers)} papers processed and ranked")
            
            return papers
            
        except Exception as e:
            logger.error(f"Error in ML processing: {e}")
            # Return papers with default ML scores
            for paper in papers:
                paper.ml_relevance_score = 0.5
                paper.ml_cluster = 0
                paper.ml_summary_confidence = 0.5
            return papers
    
    def get_paper_clusters(self) -> Dict[int, List[Paper]]:
        """
        Group papers by ML clusters
        
        Returns:
            Dictionary mapping cluster ID to list of papers
        """
        clusters = defaultdict(list)
        for paper in self.papers_data:
            clusters[paper.ml_cluster].append(paper)
        return dict(clusters)
    
    def find_similar_papers(self, paper_index: int, top_k: int = 3) -> List[Tuple[Paper, float]]:
        """
        Find similar papers using ML similarity
        
        Args:
            paper_index: Index of target paper
            top_k: Number of similar papers to return
            
        Returns:
            List of (Paper, similarity_score) tuples
        """
        if not self.paper_vectors or paper_index >= len(self.papers_data):
            return []
        
        try:
            target_vector = self.paper_vectors[paper_index:paper_index+1]
            similarities = cosine_similarity(self.paper_vectors[:-1], target_vector).flatten()
            
            # Get top-k similar papers (excluding the target paper itself)
            similar_indices = np.argsort(similarities)[::-1]
            similar_papers = []
            
            for idx in similar_indices:
                if idx != paper_index and len(similar_papers) < top_k:
                    similar_papers.append((self.papers_data[idx], similarities[idx]))
            
            return similar_papers
            
        except Exception as e:
            logger.error(f"Error finding similar papers: {e}")
            return []