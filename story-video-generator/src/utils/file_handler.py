import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any


class FileHandler:
    """Handles all file operations safely"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.output_dir = self.base_dir / "output"
        self.cache_dir = self.base_dir / "cache"
        self.temp_dir = self.output_dir / "temp"
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.output_dir / "videos",
            self.temp_dir,
            self.cache_dir,
            self.base_dir / "assets" / "fonts",
            self.base_dir / "assets" / "music"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_text(self, content: str, filename: str, directory: Optional[Path] = None) -> Path:
        """Save text content to file"""
        if directory is None:
            directory = self.temp_dir
        
        filepath = directory / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def load_text(self, filepath: Path) -> str:
        """Load text content from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_json(self, data: Dict[str, Any], filename: str, directory: Optional[Path] = None) -> Path:
        """Save JSON data to file"""
        if directory is None:
            directory = self.cache_dir
        
        filepath = directory / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_json(self, filepath: Path) -> Dict[str, Any]:
        """Load JSON data from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_binary(self, data: bytes, filename: str, directory: Optional[Path] = None) -> Path:
        """Save binary data (images, audio, etc)"""
        if directory is None:
            directory = self.temp_dir
        
        filepath = directory / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(data)
        
        return filepath
    
    def load_binary(self, filepath: Path) -> bytes:
        """Load binary data from file"""
        with open(filepath, 'rb') as f:
            return f.read()
    
    def file_exists(self, filepath: Path) -> bool:
        """Check if file exists"""
        return filepath.exists()
    
    def delete_file(self, filepath: Path) -> bool:
        """Delete a file safely"""
        try:
            if filepath.exists():
                filepath.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def clear_temp(self):
        """Clear temporary files"""
        if self.temp_dir.exists():
            for item in self.temp_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                except Exception as e:
                    print(f"Error clearing temp: {e}")
    
    def get_temp_path(self, filename: str) -> Path:
        """Get path for temporary file"""
        return self.temp_dir / filename
    
    def get_output_path(self, filename: str) -> Path:
        """Get path for output file"""
        return self.output_dir / "videos" / filename
    
    def get_cache_path(self, filename: str) -> Path:
        """Get path for cache file"""
        return self.cache_dir / filename
    
    def list_files(self, directory: Path, extension: Optional[str] = None) -> List[Path]:
        """List all files in directory"""
        if not directory.exists():
            return []
        
        if extension:
            return list(directory.glob(f"*.{extension}"))
        return [f for f in directory.iterdir() if f.is_file()]
    
    def get_file_size(self, filepath: Path) -> int:
        """Get file size in bytes"""
        return filepath.stat().st_size if filepath.exists() else 0
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


# Global instance
file_handler = FileHandler()


# Convenience functions
def save_text(content: str, filename: str) -> Path:
    return file_handler.save_text(content, filename)


def load_text(filepath: Path) -> str:
    return file_handler.load_text(filepath)


def save_json(data: dict, filename: str) -> Path:
    return file_handler.save_json(data, filename)


def load_json(filepath: Path) -> dict:
    return file_handler.load_json(filepath)


if __name__ == "__main__":
    print("\n🧪 Testing FileHandler...\n")
    
    fh = FileHandler()
    
    # Test text save/load
    test_text = "This is a test script!"
    path = fh.save_text(test_text, "test_script.txt")
    print(f"✅ Saved text to: {path}")
    
    loaded = fh.load_text(path)
    print(f"✅ Loaded text: {loaded}")
    
    # Test JSON save/load
    test_data = {"title": "Test Video", "duration": "60min"}
    json_path = fh.save_json(test_data, "test_config.json")
    print(f"✅ Saved JSON to: {json_path}")
    
    loaded_json = fh.load_json(json_path)
    print(f"✅ Loaded JSON: {loaded_json}")
    
    # Test file operations
    print(f"✅ File exists: {fh.file_exists(path)}")
    print(f"✅ File size: {fh.format_size(fh.get_file_size(path))}")
    
    # Clean up
    fh.delete_file(path)
    fh.delete_file(json_path)
    
    print("\n✅ FileHandler working perfectly!\n")