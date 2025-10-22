"""Calculator tool for basic arithmetic operations."""

from typing import Dict, Union


def calculate(operation: str, num1: float, num2: float) -> Dict[str, Union[str, float]]:
    """Performs basic arithmetic operations.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        num1: First number
        num2: Second number

    Returns:
        A dictionary containing the calculation result.
    """
    operations = {
        "add": num1 + num2,
        "subtract": num1 - num2,
        "multiply": num1 * num2,
        "divide": num1 / num2 if num2 != 0 else "Error: Division by zero"
    }

    result = operations.get(operation.lower(), "Error: Invalid operation")

    return {
        "status": "success" if isinstance(result, (int, float)) else "error",
        "operation": operation,
        "num1": num1,
        "num2": num2,
        "result": result,
        "message": f"{num1} {operation} {num2} = {result}"
    }
