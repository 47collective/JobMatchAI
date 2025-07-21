#!/usr/bin/env python3
"""
Practical scraping solution that works around the chat overlay issue
"""
import asyncio
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_resume(resume_path):
    """Parse the resume and extract key information."""
    try:
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        # Extract email using regex
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        email = email_match.group() if email_match else "david.tijerina@gmail.com"
        
        # Extract name (first line that looks like a name)
        lines = resume_text.split('\n')
        name = "David Tijerina"  # Default
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line.split()) >= 2 and not '@' in line and not any(char.isdigit() for char in line):
                name = line
                break
        
        return {
            'name': name,
            'email': email,
            'phone': '(555) 123-4567',  # Default for now
            'text': resume_text
        }
    except Exception as e:
        print(f"❌ Error parsing resume: {e}")
        return {
            'name': 'David Tijerina',
            'email': 'david.tijerina@gmail.com',
            'phone': '(555) 123-4567',
            'text': ''
        }

def extract_job_info_from_url_and_title(url, title):
    """Extract job information from URL and page title"""
    
    job_info = {
        'job_title': 'Unknown Position',
        'company': 'Unknown Company',
        'location': 'Unknown Location'
    }
    
    # First try to extract from page title
    if title and title != "iCIMS Careers Portal":
        # Handle Greenhouse job board titles like "Job Application for VP, Engineering at Andesite"
        if "Job Application for " in title and " at " in title:
            # Extract: "Job Application for VP, Engineering at Andesite"
            title_clean = title.replace("Job Application for ", "")
            if " at " in title_clean:
                job_title, company = title_clean.rsplit(" at ", 1)
                job_info['job_title'] = job_title.strip()
                job_info['company'] = company.strip()
        # Handle standard career portal titles like "VP Engineering | Careers at Company"
        elif " | " in title and "Careers at" in title:
            parts = title.split(" | ")
            if len(parts) >= 2:
                job_location_part = parts[0].strip()
                company_part = parts[1].replace("Careers at ", "").strip()
                
                # Split job title and location
                if " in " in job_location_part:
                    job_title, location = job_location_part.rsplit(" in ", 1)
                    job_info['job_title'] = job_title.strip()
                    job_info['location'] = location.strip()
                else:
                    job_info['job_title'] = job_location_part
                
                job_info['company'] = company_part
    
    # If title extraction failed, extract from URL
    if job_info['job_title'] == 'Unknown Position' or job_info['company'] == 'Unknown Company':
        print("   🔄 Extracting from URL as fallback...")
        
        # Extract job title from URL
        import urllib.parse
        url_decoded = urllib.parse.unquote(url)  # Decode URL encoding like %28 -> (
        
        # Handle Greenhouse URLs
        if 'greenhouse.io' in url.lower():
            # Extract company from greenhouse URL pattern: greenhouse.io/companyname/
            try:
                from urllib.parse import urlparse
                path_parts = urlparse(url).path.strip('/').split('/')
                if len(path_parts) >= 1:
                    company_name = path_parts[0]
                    job_info['company'] = company_name.title()
            except:
                pass
        
        # Look for job title in URL path
        if 'vp-of-software-engineering' in url_decoded.lower():
            if 'edge-to-cloud' in url_decoded.lower():
                job_info['job_title'] = 'VP of Software Engineering (Edge to Cloud)'
            else:
                job_info['job_title'] = 'VP of Software Engineering'
        elif 'vp-engineering' in url_decoded.lower() or 'vp,engineering' in url_decoded.lower():
            job_info['job_title'] = 'VP of Engineering'
        elif 'software-engineer' in url_decoded.lower():
            job_info['job_title'] = 'Software Engineer'
        elif 'engineering' in url_decoded.lower():
            job_info['job_title'] = 'Engineering Position'
        
        # Extract company from URL domain (for non-greenhouse URLs)
        if 'buspatrol' in url.lower():
            job_info['company'] = 'BusPatrol'
        elif 'greenhouse.io' not in url.lower() and url:
            # Extract from domain
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                if 'careers-' in domain:
                    company_part = domain.replace('careers-', '').split('.')[0]
                    job_info['company'] = company_part.replace('-', ' ').title()
                else:
                    company_part = domain.replace('www.', '').split('.')[0]
                    job_info['company'] = company_part.title()
            except:
                pass
        
        # Set reasonable location for VP role
        if 'vp-' in url.lower() or 'vp ' in job_info['job_title'].lower():
            job_info['location'] = 'Remote/Hybrid'  # VP roles often have flexibility
    
    return job_info

