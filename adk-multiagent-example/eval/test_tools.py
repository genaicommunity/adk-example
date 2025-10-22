"""Unit tests for tools.

Run with: python -m pytest eval/test_tools.py -v
Or: python eval/test_tools.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import get_current_time, get_weather, calculate


def test_get_current_time():
    """Test the time tool."""
    print("\n🧪 Testing get_current_time...")

    # Test basic functionality
    result = get_current_time("Tokyo")
    assert result["status"] == "success"
    assert result["city"] == "Tokyo"
    assert "time" in result
    assert "message" in result
    print(f"  ✓ Result: {result['message']}")

    # Test different cities
    cities = ["London", "New York", "Paris"]
    for city in cities:
        result = get_current_time(city)
        assert result["status"] == "success"
        assert result["city"] == city
        print(f"  ✓ {city}: {result['time']}")

    print("  ✅ get_current_time tests passed!")


def test_get_weather():
    """Test the weather tool."""
    print("\n🧪 Testing get_weather...")

    # Test basic functionality
    result = get_weather("London")
    assert result["status"] == "success"
    assert result["city"] == "London"
    assert "condition" in result
    assert "temperature" in result
    assert "message" in result
    print(f"  ✓ Result: {result['message']}")

    # Test multiple calls (should give random results)
    cities = ["Paris", "Tokyo", "Sydney"]
    for city in cities:
        result = get_weather(city)
        assert result["status"] == "success"
        print(f"  ✓ {city}: {result['condition']}, {result['temperature']}")

    print("  ✅ get_weather tests passed!")


def test_calculate():
    """Test the calculator tool."""
    print("\n🧪 Testing calculate...")

    # Test addition
    result = calculate("add", 5, 3)
    assert result["status"] == "success"
    assert result["result"] == 8
    print(f"  ✓ Addition: {result['message']}")

    # Test subtraction
    result = calculate("subtract", 10, 4)
    assert result["status"] == "success"
    assert result["result"] == 6
    print(f"  ✓ Subtraction: {result['message']}")

    # Test multiplication
    result = calculate("multiply", 7, 6)
    assert result["status"] == "success"
    assert result["result"] == 42
    print(f"  ✓ Multiplication: {result['message']}")

    # Test division
    result = calculate("divide", 20, 4)
    assert result["status"] == "success"
    assert result["result"] == 5
    print(f"  ✓ Division: {result['message']}")

    # Test division by zero
    result = calculate("divide", 10, 0)
    assert result["status"] == "error"
    assert result["result"] == "Error: Division by zero"
    print(f"  ✓ Division by zero handled: {result['message']}")

    # Test invalid operation
    result = calculate("invalid", 5, 3)
    assert result["status"] == "error"
    print(f"  ✓ Invalid operation handled: {result['message']}")

    print("  ✅ calculate tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING TOOLS")
    print("=" * 60)

    test_get_current_time()
    test_get_weather()
    test_calculate()

    print("\n" + "=" * 60)
    print("✅ ALL TOOL TESTS PASSED!")
    print("=" * 60)
