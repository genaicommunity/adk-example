"""Insight Synthesizer Agent implementation - formats results into insights.

This sub-agent transforms raw query results into business insights.

Architecture:
    Root Agent → Insight Synthesizer Sub-Agent (no tools needed)
"""

import os
from google.adk.agents import LlmAgent
from google.genai import types

# Import centralized prompts
from PROMPT_INSTRUCTION import get_insight_synthesizer_instruction


def get_insight_synthesizer_agent() -> LlmAgent:
    """Create and return the Insight Synthesizer agent.

    This agent does NOT use tools - it formats query results into insights.

    Critical: Uses very low temperature (0.1) to prevent data hallucination.
    The agent must report exact numbers from query results.

    Returns:
        LlmAgent configured for insight synthesis
    """

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="insight_synthesizer",
        instruction=get_insight_synthesizer_instruction(),
        # No tools needed - just formatting
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,  # Very low for data accuracy - no hallucinations
        ),
    )

    return agent
