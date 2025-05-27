# CV Assistant

## Motivation

In today's competitive job market, standing out is more challenging than ever. Many qualified candidates are overlooked simply because their application materials don't effectively highlight their relevant skills and experiences for specific positions. CV Assistant was born from this challenge, aiming to level the playing field by helping job seekers present their qualifications in the most compelling way possible.

While still in its early stages, CV Assistant has tremendous potential to transform how people approach job applications. By leveraging AI to tailor CVs and generate personalized cover letters, it empowers job seekers to put their best foot forward without spending hours manually customizing documents for each application.

## Purpose

CV Assistant is a Python CLI application designed to optimize your job application process by tailoring your CV and generating cover letters that highlight relevant skills and experiences for specific job descriptions.

The application uses AI to analyze job descriptions and your CV, then strategically emphasizes the matching skills and experiences to increase your chances of getting past Applicant Tracking Systems (ATS) and catching the attention of recruiters.

**Important**: CV Assistant only works with information that exists in your original CV. It does not fabricate experiences or skills, ensuring all tailoring is truthful and authentic.

## Features

- **CV Tailoring**: Customize your CV to match specific job descriptions, highlighting relevant skills and experiences
- **Cover Letter Generation**: Create targeted cover letters that emphasize your qualifications for the position
- **Template Adaptation**: Adapt your CV to different templates without changing content
- **Multiple Output Formats**: Generate Markdown, HTML, and PDF outputs for all documents

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cvtailor
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements-install.txt
   ```

4. Set up your OpenAI API key:
   
   The application uses OpenAI's models for generating tailored content. You'll need to provide your OpenAI API key as an environment variable:

   ```bash
   # Linux/macOS
   export OPENAI_API_KEY="your-api-key"
   
   # Windows Command Prompt
   set OPENAI_API_KEY=your-api-key
   
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key"
   ```

   Alternatively, you can create a `.env` file in the project root directory:

   ```
   OPENAI_API_KEY=your-api-key
   ```

## Quick Start

CV Assistant is designed for ease of use with sensible defaults. For the most common use cases, you can simply run:

```bash
# Tailor your CV to the most recent job description
python run.py cv

# Generate a cover letter for the most recent job description
python run.py letter
```

The application will automatically:
1. Use the most recent CV file in the `inputs/cv/` directory
2. Use the most recent job description in the `inputs/job_descriptions/` directory
3. Use the default template
4. Generate output files in the `outputs/` directory

## Usage

### Preparing Job Descriptions

To use the application with job descriptions:

1. Copy the job description text from a job posting
2. Create a new text file in the `inputs/job_descriptions/` directory with a `.txt` extension
3. Paste the job description into this file and save it

For example: `inputs/job_descriptions/"Company Name - senior developer position.txt"`

### Tailoring a CV to a Job Description

```bash
# Quick usage with defaults
python run.py cv

# Specifying files and template - optional
python run.py cv -cv inputs/cv/your_cv.md -jd inputs/job_descriptions/job_posting.txt -template default
```

### Generating a Cover Letter

```bash
# Quick usage with defaults
python run.py letter

# Specifying files and template - optional
python run.py letter -cv inputs/cv/your_cv.md -jd inputs/job_descriptions/job_posting.txt -template default
```

### Adapting a CV to a New Template

```bash
python run.py adopt -source inputs/cv/your_cv.md -template template_name
```

* `template_name` is the name of the template directory in the `templates/` directory, example: `... -template default `

### Command Options

- `-cv`: Path to your CV file (if not provided, uses the most recent CV in the `inputs/cv/` directory)
- `-jd`: Path to the job description file (if not provided, uses the most recent job description in the `inputs/job_descriptions/` directory)
- `-template`: Template directory to use (defaults to "default")
- `-source`: Source CV file to adapt (required for the "adopt" command)

## Output

All generated files are saved in the `outputs/` directory, organized by date and job description name. File names include the candidate's name and company name extracted from the CV and job description:

```
outputs/
└── 2025-05-27 TechForward/        # Date + job description name
    ├── cv/                         # CV pipeline output
    │   ├── John Doe - cv (TechForward).md
    │   ├── John Doe - cv (TechForward).html
    │   ├── John Doe - cv (TechForward).pdf
    │   └── TechForward.txt         # Copy of job description
    └── letter/                     # Letter pipeline output
        ├── John Doe - cover letter (TechForward).md
        ├── John Doe - cover letter (TechForward).html
        ├── John Doe - cover letter (TechForward).pdf
        └── TechForward.txt         # Copy of job description
