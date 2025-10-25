#!/usr/bin/env python3
"""
FinOps Cost Data Analyst - API Client Example

This script demonstrates how to interact with the FinOps agent via REST API.
Use this for agent-to-agent (A2A) communication or external integrations.
"""

import requests
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime


class FinOpsAgentClient:
    """Client for FinOps Cost Data Analyst Agent API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of ADK web server (default: http://localhost:8000)
        """
        self.base_url = base_url
        self.app_name = "finops-cost-data-analyst"

    def query(
        self,
        question: str,
        user_id: str = "api-client",
        session_id: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Query the FinOps agent.

        Args:
            question: The cost analysis question to ask
            user_id: Unique user identifier
            session_id: Session ID for conversation context (auto-generated if None)
            timeout: Request timeout in seconds

        Returns:
            dict: Response with status and data/error

        Example:
            >>> client = FinOpsAgentClient()
            >>> result = client.query("What is the total cost for FY26?")
            >>> if result['status'] == 'success':
            >>>     print(result['answer'])
        """
        if session_id is None:
            session_id = f"session-{uuid.uuid4()}"

        payload = {
            "appName": self.app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": question}]
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/run",
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()

            events = response.json()
            answer = self._extract_answer(events)

            return {
                "status": "success",
                "answer": answer,
                "session_id": session_id,
                "events": events
            }

        except requests.exceptions.HTTPError as e:
            return {
                "status": "error",
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "session_id": session_id
            }

        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": f"Request timeout after {timeout}s",
                "session_id": session_id
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id
            }

    def _extract_answer(self, events: list) -> str:
        """Extract agent's answer from event stream."""
        for event in events:
            if event.get("type") == "agent_output":
                parts = event.get("content", {}).get("parts", [])
                for part in parts:
                    if "text" in part:
                        return part["text"]
        return "No response from agent"

    def list_agents(self) -> list:
        """List all available agents on the server."""
        try:
            response = requests.get(f"{self.base_url}/list-apps")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Example usage functions

def example_simple_query():
    """Example 1: Simple cost query."""
    print("=" * 60)
    print("Example 1: Simple Cost Query")
    print("=" * 60)

    client = FinOpsAgentClient()
    result = client.query("What is the total cost for FY26?")

    if result['status'] == 'success':
        print(f"\n✅ Success!")
        print(f"\nQuestion: What is the total cost for FY26?")
        print(f"\nAnswer:\n{result['answer']}")
    else:
        print(f"\n❌ Error: {result['error']}")

    print()


def example_top_applications():
    """Example 2: Top applications query."""
    print("=" * 60)
    print("Example 2: Top Applications Query")
    print("=" * 60)

    client = FinOpsAgentClient()
    result = client.query("What are the top 5 applications by cost?")

    if result['status'] == 'success':
        print(f"\n✅ Success!")
        print(f"\nQuestion: What are the top 5 applications by cost?")
        print(f"\nAnswer:\n{result['answer']}")
    else:
        print(f"\n❌ Error: {result['error']}")

    print()


def example_conversation():
    """Example 3: Multi-turn conversation using same session."""
    print("=" * 60)
    print("Example 3: Multi-Turn Conversation")
    print("=" * 60)

    client = FinOpsAgentClient()

    # First query - creates session
    print("\n[Query 1]")
    result1 = client.query("What is the total cost for FY26?")

    if result1['status'] == 'success':
        session_id = result1['session_id']
        print(f"Session: {session_id}")
        print(f"Answer: {result1['answer'][:100]}...")

        # Second query - uses same session for context
        print("\n[Query 2 - Same Session]")
        result2 = client.query(
            "Break that down by cloud provider",
            session_id=session_id
        )

        if result2['status'] == 'success':
            print(f"Session: {result2['session_id']}")
            print(f"Answer: {result2['answer'][:100]}...")
        else:
            print(f"❌ Error: {result2['error']}")
    else:
        print(f"❌ Error: {result1['error']}")

    print()


def example_a2a_communication():
    """Example 4: Agent-to-Agent communication pattern."""
    print("=" * 60)
    print("Example 4: Agent-to-Agent Communication")
    print("=" * 60)

    class BudgetAnalysisAgent:
        """Example: Another agent that calls FinOps Agent."""

        def __init__(self):
            self.finops_client = FinOpsAgentClient()

        def analyze_spending(self, user_id: str) -> Dict[str, Any]:
            """Analyze spending by querying FinOps agent."""
            print(f"\n[Budget Agent] Analyzing spending for user: {user_id}")

            # Query 1: Get total cost
            print("[Budget Agent] → Querying FinOps Agent: Total cost")
            result1 = self.finops_client.query(
                "What is the total cost for FY26?",
                user_id=f"budget-agent-{user_id}"
            )

            if result1['status'] != 'success':
                return {"error": result1['error']}

            print(f"[Budget Agent] ← FinOps Agent response received")
            print(f"   {result1['answer'][:80]}...")

            # Query 2: Get top applications
            print("\n[Budget Agent] → Querying FinOps Agent: Top applications")
            result2 = self.finops_client.query(
                "What are the top 3 applications by cost?",
                user_id=f"budget-agent-{user_id}"
            )

            if result2['status'] != 'success':
                return {"error": result2['error']}

            print(f"[Budget Agent] ← FinOps Agent response received")
            print(f"   {result2['answer'][:80]}...")

            return {
                "status": "success",
                "total_cost_analysis": result1['answer'],
                "top_applications": result2['answer'],
                "timestamp": datetime.now().isoformat()
            }

    # Simulate another agent calling FinOps agent
    budget_agent = BudgetAnalysisAgent()
    analysis = budget_agent.analyze_spending(user_id="john-doe")

    print("\n[Budget Agent] Final Analysis:")
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
    else:
        print(f"✅ Analysis complete at {analysis['timestamp']}")

    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("FinOps Cost Data Analyst - API Client Examples")
    print("=" * 60)
    print()

    # Check if server is running
    client = FinOpsAgentClient()
    agents = client.list_agents()

    if isinstance(agents, dict) and agents.get("status") == "error":
        print("❌ Error: ADK Web Server not running!")
        print()
        print("Start the server first:")
        print("  cd /Users/gurukallam/projects/google-adk-agents")
        print("  adk web --port 8000")
        print()
        return

    print(f"✅ Server is running")
    print(f"Available agents: {agents}")
    print()

    # Run examples
    try:
        example_simple_query()
        example_top_applications()
        example_conversation()
        example_a2a_communication()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    print("=" * 60)
    print("All examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
