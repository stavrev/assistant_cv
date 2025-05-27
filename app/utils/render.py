"""
Template rendering utility module for the CV Assistant application.

This module provides functions for rendering templates using Jinja2.
"""
from pathlib import Path
from typing import Dict, Any, Union

import jinja2

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateRenderer:
    """
    Template renderer class using Jinja2.
    
    This class provides methods for rendering templates with context variables.
    """
    
    @staticmethod
    def render_string(template_str: str, context: Dict[str, Any], strict: bool = True) -> str:
        """
        Render a template string with the given context.
        
        Args:
            template_str: Template string to render
            context: Dictionary of context variables
            strict: If True, raises an error for undefined variables
            
        Returns:
            Rendered template as a string
        """
        try:
            if strict:
                env = jinja2.Environment(undefined=jinja2.StrictUndefined)
                template = env.from_string(template_str)
            else:
                template = jinja2.Template(template_str)
            return template.render(**context)
        except jinja2.exceptions.TemplateError as e:
            logger.error(f"Error rendering template string: {e}")
            raise
    
    @staticmethod
    def render_file(template_path: Union[str, Path], context: Dict[str, Any], strict: bool = True) -> str:
        """
        Render a template file with the given context.
        
        Args:
            template_path: Path to the template file
            context: Dictionary of context variables
            strict: If True, raises an error for undefined variables
            
        Returns:
            Rendered template as a string
        """
        template_path = Path(template_path)
        
        try:
            # Create a file system loader for the template directory
            template_dir = template_path.parent
            template_name = template_path.name
            
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                autoescape=jinja2.select_autoescape(['html', 'xml']),
                undefined=jinja2.StrictUndefined if strict else jinja2.Undefined
            )
            
            template = env.get_template(template_name)
            return template.render(**context)
        except jinja2.exceptions.TemplateError as e:
            logger.error(f"Error rendering template file {template_path}: {e}")
            raise
        except FileNotFoundError:
            logger.error(f"Template file not found: {template_path}")
            raise
