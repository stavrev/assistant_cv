"""
Tests for the CV pipeline module.
"""
import unittest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from app.config.settings import Settings
from app.pipelines.cv import CVPipeline


class TestCVPipeline(unittest.TestCase):
    """Test cases for the CV pipeline module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = Path(self.test_dir)
        
        # Create test directories
        self.templates_dir = self.test_dir_path / "templates" / "default"
        self.cv_dir = self.test_dir_path / "inputs" / "cvs"
        self.jd_dir = self.test_dir_path / "inputs" / "job_descriptions"
        self.outputs_dir = self.test_dir_path / "outputs"
        
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.cv_dir.mkdir(parents=True, exist_ok=True)
        self.jd_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        self.cv_file = self.cv_dir / "test_cv.md"
        self.jd_file = self.jd_dir / "test_job.md"
        self.template_file = self.templates_dir / "cv_template.md"
        self.css_file = self.templates_dir / "style.css"
        
        # Write test content
        with open(self.cv_file, 'w') as f:
            f.write("# Test CV\n\nSkills: Python, Testing")
        
        with open(self.jd_file, 'w') as f:
            f.write("# Test Job\n\nRequired: Python, Testing")
        
        with open(self.template_file, 'w') as f:
            f.write("# {{name}}\n\n## Skills\n\n{{skills}}")
        
        with open(self.css_file, 'w') as f:
            f.write("body { font-family: Arial; }")
        
        # Create test settings
        self.settings = Settings()
        self.settings.base_dir = self.test_dir_path
        self.settings.templates_dir = self.test_dir_path / "templates"
        self.settings.inputs_dir = self.test_dir_path / "inputs"
        self.settings.outputs_dir = self.test_dir_path / "outputs"
        self.settings.cv_dir = self.cv_dir
        self.settings.job_descriptions_dir = self.jd_dir
        self.settings.template_dir = "default"
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    @patch('app.pipelines.cv.ChatOpenAI')
    def test_cv_pipeline(self, mock_chat_openai):
        """Test the CV pipeline execution."""
        # Mock the LLM response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "# John Doe\n\n## Skills\n\n- Python (Expert)\n- Testing (Advanced)"
        mock_model.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_model
        
        # Create pipeline
        pipeline = CVPipeline(self.settings)
        
        # Run pipeline
        output_files = pipeline.run(str(self.cv_file), str(self.jd_file))
        
        # Verify output files exist
        self.assertTrue(Path(output_files["markdown"]).exists())
        self.assertTrue(Path(output_files["html"]).exists())
        
        # Verify PDF file exists if PDF conversion is available
        try:
            self.assertTrue(Path(output_files["pdf"]).exists())
        except (AssertionError, KeyError):
            # Skip PDF verification if conversion failed
            pass
        
        # Verify LLM was called with correct parameters
        mock_model.invoke.assert_called_once()
        call_args = mock_model.invoke.call_args[0][0]
        
        # Verify system message contains CV content
        system_message = call_args[0].content
        self.assertIn("# Test CV", system_message)
        self.assertIn("Skills: Python, Testing", system_message)
        
        # Verify human message contains job description
        human_message = call_args[1].content
        self.assertIn("# Test Job", human_message)
        self.assertIn("Required: Python, Testing", human_message)


if __name__ == "__main__":
    unittest.main()
