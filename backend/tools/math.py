
import math

# ---------------------------
# Basic arithmetic functions
# ---------------------------


def addition(a: float, b: float) -> float:
    """Add two numbers : a+b"""
    print("[TOOL] ADDITION invoked")
    return a + b


def subtraction(a: float, b: float) -> float:
    """Subtract b from a."""
    print("[TOOL] SUBTRACTION invoked")
    return a - b


def multiplication(a: float, b: float) -> float:
    """Multiply two numbers. : a x b"""
    print("[TOOL] MULTIPLICATION invoked")
    return a * b


def division(a: float, b: float) -> float:
    """Divide a by b """
    print("[TOOL] DIVISION invoked")
    if b == 0:
        return float('inf')
    return a / b


def power(a: float, b: float) -> float:
    """Raise a to the power of b."""
    print("[TOOL] POWER invoked")
    return math.pow(a, b)


def square_root(a: float, _: float = 0) -> float:
    """Compute the square root of a. Second argument ignored."""
    print("[TOOL] SQUARE_ROOT invoked")
    if a < 0:
        return float('nan')
    return math.sqrt(a)


def percentage(a: float, b: float) -> float:
    """Compute what percentage a is of b."""
    print("[TOOL] PERCENTAGE invoked")
    if b == 0:
        return float('inf')
    return (a / b) * 100


# ---------------------------
# Unified calculator
# ---------------------------

def calculator(a: float, b: float, operation: str) -> float:
    """
    Unified calculator interface for basic operations.

    Args:
        a (float): First number.
        b (float): Second number (ignored for unary operations like 'sqrt').
        operation (str): Operation ('add','sub','mul','div','pow','percent','sqrt').

    Returns:
        float: Computed result.
    """
    print("[TOOL] CALCULATOR invoked")
    ops = {
        'add': addition,
        'sub': subtraction,
        'mul': multiplication,
        'div': division,
        'pow': power,
        'percent': percentage,
        'sqrt': square_root
    }

    op_func = ops.get(operation.lower())
    if not op_func:
        raise ValueError(
            f"Unsupported operation: {operation}. Supported: {list(ops.keys())}"
        )

    return op_func(a, b)
