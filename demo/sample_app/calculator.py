"""Sample buggy calculator application with intentional bugs for investigation."""

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

def divide(a: float, b: float) -> float:
    """Divide a by b.
    
    BUG ALERT: Uses integer floor division `//` instead of float division `/`.
    This causes fractional truncation (e.g., 10 / 3 gives 3 instead of 3.3333).
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a // b

def calculate_average(numbers: list[float]) -> float:
    """Calculate the average of a list of numbers using divide()."""
    if not numbers:
        return 0.0
    total = sum(numbers)
    return divide(total, len(numbers))
