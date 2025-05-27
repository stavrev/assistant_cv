"""
File converter utility module for the CV Assistant application.

This module provides functions for converting between different file formats.
"""
import importlib.util
import subprocess
from pathlib import Path
from typing import Optional, Union

import markdown

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Check if optional libraries are available
pdfkit_available = importlib.util.find_spec("pdfkit") is not None
weasyprint_available = importlib.util.find_spec("weasyprint") is not None

if pdfkit_available:
    import pdfkit
if weasyprint_available:
    import weasyprint


class FileConverter:
    """
    File converter class for converting between different file formats.
    
    This class provides methods for converting Markdown to HTML and PDF.
    """
    
    @staticmethod
    def markdown_to_html(markdown_content: str, css: Optional[str] = None) -> str:
        """
        Convert Markdown content to HTML.
        
        Args:
            markdown_content: Markdown content to convert
            css: Optional CSS styling to include
            
        Returns:
            HTML content
        """
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        
        # Add CSS if provided
        if css:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                {css}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
        else:
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
        
        return html
    
    @staticmethod
    def markdown_to_pdf(
        markdown_content: str, 
        output_path: Union[str, Path], 
        css: Optional[str] = None
    ) -> Path:
        """
        Convert Markdown content to PDF and save it.
        
        Args:
            markdown_content: Markdown content to convert
            output_path: Path to save the PDF
            css: Optional CSS styling to include
            
        Returns:
            Path to the saved PDF file
        """
        output_path = Path(output_path)
        
        # Ensure the directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert markdown to HTML
        html_content = FileConverter.markdown_to_html(markdown_content, css)
        
        # Create an HTML file as an intermediate step
        html_path = output_path.with_suffix('.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Try different PDF conversion methods in order of preference
        pdf_generated = False
        
        # Method 1: Try WeasyPrint
        if weasyprint_available:
            try:
                weasyprint.HTML(string=html_content).write_pdf(output_path)
                pdf_generated = True
                logger.info(f"PDF generated using WeasyPrint: {output_path}")
            except Exception as e:
                logger.warning(f"WeasyPrint conversion failed: {e}")
        
        # Method 2: Try pdfkit (wkhtmltopdf)
        if not pdf_generated and pdfkit_available:
            try:
                pdfkit.from_string(html_content, str(output_path))
                pdf_generated = True
                logger.info(f"PDF generated using pdfkit: {output_path}")
            except Exception as e:
                logger.warning(f"pdfkit conversion failed: {e}")
        
        # Method 3: Try using headless Chrome/Chromium
        if not pdf_generated:
            try:
                # Try with chromium first
                result = subprocess.run(
                    ["chromium", "--headless", "--disable-gpu", f"--print-to-pdf={output_path}", str(html_path)],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    pdf_generated = True
                    logger.info(f"PDF generated using headless Chromium: {output_path}")
                else:
                    # Try with chrome if chromium fails
                    result = subprocess.run(
                        ["google-chrome", "--headless", "--disable-gpu", f"--print-to-pdf={output_path}", str(html_path)],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        pdf_generated = True
                        logger.info(f"PDF generated using headless Chrome: {output_path}")
                    else:
                        logger.warning("Chrome/Chromium conversion failed")
            except FileNotFoundError:
                logger.warning("Chrome/Chromium not found on the system")
            except Exception as e:
                logger.warning(f"Error using Chrome/Chromium: {e}")
        
        # Method 4: Try pandoc if available
        if not pdf_generated:
            try:
                # Save markdown to a temporary file
                md_path = output_path.with_suffix('.md')
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                result = subprocess.run(
                    ["pandoc", str(md_path), "-o", str(output_path)],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    pdf_generated = True
                    logger.info(f"PDF generated using pandoc: {output_path}")
                else:
                    logger.warning(f"pandoc conversion failed: {result.stderr}")
            except FileNotFoundError:
                logger.warning("pandoc not found on the system")
            except Exception as e:
                logger.warning(f"Error using pandoc: {e}")
        
        if not pdf_generated:
            logger.error("Failed to generate PDF using any available method")
            raise RuntimeError("Failed to generate PDF using any available method")
        
        return output_path
