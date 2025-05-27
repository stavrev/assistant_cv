"""
Base pipeline module for the CV Assistant application.

This module provides a base pipeline class that all specific pipelines extend.
"""
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import Settings
from app.utils.file_io import read_file, write_file, find_file, find_latest_file
from app.utils.converter import FileConverter
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BasePipeline(ABC):
    """
    Base pipeline class for all CV Assistant pipelines.
    
    This abstract class defines the common interface and functionality
    for all pipelines in the application.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the pipeline with settings.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.output_files = {}
    
    @abstractmethod
    def run(self, *args, **kwargs):
        """
        Run the pipeline.
        
        This method must be implemented by all subclasses.
        """
        pass
    
    def load_cv(self, cv_file: Optional[str] = None) -> Tuple[Path, str]:
        """
        Load the CV file.
        
        Args:
            cv_file: Optional path to the CV file
            
        Returns:
            Tuple of (cv_path, cv_content)
            
        Raises:
            FileNotFoundError: If the CV file is not found
        """
        # If no CV file is provided, find the most recent one
        if cv_file is None:
            cv_path = find_latest_file(self.settings.cv_dir)
            if cv_path is None:
                raise FileNotFoundError("No CV files found in the CV directory")
            logger.info(f"Using most recent CV: {cv_path}")
        else:
            # Try to find the file in the CV directory or as an absolute path
            cv_path = find_file(cv_file, [self.settings.cv_dir])
            if cv_path is None:
                raise FileNotFoundError(f"CV file not found: {cv_file}")
            logger.info(f"Using CV file: {cv_path}")
        
        # Read the CV content
        cv_content = read_file(cv_path)
        return cv_path, cv_content
    
    def load_job_description(self, jd_file: Optional[str] = None) -> Tuple[Path, str]:
        """
        Load the job description file.
        
        Args:
            jd_file: Optional path to the job description file
            
        Returns:
            Tuple of (jd_path, jd_content)
            
        Raises:
            FileNotFoundError: If the job description file is not found
        """
        # If no job description file is provided, find the most recent one
        if jd_file is None:
            jd_path = find_latest_file(self.settings.job_descriptions_dir, extension='.txt')
            if jd_path is None:
                raise FileNotFoundError("No job description files found in the job descriptions directory")
            logger.info(f"Using most recent job description: {jd_path}")
        else:
            # Try to find the file in the job descriptions directory or as an absolute path
            jd_path = find_file(jd_file, [self.settings.job_descriptions_dir])
            if jd_path is None:
                raise FileNotFoundError(f"Job description file not found: {jd_file}")
            logger.info(f"Using job description file: {jd_path}")
        
        # Read the job description content
        jd_content = read_file(jd_path)
        return jd_path, jd_content
    
    def load_template(self, template_name: str) -> str:
        """
        Load a template file from the current template directory.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Template content
            
        Raises:
            FileNotFoundError: If the template file is not found
        """
        template_path = self.settings.get_template_file(template_name)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        logger.info(f"Using template: {template_path}")
        return read_file(template_path)
    
    def setup_output_directory(self, base_name: str, pipeline_name: str) -> Path:
        """
        Set up the output directory for the pipeline results.
        
        Args:
            base_name: Base name for the output files
            pipeline_name: Name of the pipeline
            
        Returns:
            Path to the output directory
        """
        # Get current date in YYYY-MM-DD format
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create directory name with date prefix
        directory_name = f"{current_date} {base_name}"
        output_dir = self.settings.outputs_dir / directory_name / pipeline_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Output directory: {output_dir}")
        return output_dir
    
    def extract_names(self, cv_content: str, jd_content: str) -> Dict[str, str]:
        """
        Extract candidate name and company name from CV and job description.
        
        Args:
            cv_content: Content of the CV
            jd_content: Content of the job description
            
        Returns:
            Dictionary containing 'candidate_name' and 'company_name'
        """
        logger.info("Extracting candidate name and company name...")
        
        # Create LLM model
        model = ChatOpenAI(
            model=self.settings.llm_model,
            temperature=0.1  # Lower temperature for factual extraction
        )
        
        # Build system message
        system_content = """
        You are an expert at extracting specific information from documents.
        Your task is to extract the candidate's full name from the CV and the company name from the job description.
        Provide ONLY these two pieces of information in JSON format with keys 'candidate_name' and 'company_name'.
        If you cannot find the information, use 'Unknown' as the value.
        """
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=f"""Extract the candidate name and company name from these documents:

CV:
```
{cv_content[:1000]}  # Using first 1000 chars of CV which should contain the name
```

Job Description:
```
{jd_content[:1000]}  # Using first 1000 chars of job description which should contain company name
```

Respond ONLY with the JSON containing 'candidate_name' and 'company_name'.
""")
        ]
        
        response = model.invoke(messages)
        
        # Parse the response to extract the JSON
        import json
        import re
        
        # Try to find JSON in the response
        try:
            # First try to parse the entire response as JSON
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON using regex
            json_match = re.search(r'\{[^\{\}]*"candidate_name"[^\{\}]*"company_name"[^\{\}]*\}', response.content)
            if json_match:
                try:
                    result = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    # If all parsing fails, use default values
                    result = {"candidate_name": "Unknown", "company_name": "Unknown"}
            else:
                # If no JSON pattern found, use default values
                result = {"candidate_name": "Unknown", "company_name": "Unknown"}
        
        # Ensure both keys exist
        if "candidate_name" not in result:
            result["candidate_name"] = "Unknown"
        if "company_name" not in result:
            result["company_name"] = "Unknown"
            
        logger.info(f"Extracted candidate name: {result['candidate_name']}")
        logger.info(f"Extracted company name: {result['company_name']}")
        
        return result
        
    def save_output(self, content: str, output_dir: Path, base_name: str) -> Dict[str, Path]:
        """
        Save the output content to markdown and PDF files.
        
        Args:
            content: Content to save
            output_dir: Output directory
            base_name: Base name for the output files
            
        Returns:
            Dictionary of output file paths
        """
        # Get CSS content
        css_path = self.settings.get_template_file("style.css")
        css_content = read_file(css_path) if css_path.exists() else None
        
        # Save markdown file
        md_path = output_dir / f"{base_name}.md"
        write_file(content, md_path)
        logger.info(f"Markdown saved to: {md_path}")
        
        # Save PDF file
        pdf_path = output_dir / f"{base_name}.pdf"
        FileConverter.markdown_to_pdf(content, pdf_path, css_content)
        logger.info(f"PDF saved to: {pdf_path}")
        
        # Save HTML file
        html_content = FileConverter.markdown_to_html(content, css_content)
        html_path = output_dir / f"{base_name}.html"
        write_file(html_content, html_path)
        logger.info(f"HTML saved to: {html_path}")
        
        return {
            "markdown": md_path,
            "pdf": pdf_path,
            "html": html_path
        }
