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

# Load environment variables from .env file
load_dotenv()

class LLMJobProcessor:
    """Enhanced job processor using LLM for all extraction and generation tasks."""
    
    def __init__(self):
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
        
    def _call_ollama(self, prompt, system_prompt=None):
        """Call the local Ollama LLM API."""
        try:
            import requests
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.ollama_model,
                "messages": messages,
                "stream": False,
                "format": "json"
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/chat",
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
                print(f"   ⚠️ Ollama API error: {response.status_code}")
                return None, False
                
        except Exception as e:
            print(f"   ⚠️ LLM call failed: {e}")
            return None, False
    
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
        
        result, success = self._call_ollama(user_prompt, system_prompt)
        
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
            raise Exception("❌ LLM resume extraction failed. Please check your Ollama connection and model availability.")
    
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
        
        result, success = self._call_ollama(user_prompt, system_prompt)
        
        if success and result:
            print(f"   ✅ LLM extracted job info: {result.get('job_title', 'Unknown')} at {result.get('company', 'Unknown')}")
            return result
        else:
            raise Exception("❌ LLM job extraction failed. Please check your Ollama connection and model availability.")
    
    def _fallback_job_extraction(self, url, page_title):
        """This method is removed - LLM-only approach."""
        raise Exception("❌ Job extraction requires LLM. Fallback methods have been removed.")

    def _create_intelligent_folder_name(self, job_data):
        """Create an intelligent folder name using LLM insights."""
        company = job_data.get('company', 'Unknown_Company')
        job_title = job_data.get('job_title', 'Position')
        
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

def save_cover_letter_to_file(cover_letter, company_name, job_data):
    """Save the cover letter to a file with intelligent organization."""
    try:
        processor = LLMJobProcessor()
        folder_name = processor._create_intelligent_folder_name(job_data)
        
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"   📁 Created folder: {folder_name}")
        
        # Get applicant name from cover letter using LLM
        applicant_name = "Applicant"
        try:
            lines = cover_letter.split('\n')
            for line in lines[:10]:
                line = line.strip()
                if line and len(line.split()) >= 2 and len(line) < 50:
                    if not any(word in line.lower() for word in ['dear', 'hiring', 'manager', 'sincerely', 'regards', 'best']):
                        applicant_name = line.replace(' ', '').replace(',', '')
                        break
        except:
            pass
        
        # Clean company name for filename
        clean_company = re.sub(r'[^\w\s-]', '', company_name).strip()
        clean_company = re.sub(r'[-\s]+', '_', clean_company)
        
        # Save cover letter
        cover_letter_filename = os.path.join(folder_name, f"{applicant_name}_{clean_company}_CoverLetter.txt")
        with open(cover_letter_filename, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        print(f"   ✅ Cover letter saved: {cover_letter_filename}")
        
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
            folder_name = save_cover_letter_to_file(cover_letter, job_info.get('company', 'Unknown'), job_info)
            return cover_letter, folder_name
        else:
            raise Exception("❌ LLM cover letter generation failed. Please check your Ollama connection and model availability.")
        
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
                            
                            result, success = processor._call_ollama(user_prompt, system_prompt)
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
            print(f"      • Intelligent cover letter (LLM-generated)")
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
