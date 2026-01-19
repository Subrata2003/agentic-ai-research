"""Web research module for searching and extracting content"""

import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from src.utils.config import Config


class WebResearcher:
    """Handles web search and content extraction"""
    
    def __init__(self):
        self.tavily_tool = None
        self.duckduckgo_wrapper = None
        
        # Initialize Tavily if API key is available
        if Config.TAVILY_API_KEY:
            try:
                self.tavily_tool = TavilySearchResults(
                    max_results=Config.MAX_SEARCH_RESULTS,
                    api_key=Config.TAVILY_API_KEY
                )
            except Exception as e:
                print(f"Warning: Could not initialize Tavily: {e}")
        
        # Initialize DuckDuckGo as fallback
        try:
            self.duckduckgo_wrapper = DuckDuckGoSearchAPIWrapper()
        except Exception as e:
            print(f"Warning: Could not initialize DuckDuckGo: {e}")
    
    def search(self, query: str, num_results: int = None) -> List[Dict[str, str]]:
        """
        Search the web for information about a query
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            List of dictionaries with 'title', 'url', and 'content' keys
        """
        num_results = num_results or Config.MAX_SEARCH_RESULTS
        results = []
        
        # Try Tavily first (better quality)
        if self.tavily_tool:
            try:
                tavily_results = self.tavily_tool.invoke({"query": query})
                for result in tavily_results[:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "source": "tavily"
                    })
                if results:
                    return results
            except Exception as e:
                print(f"Tavily search failed: {e}, trying DuckDuckGo...")
        
        # Fallback to DuckDuckGo
        if self.duckduckgo_wrapper:
            try:
                ddg_results = self.duckduckgo_wrapper.results(query, max_results=num_results)
                for result in ddg_results[:num_results]:
                    url = result.get("link", "")
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    
                    # Try to extract more content from the page
                    content = self._extract_content(url) or snippet
                    
                    results.append({
                        "title": title,
                        "url": url,
                        "content": content[:Config.MAX_CONTENT_LENGTH],
                        "source": "duckduckgo"
                    })
            except Exception as e:
                print(f"DuckDuckGo search failed: {e}")
        
        return results
    
    def _extract_content(self, url: str) -> Optional[str]:
        """Extract main content from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Try to find main content
            main_content = (
                soup.find('main') or
                soup.find('article') or
                soup.find('div', class_='content') or
                soup.find('div', id='content') or
                soup
            )
            
            # Get text
            text = main_content.get_text(separator=' ', strip=True)
            return text[:Config.MAX_CONTENT_LENGTH]
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None
    
    def research_topic(self, topic: str, depth: str = "medium") -> List[Dict[str, str]]:
        """
        Conduct research on a topic with varying depth
        
        Args:
            topic: Research topic
            depth: Research depth (shallow: 5 results, medium: 10, deep: 20)
            
        Returns:
            List of research results
        """
        num_results_map = {
            "shallow": 5,
            "medium": 10,
            "deep": 20
        }
        num_results = num_results_map.get(depth, 10)
        
        # Generate search queries for comprehensive research
        queries = self._generate_search_queries(topic, depth)
        
        all_results = []
        seen_urls = set()
        
        for query in queries:
            results = self.search(query, num_results=num_results // len(queries))
            for result in results:
                if result["url"] not in seen_urls:
                    seen_urls.add(result["url"])
                    all_results.append(result)
        
        return all_results[:num_results]
    
    def _generate_search_queries(self, topic: str, depth: str) -> List[str]:
        """Generate multiple search queries for comprehensive research"""
        base_queries = [topic]
        
        if depth == "deep":
            # Add variations for deep research
            base_queries.extend([
                f"{topic} overview",
                f"{topic} analysis",
                f"{topic} trends",
                f"{topic} impact"
            ])
        elif depth == "medium":
            base_queries.extend([
                f"{topic} overview",
                f"{topic} analysis"
            ])
        
        return base_queries
