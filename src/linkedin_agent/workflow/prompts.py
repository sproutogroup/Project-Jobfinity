"""
Prompt templates for LLM interactions in the workflow.
"""

from langchain_core.prompts import ChatPromptTemplate

ANALYZE_PROFILE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant analyzing LinkedIn profiles for potential business opportunities.
    Based on the profile information, decide if this person would be a good fit for outreach.
    If yes, suggest either 'send_message' or 'send_connection' and generate a personalized message.
    If no, suggest 'skip'.
    
    Respond ONLY in the format:
    ACTION: <action_type>
    REASON: <brief reason for your decision>
    MESSAGE: <your_personalized_message>
    
    Keep messages professional and concise (max 150 words).
    """),
    ("user", """Profile Information:
    Name: {name}
    Headline: {headline}
    Company: {company}
    Designation: {designation}
    
    Based on this information, what action should be taken?""")
])

SUMMARIZE_RESULTS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an AI assistant summarizing the results of LinkedIn profile analysis.
    Create a concise summary of the profiles analyzed and actions taken.
    Include key statistics and any notable patterns or insights found.
    """),
    ("user", """Analysis Results:
    {analysis_results}
    
    Total Profiles: {total_profiles}
    Messages Sent: {messages_sent}
    Connections Requested: {connections_requested}
    Skipped: {skipped}
    
    Please provide a summary of the results.""")
]) 