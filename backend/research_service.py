"""
Research Service
Automated PDF discovery and download for research topics
"""

import asyncio
import aiohttp
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile
import time
from urllib.parse import urljoin, urlparse
import os

class ResearchService:
    """Service for finding and downloading research PDFs"""
    
    def __init__(self):
        self.session = None
        self.download_dir = Path(tempfile.gettempdir()) / "research_pdfs"
        self.download_dir.mkdir(exist_ok=True)
    
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
        Find PDFs related to a research topic using web search
        
        Args:
            topic: Research topic to search for
            max_pdfs: Maximum number of PDFs to find
            
        Returns:
            List of PDF information dictionaries
        """
        try:
            # Search for PDFs using multiple strategies
            search_queries = self._generate_search_queries(topic)
            found_pdfs = []
            
            for query in search_queries[:3]:  # Try top 3 queries
                if len(found_pdfs) >= max_pdfs:
                    break
                
                # Search using Google (via web scraping)
                pdfs = await self._search_google_pdfs(query, max_pdfs - len(found_pdfs))
                found_pdfs.extend(pdfs)
                
                # Add delay between searches
                await asyncio.sleep(1)
            
            # Remove duplicates and validate
            unique_pdfs = self._deduplicate_pdfs(found_pdfs)
            validated_pdfs = await self._validate_pdfs(unique_pdfs[:max_pdfs])
            
            return validated_pdfs
            
        except Exception as e:
            print(f"Error finding PDFs: {e}")
            return []
    
    def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate effective search queries for PDF discovery"""
        base_topic = topic.strip()
        
        queries = [
            f"{base_topic} filetype:pdf",
            f"{base_topic} research paper filetype:pdf",
            f"{base_topic} study analysis filetype:pdf",
            f'"{base_topic}" PDF download',
            f"{base_topic} report findings PDF"
        ]
        
        # Add academic-specific queries
        if any(word in base_topic.lower() for word in ['machine learning', 'ai', 'artificial intelligence', 'data science']):
            queries.extend([
                f"{base_topic} arxiv filetype:pdf",
                f"{base_topic} conference paper filetype:pdf"
            ])
        
        return queries
    
    async def _search_google_pdfs(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Google for PDFs (simplified version)"""
        try:
            session = await self._get_session()
            
            # Google search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={max_results * 2}"
            
            async with session.get(search_url) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                
                # Extract PDF links from search results
                pdf_pattern = r'href="([^"]*\.pdf)"'
                pdf_links = re.findall(pdf_pattern, html)
                
                # Also look for links that might lead to PDFs
                general_links = re.findall(r'href="(https?://[^"]*)"', html)
                
                pdfs = []
                all_links = list(set(pdf_links + general_links))[:max_results * 3]
                
                for link in all_links:
                    if len(pdfs) >= max_results:
                        break
                    
                    # Clean up link
                    if link.startswith('/url?q='):
                        link = link[7:].split('&')[0]
                    
                    # Check if it's a PDF or might contain PDFs
                    if self._is_pdf_link(link):
                        title = self._extract_title_from_url(link)
                        pdfs.append({
                            'url': link,
                            'title': title,
                            'source': 'Google Search',
                            'relevance_score': 1.0
                        })
                
                return pdfs
                
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    def _is_pdf_link(self, url: str) -> bool:
        """Check if URL is likely to be a PDF"""
        if not url or not url.startswith('http'):
            return False
        
        # Direct PDF links
        if url.lower().endswith('.pdf'):
            return True
        
        # Common PDF hosting patterns
        pdf_patterns = [
            'arxiv.org/pdf/',
            'researchgate.net/',
            'semanticscholar.org/',
            'ieeexplore.ieee.org/',
            'acm.org/',
            'springer.com/',
            'sciencedirect.com/',
            '.edu/',
            'github.com/',
            'papers.nips.cc/',
            'openreview.net/'
        ]
        
        return any(pattern in url.lower() for pattern in pdf_patterns)
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a reasonable title from URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # Remove file extension
            if path.endswith('.pdf'):
                path = path[:-4]
            
            # Get filename or last path component
            title = path.split('/')[-1] if '/' in path else path
            
            # Clean up
            title = title.replace('_', ' ').replace('-', ' ')
            title = re.sub(r'[^a-zA-Z0-9\s]', ' ', title)
            title = ' '.join(title.split())  # Normalize whitespace
            
            return title[:100] if title else "Research Paper"
            
        except:
            return "Research Paper"
    
    def _deduplicate_pdfs(self, pdfs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate PDFs based on URL"""
        seen_urls = set()
        unique_pdfs = []
        
        for pdf in pdfs:
            url = pdf.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_pdfs.append(pdf)
        
        return unique_pdfs
    
    async def _validate_pdfs(self, pdfs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate that PDFs are accessible"""
        session = await self._get_session()
        valid_pdfs = []
        
        for pdf in pdfs:
            try:
                # Quick HEAD request to check if PDF is accessible
                async with session.head(pdf['url'], allow_redirects=True) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '').lower()
                        if 'pdf' in content_type or pdf['url'].lower().endswith('.pdf'):
                            valid_pdfs.append(pdf)
                        else:
                            # Try to check if it might be a page with PDF download
                            valid_pdfs.append(pdf)  # Be permissive for now
                    
            except Exception as e:
                print(f"Validation failed for {pdf['url']}: {e}")
                continue
            
            # Add small delay between requests
            await asyncio.sleep(0.5)
        
        return valid_pdfs
    
    async def download_pdf(self, url: str, job_id: str, pdf_index: int) -> Optional[str]:
        """
        Download a PDF from URL
        
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
            
            async with session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    print(f"Failed to download PDF: HTTP {response.status}")
                    return None
                
                # Check content type
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Read content
                content = await response.read()
                
                # Basic PDF validation
                if not content.startswith(b'%PDF-'):
                    # Might be HTML page, try to find PDF link
                    if b'pdf' in content.lower():
                        print(f"Downloaded HTML instead of PDF from {url}")
                        return None
                    print(f"Invalid PDF content from {url}")
                    return None
                
                # Save PDF
                with open(pdf_path, 'wb') as f:
                    f.write(content)
                
                # Verify file was written
                if pdf_path.exists() and pdf_path.stat().st_size > 1024:  # At least 1KB
                    return str(pdf_path)
                
                return None
                
        except Exception as e:
            print(f"Download error for {url}: {e}")
            return None
    
    async def cleanup_downloads(self, job_id: str):
        """Clean up downloaded files for a job"""
        try:
            pattern = f"research_{job_id}_*.pdf"
            for file_path in self.download_dir.glob(pattern):
                file_path.unlink()
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()
            self.session = None 