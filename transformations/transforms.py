"""
2D Transformation matrices implemented manually using numpy.
All transformations use homogeneous coordinates (3x3 matrices).
"""

import numpy as np
import math


def identity():
    return np.eye(3, dtype=float)


def translation_matrix(tx, ty):
    m = np.eye(3, dtype=float)
    m[0, 2] = tx
    m[1, 2] = ty
    return m


def rotation_matrix(angle_deg, cx=0.0, cy=0.0):
    """Rotation around pivot (cx, cy)."""
    angle = math.radians(angle_deg)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    # Translate to origin, rotate, translate back
    t1 = translation_matrix(-cx, -cy)
    r = np.array([
        [cos_a, -sin_a, 0],
        [sin_a,  cos_a, 0],
        [0,      0,     1]
    ], dtype=float)
    t2 = translation_matrix(cx, cy)
    return t2 @ r @ t1


def scaling_matrix(sx, sy, cx=0.0, cy=0.0):
    """Scaling around pivot (cx, cy)."""
    t1 = translation_matrix(-cx, -cy)
    s = np.array([
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ], dtype=float)
    t2 = translation_matrix(cx, cy)
    return t2 @ s @ t1


def reflection_matrix(axis="x", cx=0.0, cy=0.0):
    """Reflection across 'x', 'y', 'origin', or 'y=x'."""
    t1 = translation_matrix(-cx, -cy)
    t2 = translation_matrix(cx, cy)

    if axis == "x":
        r = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]], dtype=float)
    elif axis == "y":
        r = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float)
    elif axis == "origin":
        r = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]], dtype=float)
    elif axis == "y=x":
        r = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 1]], dtype=float)
    elif axis == "y=-x":
        r = np.array([[0, -1, 0], [-1, 0, 0], [0, 0, 1]], dtype=float)
    else:
        r = np.eye(3, dtype=float)

    return t2 @ r @ t1


def shearing_matrix(shx=0.0, shy=0.0):
    """Shearing in x and/or y direction."""
    return np.array([
        [1,   shx, 0],
        [shy, 1,   0],
        [0,   0,   1]
    ], dtype=float)


def apply_transform(points, matrix):
    """
    Apply 3x3 homogeneous matrix to list of (x, y) points.
    Returns transformed list of (x, y) points.
    """
    if not points:
        return []
    pts = np.array([[p[0], p[1], 1.0] for p in points], dtype=float)
    transformed = (matrix @ pts.T).T
    return [(p[0], p[1]) for p in transformed]


def combine_transforms(matrices):
    """Combine a sequence of transformation matrices (left to right application)."""
    result = np.eye(3, dtype=float)
    for m in matrices:
        result = m @ result
    return result


def matrix_to_display(matrix):
    """Format matrix for display in UI."""
    rows = []
    for row in matrix:
        rows.append([f"{v:.3f}" for v in row])
    return rows


class TransformHistory:
    """Tracks transformation history for an object."""

    def __init__(self):
        self.steps = []  # list of (label, matrix)
        self.cumulative = np.eye(3, dtype=float)

    def add(self, label, matrix):
        self.steps.append((label, matrix.copy()))
        self.cumulative = matrix @ self.cumulative

    def clear(self):
        self.steps = []
        self.cumulative = np.eye(3, dtype=float)

    def get_combined(self):
        return self.cumulative.copy()

    def undo(self):
        if self.steps:
            self.steps.pop()
            self.cumulative = np.eye(3, dtype=float)
            for _, m in self.steps:
                self.cumulative = m @ self.cumulative
