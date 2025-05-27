"""
File I/O utility module for the CV Assistant application.

This module provides functions for reading and writing files in various formats.
"""
import os
from pathlib import Path
from typing import Optional, Union, List, Tuple

from app.utils.logger import get_logger

logger = get_logger(__name__)


def read_file(file_path: Union[str, Path]) -> str:
    """
    Read a file and return its contents as a string.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as a string
        
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If there is an error reading the file
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def write_file(content: str, file_path: Union[str, Path]) -> Path:
    """
    Write content to a file.
    
    Args:
        content: Content to write
        file_path: Path to the file to write
        
    Returns:
        Path to the written file
        
    Raises:
        IOError: If there is an error writing the file
    """
    file_path = Path(file_path)
    
    # Ensure the directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    except IOError as e:
        logger.error(f"Error writing file {file_path}: {e}")
        raise


def find_latest_file(directory: Union[str, Path], extension: Optional[str] = None) -> Optional[Path]:
    """
    Find the most recently modified file in a directory.
    
    Args:
        directory: Directory to search
        extension: Optional file extension filter (e.g., '.txt', '.md')
        
    Returns:
        Path to the most recent file, or None if no files found
    """
    directory = Path(directory)
    
    if not directory.exists() or not directory.is_dir():
        logger.warning(f"Directory not found: {directory}")
        return None
    
    # Get all files in the directory
    files = [f for f in directory.iterdir() if f.is_file()]
    
    # Filter by extension if provided
    if extension:
        files = [f for f in files if f.suffix.lower() == extension.lower()]
    
    if not files:
        return None
    
    # Sort by modification time (most recent first)
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    return files[0]


def find_file(filename: str, search_dirs: List[Path]) -> Optional[Path]:
    """
    Find a file in a list of directories.
    
    Args:
        filename: Name of the file to find
        search_dirs: List of directories to search
        
    Returns:
        Path to the file if found, None otherwise
    """
    # First check if the file exists as specified (absolute or relative to current dir)
    file_path = Path(filename)
    if file_path.exists():
        return file_path
    
    # Try to find it in the search directories
    for directory in search_dirs:
        potential_path = directory / file_path.name
        if potential_path.exists():
            return potential_path
    
    return None
