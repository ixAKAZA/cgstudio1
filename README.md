# CG Studio — Web Application

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

## Features

- **Line Algorithms:** DDA and Bresenham with step-by-step visualization
- **Circle Algorithms:** Midpoint and Bresenham circle drawing
- **Curves:** Interactive Bézier and B-Spline with control point editing  
- **Clipping:** Cohen-Sutherland (lines) and Sutherland-Hodgman (polygons)
- **Transformations:** Translate, Rotate, Scale, Reflect, Shear — with real-time 3×3 matrix display
- **Benchmark:** Side-by-side algorithm timing (µs precision, 300–500 iterations)
- **Scene:** Save/load JSON scenes, undo/redo (50 steps), layer management
- **Themes:** Dark, Neon, Professional

## Controls

| Action | Control |
|---|---|
| Select / Move | `S` or click |
| DDA Line | `D` → click start → click end |
| Bresenham Line | `B` → click start → click end |
| Midpoint Circle | `M` → click center → click edge |
| Bresenham Circle | `C` → click center → click edge |
| Bézier Curve | click tool → click control points → Enter or double-click |
| B-Spline | click tool → click control points → Enter or double-click |
| Polygon | click tool → click vertices → Enter or double-click |
| Pan camera | Middle mouse drag |
| Zoom | Mouse wheel |
| Cancel drawing | Right-click or Escape |
| Delete selected | Delete |
| Select all | Ctrl+A |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Save scene | Ctrl+S |
| Reset camera | R |
| Toggle grid | G |

## Project Structure

```
app.py                Flask server + all API endpoints
algorithms/           DDA, Bresenham line & circle
transformations/      2D matrix transformations  
clipping/             Cohen-Sutherland, Sutherland-Hodgman
curves/               Bézier (de Casteljau), B-Spline (Cox-de Boor)
templates/index.html  Full frontend — HTML5 Canvas rendering
requirements.txt
```
