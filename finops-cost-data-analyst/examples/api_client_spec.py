#!/usr/bin/env python3
"""
FinOps Cost Data Analyst - Spec-Driven API Client

This client uses agent-card.json and a2a-spec.json to:
- Load agent capabilities and intents
- Use request templates from spec
- Validate requests against schema
- Parse responses using spec patterns
"""

import requests
import json
import re
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("⚠️  jsonschema not installed. Request validation disabled.")
    print("   Install: pip install jsonschema")


class FinOpsAgentClient:
    """Spec-driven client for FinOps Cost Data Analyst Agent."""

    def __init__(self, base_url: str = "http://localhost:8000", spec_dir: Optional[str] = None):
        """
        Initialize client by loading agent card and A2A spec.

        Args:
            base_url: Base URL of ADK web server
            spec_dir: Directory containing agent-card.json and a2a-spec.json
                     (defaults to parent directory of this file)
        """
        self.base_url = base_url

        # Auto-detect spec directory
        if spec_dir is None:
            spec_dir = Path(__file__).parent.parent
        else:
            spec_dir = Path(spec_dir)

        # Load agent card
        agent_card_path = spec_dir / "agent-card.json"
        with open(agent_card_path) as f:
            self.agent_card = json.load(f)['agentCard']

        # Load A2A spec
        a2a_spec_path = spec_dir / "a2a-spec.json"
        with open(a2a_spec_path) as f:
            self.a2a_spec = json.load(f)

        # Extract useful info
        self.app_name = self.agent_card['metadata']['name']
        self.intents = self.agent_card['intents']
        self.request_schema = self.agent_card['requestSchema']
        self.templates = self.a2a_spec['templates']

        print(f"✅ Loaded specs for: {self.agent_card['metadata']['displayName']}")
        print(f"   Version: {self.agent_card['metadata']['version']}")
        print(f"   Capabilities: {', '.join(self.agent_card['capabilities']['primary'])}")

    def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return self.agent_card['capabilities']['primary']

    def get_intents(self) -> Dict[str, Any]:
        """Get all supported intents with examples."""
        return self.intents

    def get_intent_examples(self, intent: str) -> List[str]:
        """Get example queries for a specific intent."""
        if intent in self.intents:
            return self.intents[intent]['examples']
        return []

    def build_request(
        self,
        question: str,
        user_id: str = "api-client",
        session_id: Optional[str] = None,
        template: str = "basicQuery"
    ) -> Dict[str, Any]:
        """
        Build request using template from A2A spec.

        Args:
            question: Natural language question
            user_id: Calling agent/user ID
            session_id: Session ID (auto-generated if None)
            template: Template name from a2a-spec.json (default: "basicQuery")

        Returns:
            dict: Complete request payload
        """
        if session_id is None:
            session_id = f"session-{uuid.uuid4()}"

        # Get template from spec
        if template in self.templates:
            template_obj = self.templates[template]['template']
        else:
            # Fallback to basic template
            template_obj = self.templates['basicQuery']['template']

        # Build request from template
        request = {
            "appName": self.app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": question}]
            }
        }

        return request

    def validate_request(self, request: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate request against schema from agent card.

        Args:
            request: Request payload to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        if not HAS_JSONSCHEMA:
            return True, "Validation skipped (jsonschema not installed)"

        try:
            validate(instance=request, schema=self.request_schema)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def _create_session(self, user_id: str) -> str:
        """
        Create a new session.

        Args:
            user_id: User ID for the session

        Returns:
            str: Session ID
        """
        url = f"{self.base_url}/apps/{self.app_name}/users/{user_id}/sessions"
        try:
            response = requests.post(url, json={}, timeout=10)
            response.raise_for_status()
            session_id = response.json()['id']
            return session_id
        except Exception as e:
            raise Exception(f"Failed to create session: {e}")

    def query(
        self,
        question: str,
        user_id: str = "api-client",
        session_id: Optional[str] = None,
        timeout: int = 60,
        validate_request: bool = True
    ) -> Dict[str, Any]:
        """
        Query the agent using spec-driven approach.
        Automatically creates session if not provided.

        Args:
            question: Natural language question
            user_id: Calling agent/user ID
            session_id: Session ID (auto-created if None)
            timeout: Request timeout in seconds
            validate_request: Validate request before sending

        Returns:
            dict: Response with status, answer, and metadata
        """
        # Create session if not provided
        if session_id is None:
            session_id = self._create_session(user_id)

        # Build request from template
        request = self.build_request(question, user_id, session_id)

        # Validate request
        if validate_request:
            is_valid, error = self.validate_request(request)
            if not is_valid:
                return {
                    "status": "error",
                    "error": f"Request validation failed: {error}",
                    "request": request
                }

        # Send request
        try:
            response = requests.post(
                f"{self.base_url}/run",
                json=request,
                timeout=timeout
            )
            response.raise_for_status()

            events = response.json()
            answer = self._extract_answer(events)

            return {
                "status": "success",
                "answer": answer,
                "session_id": request['sessionId'],
                "events": events,
                "request": request
            }

        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "session_id": request['sessionId'],
                "request": request
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": f"Request timeout after {timeout}s",
                "session_id": request['sessionId'],
                "request": request
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "session_id": request.get('sessionId'),
                "request": request
            }

    def _extract_answer(self, events: list) -> str:
        """Extract answer using pattern from A2A spec."""
        for event in events:
            if event.get("type") == "agent_output":
                parts = event.get("content", {}).get("parts", [])
                for part in parts:
                    if "text" in part:
                        return part["text"]
        return "No response from agent"

    def parse_cost(self, text: str) -> Optional[float]:
        """
        Parse dollar amount from text using pattern from A2A spec.

        Args:
            text: Text containing cost (e.g., "$15,234,567.89")

        Returns:
            float: Parsed cost or None
        """
        # Pattern from a2a-spec.json responseHandling
        pattern = self.a2a_spec['responseHandling']['parseStructuredData']['patterns']['currency']
        match = re.search(pattern, text)
        if match:
            return float(match.group(1).replace(',', ''))
        return None

    def parse_percentage(self, text: str) -> Optional[float]:
        """Parse percentage from text."""
        pattern = self.a2a_spec['responseHandling']['parseStructuredData']['patterns']['percentage']
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
        return None

    def parse_ranked_list(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse ranked list from response.

        Args:
            text: Response text with ranked items

        Returns:
            list: Parsed items with rank, name, cost
        """
        pattern = self.a2a_spec['responseHandling']['parseStructuredData']['patterns']['listItems']
        items = []

        for line in text.split('\n'):
            match = re.match(pattern, line)
            if match:
                name = match.group(1)
                cost_str = match.group(2)
                cost = float(cost_str.replace(',', ''))
                items.append({
                    "rank": len(items) + 1,
                    "name": name,
                    "cost": cost
                })

        return items

    def query_from_intent(
        self,
        intent: str,
        example_index: int = 0,
        user_id: str = "api-client",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query using example from agent card for specific intent.

        Args:
            intent: Intent name (e.g., "COST_AGGREGATION")
            example_index: Index of example to use (default: 0)
            user_id: Calling agent ID
            session_id: Session ID

        Returns:
            dict: Response
        """
        if intent not in self.intents:
            return {
                "status": "error",
                "error": f"Unknown intent: {intent}. Available: {list(self.intents.keys())}"
            }

        examples = self.intents[intent]['examples']
        if example_index >= len(examples):
            return {
                "status": "error",
                "error": f"Example index {example_index} out of range (max: {len(examples) - 1})"
            }

        question = examples[example_index]
        return self.query(question, user_id, session_id)

    def get_example_requests(self) -> Dict[str, Any]:
        """Get example requests from agent card."""
        return self.agent_card.get('examples', {})

    def run_example(self, example_name: str) -> Dict[str, Any]:
        """
        Run a predefined example from agent card.

        Args:
            example_name: Example name (e.g., "totalCost", "topApplications")

        Returns:
            dict: Response
        """
        examples = self.get_example_requests()

        if example_name not in examples:
            return {
                "status": "error",
                "error": f"Unknown example: {example_name}. Available: {list(examples.keys())}"
            }

        example = examples[example_name]
        request_template = example['request']

        # Extract question from example
        question = request_template['newMessage']['parts'][0]['text']

        # Note: We don't use the session_id from the template because it's just an example
        # Let query() auto-create a session instead
        return self.query(
            question=question,
            user_id=request_template['userId'],
            session_id=None  # Auto-create session
        )


# Example usage functions using specs

def example_discover_capabilities():
    """Example 1: Discover agent capabilities from spec."""
    print("=" * 60)
    print("Example 1: Discover Agent Capabilities (from spec)")
    print("=" * 60)
    print()

    client = FinOpsAgentClient()

    print("📋 Agent Capabilities:")
    for capability in client.get_capabilities():
        print(f"   - {capability}")

    print()
    print("🎯 Supported Intents:")
    for intent_name, intent_data in client.get_intents().items():
        print(f"   {intent_name}:")
        print(f"      Description: {intent_data['description']}")
        print(f"      Examples:")
        for example in intent_data['examples'][:2]:  # Show first 2
            print(f"         - {example}")
    print()


def example_use_intent():
    """Example 2: Query using intent from spec."""
    print("=" * 60)
    print("Example 2: Query Using Intent (from spec)")
    print("=" * 60)
    print()

    client = FinOpsAgentClient()

    # Get example question from COST_AGGREGATION intent
    intent = "COST_AGGREGATION"
    examples = client.get_intent_examples(intent)

    print(f"📌 Using example from {intent} intent:")
    print(f"   Question: {examples[0]}")
    print()

    result = client.query_from_intent(intent, example_index=0)

    if result['status'] == 'success':
        print(f"✅ Success!")
        print(f"\nAnswer:\n{result['answer']}")

        # Parse cost using spec pattern
        cost = client.parse_cost(result['answer'])
        if cost:
            print(f"\n💰 Parsed cost: ${cost:,.2f}")
    else:
        print(f"❌ Error: {result['error']}")

    print()


def example_run_predefined():
    """Example 3: Run predefined example from agent card."""
    print("=" * 60)
    print("Example 3: Run Predefined Example (from agent card)")
    print("=" * 60)
    print()

    client = FinOpsAgentClient()

    # List available examples
    examples = client.get_example_requests()
    print("📚 Available Examples:")
    for name in examples.keys():
        print(f"   - {name}")
    print()

    # Run "totalCost" example
    print("🚀 Running 'totalCost' example...")
    result = client.run_example("totalCost")

    if result['status'] == 'success':
        print(f"✅ Success!")
        print(f"\nAnswer:\n{result['answer']}")
    else:
        print(f"❌ Error: {result['error']}")

    print()


def example_validate_request():
    """Example 4: Validate request using schema."""
    print("=" * 60)
    print("Example 4: Request Validation (using schema from spec)")
    print("=" * 60)
    print()

    client = FinOpsAgentClient()

    # Build valid request
    valid_request = client.build_request(
        question="What is the total cost?",
        user_id="test-agent"
    )

    print("✅ Validating VALID request:")
    is_valid, error = client.validate_request(valid_request)
    print(f"   Result: {'✅ VALID' if is_valid else f'❌ INVALID: {error}'}")
    print()

    # Build invalid request (missing required field)
    invalid_request = {
        "appName": "finops-cost-data-analyst",
        "userId": "test-agent"
        # Missing sessionId and newMessage
    }

    print("❌ Validating INVALID request:")
    is_valid, error = client.validate_request(invalid_request)
    print(f"   Result: {'✅ VALID' if is_valid else f'❌ INVALID'}")
    if error:
        print(f"   Error: {error}")
    print()


def example_parse_response():
    """Example 5: Parse structured data from response."""
    print("=" * 60)
    print("Example 5: Parse Response (using patterns from spec)")
    print("=" * 60)
    print()

    client = FinOpsAgentClient()

    # Query for ranked list
    result = client.query("What are the top 5 applications by cost?")

    if result['status'] == 'success':
        print(f"✅ Success!")
        print(f"\nRaw Answer:\n{result['answer'][:200]}...")
        print()

        # Parse ranked list using spec pattern
        items = client.parse_ranked_list(result['answer'])

        if items:
            print("📊 Parsed Ranked List:")
            for item in items:
                print(f"   {item['rank']}. {item['name']:30} ${item['cost']:,.2f}")
        else:
            print("⚠️  Could not parse ranked list")
    else:
        print(f"❌ Error: {result['error']}")

    print()


def main():
    """Run all spec-driven examples."""
    print("\n" + "=" * 60)
    print("FinOps Agent - Spec-Driven API Client Examples")
    print("=" * 60)
    print()

    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/list-apps", timeout=2)
        response.raise_for_status()
    except Exception:
        print("❌ Error: ADK Web Server not running!")
        print()
        print("Start the server first:")
        print("  cd /Users/gurukallam/projects/google-adk-agents")
        print("  adk web --port 8000")
        print()
        return

    print(f"✅ Server is running")
    print()

    # Run examples
    try:
        example_discover_capabilities()
        example_use_intent()
        example_run_predefined()
        example_validate_request()
        example_parse_response()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    print("=" * 60)
    print("All examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
