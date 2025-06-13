import os
import asyncio
from typing import TypedDict, List, Dict, Union
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage

# --- Playwright Imports ---
from playwright.async_api import async_playwright, Page
from playwright_stealth import stealth_async
import time
import random

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# --- Define Your State ---
class LinkedInAutomationState(TypedDict):
    query: str
    member_profiles: List[Dict]
    current_member_index: int
    message_to_send: str
    action_taken: str
    error: str
    current_member_profile: Union[Dict, None]

# --- Global/Shared Playwright Context ---
_playwright_instance = None
_playwright_browser_context = None

async def get_browser_page() -> Page:
    """Connect to a running Chrome instance and get a new page."""
    global _playwright_instance, _playwright_browser_context

    if _playwright_instance is None:
        _playwright_instance = await async_playwright().start()

    if _playwright_browser_context is None:
        try:
            print("Connecting to running Chrome instance on port 9222...")
            # Connect to the browser instance you launched manually
            browser = await _playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
            
            # Use the first available context (your Profile 1)
            _playwright_browser_context = browser.contexts[0]
            print("Successfully connected to existing Chrome session.")
        except Exception as e:
            print(f"Error connecting to Chrome: {e}")
            print("Please make sure Chrome is running with remote debugging enabled:")
            print('1. Close all Chrome windows')
            print('2. Run: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\Users\\AISpr\\AppData\\Local\\Google\\Chrome\\User Data" --profile-directory="Profile 1"')
            print('3. Ensure you are logged into LinkedIn in that browser')
            raise

    # Create a new page in the existing context
    page = await _playwright_browser_context.new_page()
    await stealth_async(page)  # Apply stealth settings to avoid detection
    return page

async def close_browser():
    """Close Playwright resources."""
    global _playwright_instance, _playwright_browser_context
    if _playwright_browser_context:
        print("Disconnecting from Chrome session...")
        _playwright_browser_context = None
    if _playwright_instance:
        print("Stopping Playwright instance...")
        await _playwright_instance.stop()
        _playwright_instance = None

# --- Define Your Tools ---

@tool
async def linkedin_search_members(query: str) -> List[Dict]:
    """Searches LinkedIn for members based on a query."""
    print(f"\n--- TOOL: Searching LinkedIn for: '{query}' ---")
    page = await get_browser_page()
    try:
        # Navigate directly to search results - no login handling needed
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={query.replace(' ', '%20')}&origin=GLOBAL_SEARCH_HEADER"
        await page.goto(search_url, wait_until="networkidle")
        await page.wait_for_selector(".search-results__list", timeout=10000)

        members_found = []
        profile_cards = await page.locator(".reusable-search__result-container").all()
        for i, card in enumerate(profile_cards[:5]):
            try:
                name_element = await card.locator(".reusable-search__result-container h3").first
                name = await name_element.text_content() if name_element else "N/A"
                url_element = await card.locator("a.app-aware-link").first
                url = await url_element.get_attribute("href") if url_element else "N/A"
                title_element = await card.locator(".entity-result__primary-subtitle").first
                title = await title_element.text_content() if title_element else "N/A"
                summary_element = await card.locator(".entity-result__secondary-subtitle").first
                summary = await summary_element.text_content() if summary_element else "N/A"

                if name != "N/A" and url != "N/A":
                    members_found.append({
                        "name": name.strip(),
                        "url": url.split('?')[0],
                        "title": title.strip(),
                        "summary": summary.strip()
                    })
            except Exception as e:
                print(f"Error parsing profile card {i}: {e}")
            await asyncio.sleep(random.uniform(0.5, 1.5))

        print(f"Found {len(members_found)} members.")
        return members_found

    except Exception as e:
        print(f"Error during LinkedIn search: {e}")
        return []
    finally:
        await page.close()

@tool
async def linkedin_get_profile_details(profile_url: str) -> Dict:
    """Gets detailed information from a LinkedIn profile URL."""
    print(f"\n--- TOOL: Getting details for: {profile_url} ---")
    page = await get_browser_page()
    try:
        await page.goto(profile_url, wait_until="networkidle")
        await page.wait_for_selector("#profile-content", timeout=10000)

        name = await page.locator(".pv-text-details__left-panel h1").text_content() if await page.locator(".pv-text-details__left-panel h1").count() > 0 else "N/A"
        experience = await page.locator(".experience-section").text_content() if await page.locator(".experience-section").count() > 0 else "N/A"
        skills_text = await page.locator("#skills-section").text_content() if await page.locator("#skills-section").count() > 0 else "N/A"
        
        skills = [s.strip() for s in skills_text.split('\n') if s.strip() and len(s.strip()) > 2] if skills_text != "N/A" else []
        interests = []

        return {
            "name": name.strip() if name else "N/A",
            "url": profile_url,
            "experience": experience.strip() if experience else "N/A",
            "skills": skills,
            "interests": interests
        }
    except Exception as e:
        print(f"Error during profile detail retrieval for {profile_url}: {e}")
        return {"name": "N/A", "url": profile_url, "experience": "Error", "skills": [], "interests": []}
    finally:
        await page.close()

