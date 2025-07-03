# scrape job posting URLs from reddit greenhouse site

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
START_URL = "https://www.redditinc.com/careers/"
OUTPUT_FILENAME = "reddit_job_urls.json"

def setup_driver() -> webdriver.Chrome:
    """Initializes and returns a Selenium Chrome WebDriver."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def collect_job_urls(driver: webdriver.Chrome) -> list[str]:
    """
    Navigates the careers page and scrapes all job URLs using a robust XPath selector.
    """
    driver.get(START_URL)
    job_urls = set()
    wait = WebDriverWait(driver, 20)

    try:
        # --- THE FIX: Using a robust, relative XPath ---
        
        # 1. Wait for the main container using its ID. This is a stable anchor point.
        wait.until(EC.visibility_of_element_located((By.ID, "job-results")))
        print("✅ Found main job container: #job-results")

        # 2. Use a relative XPath to find all job links.
        # This is much more durable than the full, absolute XPath.
        # It looks for any <a> tag inside a <div class="job">, which is itself inside <div id="job-results">.
        job_link_xpath = "//div[@id='job-results']//div[@class='job']/a"
        
        # The absolute XPath you provided is extremely brittle. If you must use it, it would be:
        # job_link_xpath = "/html/body/div[2]/main/div/div/div/div/div[7]/div/div/div[2]/div/div/div/div/div/div/div[4]/div/div[2]/div[2]/a"
        
        job_links = driver.find_elements(By.XPATH, job_link_xpath)
        
        num_jobs = len(job_links)
        if num_jobs == 0:
            print(f"❌ Found 0 job links with the XPath: {job_link_xpath}")
            return []

        print(f"Found {num_jobs} job links to process.")
        
        # 3. Loop through the found links and extract the href attribute.
        for link in job_links:
            href = link.get_attribute('href')
            if href:
                job_urls.add(href)

    except TimeoutException:
        print("❌ Timed out waiting for the #job-results container. The page structure has likely changed.")
    
    return list(job_urls)

def save_urls_to_json(urls: list[str]):
    """Saves the list of URLs to a JSON file."""
    if not urls:
        print("\nNo URLs were collected. Nothing to save.")
        return

    output_data = {"redditUrls": sorted(urls)}
    
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Successfully saved {len(urls)} unique URLs to {os.path.abspath(OUTPUT_FILENAME)}")


# --- Main execution block ---
if __name__ == "__main__":
    driver = None
    try:
        driver = setup_driver()
        collected_urls = collect_job_urls(driver)
        save_urls_to_json(collected_urls)
    except Exception as e:
        print(f"An unexpected error occurred during the main execution: {e}")
    finally:
        if driver:
            driver.quit()
            print("\nBrowser closed.")