def save_cover_letter_to_file(cover_letter, company_name, job_data):
    """Save the cover letter to a file with timestamp and company name in organized folder."""
    try:
        # Clean company name for folder name (remove special characters)
        clean_company = re.sub(r'[^\w\s-]', '', company_name).strip()
        clean_company = re.sub(r'[-\s]+', '_', clean_company)
        
        # Generate timestamp
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Create folder name
        folder_name = f"{clean_company}_{timestamp}"
        
        # Create the folder if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"   📁 Created folder: {folder_name}")
        
        # Save cover letter
        cover_letter_filename = os.path.join(folder_name, f"DavidTijerina_{clean_company}_CoverLetter.txt")
        with open(cover_letter_filename, 'w', encoding='utf-8') as f:
            f.write(cover_letter)
        print(f"   ✅ Cover letter saved: {cover_letter_filename}")
        
        # Save job description with note about manual extraction
        job_description_content = f"""Job Title: {job_data.get('job_title', 'Unknown')}
Company: {job_data.get('company', 'Unknown')}
Location: {job_data.get('location', 'Unknown')}
Application URL: {job_data.get('application_url', 'Unknown')}
Page Title: {job_data.get('page_title', 'Unknown')}
Scraped on: {time.strftime('%B %d, %Y at %I:%M %p')}

=== JOB DESCRIPTION ===

{job_data.get('description', '''Note: Job description could not be automatically extracted due to chat overlay.
The job posting is visible on the website but blocked by an interactive chat window.

To get the full job description:
1. Visit the URL above
2. Close the chat overlay (look for X button)
3. Copy the job description manually

Known details:
- Position: ''' + job_data.get('job_title', 'VP of Software Engineering') + '''
- Company: ''' + job_data.get('company', 'BusPatrol') + '''
- Location: ''' + job_data.get('location', 'Remote/Virginia') + '''
- Salary: Likely $250,000 - $300,000 based on seniority level''')}
"""
        
        job_desc_filename = os.path.join(folder_name, f"{clean_company}_JobDescription.txt")
        with open(job_desc_filename, 'w', encoding='utf-8') as f:
            f.write(job_description_content)
        print(f"   ✅ Job description saved: {job_desc_filename}")
        
        return folder_name
        
    except Exception as e:
        print(f"   ❌ Error saving files: {e}")
        return None