@tool
async def linkedin_send_message(profile_url: str, message: str) -> str:
    """Mocks sending a personalized message to a LinkedIn member."""
    print(f"\n--- TOOL: Sending message to {profile_url}:\n'{message}' ---")
    await asyncio.sleep(random.uniform(3, 7))
    return f"Message SIMULATED sent to {profile_url}. (Actual implementation needed)."

@tool
async def linkedin_send_connection_request(profile_url: str, message: str = "") -> str:
    """Mocks sending a connection request with an optional note."""
    print(f"\n--- TOOL: Sending connection request to {profile_url} with note:\n'{message}' ---")
    await asyncio.sleep(random.uniform(3, 7))
    return f"Connection request SIMULATED sent to {profile_url}. (Actual implementation needed)."

# --- LLM for Generating Messages and Deciding Actions ---
llm = ChatGoogleGenerativeAI(
    api_key=GEMINI_API_KEY,
    model="gemini-1.5-flash",
    temperature=0.7,
    max_output_tokens=200,
    timeout=None,
    max_retries=0,
)

# --- Define Nodes ---
async def search_node(state: LinkedInAutomationState) -> Dict:
    """Node to search LinkedIn members."""
    print("\n--- NODE: search_node ---")
    query = state["query"]
    members = await linkedin_search_members.ainvoke({"query": query})
    
    return {
        **state,
        "member_profiles": members,
        "current_member_index": 0
    }

async def process_member_node(state: LinkedInAutomationState) -> Dict:
    """Node to get profile details and decide on action using LLM."""
    print("\n--- NODE: process_member_node ---")
    profiles = state["member_profiles"]
    idx = state["current_member_index"]

    if idx >= len(profiles):
        print("DEBUG: No more members to process. Ending.")
        return {"action_taken": "done_processing"}

    current_profile_summary = profiles[idx]
    profile_url = current_profile_summary["url"]
    
    if state.get("action_taken") == "skip" or state.get("action_taken") == "rejected":
        print("DEBUG: Previous action was 'skip' or 'rejected'. Waiting 2-5 seconds before next profile...")
        await asyncio.sleep(random.uniform(2, 5))
        
    details = await linkedin_get_profile_details.ainvoke({"profile_url": profile_url})
    print(f"DEBUG: Processing profile: {details.get('name')} ({profile_url})")

    # LLM decides what to do with the profile
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant for LinkedIn outreach. Your goal is to identify if a profile is a good fit for an outreach based on the initial query and their profile details. If it's a good fit, propose to 'send_message' or 'send_connection_request' and generate a personalized message. Otherwise, suggest to 'skip'. "
                   "Respond ONLY in the format: 'ACTION: <action_type>\nMESSAGE: <your_personalized_message>' or 'ACTION: skip' "
                   "Actions are: 'send_message', 'send_connection_request', 'skip'. "
                   "Focus on the initial query's tags and try to incorporate details from the profile naturally. Keep messages concise and professional (max 150 words for message)."),
        ("user", f"Initial query: {state['query']}\n"
                 f"Member Name: {details.get('name', 'N/A')}\n"
                 f"Title: {details.get('title', 'N/A')}\n"
                 f"Experience Summary: {details.get('experience', 'N/A')}\n"
                 f"Skills: {', '.join(details.get('skills', []))}\n"
                 f"Interests: {', '.join(details.get('interests', []))}\n\n"
                 f"Based on this, what action should be taken and what message should be sent (if any)?")
    ])

    try:
        chain = prompt_template | llm
        llm_response = await chain.ainvoke({"query": state["query"], "details": details})
        decision_text = llm_response.content.strip()
        print(f"DEBUG: LLM Raw Response:\n{decision_text}")

        action_line = next((line for line in decision_text.split('\n') if line.startswith('ACTION:')), None)
        message_line = next((line for line in decision_text.split('\n') if line.startswith('MESSAGE:')), None)

        action = action_line.split('ACTION:', 1)[1].strip().lower() if action_line else "skip"
        message_content = message_line.split('MESSAGE:', 1)[1].strip() if message_line else ""
        
        return {
            "message_to_send": message_content,
            "action_taken": action,
            "current_member_profile": profiles[idx]
        }

    except Exception as e:
        print(f"ERROR: LLM invocation failed in process_member_node: {e}")
        return {
            "error": f"LLM error: {e}",
            "action_taken": "skip",
            "current_member_profile": profiles[idx],
        }

