# PDF Configuration Guide

## Overview
The JobApplyAI system generates cover letters in both text and PDF formats. You can customize the PDF formatting by editing the `pdf_config.json` file in your applicant folder.

## Setup Instructions
1. Copy the `ApplicantsFolder` to create your personal folder (e.g., `MyApplication`)
2. Update the `.env` file to point to your personal folder
3. Customize the configuration files with your information

## Configuration File: pdf_config.json

### Page Layout
- `page_size`: Currently supports "letter" (8.5x11 inches)
- `margins`: Set margins in inches
  - `top`, `bottom`, `left`, `right`: Margin sizes in inches

### Fonts
- `title_font`: Font for the title (e.g., "Helvetica-Bold", "Times-Bold")
- `title_size`: Title font size in points
- `body_font`: Font for main text (e.g., "Helvetica", "Times-Roman")
- `body_size`: Body text font size in points
- `contact_font`: Font for contact information
- `contact_size`: Contact info font size in points

### Spacing
- `title_space_after`: Space after title in points
- `paragraph_space_after`: Space after each paragraph in points
- `line_height`: Line height (leading) in points
- `contact_space_before`: Extra space before contact info in points

### Formatting Options
- `show_title`: true/false - Whether to show "Cover Letter" title
- `title_text`: Text to display as title
- `justify_text`: true/false - Whether to justify text (currently disabled)
- `indent_paragraphs`: true/false - Whether to indent first line of paragraphs

## Available Fonts
Common fonts you can use:
- Helvetica (default sans-serif)
- Helvetica-Bold
- Times-Roman (serif)
- Times-Bold
- Courier (monospace)

## Example Customizations

### Professional Conservative Style
```json
{
  "pdf_formatting": {
    "fonts": {
      "title_font": "Times-Bold",
      "title_size": 14,
      "body_font": "Times-Roman",
      "body_size": 12
    },
    "formatting": {
      "show_title": false,
      "indent_paragraphs": true
    }
  }
}
```

### Modern Clean Style
```json
{
  "pdf_formatting": {
    "fonts": {
      "title_font": "Helvetica-Bold",
      "title_size": 16,
      "body_font": "Helvetica",
      "body_size": 11
    },
    "spacing": {
      "paragraph_space_after": 15,
      "line_height": 16
    }
  }
}
```

## Output Files
The system creates both formats:
- `[YourName]_[Company]_coverletter.txt` - Editable text version
- `[YourName]_[Company]_coverletter.pdf` - Formatted PDF version

## Setup Workflow
1. Copy `ApplicantsFolder` to your personal folder name
2. Edit `YourName_Resume.txt` with your actual resume
3. Customize `InstructionsForCoverletter_Template` with your preferences
4. Update configuration files with your information
5. Update `.env` file paths to point to your folder
6. Run the system to generate cover letters

## Environment Variables to Update
```properties
RESUME_PATH=C:/path/to/your/folder/YourName_Resume.txt
COVER_LETTER_INSTRUCTIONS_PATH=C:/path/to/your/folder/InstructionsForCoverletter_Template
```

This allows you to:
- Keep your personal information separate from the code
- Version control your personal templates
- Share the system without exposing personal data
- Customize formatting to your preferences
