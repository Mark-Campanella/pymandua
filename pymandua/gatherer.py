"""
Module: gatherer.py

Provides reusable functions to gather content from web pages using a Selenium WebDriver instance.
Supports getting HTML, elements, images, videos, links, article text, and other DOM-based content.

Usage:
    from gatherer import Gatherer
    gatherer = Gatherer(driver)
    html = gatherer.get_dom_html()
    title = gatherer.get_page_title()
"""

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional, List
from bs4 import BeautifulSoup


class Gatherer:
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def get_dom_html(self) -> str:
        """Returns the current page's HTML DOM."""
        return self.driver.page_source

    def get_body_html(self) -> str:
        """Returns the <body> content only, excluding <script> and <style> tags."""
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        body = soup.body
        return str(body) if body else ""

    def get_page_title(self) -> str:
        """Returns the title of the current page."""
        return self.driver.title

    def get_element(self, selector: str) -> Optional[str]:
        """Returns the outer HTML of the first element that matches the CSS selector."""
        try:
            element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            return element.get_attribute("outerHTML")
        except TimeoutException:
            return None

    def get_elements(self, selector: str) -> List[str]:
        """Returns a list of outer HTMLs of elements that match the CSS selector."""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            return [el.get_attribute("outerHTML") for el in elements]
        except NoSuchElementException:
            return []

    def get_image_sources(self) -> List[str]:
        """Returns a list of all image sources from <img> tags."""
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            return [img.get_attribute("src") for img in images if img.get_attribute("src")]
        except NoSuchElementException:
            return []

    def get_video_sources(self) -> List[str]:
        """Returns a list of video source URLs from <video> and <source> tags."""
        sources = []
        try:
            videos = self.driver.find_elements(By.TAG_NAME, "video")
            for video in videos:
                src = video.get_attribute("src")
                if src:
                    sources.append(src)
                source_tags = video.find_elements(By.TAG_NAME, "source")
                for source in source_tags:
                    s = source.get_attribute("src")
                    if s:
                        sources.append(s)
        except NoSuchElementException:
            pass
        return sources

    def get_links(self) -> List[str]:
        """Returns all href links from <a> tags."""
        try:
            links = self.driver.find_elements(By.TAG_NAME, "a")
            return [link.get_attribute("href") for link in links if link.get_attribute("href")]
        except NoSuchElementException:
            return []

    def get_text_by_class(self, class_name: str) -> List[str]:
        """Returns visible text content from all elements with a specific class."""
        try:
            elements = self.driver.find_elements(By.CLASS_NAME, class_name)
            return [el.text.strip() for el in elements if el.text.strip()]
        except NoSuchElementException:
            return []

    def get_article_text(self) -> str:
        """Tries to extract text from <article> tags if present."""
        try:
            article = self.driver.find_element(By.TAG_NAME, "article")
            return article.text.strip()
        except NoSuchElementException:
            return ""