async def execute_action_node(state: LinkedInAutomationState) -> Dict:
    """Node to execute the decided action and prompt for human review."""
    print("\n--- NODE: execute_action_node ---")
    action = state["action_taken"]
    profile_url = state["current_member_profile"]["url"]
    message = state["message_to_send"]
    member_name = state["current_member_profile"].get("name", "N/A")

    if action in ["send_message", "send_connection_request"]:
        print(f"\n--- HUMAN REVIEW ---")
        print(f"Action Proposed: {action.replace('_', ' ').title()}")
        print(f"To: {member_name} ({profile_url})")
        print(f"Message:\n{message}")
        user_input = input("Approve and Send? (y/n/s for skip): ").strip().lower()

        if user_input == 'y':
            print(f"DEBUG: Human APPROVED. Executing {action} for {member_name}.")
            if action == "send_message":
                result = await linkedin_send_message.ainvoke({"profile_url": profile_url, "message": message})
            else: # send_connection_request
                result = await linkedin_send_connection_request.ainvoke({"profile_url": profile_url, "message": message})
            print(result)
            return {"current_member_index": state["current_member_index"] + 1, "action_taken": "processed"}
        elif user_input == 's':
            print(f"DEBUG: Human decided to skip {member_name}.")
            return {"current_member_index": state["current_member_index"] + 1, "action_taken": "skipped"}
        else:
            print(f"DEBUG: Human decided NOT to send message/connection for {member_name}.")
            return {"current_member_index": state["current_member_index"] + 1, "action_taken": "rejected"}
    else:
        print(f"DEBUG: No valid action to execute for {member_name}. Skipping.")
        return {"current_member_index": state["current_member_index"] + 1, "action_taken": "skipped"}

# --- Build LangGraph Workflow ---
workflow = StateGraph(LinkedInAutomationState)

workflow.add_node("search", search_node)
workflow.add_node("process_member", process_member_node)
workflow.add_node("execute_action", execute_action_node)

# Set entry point
workflow.set_entry_point("search")

# After the search node, always go to the process_member node to start iterating
workflow.add_edge("search", "process_member")

# Conditional routing from process_member
def route_action(state: LinkedInAutomationState) -> str:
    """Routes based on the LLM's action decision."""
    action = state.get("action_taken")
    print(f"DEBUG: Routing from process_member_node. Action: {action}")
    if action in ["send_message", "send_connection_request"]:
        return "execute_action"
    elif action in ["skip", "rejected", "processed"]:
        return "process_member"
    elif action == "done_processing":
        return END
    return "process_member"

workflow.add_conditional_edges(
    "process_member",
    route_action,
    {
        "execute_action": "execute_action",
        "process_member": "process_member",
        END: END
    }
)

# After executing an action, go back to process the next member
workflow.add_edge("execute_action", "process_member")

# Compile the graph
app = workflow.compile()

# --- Example Usage ---
async def run_linkedin_automation(query: str):
    print(f"\n===== Starting LinkedIn Automation Workflow for Query: '{query}' =====")
    print("IMPORTANT: Make sure Chrome is already running with remote debugging enabled")
    print('Run: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\Users\\AISpr\\AppData\\Local\\Google\\Chrome\\User Data" --profile-directory="Profile 1"')
    print("And ensure you're already logged into LinkedIn in that browser.")
    
    initial_state: LinkedInAutomationState = {
        "query": query,
        "member_profiles": [],
        "current_member_index": 0,
        "message_to_send": "",
        "action_taken": "",
        "error": "",
        "current_member_profile": None
    }
    
    final_state_list = []
    try:
        async for s in app.astream(initial_state):
            print(f"Current Graph State after node execution: {s}") 
            final_state_list.append(s)
    except Exception as e:
        print(f"\n--- WORKFLOW CRASHED ---")
        print(f"An error occurred during workflow execution: {e}")
        import traceback
        traceback.print_exc()
        if final_state_list:
            print(f"Last known state: {final_state_list[-1]}")
    finally:
        await close_browser()
    
    print("\n===== Workflow Completed =====")
    if final_state_list:
        final_state = final_state_list[-1]
        print(f"Final State: {final_state}")
        if final_state.get("action_taken") == "done_processing":
            print("All members processed (or no members found).")
        if final_state.get("error"):
            print(f"Workflow finished with error: {final_state['error']}")
    else:
        print("Workflow did not produce any states (might have failed immediately).")

if __name__ == "__main__":
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY environment variable not set. Please set it to run the LLM.")
        print("You can set it in your .env file or terminal: export GEMINI_API_KEY='your_key'")
    
    # Run the automation with a sample query
    asyncio.run(run_linkedin_automation("Software Engineer in Lahore interested in Scalable AI solutions"))
