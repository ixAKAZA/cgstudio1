"""
Clipping algorithms:
- Cohen-Sutherland line clipping
- Sutherland-Hodgman polygon clipping
"""

# Region codes for Cohen-Sutherland
INSIDE = 0
LEFT   = 1
RIGHT  = 2
BOTTOM = 4
TOP    = 8


def compute_outcode(x, y, x_min, y_min, x_max, y_max):
    code = INSIDE
    if x < x_min:
        code |= LEFT
    elif x > x_max:
        code |= RIGHT
    if y < y_min:
        code |= BOTTOM
    elif y > y_max:
        code |= TOP
    return code


def cohen_sutherland(x1, y1, x2, y2, x_min, y_min, x_max, y_max):
    """
    Cohen-Sutherland line clipping algorithm.
    Returns:
        accepted (bool), clipped line coords, list of steps for visualization
    """
    steps = []

    outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
    outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)

    steps.append({
        "p1": (x1, y1), "p2": (x2, y2),
        "code1": outcode1, "code2": outcode2,
        "action": "init"
    })

    accepted = False

    while True:
        if not (outcode1 | outcode2):
            # Trivially accept
            accepted = True
            steps.append({
                "p1": (x1, y1), "p2": (x2, y2),
                "code1": outcode1, "code2": outcode2,
                "action": "accept"
            })
            break
        elif outcode1 & outcode2:
            # Trivially reject
            steps.append({
                "p1": (x1, y1), "p2": (x2, y2),
                "code1": outcode1, "code2": outcode2,
                "action": "reject"
            })
            break
        else:
            # Pick the point outside the clip window
            outcode_out = outcode1 if outcode1 else outcode2

            x, y = 0.0, 0.0
            dx = x2 - x1
            dy = y2 - y1

            if outcode_out & TOP:
                if dy != 0:
                    x = x1 + dx * (y_max - y1) / dy
                y = y_max
            elif outcode_out & BOTTOM:
                if dy != 0:
                    x = x1 + dx * (y_min - y1) / dy
                y = y_min
            elif outcode_out & RIGHT:
                if dx != 0:
                    y = y1 + dy * (x_max - x1) / dx
                x = x_max
            elif outcode_out & LEFT:
                if dx != 0:
                    y = y1 + dy * (x_min - x1) / dx
                x = x_min

            if outcode_out == outcode1:
                x1, y1 = x, y
                outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
            else:
                x2, y2 = x, y
                outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)

            steps.append({
                "p1": (x1, y1), "p2": (x2, y2),
                "code1": outcode1, "code2": outcode2,
                "action": "clip"
            })

    if accepted:
        return True, (x1, y1, x2, y2), steps
    else:
        return False, None, steps


def _inside(p, edge_start, edge_end):
    """Check if point p is inside the half-plane defined by edge (edge_start -> edge_end)."""
    ex = edge_end[0] - edge_start[0]
    ey = edge_end[1] - edge_start[1]
    px = p[0] - edge_start[0]
    py = p[1] - edge_start[1]
    return (ex * py - ey * px) >= 0


def _intersect(p1, p2, edge_start, edge_end):
    """Compute intersection of line p1-p2 with edge."""
    d1 = (p1[0] * (edge_end[1] - edge_start[1]) -
          p1[1] * (edge_end[0] - edge_start[0]) +
          edge_start[0] * edge_end[1] - edge_start[1] * edge_end[0])
    d2 = (p2[0] * (edge_end[1] - edge_start[1]) -
          p2[1] * (edge_end[0] - edge_start[0]) +
          edge_start[0] * edge_end[1] - edge_start[1] * edge_end[0])

    if abs(d1 - d2) < 1e-9:
        return p1

    t = d1 / (d1 - d2)
    x = p1[0] + t * (p2[0] - p1[0])
    y = p1[1] + t * (p2[1] - p1[1])
    return (x, y)


def sutherland_hodgman(polygon, clip_polygon):
    """
    Sutherland-Hodgman polygon clipping algorithm.
    Args:
        polygon: list of (x, y) vertices
        clip_polygon: list of (x, y) clip region vertices (convex, CCW)
    Returns:
        clipped polygon vertices, list of intermediate steps
    """
    output = list(polygon)
    steps = [list(output)]

    n = len(clip_polygon)
    for i in range(n):
        if not output:
            break

        edge_start = clip_polygon[i]
        edge_end = clip_polygon[(i + 1) % n]

        input_list = output
        output = []

        for j in range(len(input_list)):
            current = input_list[j]
            previous = input_list[j - 1]

            if _inside(current, edge_start, edge_end):
                if not _inside(previous, edge_start, edge_end):
                    output.append(_intersect(previous, current, edge_start, edge_end))
                output.append(current)
            elif _inside(previous, edge_start, edge_end):
                output.append(_intersect(previous, current, edge_start, edge_end))

        steps.append(list(output))

    return output, steps


def rect_clip_polygon(x_min, y_min, x_max, y_max):
    """Return CCW clip polygon for a rectangle."""
    return [
        (x_min, y_min),
        (x_max, y_min),
        (x_max, y_max),
        (x_min, y_max),
    ]