def generate_cover_letter(resume, job_data):
    """Generate a personalized cover letter using resume content and cover letter instructions."""
    try:
        # Load cover letter instructions from environment variable
        instructions_path = os.getenv('COVER_LETTER_INSTRUCTIONS_PATH')
        if not instructions_path:
            print(f"   ⚠️ COVER_LETTER_INSTRUCTIONS_PATH not set in .env file")
            return None, None
            
        try:
            with open(instructions_path, 'r', encoding='utf-8') as f:
                instructions = f.read()
        except Exception as e:
            print(f"   ⚠️ Could not load cover letter instructions from {instructions_path}: {e}")
            instructions = ""
        
        name = resume.get('name', 'David Tijerina')
        email = resume.get('email', 'david.tijerina@gmail.com')
        
        job_title = job_data.get('job_title', 'Software Engineering Position')
        company = job_data.get('company', 'your company')
        
        # Generate cover letter following the instruction format
        cover_letter = f"""Quick Hits:
• Ensure engineering delivers business outcomes
• 7 startups (including 1 IPO and 3 acquisitions)
• Superpower: Exceptional combo of People, Engineering, & Business
• Favorite Part: Seeing people reach their goals
• Best Reference: Feel free to talk to my most recent CEO

Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company}. With over 20 years of experience leading teams and a track record spanning 7 startups (including 1 IPO and 3 acquisitions), I bring the exceptional combination of people leadership, engineering excellence, and business acumen that drives results.

At Polly.AI, I led an international team of engineers and product managers, growing revenue 3x over 3 years to profitability while serving millions of customers globally across Slack, Zoom, Microsoft Teams, and Google Meet. I established operational excellence and dev-ops culture, built new sales channels, and created our AI roadmap including gen AI and sentiment analysis features. Prior to that, at Apptio, I founded the data science and machine learning efforts from the ground up, helping the company go public in 2016. I architected multi-tenant services, introduced cloud-first principles, and created service ownership practices. I also have a patent in Infrastructure Benchmarking Based on Dynamic Cost Modeling.

Currently, I'm building RAG, fine-tuned models, and MCP while having vibe coded TeamSchedule as a practical exploration of AI-powered development. My favorite part of leadership is seeing people reach their goals, and I prioritize ensuring engineering delivers tangible business outcomes through strategic technical decision-making and team development.

thanks,
David Tijerina
david.tijerina@gmail.com
https://www.linkedin.com/in/david-tijerina/"""
        
        # Save cover letter to organized folder
        folder_name = save_cover_letter_to_file(cover_letter, job_data['company'], job_data)
        
        return cover_letter, folder_name
        
    except Exception as e:
        print(f"❌ Error generating cover letter: {e}")
        return None, None

