"""
Module: utils.py
Description:
    Provides utility functions for mathematical calculations, vector operations, and geometry.
    These are pure functions with no heavy dependencies on the game state.

Implementation Details:
    - Euclidean distance calculation.
    - Vector normalization, addition, subtraction, scaling.
    - Random position generation within bounds.

Dependencies:
    - Imports: math, random.
    - Used By: entities.py (movement logic), environment.py (resource spawning), main.py (checks).
"""

import math
import random
from typing import Tuple


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.

    Args:
        p1: First point (x, y)
        p2: Second point (x, y)

    Returns:
        Distance between the points
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def normalize(v: Tuple[float, float]) -> Tuple[float, float]:
    """
    Normalize a vector to unit length.

    Args:
        v: Vector (x, y)

    Returns:
        Normalized vector, or (0, 0) if magnitude is zero
    """
    magnitude = math.sqrt(v[0] * v[0] + v[1] * v[1])
    if magnitude == 0:
        return (0.0, 0.0)
    return (v[0] / magnitude, v[1] / magnitude)


def add(v1: Tuple[float, float], v2: Tuple[float, float]) -> Tuple[float, float]:
    """
    Add two vectors.

    Args:
        v1: First vector (x, y)
        v2: Second vector (x, y)

    Returns:
        Sum of vectors
    """
    return (v1[0] + v2[0], v1[1] + v2[1])


def sub(v1: Tuple[float, float], v2: Tuple[float, float]) -> Tuple[float, float]:
    """
    Subtract second vector from first.

    Args:
        v1: First vector (x, y)
        v2: Second vector (x, y)

    Returns:
        Difference of vectors (v1 - v2)
    """
    return (v1[0] - v2[0], v1[1] - v2[1])


def scale(v: Tuple[float, float], s: float) -> Tuple[float, float]:
    """
    Scale a vector by a scalar.

    Args:
        v: Vector (x, y)
        s: Scalar multiplier

    Returns:
        Scaled vector
    """
    return (v[0] * s, v[1] * s)


def random_position(bounds: Tuple[int, int, int, int]) -> Tuple[float, float]:
    """
    Generate a random position within specified bounds.

    Args:
        bounds: (min_x, min_y, max_x, max_y)

    Returns:
        Random position (x, y) within bounds
    """
    min_x, min_y, max_x, max_y = bounds
    x = random.uniform(min_x, max_x)
    y = random.uniform(min_y, max_y)
    return (x, y)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between minimum and maximum.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))
