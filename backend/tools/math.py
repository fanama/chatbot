import logging
import math

logger = logging.getLogger(__name__)

# ---------------------------
# Basic arithmetic functions
# ---------------------------


def addition(a: float, b: float) -> float:
    """Add two numbers : a+b"""
    logger.debug("[TOOL] ADDITION invoked")
    return a + b


def subtraction(a: float, b: float) -> float:
    """Subtract b from a."""
    logger.debug("[TOOL] SUBTRACTION invoked")
    return a - b


def multiplication(a: float, b: float) -> float:
    """Multiply two numbers. : a x b"""
    logger.debug("[TOOL] MULTIPLICATION invoked")
    return a * b


def division(a: float, b: float) -> float:
    """Divide a by b"""
    logger.debug("[TOOL] DIVISION invoked")
    # `float('inf')` used to be returned here. Infinity is not valid JSON and
    # poisons the agent transcript, so the tool now reports the problem.
    if b == 0:
        raise ValueError("Division by zero is undefined")
    return a / b


def power(a: float, b: float) -> float:
    """Raise a to the power of b."""
    logger.debug("[TOOL] POWER invoked")
    return math.pow(a, b)


def square_root(a: float, _: float = 0) -> float:
    """Compute the square root of a. Second argument ignored."""
    logger.debug("[TOOL] SQUARE_ROOT invoked")
    if a < 0:
        raise ValueError(f"Cannot compute the square root of {a}")
    return math.sqrt(a)


def percentage(a: float, b: float) -> float:
    """Compute what percentage a is of b."""
    logger.debug("[TOOL] PERCENTAGE invoked")
    if b == 0:
        raise ValueError("Cannot compute a percentage of zero")
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
    logger.debug("[TOOL] CALCULATOR invoked: %s %s %s", a, b, operation)
    ops = {
        'add': addition,
        'sub': subtraction,
        'mul': multiplication,
        'div': division,
        'pow': power,
        'percent': percentage,
        'sqrt': square_root
    }

    op_func = ops.get(str(operation).lower())
    if not op_func:
        raise ValueError(
            f"Unsupported operation: {operation}. Supported: {list(ops.keys())}"
        )

    return op_func(a, b)