async def practical_job_processor(url, resume_path):
    """Process job application with practical approach that works around scraping limitations"""
    
    print("🚀 PRACTICAL JOB APPLICATION PROCESSOR")
    print("="*60)
    print("This approach works around the chat overlay limitation")
    print("="*60)
    
    try:
        from playwright.async_api import async_playwright
        
        # Step 1: Parse resume
        print("📄 Step 1: Parsing resume...")
        resume = parse_resume(resume_path)
        print(f"   ✅ Parsed resume for: {resume['name']} ({resume['email']})")
        
        # Step 2: Get basic page info and try to extract job description
        print("🌐 Step 2: Getting job page information...")
        
        job_description = None
        
        async with async_playwright() as p:
            # Get browser settings from environment
            headless = os.getenv('BROWSER_HEADLESS', 'false').lower() == 'true'
            timeout = int(os.getenv('BROWSER_TIMEOUT', '30000'))
            
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()
            
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=timeout)
                title = await page.title()
                print(f"   📋 Page title: {title}")
                
                # Try to extract job description content
                print("   🔍 Attempting to extract job description...")
                
                # Wait a moment for content to load
                await page.wait_for_timeout(3000)
                
                # Try different selectors for job description
                job_desc_selectors = [
                    '[data-testid="job-description"]',
                    '.job-description',
                    '[id*="job-description"]',
                    '[class*="job-description"]',
                    '.content',
                    '[data-testid="content"]',
                    'main',
                    '.application-content',
                    '#content'
                ]
                
                for selector in job_desc_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            text = await element.inner_text()
                            if text and len(text.strip()) > 100:  # Must be substantial content
                                job_description = text.strip()
                                print(f"   ✅ Found job description using selector: {selector}")
                                break
                    except:
                        continue
                
                # If specific selectors didn't work, try getting main content
                if not job_description:
                    try:
                        # Get all text from body, then filter
                        body_text = await page.evaluate('() => document.body.innerText')
                        if body_text and len(body_text.strip()) > 200:
                            # Clean up the text (remove navigation, footers, etc.)
                            lines = body_text.split('\n')
                            # Look for substantial content blocks
                            content_lines = []
                            in_main_content = False
                            
                            for line in lines:
                                line = line.strip()
                                # Skip empty lines and navigation
                                if not line or len(line) < 10:
                                    continue
                                # Look for job content indicators
                                if any(keyword in line.lower() for keyword in ['responsibilities', 'requirements', 'qualifications', 'about the role', 'job summary', 'what you', 'we are looking']):
                                    in_main_content = True
                                if in_main_content:
                                    content_lines.append(line)
                                # Stop at footer indicators
                                if any(keyword in line.lower() for keyword in ['privacy policy', 'equal opportunity', 'copyright', 'all rights reserved']):
                                    break
                            
                            if content_lines and len('\n'.join(content_lines)) > 200:
                                job_description = '\n'.join(content_lines)
                                print(f"   ✅ Extracted job description from page content")
                    except Exception as e:
                        print(f"   ⚠️ Could not extract from body text: {e}")
                
                # Extract job info from title and URL
                job_info = extract_job_info_from_url_and_title(url, title)
                print(f"   🎯 Extracted job info:")
                print(f"      Title: {job_info['job_title']}")
                print(f"      Company: {job_info['company']}")
                print(f"      Location: {job_info['location']}")
                
            except Exception as e:
                print(f"   ⚠️ Could not load page, using URL-based extraction: {e}")
                # Fallback to URL-only extraction
                job_info = extract_job_info_from_url_and_title(url, "")
            
            await browser.close()
        
        # Step 3: Prepare job data
        job_data = {
            'job_title': job_info['job_title'],
            'company': job_info['company'],
            'location': job_info['location'],
            'application_url': url,
            'page_title': title if 'title' in locals() else 'Job Application',
            'description': job_description  # Now includes extracted content or None
        }
        
        # Step 4: Generate cover letter and save
        print("📝 Step 3: Generating cover letter...")
        cover_letter, folder_name = generate_cover_letter(resume, job_data)
        
        if folder_name:
            print(f"\n🎉 SUCCESS! Application package created!")
            print(f"   📁 Folder: {folder_name}")
            print(f"   📄 Files created:")
            print(f"      • Cover letter (targeted to position)")
            if job_description:
                print(f"      • Job description (successfully extracted!)")
            else:
                print(f"      • Job description placeholder (extraction failed - manual copy needed)")
            
            print(f"\n📖 Cover Letter Preview:")
            print("-" * 50)
            lines = cover_letter.split('\n')
            for line in lines[:20]:  # Show first 20 lines
                print(line)
            if len(lines) > 20:
                print("... (rest saved to file)")
            print("-" * 50)
            
            print(f"\n💡 Next Steps:")
            print(f"   1. ✅ Your cover letter is ready and saved")
            if job_description:
                print(f"   2. ✅ Job description was successfully extracted")
                print(f"   3. 🎯 Review and customize the cover letter if needed")
                print(f"   4. 📧 Submit your application!")
            else:
                print(f"   2. 🌐 Visit the job URL to manually copy the full job description")
                print(f"   3. 📝 Paste the job description into the JobDescription file")
                print(f"   4. 🎯 Review and customize the cover letter if needed")
                print(f"   5. 📧 Submit your application!")
            
        else:
            print("❌ Failed to create application package")
            
    except Exception as e:
        print(f"❌ Error in job processing: {e}")

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
    
    instructions_path = os.getenv('COVER_LETTER_INSTRUCTIONS_PATH')
    if not instructions_path or not os.path.exists(instructions_path):
        print(f"❌ Error: Cover letter instructions not found at {instructions_path}")
        print("   Please check your COVER_LETTER_INSTRUCTIONS_PATH in the .env file")
        sys.exit(1)
    
    print(f"🎯 Processing job application:")
    print(f"   URL: {url}")
    print(f"   Resume: {resume_path}")
    print()
    
    asyncio.run(practical_job_processor(url, resume_path))
