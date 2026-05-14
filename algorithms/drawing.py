"""
Core computer graphics drawing algorithms implemented from scratch.
All algorithms manually implemented without built-in drawing shortcuts.
"""

import math
import time
import numpy as np


def dda_line(x1, y1, x2, y2):
    """
    Digital Differential Analyzer (DDA) line drawing algorithm.
    Returns list of (x, y) pixel coordinates and execution time.
    """
    t_start = time.perf_counter()
    points = []

    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        t_end = time.perf_counter()
        return [(round(x1), round(y1))], t_end - t_start

    x_inc = dx / steps
    y_inc = dy / steps

    x, y = float(x1), float(y1)

    for _ in range(int(steps) + 1):
        points.append((round(x), round(y)))
        x += x_inc
        y += y_inc

    t_end = time.perf_counter()
    return points, t_end - t_start


def bresenham_line(x1, y1, x2, y2):
    """
    Bresenham's line drawing algorithm.
    Integer-only arithmetic, highly optimized.
    Returns list of (x, y) pixel coordinates and execution time.
    """
    t_start = time.perf_counter()
    points = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy
    x, y = x1, y1

    while True:
        points.append((x, y))
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    t_end = time.perf_counter()
    return points, t_end - t_start


def midpoint_circle(cx, cy, r):
    """
    Midpoint Circle Drawing Algorithm.
    Uses 8-way symmetry for efficiency.
    Returns list of (x, y) pixel coordinates and execution time.
    """
    t_start = time.perf_counter()
    points = []

    def plot_circle_points(cx, cy, x, y):
        pts = []
        for dx, dy in [(x,y),(-x,y),(x,-y),(-x,-y),(y,x),(-y,x),(y,-x),(-y,-x)]:
            pts.append((cx + dx, cy + dy))
        return pts

    x = 0
    y = r
    d = 1 - r

    points.extend(plot_circle_points(cx, cy, x, y))

    while x < y:
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
        points.extend(plot_circle_points(cx, cy, x, y))

    t_end = time.perf_counter()
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for p in points:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique, t_end - t_start


def bresenham_circle(cx, cy, r):
    """
    Bresenham's Circle Drawing Algorithm.
    Integer-based, uses decision parameter.
    Returns list of (x, y) pixel coordinates and execution time.
    """
    t_start = time.perf_counter()
    points = []

    def plot_8(cx, cy, x, y):
        pts = []
        for dx, dy in [(x,y),(-x,y),(x,-y),(-x,-y),(y,x),(-y,x),(y,-x),(-y,-x)]:
            pts.append((cx + dx, cy + dy))
        return pts

    x = 0
    y = r
    p = 3 - 2 * r

    points.extend(plot_8(cx, cy, x, y))

    while x <= y:
        x += 1
        if p < 0:
            p += 4 * x + 6
        else:
            y -= 1
            p += 4 * (x - y) + 10
        points.extend(plot_8(cx, cy, x, y))

    t_end = time.perf_counter()
    seen = set()
    unique = []
    for p in points:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique, t_end - t_start


def dda_line_steps(x1, y1, x2, y2):
    """Returns step-by-step points for visualization."""
    points, _ = dda_line(x1, y1, x2, y2)
    return points


def bresenham_line_steps(x1, y1, x2, y2):
    """Returns step-by-step points for Bresenham visualization."""
    points, _ = bresenham_line(x1, y1, x2, y2)
    return points


def compare_algorithms(x1, y1, x2, y2, r=None):
    """
    Compare DDA vs Bresenham line, and Midpoint vs Bresenham circle.
    Returns dict of stats.
    """
    # Line comparison
    dda_pts, dda_time = dda_line(x1, y1, x2, y2)
    bres_pts, bres_time = bresenham_line(x1, y1, x2, y2)

    result = {
        "line": {
            "dda": {"points": len(dda_pts), "time_us": dda_time * 1e6},
            "bresenham": {"points": len(bres_pts), "time_us": bres_time * 1e6},
        }
    }

    if r is not None:
        mp_pts, mp_time = midpoint_circle(x1, y1, r)
        bc_pts, bc_time = bresenham_circle(x1, y1, r)
        result["circle"] = {
            "midpoint": {"points": len(mp_pts), "time_us": mp_time * 1e6},
            "bresenham": {"points": len(bc_pts), "time_us": bc_time * 1e6},
        }

    return result
