"""Insight Synthesizer Agent implementation."""

import os
from google.adk.agents import LlmAgent
from google.genai import types
from .prompts import INSIGHT_SYNTHESIZER_INSTRUCTION


def get_insight_synthesizer_agent() -> LlmAgent:
    """Create and return the Insight Synthesizer agent."""

    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
        name="insight_synthesizer",
        instruction=INSIGHT_SYNTHESIZER_INSTRUCTION,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1,  # Very low for data accuracy - no hallucinations
        ),
    )

    return agent
