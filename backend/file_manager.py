"""
File Manager
Basic file management utilities for the data engineering project
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List

class FileManager:
    """Basic file management system"""
    
    def __init__(self):
        self.base_dir = Path(".")
        self.data_dir = self.base_dir / "data"
        self.results_dir = self.base_dir / "results"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
    
    def list_files(self, directory: str = None) -> List[str]:
        """List files in a directory"""
        target_dir = self.data_dir if directory is None else Path(directory)
        
        if not target_dir.exists():
            return []
        
        return [str(f) for f in target_dir.iterdir() if f.is_file()]
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information"""
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        return {
            'name': path.name,
            'size': path.stat().st_size,
            'modified': path.stat().st_mtime,
            'is_file': path.is_file(),
            'extension': path.suffix
        }
    
    def cleanup_old_files(self, days: int = 7):
        """Clean up old files (placeholder for future implementation)"""
        import time
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for directory in [self.data_dir, self.results_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    print(f"Cleaned up old file: {file_path}") 