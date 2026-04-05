import requests
from bs4 import BeautifulSoup
from loguru import logger
import re

class WebScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape_text(self, url: str) -> str:
        """
        Fetches the URL and extracts clean text using BeautifulSoup.
        """
        logger.info(f"Scraping content from {url}...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                # Bypass basic bot protections
                page.set_extra_http_headers(self.headers)
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                html = page.content()
                browser.close()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            text = soup.get_text(separator=' ')
            
            # Clean up whitespace
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            logger.info(f"Successfully scraped {len(cleaned_text)} characters.")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return ""
