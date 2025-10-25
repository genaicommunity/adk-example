#!/usr/bin/env python3
"""
Spec Utilities - Helper functions for working with agent-card.json and a2a-spec.json

This module provides utilities for:
- Loading and browsing specs
- Generating requests from templates
- Validating requests
- Parsing responses
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_specs(spec_dir: Optional[str] = None) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Load agent card and A2A spec.

    Args:
        spec_dir: Directory containing spec files (auto-detected if None)

    Returns:
        tuple: (agent_card, a2a_spec)
    """
    if spec_dir is None:
        spec_dir = Path(__file__).parent.parent
    else:
        spec_dir = Path(spec_dir)

    agent_card_path = spec_dir / "agent-card.json"
    a2a_spec_path = spec_dir / "a2a-spec.json"

    with open(agent_card_path) as f:
        agent_card = json.load(f)['agentCard']

    with open(a2a_spec_path) as f:
        a2a_spec = json.load(f)

    return agent_card, a2a_spec


def show_agent_info(agent_card: Dict[str, Any]):
    """Display agent metadata."""
    metadata = agent_card['metadata']

    print("=" * 60)
    print(f"Agent: {metadata['displayName']}")
    print("=" * 60)
    print(f"Name:        {metadata['name']}")
    print(f"Version:     {metadata['version']}")
    print(f"Description: {metadata['description']}")
    print(f"Tags:        {', '.join(metadata['tags'])}")
    print()


def show_capabilities(agent_card: Dict[str, Any]):
    """Display agent capabilities."""
    print("Capabilities:")
    for cap in agent_card['capabilities']['primary']:
        print(f"  - {cap}")
    print()


def show_intents(agent_card: Dict[str, Any], verbose: bool = False):
    """Display supported intents."""
    print("Supported Intents:")
    for intent_name, intent_data in agent_card['intents'].items():
        print(f"\n  {intent_name}:")
        print(f"    Description: {intent_data['description']}")
        print(f"    Output Type: {intent_data['outputType']}")

        if verbose:
            print(f"    Examples:")
            for example in intent_data['examples']:
                print(f"      - {example}")
    print()


def show_templates(a2a_spec: Dict[str, Any]):
    """Display available request templates."""
    print("Request Templates:")
    for template_name, template_data in a2a_spec['templates'].items():
        print(f"\n  {template_name}:")
        print(f"    Description: {template_data['description']}")

        if 'queryTemplates' in template_data:
            print(f"    Query Templates:")
            for qt_name, qt_value in template_data['queryTemplates'].items():
                print(f"      - {qt_name}: {qt_value}")
    print()


def show_use_cases(a2a_spec: Dict[str, Any]):
    """Display use cases."""
    print("Use Cases:")
    for use_case_name, use_case_data in a2a_spec['useCases'].items():
        print(f"\n  {use_case_name}:")
        print(f"    Scenario: {use_case_data['scenario']}")
        print(f"    Steps: {len(use_case_data['workflow'])}")
    print()


def show_examples(agent_card: Dict[str, Any]):
    """Display predefined examples."""
    print("Predefined Examples:")
    for example_name, example_data in agent_card.get('examples', {}).items():
        print(f"\n  {example_name}:")
        print(f"    Intent: {example_data['intent']}")
        print(f"    Description: {example_data['description']}")
        question = example_data['request']['newMessage']['parts'][0]['text']
        print(f"    Question: {question}")
    print()


def get_template(a2a_spec: Dict[str, Any], template_name: str = "basicQuery") -> Dict[str, Any]:
    """
    Get request template.

    Args:
        a2a_spec: A2A specification
        template_name: Template name (default: "basicQuery")

    Returns:
        dict: Template object
    """
    return a2a_spec['templates'].get(template_name, {}).get('template', {})


def get_query_template(a2a_spec: Dict[str, Any], query_template_name: str) -> str:
    """
    Get parameterized query template.

    Args:
        a2a_spec: A2A specification
        query_template_name: Query template name

    Returns:
        str: Query template with placeholders
    """
    templates = a2a_spec['templates']['parameterizedQuery'].get('queryTemplates', {})
    return templates.get(query_template_name, "")


def generate_request(
    a2a_spec: Dict[str, Any],
    agent_name: str,
    question: str,
    user_id: str,
    session_id: str,
    template_name: str = "basicQuery"
) -> Dict[str, Any]:
    """
    Generate request from template.

    Args:
        a2a_spec: A2A specification
        agent_name: Agent identifier
        question: Natural language question
        user_id: Calling agent/user ID
        session_id: Session ID
        template_name: Template to use

    Returns:
        dict: Complete request payload
    """
    template = get_template(a2a_spec, template_name)

    return {
        "appName": agent_name,
        "userId": user_id,
        "sessionId": session_id,
        "newMessage": {
            "role": "user",
            "parts": [{"text": question}]
        }
    }


def main():
    """Main CLI for exploring specs."""
    import sys

    # Load specs
    agent_card, a2a_spec = load_specs()

    # Parse command
    if len(sys.argv) < 2:
        command = "info"
    else:
        command = sys.argv[1]

    # Execute command
    if command == "info":
        show_agent_info(agent_card)
        show_capabilities(agent_card)
        show_intents(agent_card, verbose=False)

    elif command == "intents":
        show_intents(agent_card, verbose=True)

    elif command == "templates":
        show_templates(a2a_spec)

    elif command == "usecases":
        show_use_cases(a2a_spec)

    elif command == "examples":
        show_examples(agent_card)

    elif command == "all":
        show_agent_info(agent_card)
        show_capabilities(agent_card)
        show_intents(agent_card, verbose=True)
        show_templates(a2a_spec)
        show_use_cases(a2a_spec)
        show_examples(agent_card)

    else:
        print(f"Unknown command: {command}")
        print()
        print("Usage: python3 spec_utils.py [command]")
        print()
        print("Commands:")
        print("  info       - Show agent metadata and capabilities (default)")
        print("  intents    - Show all intents with examples")
        print("  templates  - Show request templates")
        print("  usecases   - Show use cases")
        print("  examples   - Show predefined examples")
        print("  all        - Show everything")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
