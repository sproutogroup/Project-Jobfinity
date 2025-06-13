"""
Configuration settings for LinkedIn automation.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Chrome Configuration
CHROME_HOST = "127.0.0.1"
CHROME_DEBUG_PORT = "9222"
CHROME_DRIVER_PATH = os.getenv(
    "CHROME_DRIVER_PATH",
    "C:\\Users\\AISpr\\Downloads\\Compressed\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
)

# Timing Configuration
PAGE_LOAD_WAIT = 10  # seconds
PROFILE_LOAD_DELAY = 3  # seconds
SEARCH_LOAD_DELAY = 3  # seconds

# LinkedIn Selectors
SELECTORS = {
    "search_box": {
        "type": "xpath",
        "value": '//input[contains(@placeholder, "Search")]'
    },
    "profile_links": {
        "type": "xpath",
        "value": '//a[contains(@href, "/in/")]'
    },
    "name": {
        "type": "class",
        "value": "QODXqhgbehVMqqndqByrWzsHbvNlvxMyoZc"
    },
    "headline": {
        "type": "css",
        "value": "div.text-body-medium.break-words"
    },
    "designation": {
        "type": "xpath",
        "value": '//*[@id="profile-content"]/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div[1]/a/div/div/div/div/span[1]'
    },
    "company": {
        "type": "xpath",
        "value": '//*[@id="profile-content"]/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div[1]/a/span[1]/span[1]'
    }
}

# Output Configuration
OUTPUT_FILE = "linkedin_profiles.json" 