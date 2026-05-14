"""
CG Studio — Flask Backend
Serves the frontend and exposes algorithm APIs.
"""

import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_from_directory

from algorithms.drawing import dda_line, bresenham_line, midpoint_circle, bresenham_circle
from transformations.transforms import (
    translation_matrix, rotation_matrix, scaling_matrix,
    reflection_matrix, shearing_matrix, apply_transform, matrix_to_display
)
from clipping.algorithms import cohen_sutherland, sutherland_hodgman, rect_clip_polygon
from curves.curve_algorithms import bezier_curve, bspline_curve, de_casteljau, bezier_subdivision

import numpy as np

app = Flask(__name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def pts_to_list(pts):
    return [[float(p[0]), float(p[1])] for p in pts]

def matrix_to_list(m):
    return m.tolist()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Drawing Algorithms ────────────────────────────────────────────────────────

@app.route("/api/dda", methods=["POST"])
def api_dda():
    d = request.json
    pts, t = dda_line(int(d["x1"]), int(d["y1"]), int(d["x2"]), int(d["y2"]))
    return jsonify({"points": pts_to_list(pts), "time_us": t * 1e6, "count": len(pts)})


@app.route("/api/bresenham_line", methods=["POST"])
def api_bresenham_line():
    d = request.json
    pts, t = bresenham_line(int(d["x1"]), int(d["y1"]), int(d["x2"]), int(d["y2"]))
    return jsonify({"points": pts_to_list(pts), "time_us": t * 1e6, "count": len(pts)})


@app.route("/api/midpoint_circle", methods=["POST"])
def api_midpoint_circle():
    d = request.json
    pts, t = midpoint_circle(int(d["cx"]), int(d["cy"]), int(d["r"]))
    return jsonify({"points": pts_to_list(pts), "time_us": t * 1e6, "count": len(pts)})


@app.route("/api/bresenham_circle", methods=["POST"])
def api_bresenham_circle():
    d = request.json
    pts, t = bresenham_circle(int(d["cx"]), int(d["cy"]), int(d["r"]))
    return jsonify({"points": pts_to_list(pts), "time_us": t * 1e6, "count": len(pts)})


# ── Benchmark ─────────────────────────────────────────────────────────────────

@app.route("/api/benchmark/lines", methods=["POST"])
def api_bench_lines():
    d = request.json
    x1, y1, x2, y2 = int(d["x1"]), int(d["y1"]), int(d["x2"]), int(d["y2"])
    iters = 500

    t0 = time.perf_counter()
    for _ in range(iters):
        dda_pts, _ = dda_line(x1, y1, x2, y2)
    dda_avg = (time.perf_counter() - t0) / iters * 1e6

    t0 = time.perf_counter()
    for _ in range(iters):
        bres_pts, _ = bresenham_line(x1, y1, x2, y2)
    bres_avg = (time.perf_counter() - t0) / iters * 1e6

    length = math.hypot(x2 - x1, y2 - y1)
    return jsonify({
        "dda": {"time_us": round(dda_avg, 2), "pixels": len(dda_pts)},
        "bresenham": {"time_us": round(bres_avg, 2), "pixels": len(bres_pts)},
        "length": round(length, 1)
    })


@app.route("/api/benchmark/circles", methods=["POST"])
def api_bench_circles():
    d = request.json
    cx, cy, r = int(d["cx"]), int(d["cy"]), max(1, int(d["r"]))
    iters = 300

    t0 = time.perf_counter()
    for _ in range(iters):
        mp_pts, _ = midpoint_circle(cx, cy, r)
    mp_avg = (time.perf_counter() - t0) / iters * 1e6

    t0 = time.perf_counter()
    for _ in range(iters):
        bc_pts, _ = bresenham_circle(cx, cy, r)
    bc_avg = (time.perf_counter() - t0) / iters * 1e6

    return jsonify({
        "midpoint": {"time_us": round(mp_avg, 2), "pixels": len(mp_pts)},
        "bresenham": {"time_us": round(bc_avg, 2), "pixels": len(bc_pts)},
        "radius": r,
        "circumference": round(2 * math.pi * r, 1)
    })


# ── Curves ────────────────────────────────────────────────────────────────────

@app.route("/api/bezier", methods=["POST"])
def api_bezier():
    d = request.json
    ctrl = [tuple(p) for p in d["points"]]
    samples = d.get("samples", 300)
    curve = bezier_curve(ctrl, num_samples=samples)
    t_val = d.get("t_viz")
    steps_data = None
    if t_val is not None:
        _, levels = de_casteljau(ctrl, float(t_val))
        steps_data = [pts_to_list(lvl) for lvl in levels]
    return jsonify({"curve": pts_to_list(curve), "steps": steps_data})


@app.route("/api/bspline", methods=["POST"])
def api_bspline():
    d = request.json
    ctrl = [tuple(p) for p in d["points"]]
    degree = d.get("degree", 3)
    samples = d.get("samples", 300)
    curve = bspline_curve(ctrl, degree=degree, num_samples=samples)
    return jsonify({"curve": pts_to_list(curve)})


# ── Transformations ────────────────────────────────────────────────────────────

def _get_points(d):
    return [tuple(p) for p in d["points"]]

@app.route("/api/transform/translate", methods=["POST"])
def api_translate():
    d = request.json
    pts = _get_points(d)
    m = translation_matrix(float(d["tx"]), float(d["ty"]))
    result = apply_transform(pts, m)
    return jsonify({"points": pts_to_list(result), "matrix": matrix_to_list(m)})

@app.route("/api/transform/rotate", methods=["POST"])
def api_rotate():
    d = request.json
    pts = _get_points(d)
    m = rotation_matrix(float(d["angle"]), float(d.get("cx", 0)), float(d.get("cy", 0)))
    result = apply_transform(pts, m)
    return jsonify({"points": pts_to_list(result), "matrix": matrix_to_list(m)})

@app.route("/api/transform/scale", methods=["POST"])
def api_scale():
    d = request.json
    pts = _get_points(d)
    m = scaling_matrix(float(d["sx"]), float(d["sy"]),
                       float(d.get("cx", 0)), float(d.get("cy", 0)))
    result = apply_transform(pts, m)
    return jsonify({"points": pts_to_list(result), "matrix": matrix_to_list(m)})

@app.route("/api/transform/reflect", methods=["POST"])
def api_reflect():
    d = request.json
    pts = _get_points(d)
    m = reflection_matrix(d.get("axis", "x"))
    result = apply_transform(pts, m)
    return jsonify({"points": pts_to_list(result), "matrix": matrix_to_list(m)})

@app.route("/api/transform/shear", methods=["POST"])
def api_shear():
    d = request.json
    pts = _get_points(d)
    m = shearing_matrix(float(d.get("shx", 0)), float(d.get("shy", 0)))
    result = apply_transform(pts, m)
    return jsonify({"points": pts_to_list(result), "matrix": matrix_to_list(m)})


# ── Clipping ──────────────────────────────────────────────────────────────────

@app.route("/api/clip/cohen_sutherland", methods=["POST"])
def api_cs():
    d = request.json
    x1, y1, x2, y2 = d["x1"], d["y1"], d["x2"], d["y2"]
    xmin, ymin, xmax, ymax = d["xmin"], d["ymin"], d["xmax"], d["ymax"]
    accepted, result, steps = cohen_sutherland(
        float(x1), float(y1), float(x2), float(y2),
        float(xmin), float(ymin), float(xmax), float(ymax)
    )
    serial_steps = []
    for s in steps:
        serial_steps.append({
            "p1": list(s["p1"]), "p2": list(s["p2"]),
            "code1": s["code1"], "code2": s["code2"],
            "action": s["action"]
        })
    return jsonify({
        "accepted": accepted,
        "result": list(result) if result else None,
        "steps": serial_steps
    })


@app.route("/api/clip/sutherland_hodgman", methods=["POST"])
def api_sh():
    d = request.json
    polygon = [tuple(p) for p in d["polygon"]]
    xmin, ymin, xmax, ymax = d["xmin"], d["ymin"], d["xmax"], d["ymax"]
    clip_poly = rect_clip_polygon(float(xmin), float(ymin), float(xmax), float(ymax))
    result, steps = sutherland_hodgman(polygon, clip_poly)
    return jsonify({
        "result": pts_to_list(result),
        "steps": [pts_to_list(s) for s in steps],
        "clip_polygon": pts_to_list(clip_poly)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print(f"\n  CG Studio running on port {port}\n")

    app.run(
        debug=False,
        host="0.0.0.0",
        port=port
    )