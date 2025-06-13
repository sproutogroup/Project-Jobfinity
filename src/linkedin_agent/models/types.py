"""
Type definitions for LinkedIn profile data structures.
"""

from typing import TypedDict, List, Dict, Union

class LinkedInProfile(TypedDict):
    """
    Represents a LinkedIn profile with attributes from the original scraper.
    """
    profile_url: str
    name: str
    headline: str
    company: str
    designation: str

class LinkedInAutomationState(TypedDict):
    """
    Represents the state of the automation workflow.
    """
    query: str  # Search query
    profile_urls: set  # Set of profile URLs to process
    current_url_index: int  # Current URL being processed
    profiles_data: List[LinkedInProfile]  # Collected profile data
    error: str  # Error message if any 