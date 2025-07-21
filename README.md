# AI Job Application Agent

An intelligent job application automation tool that generates personalized cover letters and extracts job descriptions from various job boards.

## Features

- 🤖 **Automated Job Information Extraction**: Extracts job title, company, and location from job URLs
- 📝 **Personalized Cover Letter Generation**: Creates tailored cover letters using your resume and instructions
- 🗂️ **Organized File Management**: Creates timestamped folders for each application
- 🌐 **Multi-Platform Support**: Works with various job boards (iCIMS, Greenhouse, etc.)
- 🔄 **Smart Fallbacks**: Handles different page structures and chat overlays
- ⚙️ **Environment-Based Configuration**: Secure configuration using .env files

## Supported Job Boards

- iCIMS Career Portals
- Greenhouse Job Boards
- Custom job posting sites

## Prerequisites

- Python 3.8+
- Chrome/Chromium browser (for Playwright)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd job-apply-ai
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install chromium
```

5. Set up your configuration:
```bash
cp .env.example .env
```

6. Edit `.env` file with your information:
   - Set `RESUME_PATH` to point to your resume file
   - Set `COVER_LETTER_INSTRUCTIONS_PATH` to your cover letter template
   - Adjust browser settings as needed

## Usage

### Basic Usage

```bash
python JobApplyAI.py "https://job-url-here"
```

### With Custom Resume

```bash
python JobApplyAI.py "https://job-url-here" "path/to/your/resume.txt"
```

### Example

```bash
python JobApplyAI.py "https://careers-company.icims.com/jobs/1234/software-engineer/job"
```

## Configuration

### Resume File
Create a text file containing your resume information. The script will automatically extract:
- Your name and email
- Experience highlights
- Technical skills

### Cover Letter Instructions
Create a text file with your cover letter preferences including:
- Quick hits/achievements to highlight
- Preferred tone and style
- Specific experiences to emphasize

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RESUME_PATH` | Path to your resume file | `/path/to/resume.txt` |
| `COVER_LETTER_INSTRUCTIONS_PATH` | Path to cover letter instructions | `/path/to/instructions.txt` |
| `BROWSER_HEADLESS` | Run browser in headless mode | `true` or `false` |
| `BROWSER_TIMEOUT` | Page load timeout in milliseconds | `30000` |
| `DEFAULT_JOB_URL` | Default job URL for testing | `https://example.com/job` |

## Output

For each job application, the script creates a folder named `CompanyName_YYYYMMDD_HHMMSS` containing:

- `YourName_CompanyName_CoverLetter.txt` - Personalized cover letter
- `CompanyName_JobDescription.txt` - Extracted job description

## Troubleshooting

### Common Issues

1. **"Resume file not found"**: Check the `RESUME_PATH` in your `.env` file
2. **"Cover letter instructions not found"**: Verify `COVER_LETTER_INSTRUCTIONS_PATH` is correct
3. **Job description shows "None"**: Some sites require manual job description copying due to chat overlays or dynamic content

### Browser Issues

If you encounter browser-related errors:
```bash
playwright install chromium  # Reinstall browser
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is designed to assist with job applications by automating repetitive tasks. Always review generated content before submitting applications. Respect the terms of service of job board websites and use responsibly.
