"""
Stock Image Agent: Fetches images from stock photo APIs (Unsplash, Pexels, Pixabay)
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import json

from ai_db import get_ai_db

# Import config module
import importlib.util
from pathlib import Path
config_file = Path(__file__).parent.parent / "config.py"
spec = importlib.util.spec_from_file_location("ai_config", config_file)
ai_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_config)
get_config = ai_config.get_config

logger = logging.getLogger(__name__)


class StockImageAgent:
    """Agent that fetches stock images from various APIs"""
    
    def __init__(self):
        self.db = get_ai_db()
        self.media_collection = self.db["media"]
        self.cache_collection = self.db["ai_cache"]
        self.config = get_config()
        
        # Get stock image API configuration
        self.provider = (self.config.stock_image_provider or "unsplash").lower()
        self.api_key = self.config.unsplash_api_key or self.config.pexels_api_key or self.config.pixabay_api_key
        
        # Provider-specific settings
        self.providers = {
            "unsplash": {
                "base_url": "https://api.unsplash.com",
                "search_endpoint": "/search/photos",
                "headers": lambda key: {"Authorization": f"Client-ID {key}"} if key else {}
            },
            "pexels": {
                "base_url": "https://api.pexels.com",
                "search_endpoint": "/v1/search",
                "headers": lambda key: {"Authorization": key} if key else {}
            },
            "pixabay": {
                "base_url": "https://pixabay.com/api",
                "search_endpoint": "",
                "headers": lambda key: {}
            }
        }
    
    def _get_cache_key(self, query: str, provider: str) -> str:
        """Generate cache key for search query"""
        cache_data = f"stock_{provider}_{query}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Check if search results exist in cache"""
        try:
            cached = self.cache_collection.find_one({"cache_key": cache_key, "type": "stock_image"})
            if cached and cached.get("ttl", 0) > datetime.utcnow().timestamp():
                return cached.get("results", [])
        except Exception as e:
            logger.warning(f"Cache check failed: {e}")
        return None
    
    def _store_cache(self, cache_key: str, results: List[Dict[str, Any]], ttl: int = 86400):
        """Store search results in cache"""
        try:
            self.cache_collection.update_one(
                {"cache_key": cache_key, "type": "stock_image"},
                {
                    "$set": {
                        "cache_key": cache_key,
                        "type": "stock_image",
                        "results": results,
                        "ttl": datetime.utcnow().timestamp() + ttl,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.warning(f"Cache store failed: {e}")
    
    def _search_unsplash(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """Search Unsplash API"""
        if not self.api_key:
            return {"success": False, "error": "Unsplash API key not configured"}
        
        try:
            provider_config = self.providers["unsplash"]
            url = f"{provider_config['base_url']}{provider_config['search_endpoint']}"
            headers = provider_config["headers"](self.api_key)
            
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape",  # Better for slides
                "content_filter": "high"  # High quality only
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get("results", []):
                results.append({
                    "id": photo.get("id"),
                    "url": photo["urls"].get("regular") or photo["urls"].get("small"),
                    "thumbnail": photo["urls"].get("thumb"),
                    "full": photo["urls"].get("full"),
                    "description": photo.get("description") or photo.get("alt_description", ""),
                    "author": photo.get("user", {}).get("name", "Unknown"),
                    "author_url": photo.get("user", {}).get("links", {}).get("html", ""),
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                    "provider": "unsplash",
                    "download_location": photo.get("links", {}).get("download_location", "")
                })
            
            return {
                "success": True,
                "results": results,
                "total": data.get("total", len(results))
            }
        except Exception as e:
            logger.error(f"Unsplash API error: {e}")
            return {"success": False, "error": str(e), "results": []}
    
    def _search_pexels(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """Search Pexels API"""
        if not self.api_key:
            return {"success": False, "error": "Pexels API key not configured"}
        
        try:
            provider_config = self.providers["pexels"]
            url = f"{provider_config['base_url']}{provider_config['search_endpoint']}"
            headers = provider_config["headers"](self.api_key)
            
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get("photos", []):
                results.append({
                    "id": str(photo.get("id")),
                    "url": photo.get("src", {}).get("large") or photo.get("src", {}).get("medium"),
                    "thumbnail": photo.get("src", {}).get("medium"),
                    "full": photo.get("src", {}).get("original"),
                    "description": photo.get("alt", ""),
                    "author": photo.get("photographer", "Unknown"),
                    "author_url": photo.get("photographer_url", ""),
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                    "provider": "pexels"
                })
            
            return {
                "success": True,
                "results": results,
                "total": data.get("total_results", len(results))
            }
        except Exception as e:
            logger.error(f"Pexels API error: {e}")
            return {"success": False, "error": str(e), "results": []}
    
    def _search_pixabay(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        """Search Pixabay API"""
        if not self.api_key:
            return {"success": False, "error": "Pixabay API key not configured"}
        
        try:
            provider_config = self.providers["pixabay"]
            url = f"{provider_config['base_url']}{provider_config['search_endpoint']}"
            
            params = {
                "key": self.api_key,
                "q": query,
                "image_type": "photo",
                "orientation": "horizontal",
                "safesearch": "true",
                "per_page": per_page
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for hit in data.get("hits", []):
                results.append({
                    "id": str(hit.get("id")),
                    "url": hit.get("webformatURL") or hit.get("largeImageURL"),
                    "thumbnail": hit.get("previewURL"),
                    "full": hit.get("fullHDURL") or hit.get("largeImageURL"),
                    "description": hit.get("tags", ""),
                    "author": hit.get("user", "Unknown"),
                    "author_url": f"https://pixabay.com/users/{hit.get('user', '')}-{hit.get('user_id', '')}/",
                    "width": hit.get("imageWidth"),
                    "height": hit.get("imageHeight"),
                    "provider": "pixabay"
                })
            
            return {
                "success": True,
                "results": results,
                "total": data.get("totalHits", len(results))
            }
        except Exception as e:
            logger.error(f"Pixabay API error: {e}")
            return {"success": False, "error": str(e), "results": []}
    
    def search(self,
               query: str,
               provider: Optional[str] = None,
               per_page: int = 10,
               use_cache: bool = True) -> Dict[str, Any]:
        """
        Search for stock images
        
        Args:
            query: Search query
            provider: API provider (unsplash, pexels, pixabay). Uses config default if None
            per_page: Number of results to return
            use_cache: Whether to use cache
        
        Returns:
            Dict with search results
        """
        provider = (provider or self.provider).lower()
        
        if provider not in self.providers:
            return {"success": False, "error": f"Unknown provider: {provider}"}
        
        # Check cache
        cache_key = self._get_cache_key(query, provider)
        if use_cache:
            cached_results = self._check_cache(cache_key)
            if cached_results:
                return {
                    "success": True,
                    "results": cached_results,
                    "cached": True
                }
        
        # Search API
        if provider == "unsplash":
            result = self._search_unsplash(query, per_page)
        elif provider == "pexels":
            result = self._search_pexels(query, per_page)
        elif provider == "pixabay":
            result = self._search_pixabay(query, per_page)
        else:
            return {"success": False, "error": f"Provider {provider} not implemented"}
        
        # Cache results
        if result.get("success") and use_cache:
            self._store_cache(cache_key, result.get("results", []))
        
        return result
    
    def get_image_for_slide(self,
                           slide_title: str,
                           slide_content: List[str],
                           context: Optional[Dict] = None,
                           provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a stock image for a slide based on its content
        
        Args:
            slide_title: Title of the slide
            slide_content: Content/bullets of the slide
            context: Additional context (subject, grade_level, etc.)
            provider: API provider to use
        
        Returns:
            Dict with image URL and metadata
        """
        try:
            # Build search query from slide content
            query = self._build_search_query(slide_title, slide_content, context)
            
            # Search for images
            search_result = self.search(query, provider=provider, per_page=5)
            
            if not search_result.get("success") or not search_result.get("results"):
                return {
                    "success": False,
                    "error": "No images found",
                    "query": query
                }
            
            # Select best image (first result for now, could add ranking logic)
            image = search_result["results"][0]
            
            # Store in media collection
            media_doc = {
                "type": "stock_image",
                "provider": image["provider"],
                "image_id": image["id"],
                "url": image["url"],
                "thumbnail": image.get("thumbnail"),
                "full_url": image.get("full"),
                "description": image.get("description", ""),
                "author": image.get("author", ""),
                "author_url": image.get("author_url", ""),
                "slide_title": slide_title,
                "query": query,
                "width": image.get("width"),
                "height": image.get("height"),
                "created_at": datetime.utcnow()
            }
            
            media_result = self.media_collection.insert_one(media_doc)
            
            return {
                "success": True,
                "url": image["url"],
                "thumbnail": image.get("thumbnail"),
                "full_url": image.get("full"),
                "media_id": str(media_result.inserted_id),
                "provider": image["provider"],
                "description": image.get("description", ""),
                "author": image.get("author", ""),
                "query": query,
                "metadata": image
            }
            
        except Exception as e:
            logger.error(f"Stock image search failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_images_from_markers(self,
                               markers: List[Dict[str, Any]],
                               context: Optional[Dict] = None,
                               provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get stock images based on image markers from slide generation
        
        Args:
            markers: List of image marker dicts with prompts/descriptions
            context: Additional context
            provider: API provider to use
        
        Returns:
            Dict with list of image results
        """
        items = []
        errors = []
        
        for marker in markers:
            prompt = marker.get("prompt") or marker.get("description") or marker.get("text", "")
            slide_title = marker.get("slide_title", "")
            
            if not prompt:
                errors.append(f"Marker missing prompt: {marker}")
                continue
            
            # Build query from marker
            query = self._build_query_from_prompt(prompt, slide_title, context)
            
            # Search
            search_result = self.search(query, provider=provider, per_page=3)
            
            if search_result.get("success") and search_result.get("results"):
                image = search_result["results"][0]  # Take first result
                
                # Store in media collection
                media_doc = {
                    "type": "stock_image",
                    "provider": image["provider"],
                    "image_id": image["id"],
                    "url": image["url"],
                    "thumbnail": image.get("thumbnail"),
                    "full_url": image.get("full"),
                    "description": image.get("description", ""),
                    "author": image.get("author", ""),
                    "author_url": image.get("author_url", ""),
                    "slide_title": slide_title,
                    "query": query,
                    "marker": marker,
                    "width": image.get("width"),
                    "height": image.get("height"),
                    "created_at": datetime.utcnow()
                }
                
                media_result = self.media_collection.insert_one(media_doc)
                
                items.append({
                    "url": image["url"],
                    "thumbnail": image.get("thumbnail"),
                    "full_url": image.get("full"),
                    "media_id": str(media_result.inserted_id),
                    "provider": image["provider"],
                    "description": image.get("description", ""),
                    "author": image.get("author", ""),
                    "query": query,
                    "slide_index": marker.get("slide_index"),
                    "slide_title": slide_title,
                    "metadata": image
                })
            else:
                errors.append(f"No images found for query: {query}")
        
        return {
            "success": len(items) > 0,
            "items": items,
            "errors": errors if errors else None
        }
    
    def _build_search_query(self,
                           slide_title: str,
                           slide_content: List[str],
                           context: Optional[Dict] = None) -> str:
        """Build search query from slide content"""
        # Extract key terms from title and first few bullets
        query_parts = [slide_title]
        
        # Add first few content items
        if slide_content:
            query_parts.extend(slide_content[:2])
        
        # Add context if available
        if context:
            subject = context.get("subject", "")
            if subject:
                query_parts.append(subject)
        
        # Combine and clean
        query = " ".join(query_parts)
        
        # Remove common words and limit length
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = [w for w in query.lower().split() if w not in stop_words and len(w) > 2]
        
        # Take first 5-6 meaningful words
        return " ".join(words[:6])
    
    def _build_query_from_prompt(self,
                                prompt: str,
                                slide_title: str,
                                context: Optional[Dict] = None) -> str:
        """Build search query from image generation prompt"""
        # Remove common image generation terms
        prompt_clean = prompt.lower()
        remove_terms = [
            "high quality", "detailed", "professional", "illustration",
            "educational", "classroom-appropriate", "clear", "colorful",
            "generate", "create", "image of", "picture of", "photo of"
        ]
        
        for term in remove_terms:
            prompt_clean = prompt_clean.replace(term, "")
        
        # Combine with slide title if available
        if slide_title:
            query = f"{slide_title} {prompt_clean}".strip()
        else:
            query = prompt_clean.strip()
        
        # Limit length
        words = query.split()[:6]
        return " ".join(words)

