"""
CV template adaptation pipeline module for the CV Assistant application.

This module provides a pipeline for adapting a CV to a new template.
"""
import logging
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import Settings
from app.pipelines.base import BasePipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AdoptPipeline(BasePipeline):
    """
    Pipeline for adapting a CV to a new template.
    
    This pipeline takes a CV and adapts it to a new template format,
    preserving all the original content but reorganizing it according
    to the new template.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the adopt pipeline with settings.
        
        Args:
            settings: Application settings
        """
        super().__init__(settings)
        self.pipeline_name = "adopt"
    
    def run(self, source: str) -> Dict[str, Path]:
        """
        Run the CV template adaptation pipeline.
        
        Args:
            source: Path to the source CV file
            
        Returns:
            Dictionary of output file paths
        """
        try:
            # Log detailed information to file
            logger.debug(f"Starting CV template adaptation pipeline with parameters: source={source}")
            
            # Load source CV
            cv_path, cv_content = self.load_cv(source)
            
            # Load CV template and instructions
            template_name = self.settings.template_dir
            cv_template = self.load_template("cv_template.md")
            cv_instructions = self.load_template("cv_instructions.md") if self.settings.get_template_file("cv_instructions.md").exists() else ""
            
            # Log essential information - debug for file logs only
            logger.debug(f"CV: {cv_path.name} | Template: {template_name}")
            
            # Extract base name from source CV file (without extension)
            cv_name = cv_path.stem
            
            # Set up output directory
            output_dir = self.setup_output_directory(cv_name, self.pipeline_name)
            
            # Extract candidate name for better file naming
            # Simplified extraction just to get candidate name
            candidate_name = "Unknown"
            try:
                # Use first 1000 chars which should contain the name
                first_line = cv_content.split('\n', 1)[0].strip()
                if first_line.startswith('#'):
                    candidate_name = first_line.lstrip('#').strip()
                    logger.debug(f"Extracted candidate name: {candidate_name}")
            except Exception as e:
                logger.debug(f"Could not extract candidate name: {str(e)}")
                
            # Generate adapted CV
            logger.debug(f"Adapting CV to template {template_name} using {self.settings.llm_model}...")
            adapted_cv = self.generate_adapted_cv(cv_content, cv_template, cv_instructions)
            
            # Create file name with candidate name
            file_name = f"{candidate_name} - adapted CV ({template_name})"
            if candidate_name == "Unknown":
                file_name = f"Adapted CV - {cv_name}"
            
            # Save results
            output_files = self.save_output(adapted_cv, output_dir, file_name)
            
            # Success message with clear output information
            print("✓ CV template adaptation completed successfully")
            print(f"✓ Output: {output_dir}")
            logger.debug(f"Generated files: {', '.join([path.name for path in output_files.values()])}")
            
            return output_files
            
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}\nCheck files in: CV dir: {self.settings.cv_dir}"
            logger.error(error_msg)
            print(error_msg)
            raise
        except Exception as e:
            error_msg = f"Error during CV template adaptation: {str(e)}\nCheck log file for details: {os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'run.log')}"
            logger.error(error_msg)
            logger.debug("Detailed error information:", exc_info=True)
            print(error_msg)
            raise
    
    def save_output(self, content: str, output_dir: Path, base_name: str) -> Dict[str, Path]:
        """
        Save the output content to markdown, PDF, and HTML files using CV-specific styling.
        
        Args:
            content: Content to save
            output_dir: Output directory
            base_name: Base name for the output files
            
        Returns:
            Dictionary of output file paths
        """
        # Get CV-specific CSS content
        css_path = self.settings.get_template_file("cv_style.css")
        css_content = None
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            logger.debug(f"Using CV-specific CSS from: {css_path}")
        else:
            logger.warning(f"CV CSS file not found: {css_path}")
        
        # Use the parent class's save_output method but with our CSS content
        from app.utils.file_io import read_file, write_file
        from app.utils.converter import FileConverter
        
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
        
    def generate_adapted_cv(
        self, 
        cv_content: str, 
        cv_template: str, 
        cv_instructions: str
    ) -> str:
        """
        Generate a CV adapted to a new template using LangChain.
        
        Args:
            cv_content: CV content
            cv_template: CV template
            cv_instructions: CV instructions
            
        Returns:
            Adapted CV content
        """
        logger.info("Generating adapted CV...")
        
        # Create LLM model
        model = ChatOpenAI(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature
        )
        
        # Build system message with instructions
        system_content = f"""
You are expert in writing CVs and you excel in this.

Read the source cv:
```
{cv_content}
```

Read the template:
```
{cv_template}
```

Follow these instructions for CV writing:
```
{cv_instructions}
```

# Task:
1. Strictly using the template, rewrite the CV using the template format.
2. Do not change any content from the source CV, just adapt it to the new template.
3. Generate adapted CV and nothing else.
"""
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content="# Task: Generate adapted CV and nothing else."),
        ]
        
        logger.info("Calling LLM to generate adapted CV...")
        response = model.invoke(messages)
        
        return response.content
