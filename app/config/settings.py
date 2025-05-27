"""
Settings module for the CV Assistant application.

This module contains the Settings class that manages all configuration
parameters for the application.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    """
    Application settings class.
    
    This class manages all configuration parameters for the application,
    including file paths, template directories, and model settings.
    """
    # Base directories
    base_dir: Path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    templates_dir: Path = Path("templates")
    inputs_dir: Path = Path("inputs")
    outputs_dir: Path = Path("outputs")
    
    # Input directories
    cv_dir: Path = Path("inputs/cv")
    job_descriptions_dir: Path = Path("inputs/job_descriptions")
    
    # Default template directory
    template_dir: str = "default"
    
    # LLM settings
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.3
    
    def __post_init__(self):
        """
        Initialize paths as absolute paths and ensure directories exist.
        """
        # Convert relative paths to absolute paths
        self.templates_dir = self.base_dir / self.templates_dir
        self.inputs_dir = self.base_dir / self.inputs_dir
        self.outputs_dir = self.base_dir / self.outputs_dir
        self.cv_dir = self.base_dir / self.cv_dir
        self.job_descriptions_dir = self.base_dir / self.job_descriptions_dir
        
        # Ensure directories exist
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self) -> None:
        """
        Ensure all required directories exist.
        """
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.cv_dir.mkdir(parents=True, exist_ok=True)
        self.job_descriptions_dir.mkdir(parents=True, exist_ok=True)
    
    def get_template_path(self) -> Path:
        """
        Get the path to the current template directory.
        
        Returns:
            Path to the template directory
        """
        # If template_dir is an absolute path, use it directly
        template_path = Path(self.template_dir)
        if template_path.is_absolute():
            return template_path
        
        # Otherwise, join it with the templates directory
        return self.templates_dir / self.template_dir
    
    def get_template_file(self, filename: str) -> Path:
        """
        Get the path to a specific template file.
        
        Args:
            filename: Name of the template file
            
        Returns:
            Path to the template file
        """
        return self.get_template_path() / filename
    
    def get_output_dir(self, job_name: str, pipeline_name: str) -> Path:
        """
        Get the output directory for a specific job and pipeline.
        
        Args:
            job_name: Name of the job
            pipeline_name: Name of the pipeline
            
        Returns:
            Path to the output directory
        """
        output_dir = self.outputs_dir / job_name / pipeline_name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
