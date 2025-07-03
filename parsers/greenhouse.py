import requests
from bs4 import BeautifulSoup
import logging
import json
from datetime import datetime
import re
import os

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
URL = "https://job-boards.greenhouse.io/reddit/jobs/6706371"

def fetch_job_data(url: str) -> str | None:
    """
    Fetches the HTML content from the given URL.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logging.info(f"Successfully fetched content from {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return None

def parse_job_to_json(html_content: str | None, url: str) -> dict:
    """
    Parses job posting HTML into a structured dictionary.

    Attempts a detailed parse for specific fields. If it fails to find key
    sections, it saves the bulk text to a 'text_content' field as a fallback.
    """
    if not html_content:
        logging.error("No HTML content provided to parse.")
        return {}

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # --- Initialize the data structure ---
    job_data = {
        "source_url": url,
        "date_accessed": datetime.now().isoformat(),
        "job_title": None,
        "company": None,
        "job_description": None,
        "job_requirements": None,
        "remote_location_requirement": None,
        "benefits": None,
        "pay_range": None,
        "text_content": None
    }

    # --- Basic Information Extraction ---
    try:
        # Extract company from the main page title for reliability
        page_title = soup.find('title').get_text()
        if ' at ' in page_title:
            job_data['company'] = page_title.split(' at ')[-1].strip()

        job_header = soup.find('div', class_='job__header')
        if job_header:
            job_data['job_title'] = job_header.find('h1', class_='section-header--large').get_text(strip=True)
            job_data['remote_location_requirement'] = job_header.find('div', class_='job__location').get_text(strip=True)
    except Exception as e:
        logging.warning(f"Could not parse basic header info: {e}")

    # --- Detailed Content Extraction ---
    description_body = soup.find('div', class_='job__description')
    if description_body:
        full_text = description_body.get_text('\n', strip=True)
        
        # Use regex to find sections. This is more robust than splitting.
        # The (?s) flag allows '.' to match newlines.
        desc_match = re.search(r'(?s)(About the Ads Data Science Team:.*?)(?:Responsibilities:|$)', full_text)
        req_match = re.search(r'(?s)(Responsibilities:.*?)(?:Benefits:|$)', full_text)
        benefits_match = re.search(r'(?s)(Benefits:.*?)(?:#LI-Remote|$)', full_text)

        # If we can successfully segment the text, populate the specific fields
        if desc_match and req_match and benefits_match:
            logging.info("Successfully segmented description, requirements, and benefits.")
            job_data['job_description'] = desc_match.group(1).strip()
            job_data['job_requirements'] = req_match.group(1).strip()
            job_data['benefits'] = benefits_match.group(1).strip()
        else:
            # Fallback: If segmentation fails, dump everything into text_content
            logging.warning("Could not segment job description. Dumping all text into 'text_content'.")
            job_data['text_content'] = full_text

    # --- Pay Range Extraction ---
    pay_range_div = soup.find('div', class_='job__pay-ranges')
    if pay_range_div:
        pay_amount_tags = pay_range_div.find_all('p', class_='body')
        if pay_amount_tags:
            job_data['pay_range'] = pay_amount_tags[-1].get_text(strip=True)

    return job_data

def save_to_json(data: dict):
    """Saves the dictionary to a JSON file."""
    if not data.get('job_title'):
        logging.error("No job title found, cannot save file.")
        return

    # Sanitize filename
    company_name = data.get('company', 'UnknownCompany').replace(' ', '_')
    job_title = data.get('job_title', 'UnknownTitle').replace(' ', '_').replace('/', '_')
    filename = f"{str(datetime.now())[-5:]}.json"
    
    # Create an 'output' directory if it doesn't exist
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"Successfully saved job data to {filepath}")


# --- Main execution block ---
if __name__ == "__main__":
    html = fetch_job_data(URL)
    if html:
        parsed_data = parse_job_to_json(html, URL)
        if parsed_data:
            save_to_json(parsed_data)