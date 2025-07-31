#!/usr/bin/env python3
"""
LLM-powered cover letter generation using dynamic Tier 1 LLM providers
"""
import os
import re
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)  # Force override existing environment variables

class LLMCoverLetterGenerator:
    """Generates personalized cover letters using dynamic Tier 1 LLM providers"""
    
    def __init__(self):
        """Initialize the LLM generator with dynamic tier configuration"""
        # Use Tier 1 for cover letter generation (high quality)
        self.tier1_provider = os.getenv('TIER1_LLM_PROVIDER')
        
        if not self.tier1_provider:
            raise ValueError("TIER1_LLM_PROVIDER must be set in .env file")
            
        self.tier1_provider = self.tier1_provider.lower()
        
        # Initialize Tier 1 configuration dynamically
        self._init_tier1_config()
        
        print(f"   🎯 Tier 1 LLM (Cover Letter Generation): {self.tier1_provider}")
    
    def _init_tier1_config(self):
        """Dynamically initialize Tier 1 LLM configuration based on .env file."""
        provider_upper = self.tier1_provider.upper()
        
        # Dynamic environment variable lookup
        base_url_key = f'{provider_upper}_BASE_URL'
        host_key = f'{provider_upper}_HOST'
        model_key = f'{provider_upper}_MODEL'
        api_key_key = f'{provider_upper}_API_KEY'
        
        # Check if this is an API-based service or local service
        api_key = os.getenv(api_key_key)
        base_url = os.getenv(base_url_key) or os.getenv(host_key)
        model = os.getenv(model_key)
        
        if api_key:
            # API-based service
            self.tier1_api_key = api_key
            self.tier1_model = model or f'{self.tier1_provider}-default'
            
            # Initialize API client dynamically
            if 'gemini' in self.tier1_provider.lower():
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    self.tier1_client = genai.GenerativeModel(model or 'gemini-1.5-flash')
                    print(f"   ✅ {self.tier1_provider.title()} connected - using model: {self.tier1_model}")
                except ImportError:
                    raise ValueError("google-generativeai package is required. Install with: pip install google-generativeai")
                except Exception as e:
                    raise ValueError(f"Failed to initialize {self.tier1_provider}: {e}")
            # Add other API providers here as needed
            
        elif base_url:
            # Local/self-hosted service
            self.tier1_base_url = base_url
            self.tier1_model = model
            self.temperature = float(os.getenv(f'{provider_upper}_TEMPERATURE', '0.7'))
            self.max_tokens = int(os.getenv(f'{provider_upper}_MAX_TOKENS', '2000'))
            
            if not model:
                raise ValueError(f"{model_key} must be set in .env file")
            
            # Test connection for local services
            self._test_local_connection()
            
        else:
            raise ValueError(f"No valid configuration found for {self.tier1_provider}. Need either {api_key_key} or {base_url_key}/{host_key} in .env file")
    
    def _test_local_connection(self):
        """Test connection to local LLM service"""
        try:
            response = requests.get(f"{self.tier1_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                if self.tier1_model not in available_models:
                    print(f"   ⚠️ Model '{self.tier1_model}' not found. Available models: {available_models}")
                    if available_models:
                        self.tier1_model = available_models[0]
                        print(f"   🔄 Using {self.tier1_model} instead")
                print(f"   ✅ {self.tier1_provider.title()} connected - using model: {self.tier1_model}")
            else:
                raise Exception(f"Local LLM API returned status {response.status_code}")
        except Exception as e:
            raise ValueError(f"Cannot connect to {self.tier1_provider} at {self.tier1_base_url}. Make sure service is running. Error: {e}")
    
    def generate_cover_letter(self, resume_text, job_info, instructions=""):
        """
        Generate a personalized cover letter using dynamic Tier 1 LLM
        
        Args:
            resume_text (str): The candidate's full resume text
            job_info (dict): Job information including title, company, description
            instructions (str): Optional custom instructions for the cover letter
            
        Returns:
            str: Generated cover letter
        """
        try:
            # Extract candidate information
            candidate_info = self._extract_candidate_info(resume_text)
            
            # Build the prompt
            prompt = self._build_cover_letter_prompt(
                candidate_info, 
                resume_text, 
                job_info, 
                instructions
            )
            
            # Generate cover letter using dynamic LLM
            response = self._call_tier1_llm(prompt)
            
            if not response:
                raise Exception("Empty response from LLM")
            
            # Post-process the cover letter
            cover_letter = self._post_process_cover_letter(response, candidate_info)
            
            return cover_letter
            
        except Exception as e:
            print(f"❌ Error generating cover letter with {self.tier1_provider}: {e}")
            raise
    
    def _call_tier1_llm(self, prompt):
        """Dynamically call Tier 1 LLM based on configuration"""
        try:
            # Check if this is an API-based service or local service
            if hasattr(self, 'tier1_api_key'):
                # API-based service
                return self._call_api_service(prompt)
            elif hasattr(self, 'tier1_base_url'):
                # Local service
                return self._call_local_service(prompt)
            else:
                raise ValueError(f"No valid configuration found for Tier 1 ({self.tier1_provider})")
                
        except Exception as e:
            print(f"   ⚠️ Tier 1 LLM ({self.tier1_provider}) call failed: {e}")
            raise
    
    def _call_api_service(self, prompt):
        """Call an API-based LLM service"""
        if hasattr(self, 'tier1_client') and hasattr(self.tier1_client, 'generate_content'):
            # This looks like a Google Generative AI client
            try:
                response = self.tier1_client.generate_content(prompt)
                
                if response.text:
                    return response.text.strip()
                else:
                    raise Exception("API returned empty response")
                    
            except Exception as e:
                raise Exception(f"Failed to call API service: {e}")
        else:
            raise Exception(f"Unsupported API client for {self.tier1_provider}")
    
    def _call_local_service(self, prompt):
        """Call a local LLM service"""
        try:
            payload = {
                "model": self.tier1_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.tier1_base_url}/api/generate",
                json=payload,
                timeout=120  # Allow up to 2 minutes for generation
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                raise Exception(f"Local LLM API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("Local LLM request timed out - the model may be too slow or the prompt too complex")
        except Exception as e:
            raise Exception(f"Failed to call local LLM API: {e}")
    
    def _extract_candidate_info(self, resume_text):
        """Extract key candidate information from resume"""
        candidate_info = {
            'name': 'Candidate',
            'email': 'candidate@email.com',
            'phone': '',
            'linkedin': '',
            'years_experience': 0,
            'current_title': '',
            'key_skills': [],
            'top_achievements': []
        }
        
        # Extract name (usually first substantial line)
        lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
        for line in lines[:5]:
            words = line.split()
            if (2 <= len(words) <= 3 and 
                not any(keyword in line.lower() for keyword in ['phone', 'email', '@', 'linkedin', 'experience'])):
                candidate_info['name'] = line
                break
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        if email_match:
            candidate_info['email'] = email_match.group()
        
        # Extract phone
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text)
        if phone_match:
            candidate_info['phone'] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_match = re.search(r'(https?://(?:www\.)?linkedin\.com/in/[^\s]+)', resume_text, re.IGNORECASE)
        if linkedin_match:
            candidate_info['linkedin'] = linkedin_match.group(1)
        
        # Extract years of experience
        years_matches = re.findall(r'(\d+)[+]?\s*years?', resume_text, re.IGNORECASE)
        if years_matches:
            candidate_info['years_experience'] = max([int(y) for y in years_matches])
        
        # Extract current/most recent title
        title_patterns = [
            r'(?:VP|Vice President|Director|Senior|Lead|Principal|Chief)\s+[A-Za-z\s]+',
            r'(?:Software|Engineering|Technology|Product)\s+(?:Manager|Director|Lead|Engineer)'
        ]
        for pattern in title_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                candidate_info['current_title'] = match.group().strip()
                break
        
        return candidate_info
    
    def _get_system_prompt(self):
        """Get the system prompt for the LLM - now integrated into the main prompt"""
        return """You are an expert career coach and professional writer specializing in creating compelling, personalized cover letters for technology executives and senior professionals.

Your task is to analyze a candidate's resume and a specific job posting to create a highly tailored, engaging cover letter that:

1. DEMONSTRATES CLEAR VALUE MATCH: Shows exactly how the candidate's experience aligns with the job requirements
2. TELLS A COMPELLING STORY: Weaves together the candidate's background into a narrative that leads naturally to this role
3. SHOWS DEEP RESEARCH: References specific aspects of the company and role that show genuine interest
4. QUANTIFIES IMPACT: Includes specific achievements and metrics where available
5. MAINTAINS PROFESSIONAL TONE: Confident but not arrogant, enthusiastic but not desperate

STRUCTURE REQUIREMENTS:
- Professional business letter format
- Engaging opening that hooks the reader
- 2-3 body paragraphs that build a compelling case
- Strong closing that invites action
- Professional signature block

TONE REQUIREMENTS:
- Confident and professional
- Specific and achievement-focused  
- Enthusiastic about the opportunity
- Authentic and human (not robotic)

AVOID:
- Generic template language
- Clichés and overused phrases
- Repeating the entire resume
- Desperate or begging tone
- Overly long sentences or paragraphs"""
    
    def _build_cover_letter_prompt(self, candidate_info, resume_text, job_info, instructions):
        """Build the prompt for cover letter generation"""
        
        job_title = job_info.get('job_title', 'the position')
        company = job_info.get('company', 'the company')
        job_description = job_info.get('description', '')
        
        # For local services, combine system and user prompts
        system_prompt = self._get_system_prompt()
        
        prompt = f"""{system_prompt}

**CANDIDATE INFORMATION:**
Name: {candidate_info['name']}
Email: {candidate_info['email']}
Current/Recent Title: {candidate_info.get('current_title', 'Senior Professional')}
Years of Experience: {candidate_info['years_experience']}+ years

**JOB DETAILS:**
Position: {job_title}
Company: {company}
Location: {job_info.get('location', 'Various')}

**JOB DESCRIPTION:**
{job_description if job_description else 'Job description not available - please create a cover letter based on the position title and company.'}

**CANDIDATE'S FULL RESUME:**
{resume_text}

**ADDITIONAL INSTRUCTIONS:**
{instructions if instructions else 'No additional instructions provided.'}

**YOUR TASK:**
Create a personalized, compelling cover letter that:
1. Opens with an engaging hook that immediately shows value alignment
2. Demonstrates specific understanding of the role and company
3. Tells the story of why this candidate is uniquely qualified
4. Includes specific achievements and quantifiable results from their background
5. Shows genuine enthusiasm for the opportunity
6. Ends with a confident call to action

The cover letter should be approximately 300-400 words and feel authentic and human, not like a generic template. Make it feel like it was written specifically for this role at this company.

Please write the complete cover letter now:"""

        return prompt
    
    def _post_process_cover_letter(self, cover_letter, candidate_info):
        """Post-process the generated cover letter"""
        
        # Remove LLM's introductory text (everything before Quick Hits or Dear)
        lines = cover_letter.split('\n')
        start_idx = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Look for the start of actual cover letter content
            if (line_stripped.startswith('**Quick Hits:**') or 
                line_stripped.startswith('Quick Hits:') or
                line_stripped.startswith('* Ensure engineering') or
                line_stripped.startswith('Dear ') or
                line_stripped.startswith('To the Hiring')):
                start_idx = i
                break
        
        # Keep only the cover letter content
        cover_letter = '\n'.join(lines[start_idx:])
        
        # Fix Quick Hits formatting - ensure proper bold formatting and line breaks
        if '**Quick Hits:**' in cover_letter:
            # Find and replace the Quick Hits section
            quick_hits_pattern = r'[\*\s]*\*\*Quick Hits:\*\*.*?(?=\n\n[A-Z]|Dear|To the|With over)'
            match = re.search(quick_hits_pattern, cover_letter, re.DOTALL)
            if match:
                quick_hits_text = match.group(0)
                # Extract bullet points
                bullets = re.findall(r'\* ([^*]+?)(?=\*|$)', quick_hits_text, re.DOTALL)
                if bullets:
                    # Rebuild with proper formatting
                    formatted_quick_hits = "**Quick Hits:**\n\n"
                    for bullet in bullets:
                        formatted_quick_hits += f"* {bullet.strip()}\n"
                    formatted_quick_hits += "\n"
                    
                    # Replace in cover letter
                    cover_letter = cover_letter.replace(quick_hits_text, formatted_quick_hits)
        
        # Remove duplicate signatures and contact info
        # Find all signatures (thanks, Best regards, Sincerely, etc.)
        signature_patterns = [
            r'\nthanks,\s*\n+.*?(?=\n\n|\Z)',
            r'\nBest regards,\s*\n+.*?(?=\n\n|\Z)',
            r'\nSincerely,\s*\n+.*?(?=\n\n|\Z)',
        ]
        
        # Remove all existing signatures
        for pattern in signature_patterns:
            cover_letter = re.sub(pattern, '', cover_letter, flags=re.DOTALL | re.IGNORECASE)
        
        # Add single, clean signature at the end
        cover_letter = cover_letter.strip()
        cover_letter += f"\n\nthanks,\n\n{candidate_info['name']}"
        
        # Add contact info once
        contact_lines = []
        if candidate_info['email'] and candidate_info['email'] != 'candidate@email.com':
            contact_lines.append(candidate_info['email'])
        if candidate_info.get('linkedin'):
            contact_lines.append(candidate_info['linkedin'])
        
        if contact_lines:
            cover_letter += '\n' + '\n'.join(contact_lines)
        
        # Clean up formatting issues
        cover_letter = re.sub(r'\n{3,}', '\n\n', cover_letter)  # Limit to double line breaks
        cover_letter = re.sub(r' +', ' ', cover_letter)  # Remove extra spaces
        
        return cover_letter.strip()

def generate_llm_cover_letter(resume_text, job_info, instructions_path=""):
    """
    Main function to generate LLM-powered cover letter using dynamic Tier 1 LLM
    
    Args:
        resume_text (str): Full resume text
        job_info (dict): Job information
        instructions_path (str): Path to instructions file (optional)
        
    Returns:
        tuple: (cover_letter_text, success_flag)
    """
    try:
        # Load additional instructions if provided
        instructions = ""
        if instructions_path and os.path.exists(instructions_path):
            with open(instructions_path, 'r', encoding='utf-8') as f:
                instructions = f.read()
        
        # Initialize the LLM generator
        generator = LLMCoverLetterGenerator()
        
        # Generate the cover letter
        cover_letter = generator.generate_cover_letter(
            resume_text=resume_text,
            job_info=job_info,
            instructions=instructions
        )
        
        return cover_letter, True
        
    except Exception as e:
        print(f"❌ Error in LLM cover letter generation: {e}")
        raise

if __name__ == "__main__":
    # Test the dynamic LLM cover letter generator
    print("🤖 Testing Dynamic LLM Cover Letter Generator")
    
    # Check if LLM is configured
    try:
        generator = LLMCoverLetterGenerator()
        print("✅ Dynamic LLM Cover Letter Generator ready")
    except Exception as e:
        print(f"❌ LLM setup error: {e}")
        print("💡 Make sure your LLM provider is configured in .env file:")
        print("   - For local services: Set TIER1_LLM_PROVIDER, {PROVIDER}_BASE_URL, {PROVIDER}_MODEL")
        print("   - For API services: Set TIER1_LLM_PROVIDER, {PROVIDER}_API_KEY, {PROVIDER}_MODEL")
