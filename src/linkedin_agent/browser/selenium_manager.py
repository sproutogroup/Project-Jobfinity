"""
Selenium WebDriver manager for LinkedIn automation.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..config.settings import (
    CHROME_HOST,
    CHROME_DEBUG_PORT,
    CHROME_DRIVER_PATH,
    PAGE_LOAD_WAIT
)

class SeleniumManager:
    """
    Manages Selenium WebDriver instance with debug connection.
    """
    _instance = None
    _driver = None
    _wait = None

    @classmethod
    def get_driver(cls) -> webdriver.Chrome:
        """
        Get or create a Chrome WebDriver instance.
        
        Returns:
            webdriver.Chrome: The Chrome WebDriver instance
        """
        if cls._driver is None:
            try:
                print("Initializing Chrome WebDriver...")
                options = webdriver.ChromeOptions()
                options.debugger_address = f"{CHROME_HOST}:{CHROME_DEBUG_PORT}"
                
                service = Service(CHROME_DRIVER_PATH)
                
                cls._driver = webdriver.Chrome(service=service, options=options)
                cls._wait = WebDriverWait(cls._driver, PAGE_LOAD_WAIT)
                print("Chrome WebDriver initialized successfully.")
            except Exception as e:
                print(f"Error initializing Chrome WebDriver: {e}")
                raise

        return cls._driver

    @classmethod
    def get_wait(cls) -> WebDriverWait:
        """
        Get the WebDriverWait instance.
        
        Returns:
            WebDriverWait: WebDriverWait instance for explicit waits
        """
        if cls._wait is None:
            cls.get_driver()  # This will initialize both driver and wait
        return cls._wait

    @classmethod
    def close(cls):
        """Close the WebDriver instance and clean up resources."""
        if cls._driver:
            print("Closing Chrome WebDriver...")
            try:
                cls._driver.quit()
            except Exception as e:
                print(f"Error closing Chrome WebDriver: {e}")
            finally:
                cls._driver = None
                cls._wait = None
                print("Chrome WebDriver closed.") 