"""
🔍 FACT SEARCHER - Research real information for documentaries
Uses web search to get REAL facts for authentic content
"""

import requests
from typing import Dict, List, Optional
from src.utils.logger import logger
from datetime import datetime


class FactSearcher:
    """Search for real facts about topics using free APIs"""
    
    def __init__(self):
        self.wikipedia_api = "https://en.wikipedia.org/w/api.php"
        self.duckduckgo_api = "https://api.duckduckgo.com/"
        self.cache = {}
    
    def search_facts(self, topic: str, story_type: str = "story") -> Dict:
        """
        Search for real facts about topic
        Returns research data to add to script
        """
        
        # Check cache first
        if topic in self.cache:
            logger.info(f"📚 Using cached facts for: {topic}")
            return self.cache[topic]
        
        logger.info(f"🔍 Searching facts for: {topic}")
        
        # Determine if research is needed
        needs_research = [
            "historical_documentary",
            "true_crime",
            "biographical_life",
            "conspiracy_mystery",
            "nature_wildlife",
            "science_education"
        ]
        
        if story_type not in needs_research:
            logger.info("ℹ️ Story type doesn't require research")
            return {
                "needs_research": False,
                "topic": topic,
                "research_data": ""
            }
        
        # Search Wikipedia
        wiki_facts = self._search_wikipedia(topic)
        
        # Search general facts
        general_facts = self._search_facts_general(topic)
        
        result = {
            "needs_research": True,
            "topic": topic,
            "story_type": story_type,
            "research_data": self._format_research_data(wiki_facts, general_facts),
            "sources": {
                "wikipedia": len(wiki_facts) > 0,
                "general": len(general_facts) > 0,
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the result
        self.cache[topic] = result
        
        logger.success(f"✅ Found {len(wiki_facts)} Wikipedia facts")
        
        return result
    
    def _search_wikipedia(self, topic: str) -> List[str]:
        """Search Wikipedia for facts"""
        
        try:
            params = {
                "action": "query",
                "format": "json",
                "titles": topic,
                "prop": "extracts",
                "explaintext": True,
                "exintro": True,
                "exsectionformat": "plain"
            }
            
            response = requests.get(self.wikipedia_api, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            facts = []
            for page_id, page_data in pages.items():
                if page_id != "-1":  # Valid page
                    extract = page_data.get("extract", "")
                    
                    # Extract key sentences
                    sentences = extract.split('. ')[:5]  # First 5 sentences
                    facts.extend([s.strip() for s in sentences if s.strip()])
            
            return facts
        
        except Exception as e:
            logger.warning(f"⚠️ Wikipedia search failed: {e}")
            return []
    
    def _search_facts_general(self, topic: str) -> List[str]:
        """Search general facts using DuckDuckGo"""
        
        try:
            params = {
                "q": f"{topic} facts",
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(self.duckduckgo_api, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            facts = []
            
            # Get abstract
            if data.get("Abstract"):
                facts.append(data["Abstract"])
            
            # Get related topics (brief facts)
            related = data.get("RelatedTopics", [])
            for item in related[:3]:
                if "Text" in item:
                    facts.append(item["Text"])
            
            return facts
        
        except Exception as e:
            logger.warning(f"⚠️ General search failed: {e}")
            return []
    
    def _format_research_data(self, wiki_facts: List[str], general_facts: List[str]) -> str:
        """Format research data for Gemini prompt"""
        
        if not wiki_facts and not general_facts:
            return ""
        
        formatted = "📚 RESEARCH FACTS:\n\n"
        
        if wiki_facts:
            formatted += "Wikipedia:\n"
            for i, fact in enumerate(wiki_facts[:3], 1):
                if fact:
                    formatted += f"{i}. {fact}\n"
            formatted += "\n"
        
        if general_facts:
            formatted += "Additional Facts:\n"
            for i, fact in enumerate(general_facts[:2], 1):
                if fact:
                    formatted += f"{i}. {fact}\n"
        
        return formatted
    
    def search_multiple_topics(self, topics: List[str]) -> Dict[str, Dict]:
        """Search facts for multiple topics"""
        
        results = {}
        for topic in topics:
            results[topic] = self.search_facts(topic)
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        
        return {
            "cached_topics": len(self.cache),
            "topics": list(self.cache.keys()),
            "cache_size": len(str(self.cache))
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("🧹 Cache cleared")


# Create singleton instance
fact_searcher = FactSearcher()