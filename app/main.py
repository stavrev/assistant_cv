#!/usr/bin/env python3
"""
Main module for the CV Assistant application.

This module orchestrates the execution of the different pipelines
and serves as the entry point from the CLI.
"""
import os
from typing import Optional

from app.config.settings import Settings
from app.pipelines.cv import CVPipeline
from app.pipelines.letter import LetterPipeline
from app.pipelines.adopt import AdoptPipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_cv(cv_file: Optional[str], jd_file: Optional[str], template: Optional[str]) -> None:
    """
    Run the CV tailoring pipeline.
    
    Args:
        cv_file: Path to the CV file
        jd_file: Path to the job description file
        template: Template directory to use
    """
    # Log command for debugging
    command = f"cv -cv {cv_file or 'default'} -jd {jd_file or 'default'} -template {template or 'default'}"
    logger.debug(f"Command: {command}")
    
    # Print minimal console output
    print(f"\nRunning CV tailoring pipeline...")
    
    # Initialize settings with optional overrides
    settings = Settings()
    if template:
        settings.template_dir = template
    
    # Initialize and run the CV pipeline
    pipeline = CVPipeline(settings)
    pipeline.run(cv_file, jd_file)


def run_letter(cv_file: Optional[str], jd_file: Optional[str], template: Optional[str]) -> None:
    """
    Run the cover letter generation pipeline.
    
    Args:
        cv_file: Path to the CV file
        jd_file: Path to the job description file
        template: Template directory to use
    """
    # Log command for debugging
    command = f"letter -cv {cv_file or 'default'} -jd {jd_file or 'default'} -template {template or 'default'}"
    logger.debug(f"Command: {command}")
    
    # Print minimal console output
    print(f"\nRunning cover letter generation pipeline...")
    
    # Initialize settings with optional overrides
    settings = Settings()
    if template:
        settings.template_dir = template
    
    # Initialize and run the letter pipeline
    pipeline = LetterPipeline(settings)
    pipeline.run(cv_file, jd_file)


def run_adopt(source: str, template: Optional[str]) -> None:
    """
    Run the CV template adaptation pipeline.
    
    Args:
        source: Path to the source CV file
        template: Template directory to use
    """
    # Log command for debugging
    command = f"adopt -source {source} -template {template or 'default'}"
    logger.debug(f"Command: {command}")
    
    # Print minimal console output
    print(f"\nRunning CV template adaptation pipeline...")
    
    # Initialize settings with optional overrides
    settings = Settings()
    if template:
        settings.template_dir = template
    
    # Initialize and run the adopt pipeline
    pipeline = AdoptPipeline(settings)
    pipeline.run(source)
