"""
Entry point for LinkedIn profile analysis workflow.
Processes profiles from JSON file using LangGraph workflow.
"""

import json
import asyncio
from linkedin_agent.workflow.graph import create_analysis_workflow
from linkedin_agent.workflow.states import ProfileAnalysisState
from linkedin_agent.config.settings import OUTPUT_FILE

async def analyze_profiles():
    """Run the profile analysis workflow on scraped profiles."""
    try:
        # Load profiles from JSON
        print(f"\n📂 Loading profiles from {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            profiles_data = json.load(f)

        if not profiles_data:
            print("❌ No profiles found in JSON file.")
            return

        print(f"✅ Loaded {len(profiles_data)} profiles.")

        # Initialize workflow state
        initial_state: ProfileAnalysisState = {
            "profiles_data": profiles_data,
            "current_profile_index": 0,
            "analysis_results": [],
            "action_taken": "",
            "error": "",
            "current_profile": None,
            "message_to_send": ""
        }

        # Create and run workflow
        app = create_analysis_workflow()
        print("\n🔄 Starting profile analysis workflow...")

        async for state in app.astream(initial_state):
            if state.get("error"):
                print(f"❌ Error: {state['error']}")
                break

        print("\n✅ Profile analysis completed.")

    except FileNotFoundError:
        print(f"❌ Error: {OUTPUT_FILE} not found. Please run the scraper first.")
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_profiles()) 