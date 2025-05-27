"""
Cover letter generation pipeline module for the CV Assistant application.

This module provides a pipeline for generating a cover letter based on a CV and job description.
"""
import os
import logging
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config.settings import Settings
from app.pipelines.base import BasePipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LetterPipeline(BasePipeline):
    """
    Pipeline for generating a cover letter.
    
    This pipeline takes a CV and a job description, and generates a cover letter
    that highlights the relevant skills and experience for the job.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the letter pipeline with settings.
        
        Args:
            settings: Application settings
        """
        super().__init__(settings)
        self.pipeline_name = "letter"
    
    def run(self, cv_file: Optional[str] = None, jd_file: Optional[str] = None) -> Dict[str, Path]:
        """
        Run the cover letter generation pipeline.
        
        Args:
            cv_file: Optional path to the CV file
            jd_file: Optional path to the job description file
            
        Returns:
            Dictionary of output file paths
        """
        try:
            # Log detailed information to file
            logger.debug(f"Starting cover letter generation pipeline with parameters: cv_file={cv_file}, jd_file={jd_file}")
            
            # Load CV and job description
            cv_path, cv_content = self.load_cv(cv_file)
            jd_path, jd_content = self.load_job_description(jd_file)
            
            # Load letter template and instructions
            template_name = self.settings.template_dir
            letter_template = self.load_template("letter_template.md")
            letter_instructions = self.load_template("letter_instructions.md") if self.settings.get_template_file("letter_instructions.md").exists() else ""
            
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
            
            # Generate cover letter
            logger.debug(f"Generating cover letter using {self.settings.llm_model}...")
            cover_letter = self.generate_cover_letter(cv_content, jd_content, letter_template, letter_instructions)
            
            # Create file name with candidate name and company name
            file_name = f"{candidate_name} - cover letter ({company_name})"
            
            # Save results
            output_files = self.save_output(cover_letter, output_dir, file_name)
            
            # Copy the job description to the output directory for reference
            self.copy_job_description(jd_path, output_dir)
            
            # Success message with clear output information
            print("✓ Cover letter generation completed successfully")
            print(f"✓ Output: {output_dir}")
            logger.debug(f"Generated files: {', '.join([path.name for path in output_files.values()])}")
            
            return output_files
            
        except FileNotFoundError as e:
            error_msg = f"Error: {str(e)}\nCheck files in: CV dir: {self.settings.cv_dir}, Job dir: {self.settings.job_descriptions_dir}"
            logger.error(error_msg)
            print(error_msg)
            raise
        except Exception as e:
            error_msg = f"Error during cover letter generation: {str(e)}\nCheck log file for details: {os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'run.log')}"
            logger.error(error_msg)
            logger.debug("Detailed error information:", exc_info=True)
            print(error_msg)
            raise
    
    def generate_cover_letter(
        self, 
        cv_content: str, 
        jd_content: str, 
        letter_template: str, 
        letter_instructions: str
    ) -> str:
        """
        Generate a cover letter using LangChain.
        
        Args:
            cv_content: CV content
            jd_content: Job description content
            letter_template: Letter template
            letter_instructions: Letter instructions
            
        Returns:
            Cover letter content
        """
        logger.info("Generating cover letter...")
        
        # Create LLM model
        model = ChatOpenAI(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature
        )
        
        # Get current date in a formal format
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        
        # Extract candidate and company information
        names = self.extract_names(cv_content, jd_content)
        candidate_name = names["candidate_name"]
        company_name = names["company_name"]
        
        # Extract position title from job description
        # This is a simplified extraction - the LLM will do more sophisticated extraction in the actual letter
        position_title = "the position" 
        if "# " in jd_content[:200]:
            position_title = jd_content.split("# ", 1)[1].split("\n", 1)[0].strip()
        
        # Build system message with instructions
        system_content = f"""
You are an expert in writing professional Cover Letters and you excel in this.

Read the source CV:
```
{cv_content}
```

Read the cover letter template:
```
{letter_template}
```

Follow these instructions for Cover Letter writing:
```
{letter_instructions}
```

# Important Information to Include:
- Candidate's Name: {candidate_name}
- Company Name: {company_name}
- Position Title: {position_title}
- Current Date: {current_date}

# Template Placeholders to Replace:
- Replace [Current Date] with {current_date}
- Replace [Hiring Manager's Name] with an appropriate greeting if the name is unknown
- Replace [Company Name] with {company_name}
- Replace [Position Title] with {position_title}
- Replace [Your Full Name] with {candidate_name}
- Replace other placeholders with appropriate content based on the CV and job description

# Task:
1. Strictly follow the provided cover letter template format.
2. Replace ALL placeholders with actual content - do not leave any [bracketed placeholders] in the final letter.
3. Use the important keywords and phrases from the job description to tailor the cover letter.
4. Highlight relevant skills and experiences from the CV that match the job requirements.
5. Maintain a professional tone and ensure the letter is concise (no more than one page).
6. Generate a tailored cover letter and nothing else.
"""
        
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=f"# Task: Generate a tailored cover letter and nothing else.\n\nJob Description:\n\n{jd_content}"),
        ]
        
        logger.info("Calling LLM to generate cover letter...")
        response = model.invoke(messages)
        
        return response.content
    
    def save_output(self, content: str, output_dir: Path, base_name: str) -> Dict[str, Path]:
        """
        Save the output content to markdown, PDF, and HTML files using letter-specific styling.
        
        Args:
            content: Content to save
            output_dir: Output directory
            base_name: Base name for the output files
            
        Returns:
            Dictionary of output file paths
        """
        # Get letter-specific CSS content
        css_path = self.settings.get_template_file("letter_style.css")
        css_content = None
        if css_path.exists():
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            logger.debug(f"Using letter-specific CSS from: {css_path}")
        else:
            logger.warning(f"Letter CSS file not found: {css_path}")
        
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
