"""
Tests for the file converter utility module.
"""
import unittest
from pathlib import Path
import tempfile
import shutil

from app.utils.converter import FileConverter


class TestFileConverter(unittest.TestCase):
    """Test cases for the file converter utility module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_markdown_to_html(self):
        """Test converting Markdown to HTML."""
        # Test Markdown content
        markdown_content = """# Test Heading
        
This is a test paragraph.

* Item 1
* Item 2
* Item 3
        """
        
        # Convert to HTML
        html_content = FileConverter.markdown_to_html(markdown_content)
        
        # Verify HTML content contains expected elements
        self.assertIn("<h1>Test Heading</h1>", html_content)
        self.assertIn("<ul>", html_content)
        self.assertIn("<li>Item 1</li>", html_content)
    
    def test_markdown_to_html_with_css(self):
        """Test converting Markdown to HTML with CSS."""
        # Test Markdown content
        markdown_content = "# Test Heading"
        
        # Test CSS
        css_content = "body { font-family: Arial; }"
        
        # Convert to HTML with CSS
        html_content = FileConverter.markdown_to_html(markdown_content, css_content)
        
        # Verify HTML content contains CSS
        self.assertIn("<style>", html_content)
        self.assertIn("body { font-family: Arial; }", html_content)
    
    def test_markdown_to_pdf(self):
        """Test converting Markdown to PDF."""
        # Skip this test if PDF conversion is not available
        try:
            # Test Markdown content
            markdown_content = "# Test Heading"
            
            # Output PDF path
            pdf_path = self.output_dir / "test.pdf"
            
            # Convert to PDF
            try:
                result_path = FileConverter.markdown_to_pdf(markdown_content, pdf_path)
                
                # Verify the PDF file exists
                self.assertTrue(pdf_path.exists())
                self.assertEqual(result_path, pdf_path)
            except RuntimeError as e:
                # If PDF generation fails due to missing dependencies, skip the test
                self.skipTest(f"PDF generation failed: {e}")
        except ImportError:
            self.skipTest("PDF conversion libraries not available")


if __name__ == "__main__":
    unittest.main()
