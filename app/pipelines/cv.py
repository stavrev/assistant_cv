"""
CV tailoring pipeline module for the CV Assistant application.

This module provides a pipeline for tailoring a CV to a job description.
"""
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import Settings
from app.pipelines.base import BasePipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CVPipeline(BasePipeline):
    """
    Pipeline for tailoring a CV to a job description.
    
    This pipeline takes a CV and a job description, and generates a tailored CV
    that highlights the relevant skills and experience for the job.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the CV pipeline with settings.
        
        Args:
            settings: Application settings
        """
        super().__init__(settings)
        self.pipeline_name = "cv"
    
    def run(self, cv_file: Optional[str] = None, jd_file: Optional[str] = None) -> Dict[str, Path]:
        """
        Run the CV tailoring pipeline.
        
        Args:
            cv_file: Optional path to the CV file
            jd_file: Optional path to the job description file
            
        Returns:
            Dictionary of output file paths
        """
        try:
            # Log detailed information to file
            logger.debug(f"Starting CV tailoring pipeline with parameters: cv_file={cv_file}, jd_file={jd_file}")
            
            # Load CV and job description
            cv_path, cv_content = self.load_cv(cv_file)
            jd_path, jd_content = self.load_job_description(jd_file)
            
            # Load CV template and instructions
            template_name = self.settings.template_dir
            cv_template = self.load_template("cv_template.md")
            cv_instructions = self.load_template("cv_instructions.md") if self.settings.get_template_file("cv_instructions.md").exists() else ""
            
            # Log essential information - debug for file logs only
            logger.debug(f"CV: {cv_path.name} | Job: {jd_path.name} | Template: {template_name}")
            
            # Extract candidate name and company name
            names = self.extract_names(cv_content, jd_content)
            candidate_name = names["candidate_name"]
            company_name = names["company_name"]
            logger.debug(f"Extracted candidate name: {candidate_name}")
            logger.debug(f"Extracted company name: {company_name}")
            
            # Extract base name from job description file (without extension) for directory naming
            job_name = jd_path.stem
            
            # Set up output directory
            output_dir = self.setup_output_directory(job_name, self.pipeline_name)
            
            # Generate tailored CV
            logger.debug(f"Generating tailored CV using {self.settings.llm_model}...")
            tailored_cv = self.generate_tailored_cv(cv_content, jd_content, cv_template, cv_instructions)
            
            # Create file name with candidate name and company name
            file_name = f"{candidate_name} - cv ({company_name})"
            
            # Save results
            output_files = self.save_output(tailored_cv, output_dir, file_name)
            
            # Copy the job description to the output directory for reference
            self.copy_job_description(jd_path, output_dir)
            
            # Success message with clear output information
            print("✓ CV tailoring completed successfully")
            print(f"✓ Output: {output_dir}")
            logger.debug(f"Generated files: {', '.join([path.name for path in output_files.values()])}")
            
            return output_files
            
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}\nCheck files in: CV dir: {self.settings.cv_dir}, Job dir: {self.settings.job_descriptions_dir}"
            logger.error(error_msg)
            print(error_msg)
            raise
        except Exception as e:
            error_msg = f"Error during CV tailoring: {str(e)}\nCheck log file for details: {os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'run.log')}"
            logger.error(error_msg)
            logger.debug("Detailed error information:", exc_info=True)
            print(error_msg)
            raise
    
    def generate_tailored_cv(
        self, 
        cv_content: str, 
        jd_content: str, 
        cv_template: str, 
        cv_instructions: str
    ) -> str:
        """
        Generate a tailored CV using LangChain.
        
        Args:
            cv_content: CV content
            jd_content: Job description content
            cv_template: CV template
            cv_instructions: CV instructions
            
        Returns:
            Tailored CV content
        """
        logger.info("Generating tailored CV...")
        
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
2. Using the important keywords and phrases from the job description, tailor the rewritten CV is it would best match the job description.
3. You are allowed to tune the expression of the source CV data so it would best match the job description, but do not add items which are not derived as facts from the original CV.
4. Do not mention the company name from the job description into the CV.
5. Generate Tailored complete CV and nothing else.
"""
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=f"# Task: Generate tailored CV and nothing else.\n\nJob Description:\n\n{jd_content}"),
        ]
        
        logger.info("Calling LLM to generate tailored CV...")
        response = model.invoke(messages)
        
        return response.content
    
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
        
    def copy_job_description(self, jd_path: Path, output_dir: Path) -> Path:
        """
        Copy the job description to the output directory.
        
        Args:
            jd_path: Path to the job description file
            output_dir: Output directory
            
        Returns:
            Path to the copied job description file
        """
        # Copy the job description to the output directory
        output_jd_path = output_dir / jd_path.name
        with open(jd_path, 'r', encoding='utf-8') as f:
            jd_content = f.read()
        
        with open(output_jd_path, 'w', encoding='utf-8') as f:
            f.write(jd_content)
        
        logger.info(f"Copied job description to: {output_jd_path}")
        return output_jd_path
