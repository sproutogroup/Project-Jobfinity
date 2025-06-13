"""
LangGraph workflow configuration for LinkedIn profile analysis.
"""

from typing import Dict
from langgraph.graph import StateGraph, END

from .states import ProfileAnalysisState
from .nodes import (
    load_profiles_node,
    analyze_profile_node,
    execute_action_node,
    summarize_results_node
)

def create_analysis_workflow() -> StateGraph:
    """
    Creates and configures the profile analysis workflow graph.
    
    Returns:
        StateGraph: Compiled workflow graph
    """
    # Create workflow graph
    workflow = StateGraph(ProfileAnalysisState)

    # Add nodes
    workflow.add_node("load", load_profiles_node)
    workflow.add_node("analyze", analyze_profile_node)
    workflow.add_node("execute", execute_action_node)
    workflow.add_node("summarize", summarize_results_node)

    # Set entry point
    workflow.set_entry_point("load")

    # Add edges
    workflow.add_edge("load", "analyze")

    def route_action(state: ProfileAnalysisState) -> str:
        """Routes workflow based on the action decision."""
        action = state.get("action_taken")
        
        if action == "done_processing":
            return "summarize"
        elif action in ["send_message", "send_connection"]:
            return "execute"
        elif action in ["processed", "skipped", "rejected"]:
            return "analyze"
        elif action == "completed":
            return END
        
        return "analyze"

    # Add conditional edges
    workflow.add_conditional_edges(
        "analyze",
        route_action,
        {
            "execute": "execute",
            "analyze": "analyze",
            "summarize": "summarize",
            END: END
        }
    )

    workflow.add_conditional_edges(
        "execute",
        route_action,
        {
            "analyze": "analyze",
            END: END
        }
    )

    workflow.add_conditional_edges(
        "summarize",
        route_action,
        {
            END: END
        }
    )

    return workflow.compile() 