import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import logging
import os
import sys


class WebScraper:
    """
    Base class for web scraping using Selenium and Beautiful Soup
    """

    def __init__(self, headless=True, timeout=10, implicit_wait=5):
        """
        Initialize the web scraper

        Args:
            headless (bool): Run browser in headless mode
            timeout (int): Explicit wait timeout in seconds
            implicit_wait (int): Implicit wait timeout in seconds
        """
        self.timeout = timeout
        self.driver = None
        self.soup = None
        self.page_source = None

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Setup Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")

        # Initialize driver
        self._init_driver(implicit_wait)

    def _init_driver(self, implicit_wait):
        """Initialize the Chrome driver"""
        try:
            # Try multiple methods to setup ChromeDriver
            service = None

            # Method 1: Try webdriver-manager if available
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                self.logger.info("Using webdriver-manager for ChromeDriver")
            except ImportError:
                self.logger.info("webdriver-manager not available, trying alternative methods")
            except Exception as e:
                self.logger.warning(f"webdriver-manager failed: {e}, trying alternative methods")

            # Method 2: Try to find ChromeDriver in common locations
            if not service:
                chromedriver_paths = [
                    "chromedriver.exe",  # Current directory
                    "chromedriver",  # Current directory (Linux/Mac)
                    os.path.join(os.getcwd(), "chromedriver.exe"),
                    "C:\\chromedriver\\chromedriver.exe",  # Common Windows location
                    "C:\\chromedriver\\chromedriver-win64\\chromedriver.exe",  # New download format
                    "C:\\chromedriver\\chromedriver-win32\\chromedriver.exe",  # 32-bit version
                    "/usr/local/bin/chromedriver",  # Common Linux location
                    "/usr/bin/chromedriver",  # Another Linux location
                ]

                for path in chromedriver_paths:
                    if os.path.exists(path):
                        service = Service(path)
                        self.logger.info(f"Found ChromeDriver at: {path}")
                        break

            # Method 3: Try without specifying service (ChromeDriver in PATH)
            if service:
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            else:
                self.logger.info("Trying ChromeDriver from PATH")
                self.driver = webdriver.Chrome(options=self.chrome_options)

            self.driver.implicitly_wait(implicit_wait)
            self.logger.info("Chrome driver initialized successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            self.logger.error("Please install ChromeDriver using one of these methods:")
            self.logger.error("1. pip install --upgrade webdriver-manager")
            self.logger.error("2. Download ChromeDriver from https://chromedriver.chromium.org/")
            self.logger.error("3. Add ChromeDriver to your system PATH")
            raise

    def load_page(self, url, wait_for_element=None, wait_time=None):
        """
        Load a web page and parse it with Beautiful Soup

        Args:
            url (str): URL to load
            wait_for_element (tuple): Optional (By.TYPE, "selector") to wait for specific element
            wait_time (int): Custom wait time for this request

        Returns:
            bool: True if page loaded successfully, False otherwise
        """
        try:
            self.logger.info(f"Loading page: {url}")
            self.driver.get(url)

            # Wait for specific element if provided
            if wait_for_element:
                wait = WebDriverWait(self.driver, wait_time or self.timeout)
                wait.until(EC.presence_of_element_located(wait_for_element))
                self.logger.info(f"Element {wait_for_element} found")

            # Small delay to ensure page is fully loaded
            time.sleep(2)

            # Get page source and create Beautiful Soup object
            self.page_source = self.driver.page_source
            self.soup = BeautifulSoup(self.page_source, 'html.parser')

            self.logger.info("Page loaded and parsed successfully")
            return True

        except TimeoutException:
            self.logger.error(f"Timeout waiting for element {wait_for_element}")
            return False
        except Exception as e:
            self.logger.error(f"Error loading page: {e}")
            return False

    def get_element_by_selector(self, css_selector, multiple=False):
        """
        Extract specific HTML element(s) using CSS selector

        Args:
            css_selector (str): CSS selector string
            multiple (bool): Return all matching elements if True, first match if False

        Returns:
            BeautifulSoup element(s) or None if not found
        """
        if not self.soup:
            self.logger.error("No page loaded. Call load_page() first.")
            return None

        try:
            if multiple:
                elements = self.soup.select(css_selector)
                self.logger.info(f"Found {len(elements)} elements with selector: {css_selector}")
                return elements
            else:
                element = self.soup.select_one(css_selector)
                if element:
                    self.logger.info(f"Found element with selector: {css_selector}")
                else:
                    self.logger.warning(f"No element found with selector: {css_selector}")
                return element

        except Exception as e:
            self.logger.error(f"Error finding element with selector {css_selector}: {e}")
            return None

    def get_element_by_text(self, tag, text, partial_match=False, multiple=False):
        """
        Find element(s) by tag and text content

        Args:
            tag (str): HTML tag name (e.g., 'div', 'span', 'a')
            text (str): Text to search for
            partial_match (bool): If True, use partial text matching
            multiple (bool): Return all matching elements if True

        Returns:
            BeautifulSoup element(s) or None if not found
        """
        if not self.soup:
            self.logger.error("No page loaded. Call load_page() first.")
            return None

        try:
            if partial_match:
                if multiple:
                    elements = self.soup.find_all(tag, string=lambda t: t and text in t)
                else:
                    elements = self.soup.find(tag, string=lambda t: t and text in t)
            else:
                if multiple:
                    elements = self.soup.find_all(tag, string=text)
                else:
                    elements = self.soup.find(tag, string=text)

            if multiple:
                self.logger.info(f"Found {len(elements)} {tag} elements containing '{text}'")
            else:
                if elements:
                    self.logger.info(f"Found {tag} element containing '{text}'")
                else:
                    self.logger.warning(f"No {tag} element found containing '{text}'")

            return elements

        except Exception as e:
            self.logger.error(f"Error finding element by text: {e}")
            return None

    def extract_download_options(self):
        """
        Specific method to extract download options from Coursera video pages

        Returns:
            list: List of download option dictionaries
        """
        download_options = []

        # Common selectors for download links/buttons on video platforms
        selectors_to_try = [
            'a[data-click-key*="download_video"]'
            # 'a[href*="download"]',
            # 'button[class*="download"]',
            # '.download-link',
            # '.download-button',
            # 'a[download]',
            # '[data-track-action*="download"]',
            # '.video-download'
        ]

        for selector in selectors_to_try:
            elements = self.get_element_by_selector(selector, multiple=True)
            if elements:
                for element in elements:
                    option = {
                        'text': element.get_text(strip=True),
                        'href': element.get('href', ''),
                        'title': element.get('title', ''),
                        'data_attributes': {k: v for k, v in element.attrs.items() if k.startswith('data-')}
                    }
                    download_options.append(option)

        self.logger.info(f"Found {len(download_options)} potential download options")
        return download_options

    def get_raw_html(self, css_selector=None):
        """
        Get raw HTML content

        Args:
            css_selector (str): Optional CSS selector to get specific part

        Returns:
            str: Raw HTML content
        """
        if not self.soup:
            self.logger.error("No page loaded. Call load_page() first.")
            return None

        if css_selector:
            element = self.get_element_by_selector(css_selector)
            return str(element) if element else None
        else:
            return str(self.soup)

    def wait_and_click(self, by_type, selector, wait_time=None):
        """
        Wait for an element and click it (useful for dynamic content)

        Args:
            by_type: Selenium By type (e.g., By.CSS_SELECTOR, By.XPATH)
            selector (str): Element selector
            wait_time (int): Custom wait time

        Returns:
            bool: True if clicked successfully, False otherwise
        """
        try:
            wait = WebDriverWait(self.driver, wait_time or self.timeout)
            element = wait.until(EC.element_to_be_clickable((by_type, selector)))
            element.click()
            self.logger.info(f"Clicked element: {selector}")
            return True
        except TimeoutException:
            self.logger.error(f"Timeout waiting for clickable element: {selector}")
            return False
        except Exception as e:
            self.logger.error(f"Error clicking element {selector}: {e}")
            return False

    def scroll_to_element(self, css_selector):
        """
        Scroll to a specific element on the page

        Args:
            css_selector (str): CSS selector for the element

        Returns:
            bool: True if scrolled successfully, False otherwise
        """
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, css_selector)
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(1)  # Allow time for any lazy loading
            return True
        except NoSuchElementException:
            self.logger.error(f"Element not found: {css_selector}")
            return False
        except Exception as e:
            self.logger.error(f"Error scrolling to element: {e}")
            return False

    def refresh_soup(self):
        """
        Refresh the Beautiful Soup object with current page source
        (useful after dynamic content loads)
        """
        if self.driver:
            self.page_source = self.driver.page_source
            self.soup = BeautifulSoup(self.page_source, 'html.parser')
            self.logger.info("Beautiful Soup object refreshed")

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser driver closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage for Coursera video page
if __name__ == "__main__":
    # Example usage
    with WebScraper() as scraper:
        # Load the Coursera video page
        url = "https://www.coursera.org/learn/machine-learning/lecture/qrxwU/decision-boundary"

        if scraper.load_page(url):
            # Try to extract download options
            download_options = scraper.extract_download_options()

            if download_options:
                print("Found download options:")
                for i, option in enumerate(download_options, 1):
                    print(f"{i}. Text: {option['text']}")
                    print(f"   Link: {option['href']}")
                    print(f"   Title: {option['title']}")
                    print("---")
            else:
                print("No download options found")

            # Example: Get specific HTML section
            video_container = scraper.get_element_by_selector('.video-container')
            if video_container:
                print("Video container HTML:")
                print(video_container.prettify()[:500] + "...")

            # Example: Search for elements containing specific text
            download_elements = scraper.get_element_by_text('a', 'download', partial_match=True, multiple=True)
            if download_elements:
                print(f"Found {len(download_elements)} elements with 'download' in text")