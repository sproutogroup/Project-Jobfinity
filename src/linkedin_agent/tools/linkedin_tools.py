"""
LinkedIn interaction tools using Selenium for profile data extraction.
"""

import time
from typing import List, Set, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from ..browser.selenium_manager import SeleniumManager
from ..config.settings import SELECTORS, SEARCH_LOAD_DELAY, PROFILE_LOAD_DELAY
from ..models.types import LinkedInProfile

def search_linkedin_profiles(query: str) -> Set[str]:
    """
    Search LinkedIn and collect profile URLs.
    
    Args:
        query (str): Search query for finding LinkedIn members
        
    Returns:
        Set[str]: Set of profile URLs
    """
    driver = SeleniumManager.get_driver()
    wait = SeleniumManager.get_wait()
    profile_urls = set()

    try:
        # Go to LinkedIn homepage
        driver.get("https://www.linkedin.com/")
        time.sleep(2)

        # Search for profiles
        search_box = wait.until(EC.presence_of_element_located(
            (By.XPATH, SELECTORS["search_box"]["value"])
        ))
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Wait for results
        time.sleep(SEARCH_LOAD_DELAY)

        # Extract profile URLs
        profile_links = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, SELECTORS["profile_links"]["value"])
        ))
        
        for link in profile_links:
            href = link.get_attribute('href')
            if href:
                profile_urls.add(href)

    except Exception as e:
        print("❌ Error during profile search:")
        print(e)

    return profile_urls

def extract_profile_data(profile_url: str) -> LinkedInProfile:
    """
    Extract data from a single LinkedIn profile.
    
    Args:
        profile_url (str): URL of the LinkedIn profile
        
    Returns:
        LinkedInProfile: Extracted profile data
    """
    driver = SeleniumManager.get_driver()
    wait = SeleniumManager.get_wait()
    
    print(f"\n🔗 Opening profile: {profile_url}")
    driver.get(profile_url)
    time.sleep(PROFILE_LOAD_DELAY)

    try:
        # Extract Name
        name_elem = wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, SELECTORS["name"]["value"])
        ))
        name = name_elem.text
    except:
        name = "Name not found"

    try:
        # Extract Headline
        headline_elem = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, SELECTORS["headline"]["value"])
        ))
        headline = headline_elem.text
    except:
        headline = "Headline not found"

    try:
        # Extract Designation
        designation_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, SELECTORS["designation"]["value"])
        ))
        designation = designation_elem.text
    except:
        designation = "Designation not found"

    try:
        # Extract Company
        company_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, SELECTORS["company"]["value"])
        ))
        company = company_elem.text
    except:
        company = "Company not found"

    print(f"👤 Name: {name}")
    print(f"💼 Headline: {headline}")
    print(f"🏢 Company: {company}")
    print(f"🪪 Designation: {designation}")

    return {
        "profile_url": profile_url,
        "name": name,
        "headline": headline,
        "company": company,
        "designation": designation
    } 