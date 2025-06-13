"""
LangGraph workflow nodes for LinkedIn profile analysis.
"""

from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from ..config.settings import GEMINI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from .states import ProfileAnalysisState
from .prompts import ANALYZE_PROFILE_PROMPT, SUMMARIZE_RESULTS_PROMPT

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    api_key=GEMINI_API_KEY,
    model=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    max_output_tokens=LLM_MAX_TOKENS
)

async def load_profiles_node(state: ProfileAnalysisState) -> Dict:
    """
    Node to initialize profile analysis with data from JSON.
    """
    print("\n--- NODE: load_profiles_node ---")
    if not state["profiles_data"]:
        return {"error": "No profiles data provided"}
    
    return {
        **state,
        "current_profile_index": 0,
        "analysis_results": [],
        "action_taken": "",
        "current_profile": None,
        "message_to_send": ""
    }

async def analyze_profile_node(state: ProfileAnalysisState) -> Dict:
    """
    Node to analyze a single profile using LLM.
    """
    print("\n--- NODE: analyze_profile_node ---")
    profiles = state["profiles_data"]
    idx = state["current_profile_index"]

    if idx >= len(profiles):
        print("DEBUG: No more profiles to analyze. Ending.")
        return {"action_taken": "done_processing"}

    current_profile = profiles[idx]
    print(f"DEBUG: Analyzing profile: {current_profile.get('name')}")

    # Get LLM analysis
    chain = ANALYZE_PROFILE_PROMPT | llm
    response = await chain.ainvoke(current_profile)
    
    # Parse LLM response
    lines = response.content.strip().split('\n')
    action = next((line.split(':', 1)[1].strip() for line in lines if line.startswith('ACTION:')), 'skip')
    reason = next((line.split(':', 1)[1].strip() for line in lines if line.startswith('REASON:')), '')
    message = next((line.split(':', 1)[1].strip() for line in lines if line.startswith('MESSAGE:')), '')

    analysis_result = {
        **current_profile,
        "action": action,
        "reason": reason,
        "message": message
    }

    return {
        "current_profile": current_profile,
        "message_to_send": message,
        "action_taken": action,
        "analysis_results": state["analysis_results"] + [analysis_result]
    }

async def execute_action_node(state: ProfileAnalysisState) -> Dict:
    """
    Node to execute the decided action with human review.
    """
    print("\n--- NODE: execute_action_node ---")
    action = state["action_taken"]
    profile = state["current_profile"]
    message = state["message_to_send"]

    if action in ["send_message", "send_connection"]:
        print(f"\n--- HUMAN REVIEW ---")
        print(f"Profile: {profile['name']} ({profile['headline']})")
        print(f"Action: {action}")
        print(f"Reason: {next((r['reason'] for r in state['analysis_results'] if r['name'] == profile['name']), '')}")
        print(f"Message:\n{message}")
        
        user_input = input("Approve action? (y/n/s for skip): ").strip().lower()
        
        if user_input == 'y':
            print(f"✅ Action approved for {profile['name']}")
            return {"current_profile_index": state["current_profile_index"] + 1, "action_taken": "processed"}
        elif user_input == 's':
            print(f"⏭️ Skipping {profile['name']}")
            return {"current_profile_index": state["current_profile_index"] + 1, "action_taken": "skipped"}
        else:
            print(f"❌ Action rejected for {profile['name']}")
            return {"current_profile_index": state["current_profile_index"] + 1, "action_taken": "rejected"}
    
    return {"current_profile_index": state["current_profile_index"] + 1, "action_taken": "skipped"}

async def summarize_results_node(state: ProfileAnalysisState) -> Dict:
    """
    Node to generate summary of analysis results.
    """
    print("\n--- NODE: summarize_results_node ---")
    results = state["analysis_results"]
    
    stats = {
        "total_profiles": len(results),
        "messages_sent": sum(1 for r in results if r["action"] == "send_message"),
        "connections_requested": sum(1 for r in results if r["action"] == "send_connection"),
        "skipped": sum(1 for r in results if r["action"] == "skip")
    }
    
    chain = SUMMARIZE_RESULTS_PROMPT | llm
    response = await chain.ainvoke({**stats, "analysis_results": results})
    
    print("\n=== Analysis Summary ===")
    print(response.content)
    
    return {"action_taken": "completed"} 