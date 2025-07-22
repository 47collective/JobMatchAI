#!/usr/bin/env python3
"""
LLM-powered cover letter generation using Ollama local LLM
"""
import os
import re
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMCoverLetterGenerator:
    """Generates personalized cover letters using local Ollama LLM"""
    
    def __init__(self):
        """Initialize the LLM generator with Ollama configuration"""
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        self.temperature = float(os.getenv('OLLAMA_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('OLLAMA_MAX_TOKENS', '2000'))
        
        # Test Ollama connection
        self._test_ollama_connection()
    
    def _test_ollama_connection(self):
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                if self.model not in available_models:
                    print(f"   ⚠️ Model '{self.model}' not found. Available models: {available_models}")
                    if available_models:
                        self.model = available_models[0]
                        print(f"   🔄 Using {self.model} instead")
                print(f"   ✅ Ollama connected - using model: {self.model}")
            else:
                raise Exception(f"Ollama API returned status {response.status_code}")
        except Exception as e:
            raise ValueError(f"Cannot connect to Ollama at {self.ollama_host}. Make sure Ollama is running. Error: {e}")
    
    def generate_cover_letter(self, resume_text, job_info, instructions=""):
        """
        Generate a personalized cover letter using local Ollama LLM
        
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
            
            # Generate cover letter using Ollama
            response = self._call_ollama(prompt)
            
            if not response:
                raise Exception("Empty response from Ollama")
            
            # Post-process the cover letter
            cover_letter = self._post_process_cover_letter(response, candidate_info)
            
            return cover_letter
            
        except Exception as e:
            print(f"❌ Error generating cover letter with Ollama: {e}")
            raise
    
    def _call_ollama(self, prompt):
        """Make API call to Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=120  # Allow up to 2 minutes for generation
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out - the model may be too slow or the prompt too complex")
        except Exception as e:
            raise Exception(f"Failed to call Ollama API: {e}")
    
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
        
        # For Ollama, we need to combine system and user prompts
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
        
        # Ensure proper signature
        if not any(line.strip() == candidate_info['name'] for line in cover_letter.split('\n')):
            # Add signature if not present
            if not cover_letter.endswith('\n'):
                cover_letter += '\n'
            
            cover_letter += f"\nBest regards,\n\n{candidate_info['name']}"
            
            # Add contact info if available
            contact_lines = []
            if candidate_info['email'] != 'candidate@email.com':
                contact_lines.append(candidate_info['email'])
            if candidate_info['phone']:
                contact_lines.append(candidate_info['phone'])
            if candidate_info['linkedin']:
                contact_lines.append(candidate_info['linkedin'])
            
            if contact_lines:
                cover_letter += '\n' + '\n'.join(contact_lines)
        
        # Clean up any formatting issues
        cover_letter = re.sub(r'\n{3,}', '\n\n', cover_letter)  # Limit to double line breaks
        cover_letter = re.sub(r' +', ' ', cover_letter)  # Remove extra spaces
        
        return cover_letter.strip()

def generate_llm_cover_letter(resume_text, job_info, instructions_path=""):
    """
    Main function to generate LLM-powered cover letter using Ollama
    
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
        print(f"❌ Error in Ollama cover letter generation: {e}")
        raise

if __name__ == "__main__":
    # Test the Ollama cover letter generator
    print("🤖 Testing Ollama Cover Letter Generator")
    
    # Check if Ollama is configured
    try:
        generator = LLMCoverLetterGenerator()
        print("✅ Ollama Cover Letter Generator ready")
    except Exception as e:
        print(f"❌ Ollama setup error: {e}")
        print("💡 Make sure Ollama is installed and running:")
        print("   1. Install Ollama: https://ollama.ai/download")
        print("   2. Start Ollama: ollama serve")
        print("   3. Pull a model: ollama pull llama3.1")
