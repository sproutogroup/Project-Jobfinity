"""
State definitions for the LinkedIn agent workflow.
"""

from typing import TypedDict, List, Dict, Union

class ProfileAnalysisState(TypedDict):
    """State for profile analysis workflow."""
    profiles_data: List[Dict]  # List of profiles from JSON
    current_profile_index: int  # Current profile being processed
    analysis_results: List[Dict]  # Analysis results for each profile
    action_taken: str  # Current action status
    error: str  # Error message if any
    current_profile: Union[Dict, None]  # Current profile being analyzed
    message_to_send: str  # Generated message if any 