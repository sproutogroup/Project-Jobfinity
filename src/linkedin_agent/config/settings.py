"""
Configuration settings for LinkedIn automation.
"""

import os
from dotenv import load_dotenv
import sys

# Get the absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
ENV_PATH = os.path.join(PROJECT_ROOT, '.env-dev')


# Load the .env-dev file
load_dotenv(dotenv_path=ENV_PATH)

# Get API key with debug logging
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(f"GEMINI_API_KEY not found in environment. Please check {ENV_PATH}")

# LLM Configuration
LLM_MODEL = "gemini-1.5-flash"  # Default model for Gemini Pro
LLM_TEMPERATURE = 0.7     # Default temperature for more creative responses
LLM_MAX_TOKENS = 1000    # Maximum tokens for LLM responses

# Chrome Configuration
CHROME_HOST = "127.0.0.1"
CHROME_DEBUG_PORT = "9222"
CHROME_DRIVER_PATH = os.getenv(
    "CHROME_DRIVER_PATH",
    # "C:\Users\AISpr\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"
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