"""
Configuration settings for ML Research Assistant
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_API_KEY = os.getenv('SEMANTIC_SCHOLAR_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Rate Limiting
REQUEST_DELAY = 1.2  # seconds between requests
TIMEOUT = 30  # seconds

# ML Configuration
MAX_TF_IDF_FEATURES = 1000
NGRAM_RANGE = (1, 2)
MAX_CLUSTERS = 3
MIN_PAPERS_FOR_CLUSTERING = 4

# Search Configuration
DEFAULT_PAPER_LIMIT = 20  # Changed default from 10 to 20
MAX_PAPER_LIMIT = 50
FIELDS = "paperId,title,authors,year,abstract,url,citationCount,venue,externalIds,tldr,fieldsOfStudy,influentialCitationCount,openAccessPdf"

# Thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.7
MEDIUM_CONFIDENCE_THRESHOLD = 0.5
HIGH_RELEVANCE_THRESHOLD = 0.6
MEDIUM_RELEVANCE_THRESHOLD = 0.3
RECENT_YEAR_THRESHOLD = 2020

# Consensus Analysis
STRONG_POSITIVE_THRESHOLD = 70
MODERATE_POSITIVE_THRESHOLD = 55
MODERATE_NEGATIVE_THRESHOLD = 45
STRONG_NEGATIVE_THRESHOLD = 30

# Data Storage
DATA_DIR = 'data'
SESSION_FILE = 'research_session.pkl'

# UI Configuration
PAGE_TITLE = "ML Research Assistant - Final Year Project"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# Sentiment Indicators
POSITIVE_INDICATORS = [
    'effective', 'improves', 'increases', 'beneficial', 'positive', 'significantly',
    'reduces', 'decreases', 'prevents', 'enhances', 'better', 'successful',
    'improvement', 'correlation', 'associated with', 'leads to'
]

NEGATIVE_INDICATORS = [
    'ineffective', 'no effect', 'no difference', 'harmful', 'negative',
    'worse', 'fails', 'unsuccessful', 'no significant', 'not significant',
    'no improvement', 'no correlation', 'unrelated'
]