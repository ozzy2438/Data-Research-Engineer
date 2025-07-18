"""
Research Service - Enhanced with Perplexity AI
Automated PDF discovery using Perplexity's sonar-deep-research model
"""

import asyncio
import aiohttp
import requests
import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import time
from urllib.parse import urljoin, urlparse
import os
from config import Config

class ResearchService:
    """Advanced research service powered by Perplexity AI"""
    
    def __init__(self):
        self.session = None
        self.download_dir = Path(tempfile.gettempdir()) / "research_pdfs"
        self.download_dir.mkdir(exist_ok=True)
        self.config = Config.get_research_config()
        self.headers = Config.get_perplexity_headers()
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
        return self.session
    
    async def find_pdfs(self, topic: str, max_pdfs: int = 5) -> List[Dict[str, Any]]:
        """
        Find PDFs using Perplexity AI's deep research capabilities
        
        Args:
            topic: Research topic to search for
            max_pdfs: Maximum number of PDFs to find
            
        Returns:
            List of PDF information dictionaries with enhanced metadata
        """
        try:
            print(f"🔍 Starting Perplexity-powered research for: {topic}")
            
            # Use Perplexity's sonar-deep-research for comprehensive PDF discovery
            research_queries = self._generate_research_queries(topic)
            found_pdfs = []
            
            for query in research_queries[:2]:  # Use top 2 most effective queries
                if len(found_pdfs) >= max_pdfs:
                    break
                
                print(f"📊 Researching: {query}")
                pdfs = await self._perplexity_research(query, max_pdfs - len(found_pdfs))
                found_pdfs.extend(pdfs)
                
                # Rate limiting
                await asyncio.sleep(1)
            
            # Enhance with additional metadata and validation
            enhanced_pdfs = await self._enhance_pdf_metadata(found_pdfs[:max_pdfs])
            validated_pdfs = await self._validate_pdfs(enhanced_pdfs)
            
            print(f"✅ Found {len(validated_pdfs)} validated PDFs")
            return validated_pdfs
            
        except Exception as e:
            print(f"❌ Research error: {e}")
            return []
    
    def _generate_research_queries(self, topic: str) -> List[str]:
        """Generate sophisticated research queries optimized for academic content"""
        base_topic = topic.strip()
        
        queries = [
            f"Find recent academic research papers and reports about {base_topic} in PDF format with downloadable links",
            f"Locate comprehensive studies and analysis on {base_topic} published in the last 3 years with full PDF access",
            f"Search for peer-reviewed research, white papers, and technical reports on {base_topic} available as PDF downloads"
        ]
        
        # Add domain-specific academic queries
        if any(word in base_topic.lower() for word in ['ai', 'artificial intelligence', 'machine learning', 'deep learning']):
            queries.append(f"Find AI research papers on {base_topic} from arXiv, IEEE, ACM with PDF links")
        
        if any(word in base_topic.lower() for word in ['climate', 'environment', 'sustainability']):
            queries.append(f"Locate environmental research and climate studies on {base_topic} with PDF access")
        
        if any(word in base_topic.lower() for word in ['health', 'medical', 'healthcare']):
            queries.append(f"Find medical research papers and healthcare studies on {base_topic} with downloadable PDFs")
        
        return queries
    
    async def _perplexity_research(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Use Perplexity AI for advanced research and PDF discovery"""
        try:
            # Enhanced research prompt for PDF discovery
            research_prompt = f"""
            Research task: {query}
            
            Please provide a comprehensive research response that includes:
            1. Key findings and insights about the topic
            2. Direct links to relevant PDF documents (research papers, reports, studies)
            3. For each PDF link, provide: title, source, publication date, and brief description
            4. Focus on authoritative sources: academic institutions, research organizations, government agencies
            5. Prioritize recent publications (last 3-5 years)
            
            Format your response to clearly separate the research insights from the PDF resources.
            """
            
            payload = {
                "model": self.config["model"],
                "messages": [
                    {"role": "user", "content": research_prompt}
                ],
                "max_tokens": self.config["max_tokens"],
                "temperature": 0.3,  # Lower temperature for more focused results
                "top_p": 0.9
            }
            
            # Make synchronous request to Perplexity API
            response = requests.post(
                Config.PERPLEXITY_BASE_URL,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"⚠️ Perplexity API error: {response.status_code}")
                return []
            
            research_data = response.json()
            content = research_data.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Extract PDF links and metadata from the research response
            pdfs = self._extract_pdfs_from_research(content, query)
            
            return pdfs[:max_results]
            
        except Exception as e:
            print(f"❌ Perplexity research error: {e}")
            return []
    
    def _extract_pdfs_from_research(self, content: str, original_query: str) -> List[Dict[str, Any]]:
        """Extract PDF links and metadata from Perplexity research content"""
        pdfs = []
        
        # Enhanced PDF URL patterns
        pdf_patterns = [
            r'https?://[^\s<>"]+\.pdf',  # Direct PDF links
            r'https?://arxiv\.org/pdf/[^\s<>"]+',  # arXiv papers
            r'https?://[^\s<>"]*(?:research|paper|study|report)[^\s<>"]*\.pdf',  # Research PDFs
            r'https?://[^\s<>"]*(?:gov|edu|org)[^\s<>"]*\.pdf'  # Institutional PDFs
        ]
        
        all_urls = []
        for pattern in pdf_patterns:
            urls = re.findall(pattern, content, re.IGNORECASE)
            all_urls.extend(urls)
        
        # Also look for indirect PDF references
        indirect_patterns = [
            r'https?://(?:www\.)?researchgate\.net/[^\s<>"]+',
            r'https?://(?:www\.)?semanticscholar\.org/[^\s<>"]+',
            r'https?://ieeexplore\.ieee\.org/[^\s<>"]+',
            r'https?://dl\.acm\.org/[^\s<>"]+',
            r'https?://link\.springer\.com/[^\s<>"]+',
            r'https?://www\.sciencedirect\.com/[^\s<>"]+',
            r'https?://[^\s<>"]*\.edu/[^\s<>"]*(?:pdf|paper|research)[^\s<>"]*'
        ]
        
        for pattern in indirect_patterns:
            urls = re.findall(pattern, content, re.IGNORECASE)
            all_urls.extend(urls)
        
        # Process each URL and extract metadata
        for url in set(all_urls):  # Remove duplicates
            url = url.rstrip('.,;)')  # Clean trailing punctuation
            
            # Extract title and context from surrounding text
            title, description = self._extract_title_and_description(content, url, original_query)
            
            pdf_info = {
                'url': url,
                'title': title,
                'description': description,
                'source': 'Perplexity AI Research',
                'relevance_score': self._calculate_relevance_score(title, description, original_query),
                'confidence': 0.9,  # High confidence from Perplexity
                'research_context': True
            }
            
            pdfs.append(pdf_info)
        
        # Sort by relevance score
        pdfs.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return pdfs
    
    def _extract_title_and_description(self, content: str, url: str, query: str) -> tuple:
        """Extract title and description from research content around the URL"""
        try:
            # Find the context around the URL
            url_index = content.find(url)
            if url_index == -1:
                return "Research Paper", f"Academic content related to {query}"
            
            # Get surrounding context (500 chars before and after)
            start = max(0, url_index - 500)
            end = min(len(content), url_index + len(url) + 500)
            context = content[start:end]
            
            # Look for title patterns in context
            title_patterns = [
                r'"([^"]+)"',  # Quoted titles
                r'\*\*([^*]+)\*\*',  # Bold markdown titles
                r'Title:\s*([^\n\r]+)',  # Explicit title labels
                r'Paper:\s*([^\n\r]+)',  # Paper labels
                r'Study:\s*([^\n\r]+)'   # Study labels
            ]
            
            title = "Research Document"
            for pattern in title_patterns:
                matches = re.findall(pattern, context, re.IGNORECASE)
                if matches:
                    title = matches[0].strip()[:100]  # Limit length
                    break
            
            # Extract description from nearby sentences
            sentences = re.split(r'[.!?]+', context)
            description = f"Academic research on {query}"
            
            for sentence in sentences:
                if len(sentence.strip()) > 20 and any(word in sentence.lower() for word in query.lower().split()):
                    description = sentence.strip()[:200]  # Limit length
                    break
            
            return title, description
            
        except Exception:
            return "Research Paper", f"Academic content related to {query}"
    
    def _calculate_relevance_score(self, title: str, description: str, query: str) -> float:
        """Calculate relevance score based on content similarity"""
        try:
            query_words = set(query.lower().split())
            text_words = set((title + " " + description).lower().split())
            
            # Simple word overlap scoring
            overlap = len(query_words.intersection(text_words))
            total_query_words = len(query_words)
            
            if total_query_words == 0:
                return 0.5
            
            # Base score from word overlap
            base_score = overlap / total_query_words
            
            # Boost for academic indicators
            academic_indicators = ['research', 'study', 'analysis', 'paper', 'report', 'journal', 'conference']
            academic_boost = sum(1 for indicator in academic_indicators if indicator in text_words.union(query_words)) * 0.1
            
            # Boost for recent content indicators
            recent_indicators = ['2024', '2023', '2022', 'recent', 'latest', 'current']
            recent_boost = sum(1 for indicator in recent_indicators if indicator in text_words) * 0.05
            
            final_score = min(1.0, base_score + academic_boost + recent_boost)
            return round(final_score, 2)
            
        except Exception:
            return 0.5
    
    async def _enhance_pdf_metadata(self, pdfs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance PDF metadata with additional information"""
        enhanced_pdfs = []
        
        for pdf in pdfs:
            try:
                # Add domain classification
                domain = self._classify_domain(pdf['url'])
                pdf['domain_type'] = domain
                
                # Add estimated quality score
                quality_score = self._estimate_quality(pdf)
                pdf['estimated_quality'] = quality_score
                
                # Add publication type
                pub_type = self._classify_publication_type(pdf['url'], pdf['title'])
                pdf['publication_type'] = pub_type
                
                enhanced_pdfs.append(pdf)
                
            except Exception as e:
                print(f"⚠️ Enhancement error for {pdf.get('url', 'unknown')}: {e}")
                enhanced_pdfs.append(pdf)  # Include anyway
        
        return enhanced_pdfs
    
    def _classify_domain(self, url: str) -> str:
        """Classify the domain type of the PDF source"""
        domain = urlparse(url).netloc.lower()
        
        if '.edu' in domain:
            return 'Academic Institution'
        elif '.gov' in domain:
            return 'Government/Official'
        elif any(site in domain for site in ['arxiv', 'researchgate', 'semanticscholar']):
            return 'Research Repository'
        elif any(site in domain for site in ['ieee', 'acm', 'springer']):
            return 'Academic Publisher'
        elif '.org' in domain:
            return 'Organization/NGO'
        else:
            return 'Other'
    
    def _estimate_quality(self, pdf: Dict[str, Any]) -> float:
        """Estimate PDF quality based on available metadata"""
        score = 0.5  # Base score
        
        # Boost for academic domains
        if pdf.get('domain_type') in ['Academic Institution', 'Research Repository', 'Academic Publisher']:
            score += 0.3
        
        # Boost for high relevance
        if pdf.get('relevance_score', 0) > 0.7:
            score += 0.2
        
        # Boost for research context
        if pdf.get('research_context'):
            score += 0.1
        
        return min(1.0, round(score, 2))
    
    def _classify_publication_type(self, url: str, title: str) -> str:
        """Classify the type of publication"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        if 'arxiv' in url_lower:
            return 'Preprint'
        elif any(word in title_lower for word in ['conference', 'proceedings']):
            return 'Conference Paper'
        elif any(word in title_lower for word in ['journal', 'article']):
            return 'Journal Article'
        elif any(word in title_lower for word in ['report', 'white paper']):
            return 'Technical Report'
        elif any(word in title_lower for word in ['thesis', 'dissertation']):
            return 'Thesis/Dissertation'
        else:
            return 'Research Document'
    
    async def _validate_pdfs(self, pdfs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate PDF accessibility with enhanced checks"""
        session = await self._get_session()
        valid_pdfs = []
        
        for pdf in pdfs:
            try:
                # Quick HEAD request to check accessibility
                async with session.head(pdf['url'], allow_redirects=True) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '').lower()
                        content_length = response.headers.get('Content-Length', '0')
                        
                        # Enhanced validation
                        is_valid = (
                            'pdf' in content_type or 
                            pdf['url'].lower().endswith('.pdf') or
                            int(content_length) > 1024  # At least 1KB
                        )
                        
                        if is_valid:
                            pdf['content_type'] = content_type
                            pdf['content_length'] = content_length
                            pdf['validated'] = True
                            valid_pdfs.append(pdf)
                    
            except Exception as e:
                print(f"⚠️ Validation failed for {pdf['url']}: {e}")
                # Include anyway with lower confidence
                pdf['validated'] = False
                pdf['validation_error'] = str(e)
                valid_pdfs.append(pdf)
            
            # Rate limiting
            await asyncio.sleep(0.3)
        
        return valid_pdfs
    
    async def download_pdf(self, url: str, job_id: str, pdf_index: int) -> Optional[str]:
        """
        Download a PDF from URL with enhanced error handling
        
        Args:
            url: PDF URL to download
            job_id: Job identifier for organization
            pdf_index: Index of PDF in the batch
            
        Returns:
            Path to downloaded PDF file, or None if failed
        """
        try:
            session = await self._get_session()
            
            # Create unique filename
            filename = f"research_{job_id}_{pdf_index}.pdf"
            pdf_path = self.download_dir / filename
            
            print(f"📥 Downloading: {url}")
            
            async with session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    print(f"❌ Download failed: HTTP {response.status}")
                    return None
                
                # Read content
                content = await response.read()
                
                # Enhanced PDF validation
                if not self._validate_pdf_content(content):
                    print(f"❌ Invalid PDF content from {url}")
                    return None
                
                # Save PDF
                with open(pdf_path, 'wb') as f:
                    f.write(content)
                
                # Verify file was written correctly
                if pdf_path.exists() and pdf_path.stat().st_size > 1024:  # At least 1KB
                    print(f"✅ Downloaded: {filename} ({len(content)} bytes)")
                    return str(pdf_path)
                
                return None
                
        except Exception as e:
            print(f"❌ Download error for {url}: {e}")
            return None
    
    def _validate_pdf_content(self, content: bytes) -> bool:
        """Validate that content is actually a PDF"""
        try:
            # Check PDF magic number
            if content.startswith(b'%PDF-'):
                return True
            
            # Check for common PDF patterns
            pdf_patterns = [b'PDF', b'Adobe', b'Acrobat']
            return any(pattern in content[:1024] for pattern in pdf_patterns)
            
        except Exception:
            return False
    
    async def cleanup_downloads(self, job_id: str):
        """Clean up downloaded files for a job"""
        try:
            pattern = f"research_{job_id}_*.pdf"
            for file_path in self.download_dir.glob(pattern):
                file_path.unlink()
                print(f"🗑️ Cleaned up: {file_path.name}")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None 