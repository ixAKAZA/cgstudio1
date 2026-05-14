"""
Curve implementations:
- Bezier curves (arbitrary degree via de Casteljau)
- B-Spline curves (uniform, clamped)
"""

import numpy as np
import math


def de_casteljau(control_points, t):
    """
    Evaluate Bezier curve at parameter t using de Casteljau's algorithm.
    Returns point and intermediate points for visualization.
    """
    pts = [list(p) for p in control_points]
    levels = [[(p[0], p[1]) for p in pts]]

    while len(pts) > 1:
        new_pts = []
        for i in range(len(pts) - 1):
            x = (1 - t) * pts[i][0] + t * pts[i + 1][0]
            y = (1 - t) * pts[i][1] + t * pts[i + 1][1]
            new_pts.append([x, y])
        pts = new_pts
        levels.append([(p[0], p[1]) for p in pts])

    return (pts[0][0], pts[0][1]), levels


def bezier_curve(control_points, num_samples=200):
    """
    Generate Bezier curve points via de Casteljau.
    Returns list of (x, y) points on the curve.
    """
    if len(control_points) < 2:
        return []

    curve_points = []
    for i in range(num_samples + 1):
        t = i / num_samples
        pt, _ = de_casteljau(control_points, t)
        curve_points.append(pt)
    return curve_points


def bezier_tangent(control_points, t):
    """Compute tangent direction at parameter t."""
    n = len(control_points) - 1
    if n == 0:
        return (0, 0)

    # Derivative control points
    d_pts = []
    for i in range(n):
        dx = n * (control_points[i + 1][0] - control_points[i][0])
        dy = n * (control_points[i + 1][1] - control_points[i][1])
        d_pts.append((dx, dy))

    if len(d_pts) == 1:
        return d_pts[0]

    pt, _ = de_casteljau(d_pts, t)
    return pt


# B-Spline

def _bspline_basis(i, k, t, knots):
    """Cox-de Boor recursion for B-spline basis functions."""
    if k == 1:
        if knots[i] <= t < knots[i + 1]:
            return 1.0
        elif t == knots[-1] and knots[i] <= t <= knots[i + 1]:
            return 1.0
        return 0.0

    denom1 = knots[i + k - 1] - knots[i]
    denom2 = knots[i + k] - knots[i + 1]

    term1 = 0.0
    if denom1 != 0:
        term1 = ((t - knots[i]) / denom1) * _bspline_basis(i, k - 1, t, knots)

    term2 = 0.0
    if denom2 != 0:
        term2 = ((knots[i + k] - t) / denom2) * _bspline_basis(i + 1, k - 1, t, knots)

    return term1 + term2


def generate_clamped_knots(n_control, degree):
    """Generate clamped (open) uniform knot vector."""
    order = degree + 1
    n_knots = n_control + order
    knots = [0.0] * order
    for i in range(1, n_control - degree):
        knots.append(float(i))
    knots += [float(n_control - degree)] * order
    return knots


def bspline_curve(control_points, degree=3, num_samples=200):
    """
    Generate B-Spline curve using clamped uniform knot vector.
    Returns list of (x, y) points.
    """
    n = len(control_points)
    if n < 2:
        return []

    degree = min(degree, n - 1)
    knots = generate_clamped_knots(n, degree)
    k = degree + 1

    t_min = knots[k - 1]
    t_max = knots[n]

    curve_points = []
    for step in range(num_samples + 1):
        t = t_min + (t_max - t_min) * step / num_samples
        x = sum(_bspline_basis(i, k, t, knots) * control_points[i][0] for i in range(n))
        y = sum(_bspline_basis(i, k, t, knots) * control_points[i][1] for i in range(n))
        curve_points.append((x, y))

    return curve_points


def bezier_subdivision(control_points, t=0.5):
    """
    Subdivide Bezier curve at parameter t.
    Returns two sets of control points.
    """
    pts = list(control_points)
    left = [pts[0]]
    right = [pts[-1]]
    levels = [pts]

    while len(pts) > 1:
        new_pts = []
        for i in range(len(pts) - 1):
            x = (1 - t) * pts[i][0] + t * pts[i + 1][0]
            y = (1 - t) * pts[i][1] + t * pts[i + 1][1]
            new_pts.append((x, y))
        pts = new_pts
        levels.append(pts)
        left.append(pts[0])
        right.insert(0, pts[-1])

    return left, right, levels
