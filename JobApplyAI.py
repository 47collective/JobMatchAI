#!/usr/bin/env python3
"""
Enhanced LLM-powered job application processor that eliminates hardcoded patterns
and uses AI for intelligent resume parsing and job information extraction.
"""
import asyncio
import time
import re
import os
import sys
import json
import urllib.parse
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

# Load environment variables from .env file
load_dotenv(override=True)  # Force override system environment variables

class LLMJobProcessor:
    """Enhanced job processor using LLM for all extraction and generation tasks."""
    
    def __init__(self):
        # Initialize tiered LLM system
        self.tier1_provider = os.getenv('TIER1_LLM_PROVIDER')  # For cover letter generation
        self.tier2_provider = os.getenv('TIER2_LLM_PROVIDER')  # For web scraping/parsing
        
        # Validate required tier configurations
        if not self.tier1_provider:
            raise ValueError("TIER1_LLM_PROVIDER must be set in .env file")
        if not self.tier2_provider:
            raise ValueError("TIER2_LLM_PROVIDER must be set in .env file")
            
        self.tier1_provider = self.tier1_provider.lower()
        self.tier2_provider = self.tier2_provider.lower()
        
        # Initialize provider configurations dynamically
        self._init_provider_configs()
        
        print(f"   🎯 Tier 1 LLM (Cover Letters): {self.tier1_provider}")
        print(f"   🔍 Tier 2 LLM (Web Scraping): {self.tier2_provider}")
        self._print_provider_details()
    
    def _init_provider_configs(self):
        """Initialize provider configurations for both tiers."""
        # Initialize Tier 1 LLM configuration
        self._init_Tier1LLM_config()
        
        # Initialize Tier 2 LLM configuration (only if different from Tier 1)
        if self.tier2_provider != self.tier1_provider:
            self._init_Tier2LLM_config()
    
    def _init_Tier1LLM_config(self):
        """Initialize Tier 1 LLM configuration dynamically based on provider from .env."""
        self._init_tier_config(1, self.tier1_provider)
    
    def _init_Tier2LLM_config(self):
        """Initialize Tier 2 LLM configuration dynamically based on provider from .env."""
        # Only initialize if different from Tier 1 to avoid duplicate initialization
        if self.tier2_provider != self.tier1_provider:
            self._init_tier_config(2, self.tier2_provider)
    
    def _init_tier_config(self, tier, provider):
        """Dynamically initialize any provider configuration based on .env file."""
        provider_upper = provider.upper()
        
        # Dynamic environment variable lookup - let .env file drive everything
        base_url_key = f'{provider_upper}_BASE_URL'
        host_key = f'{provider_upper}_HOST'  # Alternative key name
        model_key = f'{provider_upper}_MODEL'
        api_key_key = f'{provider_upper}_API_KEY'
        
        # Check if this is an API-based service (has API key) or local service (has base URL/host)
        api_key = os.getenv(api_key_key)
        base_url = os.getenv(base_url_key) or os.getenv(host_key)
        model = os.getenv(model_key)
        
        if api_key:
            # This is an API-based service (external APIs)
            if not api_key:
                raise ValueError(f"{api_key_key} must be set in .env file for Tier {tier}")
            
            # Store with generic tier-based naming
            setattr(self, f'tier{tier}_api_key', api_key)
            setattr(self, f'tier{tier}_model', model or f'{provider}-default-model')
            
            # Initialize API client dynamically based on provider
            # Use environment variable pattern to determine provider type
            provider_upper = provider.upper()
            if os.getenv(f'{provider_upper}_API_KEY'):
                # Configure based on known API patterns
                if 'gemini' in provider.lower():
                    try:
                        import google.generativeai as genai
                        genai.configure(api_key=api_key)
                        setattr(self, f'tier{tier}_client', genai.GenerativeModel(model or f'{provider}-default'))
                    except ImportError:
                        raise ValueError("google-generativeai package is required. Install with: pip install google-generativeai")
                # Add other API-based providers here as needed
                # elif 'openai' in provider.lower():
                #     # Add OpenAI configuration here
                #     pass
            else:
                # Generic API client initialization for unknown providers
                setattr(self, f'tier{tier}_client', {'api_key': api_key, 'model': model})
            
        elif base_url:
            # This is a local/self-hosted service
            if not base_url:
                raise ValueError(f"{base_url_key} or {host_key} must be set in .env file for Tier {tier}")
            if not model:
                raise ValueError(f"{model_key} must be set in .env file for Tier {tier}")
            
            # Store with generic tier-based naming
            setattr(self, f'tier{tier}_base_url', base_url)
            setattr(self, f'tier{tier}_model', model)
            
        else:
            raise ValueError(f"No valid configuration found for {provider}. Need either {api_key_key} or {base_url_key}/{host_key} in .env file")
    
    def _print_provider_details(self):
        """Print provider-specific details dynamically."""
        # Print details for each tier dynamically
        for tier in [1, 2]:
            provider = self.tier1_provider if tier == 1 else self.tier2_provider
            
            # Check what configuration exists for this tier
            model_attr = f'tier{tier}_model'
            if hasattr(self, model_attr):
                model_value = getattr(self, model_attr)
                print(f"   🔗 Tier {tier} ({provider.title()}) model: {model_value}")
        
    def _call_llm(self, prompt, system_prompt=None, tier=2):
        """
        Call the appropriate LLM based on tier - completely dynamic.
        tier=1: Use Tier 1 LLM (high-quality for cover letters)
        tier=2: Use Tier 2 LLM (cost-effective for parsing/scraping)
        """
        provider = self.tier1_provider if tier == 1 else self.tier2_provider
        
        # Dynamic tier-based method dispatch
        return self._call_tier_llm(tier, provider, prompt, system_prompt)
    
    def _call_tier_llm(self, tier, provider, prompt, system_prompt=None):
        """Dynamically call any LLM provider based on tier configuration."""
        try:
            model_attr = f'tier{tier}_model'
            model = getattr(self, model_attr)
            
            print(f"   🤖 Using Tier {tier} LLM ({provider.title()}): {model}")
            
            # Check if this is an API-based service or local service
            api_key_attr = f'tier{tier}_api_key'
            base_url_attr = f'tier{tier}_base_url'
            client_attr = f'tier{tier}_client'
            
            if hasattr(self, api_key_attr):
                # API-based service
                return self._call_api_service(tier, provider, prompt, system_prompt)
            elif hasattr(self, base_url_attr):
                # Local/self-hosted service
                return self._call_local_service(tier, provider, prompt, system_prompt)
            else:
                raise ValueError(f"No valid configuration found for Tier {tier} ({provider})")
                
        except Exception as e:
            print(f"   ⚠️ Tier {tier} LLM ({provider}) call failed: {e}")
            return None, False
    
    def _call_api_service(self, tier, provider, prompt, system_prompt=None):
        """Call an API-based LLM service."""
        client_attr = f'tier{tier}_client'
        
        if hasattr(self, client_attr):
            client = getattr(self, client_attr)
            
            # Handle different types of API clients dynamically
            if hasattr(client, 'generate_content'):
                # This looks like a Google Generative AI client
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                # For JSON responses, add explicit instruction
                if "Return a JSON object" in prompt or "as JSON" in prompt:
                    full_prompt += "\n\nIMPORTANT: Return only valid JSON, no additional text or markdown formatting."
                
                response = client.generate_content(full_prompt)
                
                if response.text:
                    content = response.text.strip()
                    
                    # Clean up potential markdown formatting
                    if content.startswith("```json"):
                        content = content.replace("```json", "").replace("```", "").strip()
                    elif content.startswith("```"):
                        content = content.replace("```", "").strip()
                    
                    try:
                        # Try to parse as JSON first
                        return json.loads(content), True
                    except json.JSONDecodeError:
                        # If JSON parsing fails, return raw content
                        return {"content": content}, True
                else:
                    print(f"   ⚠️ Tier {tier} API returned empty response")
                    return None, False
            else:
                # Generic API client handling for unknown providers
                print(f"   ⚠️ Generic API client not yet implemented for {provider}")
                return None, False
        else:
            raise ValueError(f"No client found for Tier {tier} ({provider})")
    
    def _call_local_service(self, tier, provider, prompt, system_prompt=None):
        """Call a local/self-hosted LLM service."""
        try:
            import requests
            
            base_url_attr = f'tier{tier}_base_url'
            model_attr = f'tier{tier}_model'
            
            base_url = getattr(self, base_url_attr)
            model = getattr(self, model_attr)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Use standard local API format (local service compatible)
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "format": "json"
            }
            
            response = requests.post(
                f"{base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('message', {}).get('content', '')
                try:
                    return json.loads(content), True
                except json.JSONDecodeError:
                    # If JSON parsing fails, return raw content
                    return {"content": content}, True
            else:
                print(f"   ⚠️ Tier {tier} Local API error: {response.status_code}")
                return None, False
                
        except ImportError:
            raise ValueError("requests package is required for local services. Install with: pip install requests")
        except Exception as e:
            print(f"   ⚠️ Local service call failed: {e}")
            return None, False
    
    def _load_pdf_config(self):
        """Load PDF formatting configuration from config file."""
        config_path = os.path.join(os.path.dirname(__file__), 'AllMyStuff', 'pdf_config.json')
        default_config = {
            "pdf_formatting": {
                "page_size": "letter",
                "margins": {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                "fonts": {
                    "title_font": "Helvetica-Bold", "title_size": 16,
                    "body_font": "Helvetica", "body_size": 11,
                    "contact_font": "Helvetica", "contact_size": 10
                },
                "spacing": {
                    "title_space_after": 20, "paragraph_space_after": 12,
                    "line_height": 14, "contact_space_before": 20
                },
                "formatting": {
                    "show_title": True, "title_text": "Cover Letter",
                    "justify_text": False, "indent_paragraphs": False
                }
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return config.get('pdf_formatting', default_config['pdf_formatting'])
            else:
                print(f"   ℹ️  PDF config not found, using defaults")
                return default_config['pdf_formatting']
        except Exception as e:
            print(f"   ⚠️ Error loading PDF config: {e}, using defaults")
            return default_config['pdf_formatting']
    
    def _load_cover_letter_config(self):
        """Load cover letter configuration from config file."""
        config_path = os.path.join(os.path.dirname(__file__), 'AllMyStuff', 'cover_letter_config.json')
        default_config = {
            "template_config": {
                "structure": {
                    "quick_hits": {
                        "enabled": True,
                        "title": "Quick Hits",
                        "items": [
                            "Ensure engineering delivers business outcomes",
                            "7 startups (including 1 IPO and 3 acquisitions)", 
                            "Superpower: Exceptional combo of People, Engineering, & Business",
                            "Favorite Part: Seeing people reach their goals",
                            "Best Reference: Feel free to talk to my most recent CEO"
                        ]
                    },
                    "salutation": {"format": "Dear {{company_name}},"},
                    "signature": {
                        "closing": "thanks,",
                        "name": "DAVID TIJERINA",
                        "contact_info": [
                            "david.tijerina@gmail.com",
                            "https://www.linkedin.com/in/david-tijerina/"
                        ]
                    }
                }
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return config.get('template_config', default_config['template_config'])
            else:
                print(f"   ℹ️  Cover letter config not found, using defaults")
                return default_config['template_config']
        except Exception as e:
            print(f"   ⚠️ Error loading cover letter config: {e}")
            return default_config['template_config']

    def _parse_markdown_to_reportlab(self, text, body_style, bold_style):
        """Parse markdown to create a professional cover letter layout using configuration."""
        # Load cover letter configuration
        config = self._load_cover_letter_config()
        quick_hits_config = config['structure']['quick_hits']
        signature_config = config['structure']['signature']
        
        paragraphs = []
        lines = text.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Handle Quick Hits section using config
            if line == "**Quick Hits:**" and quick_hits_config['enabled']:
                # Add Quick Hits header with bold formatting
                quick_hits_style = ParagraphStyle(
                    'QuickHitsHeader',
                    parent=body_style,
                    fontName='Helvetica-Bold',
                    fontSize=14,
                    spaceAfter=12,
                    spaceBefore=0
                )
                paragraphs.append(Paragraph(quick_hits_config['title'], quick_hits_style))
                
                # Process bullet points from config instead of parsing text
                for bullet_item in quick_hits_config['items']:
                    bullet_style = ParagraphStyle(
                        'BulletPoint',
                        parent=body_style,
                        fontName='Helvetica',
                        fontSize=11,
                        leftIndent=24,  # Indent for bullet
                        bulletIndent=12,  # Bullet position
                        spaceAfter=4,
                        spaceBefore=2
                    )
                    paragraphs.append(Paragraph(f"• {bullet_item}", bullet_style))
                
                # Skip past the bullet points in the text
                i += 1
                while i < len(lines):
                    if lines[i].strip().startswith('* ') or lines[i].strip() == "":
                        i += 1
                    else:
                        break
                
                # Add space after Quick Hits section
                paragraphs.append(Spacer(1, 16))
                continue
            
            # Handle Dear [Company] greeting
            elif line.startswith("Dear "):
                greeting_style = ParagraphStyle(
                    'Greeting',
                    parent=body_style,
                    fontName='Helvetica',
                    fontSize=11,
                    spaceAfter=12,
                    spaceBefore=0
                )
                paragraphs.append(Paragraph(line, greeting_style))
            
            # Handle signature section using config
            elif line == "thanks,":
                # Add space before signature
                paragraphs.append(Spacer(1, 12))
                
                # Thanks line from config
                signature_style = ParagraphStyle(
                    'Signature',
                    parent=body_style,
                    fontName='Helvetica',
                    fontSize=11,
                    spaceAfter=12,
                    spaceBefore=0
                )
                paragraphs.append(Paragraph(signature_config['closing'], signature_style))
                
                # Add name from config
                name_style = ParagraphStyle(
                    'Name',
                    parent=body_style,
                    fontName='Helvetica',
                    fontSize=11,
                    spaceAfter=4,
                    spaceBefore=0
                )
                paragraphs.append(Paragraph(signature_config['name'], name_style))
                
                # Add contact info from config
                contact_style = ParagraphStyle(
                    'ContactInfo',
                    parent=body_style,
                    fontName='Helvetica',
                    fontSize=10,
                    spaceAfter=2,
                    spaceBefore=0
                )
                for contact_line in signature_config['contact_info']:
                    paragraphs.append(Paragraph(contact_line, contact_style))
                
                # Skip past signature lines in text since we're using config
                i += 1
                while i < len(lines):
                    sig_line = lines[i].strip()
                    if (sig_line and 
                        (sig_line == signature_config['name'] or 
                         any(contact in sig_line for contact in signature_config['contact_info']))):
                        i += 1
                    else:
                        break
                break
            
            # Handle regular paragraphs
            elif line and not line.startswith('*'):
                # Regular paragraph with proper spacing
                paragraph_style = ParagraphStyle(
                    'BodyParagraph',
                    parent=body_style,
                    fontName='Helvetica',
                    fontSize=11,
                    spaceAfter=12,
                    spaceBefore=0,
                    alignment=TA_LEFT,
                    leading=16  # Line height
                )
                paragraphs.append(Paragraph(line, paragraph_style))
            
            i += 1
        
        return paragraphs

    def _generate_cover_letter_pdf(self, cover_letter_text, output_filename):
        """Generate a professional PDF cover letter with configurable formatting."""
        try:
            # Load configuration
            config = self._load_pdf_config()
            
            # Set up page size and margins
            page_size = letter  # Default to letter, could be extended to support other sizes
            margins = config['margins']
            
            # Create PDF document with margins
            doc = SimpleDocTemplate(
                output_filename, 
                pagesize=page_size,
                topMargin=margins['top']*inch,
                bottomMargin=margins['bottom']*inch,
                leftMargin=margins['left']*inch,
                rightMargin=margins['right']*inch
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles from config
            fonts = config['fonts']
            spacing = config['spacing']
            formatting = config['formatting']
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=fonts['title_font'],
                fontSize=fonts['title_size'],
                spaceAfter=spacing['title_space_after'],
                alignment=TA_LEFT
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['Normal'],
                fontName=fonts['body_font'],
                fontSize=fonts['body_size'],
                leftIndent=0,  # Indent handled in markdown parsing
                rightIndent=0,
                spaceAfter=spacing['paragraph_space_after'],
                alignment=TA_LEFT,
                leading=spacing['line_height']
            )

            bold_style = ParagraphStyle(
                'CustomBold',
                parent=body_style,
                fontName=fonts.get('bold_font', 'Helvetica-Bold') # Use a bold font
            )
            
            contact_style = ParagraphStyle(
                'ContactInfo',
                parent=styles['Normal'],
                fontName=fonts['contact_font'],
                fontSize=fonts['contact_size'],
                spaceBefore=spacing['contact_space_before'],
                spaceAfter=6,
                alignment=TA_LEFT,
                leading=spacing['line_height']
            )
            
            # Build the PDF content
            story = []
            
            # Skip title to remove blank space at top - go directly to content
            # Parse markdown and add to story
            story.extend(self._parse_markdown_to_reportlab(cover_letter_text, body_style, bold_style))

            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"   ⚠️ PDF generation failed: {e}")
            return False
    
    def _llm_extract_resume_info(self, resume_text):
        """Use LLM to intelligently extract resume information."""
        system_prompt = """You are an expert resume parser. Extract key information from resumes and return it as JSON.
        Focus on identifying the candidate's name, contact information, and professional details."""
        
        user_prompt = f"""Please analyze this resume text and extract the following information as JSON:

RESUME TEXT:
{resume_text}

Return a JSON object with these fields:
- "name": Full name of the candidate
- "email": Email address  
- "phone": Phone number (if available)
- "location": Location/address (if available)
- "title": Current/target job title or professional summary
- "experience_summary": Brief summary of key experience and skills
- "years_experience": Estimated years of experience (number)
- "key_skills": Array of top 5-7 key technical/professional skills
- "education": Highest degree or relevant education
- "certifications": Any relevant certifications (array)

If information is not clearly available, use "Not specified" for text fields, 0 for years_experience, and empty arrays for lists."""
        
        result, success = self._call_llm(user_prompt, system_prompt, tier=2)
        
        if success and result:
            # Ensure we have the basic structure with fallbacks
            resume_info = {
                'name': result.get('name', 'Candidate'),
                'email': result.get('email', 'candidate@email.com'), 
                'phone': result.get('phone', 'Not specified'),
                'location': result.get('location', 'Not specified'),
                'title': result.get('title', 'Professional'),
                'experience_summary': result.get('experience_summary', ''),
                'years_experience': result.get('years_experience', 0),
                'key_skills': result.get('key_skills', []),
                'education': result.get('education', 'Not specified'),
                'certifications': result.get('certifications', []),
                'full_content': resume_text
            }
            print(f"   ✅ LLM extracted resume info for: {resume_info['name']}")
            return resume_info
        else:
            raise Exception("❌ LLM resume extraction failed. Please check your LLM connection and model availability.")
    
    def _fallback_resume_parse(self, resume_text):
        """This method is removed - LLM-only approach."""
        raise Exception("❌ Resume parsing requires LLM. Fallback methods have been removed.")

    def _llm_extract_job_info(self, url, page_title, page_content=None):
        """Use LLM to intelligently extract job information from URL, title, and content."""
        system_prompt = """You are an expert at extracting job information from URLs, page titles, and job descriptions.
        Extract key details and return them as structured JSON."""
        
        content_section = ""
        if page_content:
            # Limit content size for LLM processing
            content_preview = page_content[:2000] + "..." if len(page_content) > 2000 else page_content
            content_section = f"\nPAGE CONTENT:\n{content_preview}"
        
        user_prompt = f"""Please analyze this job posting information and extract details as JSON:

URL: {url}
PAGE TITLE: {page_title}{content_section}

Return a JSON object with these fields:
- "job_title": The specific job title/position name
- "company": Company name
- "location": Job location (city, state, remote, etc.)
- "employment_type": Full-time, Part-time, Contract, etc.
- "experience_level": Entry, Mid, Senior, Executive, etc.
- "department": Engineering, Marketing, Sales, etc.
- "salary_range": If mentioned (or "Not specified")
- "remote_options": Remote, Hybrid, On-site, or "Not specified"
- "key_requirements": Array of 3-5 main requirements/qualifications
- "key_responsibilities": Array of 3-5 main job responsibilities
- "required_skills": Array of technical/professional skills mentioned
- "company_description": Brief description of the company (if available)

Extract information from the URL pattern, page title, and content. Be intelligent about parsing different URL structures and job board formats."""
        
        result, success = self._call_llm(user_prompt, system_prompt, tier=2)
        
        if success and result:
            print(f"   ✅ LLM extracted job info: {result.get('job_title', 'Unknown')} at {result.get('company', 'Unknown')}")
            return result
        else:
            raise Exception("❌ LLM job extraction failed. Please check your LLM connection and model availability.")
    
    def _fallback_job_extraction(self, url, page_title):
        """This method is removed - LLM-only approach."""
        raise Exception("❌ Job extraction requires LLM. Fallback methods have been removed.")

    def _create_intelligent_folder_name(self, job_data):
        """Create an intelligent folder name using LLM insights."""
        company = job_data.get('company', 'Unknown_Company')
        job_title = job_data.get('job_title', 'Position')
        
        # Handle list/array data types
        if isinstance(company, list):
            company = company[0] if company else 'Unknown_Company'
        elif not isinstance(company, str):
            company = str(company) if company else 'Unknown_Company'
            
        if isinstance(job_title, list):
            job_title = job_title[0] if job_title else 'Position'
        elif not isinstance(job_title, str):
            job_title = str(job_title) if job_title else 'Position'
        
        # Clean company name for folder
        clean_company = re.sub(r'[^\w\s-]', '', company).strip()
        clean_company = re.sub(r'[-\s]+', '_', clean_company)
        
        # Clean job title for folder  
        clean_title = re.sub(r'[^\w\s-]', '', job_title).strip()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        
        # Limit length
        if len(clean_title) > 25:
            clean_title = clean_title[:25]
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        return f"{clean_company}_{clean_title}_{timestamp}"

def parse_resume(resume_path):
    """Parse the resume and extract key information using LLM."""
    try:
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        processor = LLMJobProcessor()
        return processor._llm_extract_resume_info(resume_text)
        
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        raise e

def extract_job_info_from_url_and_title(url, title, page_content=None):
    """Extract job information using LLM intelligence."""
    processor = LLMJobProcessor()
    return processor._llm_extract_job_info(url, title, page_content)

def save_cover_letter_to_file(cover_letter, company_name, job_data, resume_info=None):
    """Save the cover letter to a file with intelligent organization."""
    try:
        processor = LLMJobProcessor()
        folder_name = processor._create_intelligent_folder_name(job_data)
        
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"   📁 Created folder: {folder_name}")
        
        # Get applicant name from resume_info first, then fallback methods
        applicant_name = "Unknown"
        
        # Try to get name from resume_info first (most reliable)
        if resume_info and resume_info.get('name'):
            applicant_name = resume_info['name']
        else:
            # Fallback: try to get name from cover letter
            try:
                lines = cover_letter.split('\n')
                for line in lines[:10]:
                    line = line.strip()
                    if line and len(line.split()) >= 2 and len(line) < 50:
                        if not any(word in line.lower() for word in ['dear', 'hiring', 'manager', 'sincerely', 'regards', 'best', 'quick', 'hits']):
                            # Found a potential name, clean it up
                            potential_name = line.replace(',', '').strip()
                            if len(potential_name.split()) >= 2:  # At least first and last name
                                name_parts = potential_name.split()
                                if len(name_parts) >= 2:
                                    first_name = name_parts[0]
                                    last_name = name_parts[-1]  # Take the last word as last name
                                    applicant_name = f"{first_name}_{last_name}"
                                    break
            except:
                pass
        
        # If we still couldn't extract a name, use default
        if applicant_name == "Unknown":
            applicant_name = "David_Tijerina"  # Default based on your resume
        
        # Clean applicant name for filename (remove invalid characters)
        applicant_name = re.sub(r'[^\w\s-]', '', applicant_name).strip()
        applicant_name = re.sub(r'[-\s]+', '_', applicant_name)
        
        # Clean company name for filename
        company_for_filename = company_name
        if isinstance(company_name, list):
            company_for_filename = company_name[0] if company_name else "Unknown"
        elif not isinstance(company_name, str):
            company_for_filename = str(company_name) if company_name else "Unknown"
        
        clean_company = re.sub(r'[^\w\s-]', '', company_for_filename).strip()
        clean_company = re.sub(r'[-\s]+', '_', clean_company)
        
        # Save cover letter in both formats with new naming convention
        base_filename = f"{applicant_name}_{clean_company}_coverletter"
        
        # Save as text file first
        cover_letter_filename_txt = os.path.join(folder_name, f"{base_filename}.txt")
        with open(cover_letter_filename_txt, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        print(f"   ✅ Cover letter saved as text: {cover_letter_filename_txt}")
        
        # Save as PDF
        cover_letter_filename_pdf = os.path.join(folder_name, f"{base_filename}.pdf")
        if processor._generate_cover_letter_pdf(cover_letter, cover_letter_filename_pdf):
            print(f"   ✅ Cover letter saved as PDF: {cover_letter_filename_pdf}")
        else:
            print(f"   ⚠️ PDF generation failed, but text version is available")
        
        # Save comprehensive job information
        job_description_content = f"""=== JOB APPLICATION DETAILS ===
Generated on: {time.strftime('%B %d, %Y at %I:%M %p')}

=== BASIC INFORMATION ===
Job Title: {job_data.get('job_title', 'Unknown')}
Company: {job_data.get('company', 'Unknown')}
Location: {job_data.get('location', 'Unknown')}
Employment Type: {job_data.get('employment_type', 'Not specified')}
Experience Level: {job_data.get('experience_level', 'Not specified')}
Department: {job_data.get('department', 'Not specified')}
Salary Range: {job_data.get('salary_range', 'Not specified')}
Remote Options: {job_data.get('remote_options', 'Not specified')}

=== APPLICATION DETAILS ===
Application URL: {job_data.get('application_url', 'Unknown')}
Page Title: {job_data.get('page_title', 'Unknown')}

=== JOB REQUIREMENTS ==="""

        if job_data.get('key_requirements'):
            job_description_content += "\nKey Requirements:\n"
            for req in job_data.get('key_requirements', []):
                job_description_content += f"• {req}\n"
        
        if job_data.get('required_skills'):
            job_description_content += "\nRequired Skills:\n"
            for skill in job_data.get('required_skills', []):
                job_description_content += f"• {skill}\n"

        job_description_content += "\n=== JOB RESPONSIBILITIES ==="
        if job_data.get('key_responsibilities'):
            job_description_content += "\n"
            for resp in job_data.get('key_responsibilities', []):
                job_description_content += f"• {resp}\n"

        if job_data.get('company_description'):
            job_description_content += f"\n=== COMPANY INFORMATION ===\n{job_data.get('company_description')}"

        if job_data.get('description'):
            job_description_content += f"\n\n=== FULL JOB DESCRIPTION ===\n\n{job_data.get('description')}"
        else:
            job_description_content += f"""

=== FULL JOB DESCRIPTION ===

Note: Full job description could not be automatically extracted.
Please visit the URL above to get the complete job posting details.

To get the full job description:
1. Visit the application URL above
2. Close any chat overlays (look for X button)
3. Copy the complete job description
4. Paste it here to complete your application package"""
        
        job_desc_filename = os.path.join(folder_name, f"{clean_company}_JobDetails.txt")
        with open(job_desc_filename, 'w', encoding='utf-8') as f:
            f.write(job_description_content)
        print(f"   ✅ Job details saved: {job_desc_filename}")
        
        return folder_name
        
    except Exception as e:
        print(f"   ❌ Error saving files: {e}")
        return None

def generate_cover_letter(job_info, resume_info, cover_letter_instructions_path=None):
    """Generate a fully dynamic and personalized cover letter using LLM."""
    try:
        # Import the LLM cover letter generator
        from llm_cover_letter import generate_llm_cover_letter
        
        # Get the full resume text
        resume_text = resume_info.get('full_content', '')
        if not resume_text:
            raise Exception("❌ No resume text available for LLM generation")
        
        # Get instructions path from environment or parameter
        instructions_path = cover_letter_instructions_path or os.getenv('COVER_LETTER_INSTRUCTIONS_PATH', '')
        
        print("   🤖 Generating cover letter using LLM...")
        
        # Generate cover letter using LLM
        cover_letter, success = generate_llm_cover_letter(
            resume_text=resume_text,
            job_info=job_info,
            instructions_path=instructions_path
        )
        
        if success:
            print("   ✅ LLM cover letter generation successful")
            # Save cover letter to organized folder
            folder_name = save_cover_letter_to_file(cover_letter, job_info.get('company', 'Unknown'), job_info, resume_info)
            return cover_letter, folder_name
        else:
            raise Exception("❌ LLM cover letter generation failed. Please check your LLM connection and model availability.")
        
    except ImportError:
        raise Exception("❌ LLM cover letter module not available. Please ensure llm_cover_letter.py is present.")
    except Exception as e:
        print(f"   ❌ Error generating LLM cover letter: {e}")
        raise e

def generate_fallback_cover_letter(job_info, resume_info):
    """This function is removed - LLM-only approach."""
    raise Exception("❌ Cover letter generation requires LLM. Fallback methods have been removed.")

async def enhanced_job_processor(url, resume_path):
    """Enhanced job application processor using LLM intelligence throughout."""
    
    print("🚀 ENHANCED LLM-POWERED JOB APPLICATION PROCESSOR")
    print("="*65)
    print("Using AI intelligence for all extraction and generation tasks")
    print("="*65)
    
    try:
        from playwright.async_api import async_playwright
        
        # Step 1: Parse resume using LLM
        print("📄 Step 1: Parsing resume with LLM intelligence...")
        resume_info = parse_resume(resume_path)
        print(f"   ✅ Parsed resume for: {resume_info['name']} ({resume_info['email']})")
        if resume_info.get('key_skills'):
            print(f"   🎯 Key skills identified: {', '.join(resume_info['key_skills'][:5])}")
        
        # Step 2: Enhanced web scraping and extraction
        print("🌐 Step 2: Getting job page information with enhanced extraction...")
        
        job_description = None
        page_title = "Job Application"
        
        async with async_playwright() as p:
            # Get browser settings from environment
            headless = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
            timeout = int(os.getenv('BROWSER_TIMEOUT', '30000'))
            
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                page_title = await page.title()
                print(f"   📋 Page title: {page_title}")
                
                # Enhanced job description extraction
                print("   🔍 Attempting enhanced content extraction...")
                
                # Wait for content to load
                await page.wait_for_timeout(3000)
                
                # Try comprehensive content extraction
                extraction_strategies = [
                    # Specific job description selectors
                    '[data-testid="job-description"]',
                    '.job-description',
                    '[id*="job-description"]',
                    '[class*="job-description"]',
                    '[data-testid="jobDescription"]',
                    
                    # Content area selectors
                    '.content',
                    '[data-testid="content"]',
                    'main',
                    '.application-content',
                    '#content',
                    '.job-details',
                    '.position-details',
                    
                    # Greenhouse specific
                    '.application-question',
                    '.job-post',
                    '#main-content',
                    
                    # Generic content areas
                    'article',
                    '.job-posting',
                    '.posting-requirements'
                ]
                
                for selector in extraction_strategies:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.inner_text()
                            if text and len(text.strip()) > 150:  # Substantial content
                                job_description = text.strip()
                                print(f"   ✅ Found job description using: {selector}")
                                break
                    except:
                        continue
                
                # Enhanced fallback: intelligent body text filtering
                if not job_description:
                    try:
                        body_text = await page.evaluate('() => document.body.innerText')
                        if body_text and len(body_text.strip()) > 300:
                            # Use LLM to extract relevant job content from page
                            processor = LLMJobProcessor()
                            system_prompt = "Extract job description content from webpage text. Return only the relevant job posting content, filtering out navigation, ads, and footer content."
                            
                            user_prompt = f"Extract the job description and requirements from this webpage text:\n\n{body_text[:3000]}"
                            
                            result, success = processor._call_llm(user_prompt, system_prompt)
                            if success and result.get('content'):
                                job_description = result['content']
                                print(f"   ✅ LLM extracted job content from page body")
                            else:
                                print(f"   ⚠️ LLM content extraction failed - no job description available")
                    except Exception as e:
                        print(f"   ⚠️ Body text extraction failed: {e}")
                
            except Exception as e:
                print(f"   ⚠️ Could not load page: {e}")
            
            await browser.close()
        
        # Step 3: LLM-powered job information extraction
        print("🎯 Step 3: Extracting job information with LLM intelligence...")
        job_info = extract_job_info_from_url_and_title(url, page_title, job_description)
        
        print(f"   📊 Extracted comprehensive job details:")
        print(f"      Title: {job_info.get('job_title', 'Unknown')}")
        print(f"      Company: {job_info.get('company', 'Unknown')}")
        print(f"      Location: {job_info.get('location', 'Unknown')}")
        print(f"      Type: {job_info.get('employment_type', 'Not specified')}")
        print(f"      Level: {job_info.get('experience_level', 'Not specified')}")
        print(f"      Remote: {job_info.get('remote_options', 'Not specified')}")
        
        if job_info.get('required_skills'):
            print(f"      Skills: {', '.join(job_info.get('required_skills', [])[:5])}")
        
        # Step 4: Prepare comprehensive job data
        job_data = {
            **job_info,  # Include all LLM-extracted fields
            'application_url': url,
            'page_title': page_title,
            'description': job_description
        }
        
        # Step 5: Generate intelligent cover letter
        print("📝 Step 4: Generating intelligent cover letter...")
        cover_letter, folder_name = generate_cover_letter(job_data, resume_info)
        
        if folder_name:
            print(f"\n🎉 SUCCESS! Enhanced application package created!")
            print(f"   📁 Folder: {folder_name}")
            print(f"   📄 Files created:")
            print(f"      • Intelligent cover letter (Text + PDF formats)")
            print(f"      • Comprehensive job details (LLM-extracted)")
            
            if job_description:
                print(f"      • ✅ Job description successfully extracted")
            else:
                print(f"      • ⚠️  Job description placeholder (manual copy needed)")
            
            print(f"\n📖 Cover Letter Preview:")
            print("-" * 50)
            lines = cover_letter.split('\n')
            for line in lines[:15]:  # Show first 15 lines
                print(line)
            if len(lines) > 15:
                print("... (complete letter saved to file)")
            print("-" * 50)
            
            print(f"\n💡 Next Steps:")
            print(f"   1. ✅ Your intelligent cover letter is ready")
            print(f"   2. ✅ Comprehensive job analysis completed")
            if job_description:
                print(f"   3. ✅ Job requirements automatically extracted")
                print(f"   4. 🎯 Review the AI-generated content")
                print(f"   5. 📧 Submit your optimized application!")
            else:
                print(f"   3. 🌐 Visit the URL to copy any missing job details")
                print(f"   4. 🎯 Review the AI-generated content")
                print(f"   5. 📧 Submit your optimized application!")
            
        else:
            print("❌ Failed to create enhanced application package")
            
    except Exception as e:
        print(f"❌ Error in enhanced job processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    
    # Get configuration from environment variables
    default_url = os.getenv('DEFAULT_JOB_URL', 'https://example.com/job-posting')
    default_resume_path = os.getenv('RESUME_PATH', 'resume.txt')
    
    # Use command line arguments if provided, otherwise use environment defaults
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    resume_path = sys.argv[2] if len(sys.argv) > 2 else default_resume_path
    
    # Validate that required files exist
    if not os.path.exists(resume_path):
        print(f"❌ Error: Resume file not found at {resume_path}")
        print("   Please check your RESUME_PATH in the .env file")
        sys.exit(1)
    
    # Instructions path is now optional for LLM-based generation
    instructions_path = os.getenv('COVER_LETTER_INSTRUCTIONS_PATH')
    if instructions_path and not os.path.exists(instructions_path):
        print(f"⚠️  Warning: Cover letter instructions not found at {instructions_path}")
        print("   Proceeding with LLM-only generation")
    
    print(f"🎯 Processing job application with LLM intelligence:")
    print(f"   URL: {url}")
    print(f"   Resume: {resume_path}")
    if instructions_path and os.path.exists(instructions_path):
        print(f"   Instructions: {instructions_path}")
    print()
    
    asyncio.run(enhanced_job_processor(url, resume_path))
