# ApplicantsFolder - Template Directory

This folder contains template files for new users of the JobApplyAI system. **DO NOT** edit these files directly. Instead, copy this entire folder and customize it with your personal information.

## Quick Setup

1. **Copy this folder** to create your personal directory:
   ```
   Copy: ApplicantsFolder → YourName_JobApply
   ```

2. **Customize the files** with your information:
   - `YourName_Resume.txt` → Replace with your actual resume
   - `InstructionsForCoverletter_Template` → Update with your preferences
   - `cover_letter_config.json` → Update Quick Hits and contact info
   - `pdf_config.json` → Adjust formatting preferences (optional)

3. **Update your `.env` file** to point to your folder:
   ```properties
   RESUME_PATH=C:/path/to/YourName_JobApply/YourName_Resume.txt
   COVER_LETTER_INSTRUCTIONS_PATH=C:/path/to/YourName_JobApply/InstructionsForCoverletter_Template
   ```

## File Descriptions

### Required Files (Customize These)
- **`YourName_Resume.txt`** - Your resume in plain text format
- **`InstructionsForCoverletter_Template`** - Your personal cover letter instructions for the LLM

### Configuration Files (Optional to customize)
- **`cover_letter_config.json`** - Quick Hits and formatting preferences
- **`pdf_config.json`** - PDF formatting settings

### Documentation
- **`PDF_CONFIG_GUIDE.md`** - Guide for customizing PDF output
- **`README.md`** - This file

## Important Notes

⚠️ **Privacy**: Never commit your personal folder to version control if it contains real resume data and personal information.

✅ **Template**: This ApplicantsFolder should be the only applicant folder committed to the repository.

🔄 **Updates**: When the template files are updated, you can copy individual files to your personal folder as needed.

## Example .env Configuration

```properties
# Personal Configuration
RESUME_PATH=C:/Users/yourname/JobApplyAI/MyJobApply/YourName_Resume.txt
COVER_LETTER_INSTRUCTIONS_PATH=C:/Users/yourname/JobApplyAI/MyJobApply/InstructionsForCoverletter_Template

# LLM Configuration
TIER1_LLM_PROVIDER=gemini
TIER2_LLM_PROVIDER=ollama
GEMINI_API_KEY=your_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b
```

## Getting Started

1. Run through the Quick Setup above
2. Test the system: `python JobApplyAI.py "https://example-job-url.com"`
3. Review and customize generated cover letters
4. Adjust instructions and configuration as needed

Need help? Check the main README.md in the root directory.
