#!/usr/bin/env python3
import argparse
import logging
import time
import random
import json
import os
from datetime import datetime
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Retry decorator with exponential backoff
def retry(exc_types, tries=3, delay=2, backoff=2):
	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			m, d = tries, delay
			while m > 1:
				try:
					return fn(*args, **kwargs)
				except exc_types as e:
					logging.warning(f"{fn.__name__} failed ({e}), retrying in {d}s...")
					time.sleep(d)
					m -= 1
					d *= backoff
			return fn(*args, **kwargs)
		return wrapper
	return decorator

# A small pool of user agents
USER_AGENTS = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 Safari/605.1.15",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
]

class JobScraper:
	def __init__(self, query, max_pages, headless, proxies, output):
		self.query = query.replace(" ", "+")
		self.max_pages = max_pages
		self.output = output
		self.proxies = proxies or []
		self.results = []
		logging.basicConfig(
			level=logging.INFO,
			format="%(asctime)s [%(levelname)s] %(message)s",
			datefmt="%Y-%m-%d %H:%M:%S",
		)
		self.driver = self._init_driver(headless)

	def _init_driver(self, headless):
		opts = webdriver.ChromeOptions()
		if headless:
			opts.add_argument("--headless=new")
		ua = random.choice(USER_AGENTS)
		opts.add_argument(f"user-agent={ua}")
		if self.proxies:
			proxy = random.choice(self.proxies)
			opts.add_argument(f"--proxy-server={proxy}")
		opts.add_argument("--disable-blink-features=AutomationControlled")
		return webdriver.Chrome(
			service=Service(ChromeDriverManager().install()),
			options=opts
		)

	@retry((Exception,), tries=3, delay=2)
	def _get(self, url):
		self.driver.get(url)

	def _scroll_to_bottom(self):
		last_height = self.driver.execute_script("return document.body.scrollHeight")
		while True:
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(random.uniform(1, 2))
			new_height = self.driver.execute_script("return document.body.scrollHeight")
			if new_height == last_height:
				break
			last_height = new_height

	def _parse_cards(self):
		return WebDriverWait(self.driver, 10).until(
			EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.tapItem"))
		)

	@retry((Exception,), tries=2, delay=1)
	def _scrape_job(self, url):
		main = self.driver.current_window_handle
		self.driver.execute_script("window.open(arguments[0]);", url)
		self.driver.switch_to.window(self.driver.window_handles[-1])
		try:
			WebDriverWait(self.driver, 5).until(
				EC.presence_of_element_located((By.ID, "jobDescriptionText"))
			)
			text = self.driver.find_element(By.ID, "jobDescriptionText").text
		except Exception:
			text = self.driver.find_element(By.TAG_NAME, "body").text
		return text
		"""
        try:
			self.driver.save_screenshot(f"screenshot_{int(time.time())}.png")
			self.driver.close()
			self.driver.switch_to.window(main)
        """
        
	def run(self):
		try:
			base = f"https://www.indeed.com/jobs?q={self.query}&start="
			for page in range(0, self.max_pages):
				url = base + str(page * 10)
				logging.info(f"Loading page {page+1}/{self.max_pages}: {url}")
				try:
					self._get(url)
				except Exception as e:
					logging.error(f"Page load failed: {e}")
					continue
				self._scroll_to_bottom()
				try:
					cards = self._parse_cards()
				except Exception as e:
					logging.error(f"No job cards found: {e}")
					break
				for card in cards:
					href = card.get_attribute("href")
					if not href: continue
					logging.info(f"Scraping job: {href}")
					try:
						text = self._scrape_job(href)
						self.results.append({
							"source_url": href,
							"access_datetime": datetime.utcnow().isoformat(),
							"textContent": text
						})
					except Exception as e:
						logging.error(f"Failed to scrape {href}: {e}")
				time.sleep(random.uniform(2, 4))
		except:
			self.driver.quit()
			self._save()

	def _save(self):
		try:
			with open(self.output, "w", encoding="utf-8") as f:
				json.dump(self.results, f, ensure_ascii=False, indent=2)
			logging.info(f"Wrote {len(self.results)} jobs to {self.output}")
		except Exception as e:
			logging.error(f"Error writing JSON: {e}")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Indeed job scraper")
	parser.add_argument("--query", default="Machine Learning Engineer", help="Search term")
	parser.add_argument("--max-pages", type=int, default=3, help="Number of pages to scrape")
	parser.add_argument("--output", default="jobs.json", help="Output JSON file")
	parser.add_argument("--headless", action="store_true", help="Run headless")
	parser.add_argument("--proxies", nargs="*", help="Optional list of proxy URLs")
	args = parser.parse_args()

	scraper = JobScraper(
		query=args.query,
		max_pages=args.max_pages,
		headless=args.headless,
		proxies=args.proxies,
		output=args.output
	)
	scraper.run()