```

The application automatically extracts the candidate name from the CV and the company name from the job description to create more descriptive file names.

## Templates

Templates are stored in the `templates/` directory, with each template in its own subdirectory. The default template is provided as a starting point.

To create a new template:

1. Create a new directory under `templates/` (e.g., `templates/professional/`)
2. Add the following files:
   - `cv_template.md`: Template for CV
   - `letter_template.md`: Template for cover letter
   - `cv_style.css`: CSS styling for CV HTML and PDF outputs
   - `letter_style.css`: CSS styling for cover letter HTML and PDF outputs
   - `cv_instructions.md`: Instructions for CV generation
   - `letter_instructions.md`: Instructions for cover letter generation

See [Architecture.md](Architecture.md) for more details on creating templates.

## Running Tests

The application includes comprehensive tests to ensure functionality:

```bash
python -m unittest discover -s tests
```

Test modules:
- `test_file_io.py`: Tests file reading/writing and file finding utilities
- `test_converter.py`: Tests Markdown to HTML/PDF conversion
- `test_render.py`: Tests template rendering functionality
- `test_cv_pipeline.py`: Tests the CV pipeline execution

For more details on tests, see [Architecture.md](Architecture.md).

## Directory Structure

```
cvtailor/
├── run.py                     # CLI entry point
├── app/                       # Main application code
│   ├── main.py                # Orchestrates pipeline execution
│   ├── pipelines/             # Pipeline implementations
│   │   ├── base.py            # Base pipeline class
│   │   ├── cv.py              # CV tailoring pipeline
│   │   ├── letter.py          # Cover letter pipeline
│   │   └── adopt.py           # Template adaptation pipeline
│   ├── utils/                 # Utility modules
│   │   ├── file_io.py         # File I/O utilities
│   │   ├── render.py          # Template rendering
│   │   ├── converter.py       # Format conversion
│   │   └── logger.py          # Logging configuration
│   └── config/                # Configuration
│       └── settings.py        # Application settings
├── templates/                 # Template directories
├── inputs/                    # Input files
│   ├── job_descriptions/      # Job description files
│   └── cv/                    # CV files
├── outputs/                   # Generated output files
└── tests/                     # Unit tests
```

For a detailed explanation of the architecture, see [Architecture.md](Architecture.md).

## Requirements

- Python 3.8+
- Dependencies listed in requirements-install.txt

## Future Development

The CV Assistant application has several potential areas for future development:

### Template Expansion
- **Role-Specific Templates**: Create specialized templates for different job functions (engineer, manager, executive, etc.)
- **Seniority-Based Templates**: Develop templates optimized for different career levels (entry-level, mid-career, senior)
- **Industry-Specific Templates**: Design templates tailored to specific industries (tech, finance, healthcare, etc.)

### LLM Provider Options
- **Multiple LLM Providers**: Add support for alternative LLM providers (Anthropic, Gemini, Llama, etc.)
- **Provider Selection**: Allow users to choose their preferred LLM provider through configuration
- **Local LLM Support**: Add capability to run with locally hosted models for privacy and cost savings

### Enhanced AI Capabilities
- **Agentic Execution**: Implement more sophisticated AI agents to verify output quality and consistency
- **Feedback Loop**: Add capability for the system to refine outputs based on user feedback
- **Automated Quality Checks**: Implement automated checks for factual accuracy and alignment with source CV

### Additional Features
- **Interview Preparation**: Generate potential interview questions based on the job description and CV
- **Skills Gap Analysis**: Identify skills mentioned in job descriptions that are missing from the CV
- **Application Tracking**: Add functionality to track job applications and their statuses
- **Interview Guide Generation**: Create comprehensive interview preparation guides for different stages (screening, leadership, technical, and final rounds)
- **Quality Assurance Testing**: Implement semantic analysis to verify that generated content strictly adheres to the source CV without fabricating information

## Contributing

CV Assistant is in its infancy, and we welcome contributions from the community to help it grow and improve. Whether you're a developer, designer, or someone with experience in HR and recruitment, your insights can be valuable.

### How to Contribute

1. **Fork the Repository**: Start by forking the repository to your GitHub account.

2. **Clone Your Fork**: Clone your fork to your local machine.
   ```bash
   git clone https://github.com/YOUR-USERNAME/assistant_cv.git
   cd assistant_cv
   ```

3. **Create a Branch**: Create a branch for your feature or bugfix.
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Your Changes**: Implement your changes, following the code style of the project.

5. **Write Tests**: Add tests for your changes to ensure they work as expected.

6. **Run Tests**: Make sure all tests pass.
   ```bash
   python -m unittest discover -s tests
   ```

7. **Commit Your Changes**: Commit your changes with a clear message describing what you've done.
   ```bash
   git commit -m "Add feature: your feature description"
   ```

8. **Push to GitHub**: Push your changes to your fork.
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Submit a Pull Request**: Go to the original repository and submit a pull request from your branch to the main branch.

### Types of Contributions

We're looking for various types of contributions:

- **Code Improvements**: Enhance existing functionality or add new features
- **Documentation**: Improve or expand documentation
- **Templates**: Create new CV or cover letter templates
- **Testing**: Add or improve tests
- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Write docstrings for all functions, classes, and modules
- Add appropriate error handling
- Maintain backward compatibility when possible
- Write tests for new functionality

We appreciate your interest in contributing to CV Assistant! Together, we can build a tool that truly helps people in their job search journey.

## License

MIT
