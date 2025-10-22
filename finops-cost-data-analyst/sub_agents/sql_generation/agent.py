"""SQL Generation Agent - converts natural language to SQL.

This agent generates BigQuery SQL from user questions.
NO TOOLS NEEDED - schema is hardcoded for performance.
"""

import os
from google.adk.agents import LlmAgent
from google.genai import types

from prompts import get_sql_generation_prompt


# Create the agent instance
sql_generation_agent = LlmAgent(
    model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.0-flash-exp"),
    name="sql_generation",
    instruction=get_sql_generation_prompt(),
    # No tools - schema is hardcoded in prompt
    generate_content_config=types.GenerateContentConfig(
        temperature=0.01,  # Very low for deterministic SQL generation
    ),
)
