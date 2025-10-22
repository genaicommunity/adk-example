"""Insight Synthesis Agent - formats results into business insights.

This agent transforms raw query results into insights.
NO TOOLS NEEDED - just text formatting.
"""

import os
from google.adk.agents import LlmAgent
from google.genai import types

from prompts import INSIGHT_SYNTHESIS_PROMPT


# Create the agent instance
insight_synthesis_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="insight_synthesis",
    instruction=INSIGHT_SYNTHESIS_PROMPT,
    # No tools needed - just formatting
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,  # Very low for data accuracy - no hallucinations
    ),
)
