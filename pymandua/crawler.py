"""
Module: crawler.py

Crawls through links or buttons matching specified keywords (using fuzzy matching), separates hyperlinks and non-hyperlink buttons,
and gathers HTML from each interaction.

Usage:
    from crawler import Crawler
    crawler = Crawler(driver, gatherer, keywords=["Next", "Continue"], threshold=80)
    html_pages = crawler.crawl()
"""
import time
from selenium.webdriver.remote.webdriver import WebDriver
from .gatherer import Gatherer
from rapidfuzz import fuzz
from urllib.parse import urlparse

class Crawler:
    def __init__(self, driver: WebDriver, gatherer: Gatherer, keywords, wait: float = 2.0, threshold: float = 80.0):
        """
        Initializes the crawler.

        Args:
            driver (WebDriver): Selenium WebDriver instance.
            gatherer (Gatherer): Instance to extract HTML (must implement get_body_html()).
            keywords (str or list): Keyword or list of keywords to match in link/button text.
            wait (float): Seconds to wait after click before gathering HTML.
            threshold (float): Minimum fuzzy match score (0-100) to consider a match.
        """
        self.driver = driver
        self.gatherer = gatherer
        self.keywords = keywords if isinstance(keywords, list) else [keywords]
        self.wait = wait
        self.threshold = threshold

    def _fuzzy_ratio(self, a: str, b: str) -> float:
        """Compute fuzzy match ratio between two strings using rapidfuzz."""
        return fuzz.partial_ratio(a.lower(), b.lower())

    def _find_clickable_elements(self):
        """
        Finds <a> or <button> elements whose visible text fuzzily matches any of the keywords above a threshold.

        Returns:
            tuple: (hyperlink_elements, button_elements)
        """
        candidates = self.driver.find_elements("xpath", "//a | //button")
        hyperlink_elements = []
        button_elements = []

        for elem in candidates:
            text = elem.text.strip()
            if not text:
                continue
            for kw in self.keywords:
                score = self._fuzzy_ratio(text, kw)
                if score >= self.threshold:
                    href = elem.get_attribute("href")
                    onclick = elem.get_attribute("onclick")
                    if href or (onclick and "location.href" in onclick):
                        hyperlink_elements.append(elem)
                    else:
                        button_elements.append(elem)
                    break
        return hyperlink_elements, button_elements

    def crawl(self):
        """
        Crawl through matched elements, gathering HTML contents from navigated or interacted pages.

        Returns:
            list: List of HTML strings from crawled pages.
        """
        html_pages = []
        visited_urls = set()

        hyperlink_elements, button_elements = self._find_clickable_elements()

        # Handle buttons without hrefs
        for button in button_elements:
            try:
                prev_url = self.driver.current_url
                button.click()
                time.sleep(self.wait)
                new_url = self.driver.current_url
                if new_url != prev_url:
                    if new_url not in visited_urls:
                        visited_urls.add(new_url)
                else:
                    html_pages.append(self.gatherer.get_body_html())
                self.driver.back()
                time.sleep(self.wait)
            except Exception:
                continue

        # Handle elements with hyperlinks
        for link in hyperlink_elements:
            try:
                href = link.get_attribute("href")
                if not href or href in visited_urls:
                    continue
                if href == self.driver.current_url:
                    continue
                visited_urls.add(href)
                self.driver.get(href)
                time.sleep(self.wait)
                html_pages.append(self.gatherer.get_body_html())
                self.driver.back()
                time.sleep(self.wait)
            except Exception:
                continue

        return html_pages
