"""
Tests for the template rendering utility module.
"""
import unittest
from pathlib import Path
import tempfile
import shutil

from app.utils.render import TemplateRenderer


class TestTemplateRenderer(unittest.TestCase):
    """Test cases for the template rendering utility module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = Path(self.test_dir)
        
        # Create a test template file
        self.template_file = self.test_dir_path / "test_template.md"
        with open(self.template_file, 'w') as f:
            f.write("# {{ name }}\n\n{{ content }}")
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_render_string(self):
        """Test rendering a template string."""
        # Test template string
        template_str = "# {{ name }}\n\n{{ content }}"
        
        # Test context
        context = {
            "name": "John Doe",
            "content": "This is a test."
        }
        
        # Render template
        result = TemplateRenderer.render_string(template_str, context)
        
        # Verify result
        self.assertEqual(result, "# John Doe\n\nThis is a test.")
    
    def test_render_file(self):
        """Test rendering a template file."""
        # Test context
        context = {
            "name": "John Doe",
            "content": "This is a test."
        }
        
        # Render template
        result = TemplateRenderer.render_file(self.template_file, context)
        
        # Verify result
        self.assertEqual(result, "# John Doe\n\nThis is a test.")
    
    def test_render_with_missing_variable(self):
        """Test rendering with a missing variable."""
        # Test template string with strict variable handling
        template_str = "# {{ name }}\n\n{{ content | strict }}"
        
        # Test context with missing variable
        context = {
            "name": "John Doe"
        }
        
        # Verify that rendering with a missing variable raises an exception
        with self.assertRaises(Exception):
            TemplateRenderer.render_string(template_str, context)
    
    def test_render_with_conditional(self):
        """Test rendering with conditional logic."""
        # Test template string with conditional
        template_str = """# {{ name }}
        
{% if show_email %}
Email: {{ email }}
{% endif %}
"""
        
        # Test context with show_email=True
        context1 = {
            "name": "John Doe",
            "email": "john@example.com",
            "show_email": True
        }
        
        # Test context with show_email=False
        context2 = {
            "name": "John Doe",
            "email": "john@example.com",
            "show_email": False
        }
        
        # Render templates
        result1 = TemplateRenderer.render_string(template_str, context1)
        result2 = TemplateRenderer.render_string(template_str, context2)
        
        # Verify results
        self.assertIn("Email: john@example.com", result1)
        self.assertNotIn("Email:", result2)


if __name__ == "__main__":
    unittest.main()
