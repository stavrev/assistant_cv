# CV Assistant Architecture

This document describes the architecture of the CV Assistant application, explaining the directory structure, how components interact, and how to extend the application.

## Directory Structure

```
cvtailor/
├── run.py                     # CLI entry point
├── app/                       # Main application code
│   ├── main.py                # Orchestrates pipeline execution
│   ├── pipelines/             # Pipeline implementations
│   │   ├── base.py            # Base pipeline class with common functionality
│   │   ├── cv.py              # CV tailoring pipeline
│   │   ├── letter.py          # Cover letter generation pipeline
│   │   └── adopt.py           # Template adaptation pipeline
│   ├── utils/                 # Utility modules
│   │   ├── file_io.py         # File reading/writing utilities
│   │   ├── render.py          # Template rendering with Jinja2
│   │   ├── converter.py       # File format conversion (MD→HTML→PDF)
│   │   └── logger.py          # Logging configuration
│   └── config/                # Configuration
│       └── settings.py        # Application settings
├── templates/                 # Template directories
│   └── default/               # Default template
│       ├── cv_template.md     # CV template
│       ├── letter_template.md # Cover letter template
│       ├── style.css          # CSS styling for HTML/PDF
│       ├── cv_instructions.md # Instructions for CV generation
│       └── letter_instructions.md # Instructions for letter generation
├── inputs/                    # Input files
│   ├── job_descriptions/      # Job description files
│   └── cv/                    # CV files
├── outputs/                   # Generated output files
├── logs/                      # Application logs
│   └── run.log                # Unified log file with rotation
└── tests/                     # Unit tests
```

## Logging Strategy

The application uses a comprehensive logging strategy to balance user experience with debugging capabilities:

1. **Unified Log File**: All application logs are written to a single `run.log` file in the `logs/` directory, providing a complete record of application activity.

2. **Log Rotation**: The log file uses rotation to prevent excessive disk usage, keeping up to 5 backup files with a maximum size of 10MB each.

3. **Verbosity Levels**:
   - **File Logs**: Detailed DEBUG-level logs capture all operations, including API calls, file operations, and processing steps.
   - **Console Output**: Minimal user-friendly output shows only essential information and error messages with clear instructions on how to fix issues.

4. **Command Logging**: Each command executed by the user is logged with its parameters for reference and debugging.

5. **Error Handling**: Detailed error information is logged to the file while concise, actionable error messages are shown to the user.

## Component Interaction

### Execution Flow

1. **Entry Point**: `run.py` parses command-line arguments and delegates to `app/main.py`
2. **Main Module**: `app/main.py` initializes settings and the appropriate pipeline
3. **Pipeline Execution**: The pipeline loads inputs, processes them, and generates outputs
4. **Output Generation**: Results are saved as Markdown, HTML, and PDF files

### Pipeline Structure

All pipelines inherit from `BasePipeline` in `app/pipelines/base.py`, which provides common functionality:

- Loading CV and job description files
- Loading templates and instructions
- Setting up output directories
- Saving output files in multiple formats

Each specific pipeline (`cv.py`, `letter.py`, `adopt.py`) implements its own `run()` method and specialized processing logic.

## Adding New Templates

To create a new template:

1. Create a new directory under `templates/` (e.g., `templates/professional/`)
2. Add the following files:

   - **cv_template.md**: Template for CV in Markdown format
   - **letter_template.md**: Template for cover letter in Markdown format
   - **style.css**: CSS styling for HTML and PDF outputs
   - **cv_instructions.md** (optional): Instructions for CV generation
   - **letter_instructions.md** (optional): Instructions for cover letter generation

### Template Format

Templates use Markdown with Jinja2 templating syntax. While the application doesn't currently use variables in templates (it passes the entire template to the LLM), you can structure your templates with placeholders for future enhancements.

Example CV template structure:
```markdown
# {{name}}

**Email:** {{email}} | **Phone:** {{phone}} | **Location:** {{location}}

## PROFESSIONAL SUMMARY

{{summary}}

## SKILLS

{{skills}}

## PROFESSIONAL EXPERIENCE

{{experience}}

...
```

## How the Application Works

### Command Processing

1. `run.py` parses command-line arguments using `argparse`
2. Based on the command (`cv`, `letter`, or `adopt`), it calls the appropriate function in `app/main.py`
3. `app/main.py` initializes settings and the corresponding pipeline class

### CV Pipeline (`cv.py`)

1. Loads the CV and job description files using utilities from `BasePipeline`
2. Loads the CV template and instructions
3. Calls the LLM to generate a tailored CV based on the inputs
4. Saves the results in multiple formats (MD, HTML, PDF)

### Letter Pipeline (`letter.py`)

1. Loads the CV and job description files
2. Loads the letter template and instructions
3. Calls the LLM to generate a cover letter based on the inputs
4. Saves the results in multiple formats

### Adopt Pipeline (`adopt.py`)

1. Loads the source CV file
2. Loads the target CV template and instructions
3. Calls the LLM to adapt the CV to the new template format
4. Saves the results in multiple formats

## Testing

The application includes unit tests for core functionality:

- `test_file_io.py`: Tests file reading/writing utilities
- `test_converter.py`: Tests file format conversion
- `test_render.py`: Tests template rendering
- `test_cv_pipeline.py`: Tests the CV pipeline execution

Run tests using:
```bash
python -m unittest discover -s tests
```

### Test Details

- **test_file_io.py**: Tests reading/writing files, finding the latest file in a directory, and finding files in multiple directories
- **test_converter.py**: Tests converting Markdown to HTML and PDF, with and without CSS styling
- **test_render.py**: Tests rendering template strings and files with context variables, handling missing variables, and conditional logic
- **test_cv_pipeline.py**: Tests the end-to-end execution of the CV pipeline, including mocking the LLM response

## Extension Points

The application is designed to be easily extensible:

1. **New Pipelines**: Create a new class in `app/pipelines/` that inherits from `BasePipeline`
2. **New Templates**: Add a new directory under `templates/` with the required files
3. **New Commands**: Add a new subparser in `run.py` and a corresponding function in `app/main.py`
4. **New Output Formats**: Extend the `FileConverter` class in `app/utils/converter.py`
