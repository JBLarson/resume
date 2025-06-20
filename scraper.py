import requests
from bs4 import BeautifulSoup

def fetch_url(url: str) -> str:
    """Download HTML (or use Playwright for JS‐heavy pages)."""
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text
