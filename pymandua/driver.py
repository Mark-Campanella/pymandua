"""
driver.py

A module to create a stealthy Chrome WebDriver instance for web scraping purposes.
Supports default anti-detection configurations and allows user-defined options, including proxy and user profile.

Requirements:
- undetected-chromedriver
- selenium
- selenium-stealth
- python-dotenv

Usage:
    from driver import Driver, DriverUtils

    driver = Driver(proxy="http://user:pass@host:port", user_profile="/path/to/profile").init()
    driver.get("https://www.example.com")
    driver_utils = DriverUtils(driver)
    driver_utils.click_element_by_selector("#button")
"""

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.chrome.service import Service

from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    ElementClickInterceptedException, StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import selenium_stealth
import undetected_chromedriver as uc
from typing import Optional, Dict, Any
import time
import random


class Driver:
    """
    A class to initialize a stealthy Chrome WebDriver using undetected-chromedriver
    and selenium-stealth to bypass bot detection.
    """

    def __init__(self, user_options: Optional[Dict[str, Any]] = None, proxy: Optional[str] = None, user_profile: Optional[str] = None):
        """
        Initialize the StealthDriver class.

        :param user_options: Dictionary with user-defined Chrome options.
        :param proxy: Optional proxy string, e.g., "http://user:pass@host:port"
        :param user_profile: Optional path to Chrome user profile
        """
        self.user_options = user_options or {}
        self.proxy = proxy
        self.user_profile = user_profile

    def _default_options(self) -> uc.ChromeOptions:
        """
        Configure default Chrome options for stealth browsing.

        :return: ChromeOptions object
        """
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--password-store=basic")
        options.add_argument("--lang=en-US")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0")

        if self.proxy:
            options.add_argument(f'--proxy-server={self.proxy}')

        if self.user_profile:
            options.add_argument(f'--user-data-dir={self.user_profile}')

        # Apply user-defined options
        for key, value in self.user_options.items():
            if isinstance(value, bool) and value:
                options.add_argument(f"--{key}")
            elif isinstance(value, str):
                options.add_argument(f"--{key}={value}")

        return options

    def init(self) -> ChromeWebDriver:
        """
        Initialize and return a stealthy Chrome WebDriver instance.

        :return: Chrome WebDriver instance
        """
        options = self._default_options()
        driver = uc.Chrome(driver_executable_path=ChromeDriverManager().install(), options=options)

        selenium_stealth.stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        return driver


class DriverUtils:
    """
    Utility class for common user-like browser actions with exception handling.
    """
    def __init__(self, driver: ChromeWebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def click_element_by_selector(self, selector: str):
        try:
            element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            ActionChains(self.driver).move_to_element(element).click().perform()
        except (TimeoutException, ElementClickInterceptedException, NoSuchElementException, WebDriverException) as e:
            print(f"Click error on {selector}: {e}")

    def find_element(self, selector: str) -> Optional[Any]:
        try:
            return self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            print(f"Element not found: {selector}")
            return None

    def random_clicks(self, selector: str, max_clicks: int = 3):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            random.shuffle(elements)
            for el in elements[:max_clicks]:
                ActionChains(self.driver).move_to_element(el).click().perform()
                time.sleep(random.uniform(0.5, 2.0))
        except Exception as e:
            print(f"Random click error: {e}")

    def go_back(self):
        self.driver.back()

    def go_forward(self):
        self.driver.forward()

    def wait_for_text(self, selector: str, text: str):
        try:
            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), text))
            return True
        except TimeoutException:
            return False

    def wait_for_element(self, selector: str):
        try:
            return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            return None
