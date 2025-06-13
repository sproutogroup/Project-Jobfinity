# Author: Sprouto Group

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Setup Chrome driver
options = webdriver.ChromeOptions()
options.debugger_address = "127.0.0.1:9222"
service = Service("C:\\Users\\AISpr\\Downloads\\Compressed\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Step 1: Go to LinkedIn homepage
driver.get("https://www.linkedin.com/")
time.sleep(2)

# Step 2: Search input
search_input = input("Enter the search query: ")
search_box = wait.until(EC.presence_of_element_located((By.XPATH, '//input[contains(@placeholder, "Search")]')))
search_box.clear()
search_box.send_keys(search_input)
search_box.send_keys(Keys.RETURN)

# Step 3: Wait for results to load
time.sleep(3)

# Step 4: Extract all profile hrefs first
profile_urls = set()
try:
    profile_links = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@href, "/in/")]')))
    for link in profile_links:
        href = link.get_attribute('href')
        if href:
            profile_urls.add(href)
except Exception as e:
    print("❌ No profile links found.")
    print(e)

# Container for all profiles' data
all_profiles_data = []

# Step 5: Visit each profile and extract info
for href in profile_urls:
    print(f"\n🔗 Opening profile: {href}")
    driver.get(href)
    time.sleep(3)

    # Extract Name
    try:
        name_elem = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'QODXqhgbehVMqqndqByrWzsHbvNlvxMyoZc')))
        name = name_elem.text
    except:
        name = "Name not found"

    # Extract Headline
    try:
        headline_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.text-body-medium.break-words')))
        headline = headline_elem.text
    except:
        headline = "Headline not found"

    # Extract Designation using XPath
    try:
        designation_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div[1]/a/div/div/div/div/span[1]')
        ))
        designation = designation_elem.text
    except:
        designation = "Designation not found"

    # Extract Company Name using XPath
    try:
        company_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[4]/div[3]/ul/li[1]/div/div[2]/div[1]/a/span[1]/span[1]')
        ))
        company = company_elem.text
    except:
        company = "Company not found"

    print(f"👤 Name: {name}")
    print(f"💼 Headline: {headline}")
    print(f"🏢 Company: {company}")
    print(f"🪪 Designation: {designation}")

    # Save profile data
    profile_data = {
        "profile_url": href,
        "name": name,
        "headline": headline,
        "company": company,
        "designation": designation
    }
    all_profiles_data.append(profile_data)

# Save all profiles to JSON
with open("linkedin_profiles.json", "w", encoding="utf-8") as f:
    json.dump(all_profiles_data, f, ensure_ascii=False, indent=4)

print("\n✅ All data saved to linkedin_profiles.json.")
