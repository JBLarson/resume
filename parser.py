from bs4 import BeautifulSoup
from typing import Dict

def extract_job_text(html: str) -> str:
    """Strip boilerplate, return full job description text."""
    soup = BeautifulSoup(html, "html.parser")
    # e.g. grab <div class="job-description">
    desc = soup.select_one(".job-description") or soup.body
    return desc.get_text(separator="\n").strip()

def sectionize(text: str) -> Dict[str, str]:
    """
    (Optional)
    Split into sections: requirements, responsibilities, qualifications.
    """
    # Naïve regex or headings-based split
    return {"responsibilities": "...", "requirements": "..."}
