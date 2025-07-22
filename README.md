# AI Job Application Agent

An intelligent job application automation tool that uses local Large Language Models (LLMs) via Ollama to generate highly personalized cover letters and extract job information from various job boards.

## Features

- 🤖 **Local LLM-Powered Cover Letters**: Uses Ollama with local models (no API costs!)
- 📊 **Intelligent Job Matching**: Analyzes resume and job descriptions to find the best alignment points
- 🗂️ **Organized File Management**: Creates timestamped folders for each application
- 🌐 **Multi-Platform Support**: Works with various job boards (iCIMS, Greenhouse, etc.)
- 🔄 **Smart Fallbacks**: Handles different page structures and chat overlays
- ⚙️ **Environment-Based Configuration**: Secure configuration using .env files
- 🎯 **Dynamic Content Generation**: No templates - each cover letter is uniquely crafted
- 🔒 **Privacy-First**: Everything runs locally - no data sent to external APIs

## How It Works

1. **Resume Analysis**: Extracts key information, skills, and achievements from your resume
2. **Job Intelligence**: Analyzes job descriptions to understand requirements and company focus
3. **Local LLM Generation**: Uses Ollama to craft compelling, personalized cover letters locally
4. **Quality Assurance**: Ensures professional formatting and appropriate tone
5. **File Organization**: Saves everything in organized folders for easy access

## Supported Job Boards

- iCIMS Career Portals
- Greenhouse Job Boards  
- Custom job posting sites
- Any job board with accessible content

## Prerequisites

- Python 3.8+
- Chrome/Chromium browser (for Playwright)
- Ollama installed and running locally (https://ollama.ai/download)
- A local LLM model (e.g., llama3.1, mistral, codellama)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/47collective/JobMatchAI.git
cd JobMatchAI
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

5. Install and start Ollama:
```bash
# Install Ollama from https://ollama.ai/download
# Then pull a suitable model (recommended):
ollama pull llama3

# Or try other models:
ollama pull llama3.1
ollama pull mistral
ollama pull codellama
```

6. Set up your configuration:
```bash
cp .env.example .env
```

7. Edit `.env` file with your information:
   - **REQUIRED**: Set `RESUME_PATH` to point to your resume file
   - **RECOMMENDED**: Adjust `OLLAMA_MODEL` to match your preferred local model (default: llama3)
   - Set `COVER_LETTER_INSTRUCTIONS_PATH` to any additional instructions (optional)
   - Adjust Ollama and browser settings as needed

## Configuration

### Required Configuration
- `RESUME_PATH`: Path to your resume file (plain text format recommended)
- Ollama running locally with a suitable model

### Optional Configuration
- `COVER_LETTER_INSTRUCTIONS_PATH`: Additional instructions for cover letter style
- `OLLAMA_HOST`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: AI model to use (default: llama3)
- `OLLAMA_MAX_TOKENS`: Maximum response length (default: 2000)
- `OLLAMA_TEMPERATURE`: Creativity level 0-1 (default: 0.7)
- `BROWSER_HEADLESS`: Run browser in background (default: true)

## Recommended Models

For best results, use these Ollama models:
- **llama3** (8B): Excellent general purpose, great for professional writing (recommended)
- **llama3.1** (8B or 70B): Latest version with improvements
- **mistral** (7B): Fast and efficient, good quality output
- **codellama** (7B): Good for technical roles with coding focus
- **llama2** (7B/13B): Reliable fallback option

## Testing Your Setup

Test your Ollama connection:
```bash
curl http://localhost:11434/api/generate -d '{"model": "llama3", "prompt": "Hello, world!"}'
```

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
Create a text file with your cover letter preferences. The script will automatically parse:

**Quick Hits Section**: List your key achievements starting with bullet points (• or -)
```
Quick Hits:
• Your first major achievement
• Your second accomplishment  
• Your unique superpower
• What motivates you
• Your best reference
```

**Experience Content**: Include paragraphs describing your experience that the script can extract:
- Recent leadership roles and achievements
- Technical expertise and projects
- Current activities and interests

**Contact Info**: Include your LinkedIn profile URL in the format:
```
https://www.linkedin.com/in/your-profile/
```

The script will automatically extract and format these elements into a professional cover letter.

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

- `ApplicantName_CompanyName_CoverLetter.txt` - Personalized cover letter
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
