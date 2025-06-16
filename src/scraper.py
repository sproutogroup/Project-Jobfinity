"""
LinkedIn profile scraper main script.
Searches and extracts profile information based on search query.
"""

import json
from linkedin_agent.tools.linkedin_tools import search_linkedin_profiles, extract_profile_data
from linkedin_agent.browser.selenium_manager import SeleniumManager
from linkedin_agent.config.settings import OUTPUT_FILE

def main():
    """Main function to run the LinkedIn profile scraper."""
    try:
        # Get search query from user
        search_input = input("Enter the search query: ")

        # Step 1: Search and collect profile URLs
        profile_urls = search_linkedin_profiles(search_input)
        
        if not profile_urls:
            print("❌ No profile links found.")
            return

        # Step 2: Process each profile
        all_profiles_data = []
        
        for href in profile_urls:
            try:
                profile_data = extract_profile_data(href)
                all_profiles_data.append(profile_data)
            except Exception as e:
                print(f"❌ Error processing profile {href}:")
                print(e)

        # Step 3: Save results to JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_profiles_data, f, ensure_ascii=False, indent=4)

        print(f"\n✅ All data saved to {OUTPUT_FILE}.")

    except Exception as e:
        print("❌ An error occurred during execution:")
        print(e)
    finally:
        SeleniumManager.close()

if __name__ == "__main__":
    main() 


    # 3247456111