#!/usr/bin/env python3
"""
CV Assistant - A CLI tool for tailoring CVs and cover letters to job descriptions.

This is the main entry point for the application that handles command line arguments
and delegates execution to the appropriate pipeline.
"""
import argparse
import sys
from app import main


def parse_arguments():
    """
    Parse command line arguments for the CV Assistant application.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="Tailor your CV or cover letter to a job description using templates."
    )

    subparsers = parser.add_subparsers(dest="command", help="Pipeline to run (required)")

    # CV command
    cv_parser = subparsers.add_parser("cv", help="Generate a tailored CV")
    cv_parser.add_argument("-cv", dest="cv_file", help="Path to your CV file")
    cv_parser.add_argument("-jd", dest="jd_file", help="Path to the job description file")
    cv_parser.add_argument("-template", dest="template", help="Template directory to use")

    # Letter command
    letter_parser = subparsers.add_parser("letter", help="Generate a cover letter")
    letter_parser.add_argument("-cv", dest="cv_file", help="Path to your CV file")
    letter_parser.add_argument("-jd", dest="jd_file", help="Path to the job description file")
    letter_parser.add_argument("-template", dest="template", help="Template directory to use")

    # Adopt command
    adopt_parser = subparsers.add_parser("adopt", help="Adapt a CV to a new template")
    adopt_parser.add_argument("-source", required=True, help="Source CV file to adapt")
    adopt_parser.add_argument("-template", dest="template", help="Template directory to use")

    return parser


def main_cli():
    """
    Main CLI entry point for the application.
    
    Parses command line arguments and delegates execution to the appropriate
    pipeline in the main module.
    """
    parser = parse_arguments()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "cv":
            main.run_cv(args.cv_file, args.jd_file, args.template)
        elif args.command == "letter":
            main.run_letter(args.cv_file, args.jd_file, args.template)
        elif args.command == "adopt":
            main.run_adopt(args.source, args.template)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_cli()
