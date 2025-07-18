"""
Configuration for Data Research Engineer
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Perplexity AI Settings
    PERPLEXITY_API_KEY = "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"
    PERPLEXITY_BASE_URL = "https://api.perplexity.ai/chat/completions"
    PERPLEXITY_MODEL = "sonar-deep-research"
    PERPLEXITY_MAX_TOKENS = 1000
    
    # Research Settings
    MAX_RESEARCH_PDFS = 10
    RESEARCH_TIMEOUT = 300
    PDF_SEARCH_DEPTH = 3
    
    # Application Settings
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_perplexity_headers(cls):
        """Get headers for Perplexity API requests"""
        return {
            "Authorization": f"Bearer {cls.PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def get_research_config(cls):
        """Get research configuration"""
        return {
            "model": cls.PERPLEXITY_MODEL,
            "max_tokens": cls.PERPLEXITY_MAX_TOKENS,
            "max_pdfs": cls.MAX_RESEARCH_PDFS,
            "timeout": cls.RESEARCH_TIMEOUT,
            "search_depth": cls.PDF_SEARCH_DEPTH
        } 