"""
Tests for the file I/O utility module.
"""
import os
import unittest
from pathlib import Path
import tempfile
import shutil

from app.utils.file_io import read_file, write_file, find_latest_file, find_file


class TestFileIO(unittest.TestCase):
    """Test cases for the file I/O utility module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_read_write_file(self):
        """Test reading and writing files."""
        # Create a test file
        test_content = "This is a test file."
        test_file = Path(self.test_dir) / "test.txt"
        
        # Write to the file
        write_file(test_content, test_file)
        
        # Verify the file exists
        self.assertTrue(test_file.exists())
        
        # Read the file
        content = read_file(test_file)
        
        # Verify the content
        self.assertEqual(content, test_content)
    
    def test_read_nonexistent_file(self):
        """Test reading a nonexistent file."""
        nonexistent_file = Path(self.test_dir) / "nonexistent.txt"
        
        # Verify that reading a nonexistent file raises FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            read_file(nonexistent_file)
    
    def test_find_latest_file(self):
        """Test finding the latest file in a directory."""
        # Create test files with different modification times
        file1 = Path(self.test_dir) / "file1.txt"
        file2 = Path(self.test_dir) / "file2.txt"
        file3 = Path(self.test_dir) / "file3.md"
        
        write_file("File 1", file1)
        write_file("File 2", file2)
        write_file("File 3", file3)
        
        # Set modification times
        os.utime(file1, (0, 100))
        os.utime(file2, (0, 200))
        os.utime(file3, (0, 150))
        
        # Find the latest file
        latest_file = find_latest_file(self.test_dir)
        
        # Verify the latest file is file2.txt
        self.assertEqual(latest_file, file2)
        
        # Find the latest file with extension filter
        latest_md_file = find_latest_file(self.test_dir, extension=".md")
        
        # Verify the latest .md file is file3.md
        self.assertEqual(latest_md_file, file3)
    
    def test_find_file(self):
        """Test finding a file in a list of directories."""
        # Create test directories and files
        dir1 = Path(self.test_dir) / "dir1"
        dir2 = Path(self.test_dir) / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        
        file1 = dir1 / "file.txt"
        file2 = dir2 / "file.md"
        
        write_file("File 1", file1)
        write_file("File 2", file2)
        
        # Find files
        found_file1 = find_file("file.txt", [dir1, dir2])
        found_file2 = find_file("file.md", [dir1, dir2])
        
        # Verify the files are found
        self.assertEqual(found_file1, file1)
        self.assertEqual(found_file2, file2)
        
        # Verify that a nonexistent file returns None
        nonexistent_file = find_file("nonexistent.txt", [dir1, dir2])
        self.assertIsNone(nonexistent_file)


if __name__ == "__main__":
    unittest.main()
