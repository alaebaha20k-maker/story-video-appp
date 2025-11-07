"""
📥 STOCK DOWNLOADER - Downloads stock media from Pexels
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
import time
from typing import List, Dict, Optional

from config.settings import PEXELS_SETTINGS
from src.utils.api_manager import api_manager
from src.utils.file_handler import file_handler


class StockDownloader:
    """Downloads stock photos and videos from Pexels API"""
    
    def __init__(self):
        self.api_key = api_manager.get_key('pexels')
        if not self.api_key:
            print("⚠️  Pexels API key not found")
            print("Get FREE key: https://www.pexels.com/api/")
        
        self.base_url = "https://api.pexels.com/v1"
        self.video_url = "https://api.pexels.com/videos"
        self.headers = {"Authorization": self.api_key} if self.api_key else {}
    
    def search_photos(
        self,
        query: str,
        per_page: int = 15,
        orientation: str = "landscape"
    ) -> List[Dict]:
        """Search for photos on Pexels"""
        
        if not self.api_key:
            return []
        
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("photos", [])
            else:
                print(f"⚠️  Pexels API error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"❌ Error searching photos: {e}")
            return []
    
    def search_videos(
        self,
        query: str,
        per_page: int = 15,
        orientation: str = "landscape"
    ) -> List[Dict]:
        """Search for videos on Pexels"""
        
        if not self.api_key:
            return []
        
        url = f"{self.video_url}/search"
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("videos", [])
            else:
                print(f"⚠️  Pexels API error: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"❌ Error searching videos: {e}")
            return []
    
    def download_photo(self, photo_data: Dict, filename: str) -> Optional[Path]:
        """Download a photo"""
        
        try:
            # Get the large size URL
            photo_url = photo_data["src"]["large2x"]
            
            response = requests.get(photo_url)
            
            if response.status_code == 200:
                filepath = file_handler.save_binary(
                    response.content,
                    filename,
                    file_handler.temp_dir
                )
                return filepath
            
        except Exception as e:
            print(f"❌ Error downloading photo: {e}")
        
        return None
    
    def download_video(self, video_data: Dict, filename: str) -> Optional[Path]:
        """Download a video"""
        
        try:
            # Get HD quality video
            video_files = video_data.get("video_files", [])
            
            # Find HD version
            hd_video = None
            for vf in video_files:
                if vf.get("quality") == "hd":
                    hd_video = vf
                    break
            
            if not hd_video and video_files:
                hd_video = video_files[0]  # Fallback to first available
            
            if hd_video:
                video_url = hd_video["link"]
                
                response = requests.get(video_url, stream=True)
                
                if response.status_code == 200:
                    filepath = file_handler.save_binary(
                        response.content,
                        filename,
                        file_handler.temp_dir
                    )
                    return filepath
        
        except Exception as e:
            print(f"❌ Error downloading video: {e}")
        
        return None
    
    def search_and_download_photos(
        self,
        keywords: List[str],
        max_per_keyword: int = 10
    ) -> List[Path]:
        """Search and download photos for multiple keywords"""
        
        print(f"📷 Searching for {len(keywords)} photo topics...")
        
        downloaded = []
        
        for i, keyword in enumerate(keywords):
            print(f"   Searching: {keyword}...")
            
            photos = self.search_photos(keyword, per_page=max_per_keyword)
            
            if photos:
                print(f"   Found {len(photos)} photos, downloading...")
                
                for j, photo in enumerate(photos[:max_per_keyword]):
                    filename = f"photo_{i+1:03d}_{j+1:03d}.jpg"
                    filepath = self.download_photo(photo, filename)
                    
                    if filepath:
                        downloaded.append(filepath)
                        print(f"      ✅ Downloaded: {filename}")
                    
                    time.sleep(0.2)  # Rate limiting
            else:
                print(f"   ⚠️  No photos found for: {keyword}")
            
            time.sleep(0.5)
        
        print(f"\n✅ Downloaded {len(downloaded)} photos")
        return downloaded
    
    def search_and_download_videos(
        self,
        keywords: List[str],
        max_per_keyword: int = 3
    ) -> List[Dict]:
        """Search and download videos for multiple keywords"""
        
        print(f"🎬 Searching for {len(keywords)} video topics...")
        
        downloaded = []
        
        for i, keyword in enumerate(keywords):
            print(f"   Searching: {keyword}...")
            
            videos = self.search_videos(keyword, per_page=max_per_keyword)
            
            if videos:
                print(f"   Found {len(videos)} videos, downloading...")
                
                for j, video in enumerate(videos[:max_per_keyword]):
                    filename = f"video_{i+1:03d}_{j+1:03d}.mp4"
                    filepath = self.download_video(video, filename)
                    
                    if filepath:
                        duration = video.get("duration", 0)
                        downloaded.append({
                            "filepath": filepath,
                            "duration": duration,
                            "keyword": keyword
                        })
                        print(f"      ✅ Downloaded: {filename} ({duration}s)")
                    
                    time.sleep(0.3)
            else:
                print(f"   ⚠️  No videos found for: {keyword}")
            
            time.sleep(0.5)
        
        print(f"\n✅ Downloaded {len(downloaded)} videos")
        return downloaded
    
    def extract_keywords_from_script(self, script: str, max_keywords: int = 10) -> List[str]:
        """Extract visual keywords from script"""
        
        # Simple keyword extraction (can be improved with NLP)
        import re
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        
        # Extract nouns and descriptive phrases
        words = re.findall(r'\b[a-z]{4,}\b', script.lower())
        
        # Filter and count
        keyword_counts = {}
        for word in words:
            if word not in common_words:
                keyword_counts[word] = keyword_counts.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Return top keywords
        return [kw for kw, count in sorted_keywords[:max_keywords]]


stock_downloader = StockDownloader()


def search_photos(query: str, count: int = 15) -> List[Dict]:
    return stock_downloader.search_photos(query, per_page=count)


def search_videos(query: str, count: int = 15) -> List[Dict]:
    return stock_downloader.search_videos(query, per_page=count)


if __name__ == "__main__":
    print("\n🧪 Testing StockDownloader...\n")
    
    downloader = StockDownloader()
    
    if downloader.api_key:
        # Test photo search
        print("Testing photo search...")
        photos = downloader.search_photos("lighthouse", per_page=3)
        print(f"✅ Found {len(photos)} photos")
        
        # Test video search
        print("\nTesting video search...")
        videos = downloader.search_videos("ocean storm", per_page=3)
        print(f"✅ Found {len(videos)} videos")
        
        print("\n✅ StockDownloader working!")
    else:
        print("⚠️  No API key - add PEXELS_API_KEY to .env file")
    
    print("\n✅ StockDownloader module complete!\n")