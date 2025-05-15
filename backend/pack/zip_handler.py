import os
import zipfile
import tempfile
import shutil
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

class ZipFileHandler:
    """Class to handle ZIP file extraction and processing."""
    
    def __init__(self):
        """Initialize the ZIP file handler."""
        self.temp_dir = None
        self.extracted_path = None
    
    def extract_zip(self, zip_path: str) -> Optional[str]:
        """
        Extract a ZIP file to a temporary directory.
        
        Args:
            zip_path (str): Path to the ZIP file
            
        Returns:
            Optional[str]: Path to the extracted directory or None if extraction fails
        """
        try:
            # Create a temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="code_analysis_")
            logger.info(f"Created temporary directory: {self.temp_dir}")
            
            # Extract the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Find the root directory of the extracted content
            contents = os.listdir(self.temp_dir)
            
            # If there's only one directory in the extracted content and it's not a hidden file,
            # use that as the project root
            if len(contents) == 1 and not contents[0].startswith('.'):
                potential_root = os.path.join(self.temp_dir, contents[0])
                if os.path.isdir(potential_root):
                    self.extracted_path = potential_root
                else:
                    self.extracted_path = self.temp_dir
            else:
                self.extracted_path = self.temp_dir
            
            logger.info(f"ZIP file extracted to: {self.extracted_path}")
            return self.extracted_path
            
        except Exception as e:
            logger.error(f"Error extracting ZIP file: {e}")
            self.cleanup()
            return None
    
    def get_file_list(self, directory: str = None, extensions: List[str] = None) -> List[str]:
        """
        Get list of files in the extracted directory with optional filtering by extension.
        
        Args:
            directory (str, optional): Directory to scan, defaults to extracted root
            extensions (List[str], optional): List of file extensions to include
            
        Returns:
            List[str]: List of file paths
        """
        if directory is None:
            directory = self.extracted_path
        
        if directory is None:
            logger.error("No extracted directory available")
            return []
        
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                # Skip hidden files
                if filename.startswith('.'):
                    continue
                
                # Filter by extension if provided
                if extensions:
                    if not any(filename.endswith(ext) for ext in extensions):
                        continue
                
                file_path = os.path.join(root, filename)
                # Get relative path from the extracted directory
                rel_path = os.path.relpath(file_path, directory)
                files.append(rel_path)
        
        return files
    
    def get_full_path(self, relative_path: str) -> str:
        """
        Get the full path for a relative path within the extracted directory.
        
        Args:
            relative_path (str): Relative path within the project
            
        Returns:
            str: Full path
        """
        if self.extracted_path is None:
            raise ValueError("No extracted directory available")
        
        return os.path.join(self.extracted_path, relative_path)
    
    def cleanup(self):
        """Clean up temporary directories."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
                self.temp_dir = None
                self.extracted_path = None
            except Exception as e:
                logger.error(f"Error cleaning up temporary directory: {e}")