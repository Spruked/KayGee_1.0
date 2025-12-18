# PDCo Space Field 3D Generator - Usage Guide

## Overview

Complete Python port of the SketchUp Ruby extension by Alex London (Primary Design Co.)

**Faithful implementation of:**
- Exact geometric series (2^n for even sides, 1.5^n for odd)
- Ruby `multiplier` function
- Ruby `calculate_next_level_origin` (THE CORE - creates recursive drift)
- Ruby `generate_vertices` (polygon generation with odd/even symmetry)
- Ruby `draw_interdimensional_lines` (CC and MSC patterns)
- Ruby `generate_levels` (main recursive expansion)
- Ruby `batch_generate` (optimal level calculation)

---

## Installation

```bash
pip install plotly kaleido numpy
```

---

## Quick Start

### Single Field Generation

```bash
# Generate 4-sided field, 3 levels, Corners Connected pattern
python space_field_3d.py --sides 4 --levels 3 --pattern CC --output field.html

# Generate hexagon (6 sides), 2 levels
python space_field_3d.py --sides 6 --levels 2 --pattern MSC --output hexagon.html

# Generate triangle (3 sides), 4 levels
python space_field_3d.py --sides 3 --levels 4 --pattern CC --output triangle.html
```

### Batch Generation

```bash
# Generate first 10% of valid dimensions (3-360)
python space_field_3d.py --batch --batch-dir output_fields

# This will create JSON + HTML for optimal level at each dimension
```

---

## Parameter Format (Ruby Convention)

Format: `O<sides><pattern>xx<level>`

Examples:
- `O4CCxx3` - 4 sides, Corners Connected, 3 levels
- `O6MSCxx2` - 6 sides, Mid Sides Connected, 2 levels
- `O30CCxx5` - 30 sides, Corners Connected, 5 levels

---

## Patterns

### CC (Corners Connected)
Connects vertex 0 to all vertices in first half of polygon.
Creates **radial triangular subdivisions**.

### MSC (Mid Sides Connected)
Connects midpoints of edges.
Creates **nested polygon structures**.

---

## Mathematical Core

### Multiplier Function
```python
def multiplier(level: int, sides: int) -> float:
    if sides % 2 == 0:
        return 2 ** (level - 2)  # Powers of 2
    else:
        return 1.5 ** (level - 2)  # Musical fifths
```

**Example (4 sides):**
- Level 2: multiplier = 2^0 = 1
- Level 3: multiplier = 2^1 = 2
- Level 4: multiplier = 2^2 = 4
- Level 5: multiplier = 2^3 = 8

**Offset progression:**
- Level 2: radius × 1 = 1
- Level 3: radius × (1 + 2) = 3
- Level 4: radius × (1 + 2 + 4) = 7
- Level 5: radius × (1 + 2 + 4 + 8) = 15

**Geometric series:** `offset = radius × (2^n - 1)`

### Origin Calculation

```python
def calculate_next_level_origin(center, radius, sides, level):
    scaling_factor = multiplier(level, sides)
    adjusted_radius = radius * scaling_factor
    verts = generate_vertices(center, adjusted_radius, sides)
    
    if sides % 2 == 1:
        return midpoint(verts[0], verts[1])  # Odd: edge midpoint
    else:
        return verts[0]  # Even: vertex
```

**This creates the "drift" pattern** - each level's origin shifts along a geometric series.

---

## Output Files

### HTML (Interactive)
- Plotly 3D visualization
- Rotatable with mouse
- Zoomable with scroll
- Dark theme for clarity

### JSON (Data Export)
```json
{
  "faces": [
    {
      "vertices": [[x, y, z], ...],
      "level": 0,
      "pattern": "CC"
    }
  ],
  "edges": [
    [[x1, y1, z1], [x2, y2, z2]]
  ],
  "metadata": {
    "total_faces": 256,
    "total_edges": 512,
    "levels": 4
  }
}
```

---

## Valid Dimensions

Only dimensions where `360/n` produces terminating decimals:

**Low dimensions:** 3, 4, 5, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 25, 30, 32, 36, 40, 45, 48, 50, 60, 72, 75, 80, 90, 96, 100, 120, 144, 150, 180, 200, 225, 240, 300, 360

**Total valid:** ~70 dimensions (out of 358)

---

## Performance Notes

### Memory Usage
- **Level 4, 4 sides:** ~256 faces
- **Level 5, 6 sides:** ~7,776 faces
- **Level 6, 8 sides:** ~262,144 faces

**Recommendation:** Keep `sides^level < 500,000` to avoid memory exhaustion

### Batch Generation Timing
Estimated for full valid dimension set (3-360):
- **10% (~7 dims):** ~30 seconds
- **100% (~70 dims):** ~5 minutes

---

## Integration with KayGee

### As Symbolic Cognition Visualizer

```python
from space_field_3d import SpaceField3D

# Map reasoning state to geometry
def visualize_reasoning(kaygee_state):
    sides = 4 + int(kaygee_state["philosopher_count"])
    levels = max(2, int(kaygee_state["reasoning_depth"] * 5))
    confidence = kaygee_state["confidence"]
    
    field = SpaceField3D()
    field.generate_levels(
        radius=confidence,  # Confidence = scale
        sides=sides,        # Philosophers = symmetry
        max_levels=levels,  # Reasoning depth = recursion
        pattern="CC" if kaygee_state["mode"] == "deductive" else "MSC"
    )
    
    return field.visualize_plotly(f"Reasoning: {kaygee_state['interaction_id']}")
```

### Live Rotation Parameter

The JavaScript visualizer adds **live rotation** by passing `rotation_angle` parameter.

**To add rotation to Python version:**
```python
# In generate_levels, rotate entire structure after generation
def apply_global_rotation(self, angle_deg: float):
    center = Vertex3D(0, 0, 0)
    for i, face in enumerate(self.faces):
        self.faces[i].vertices = self.rotate_vertices(
            face.vertices, center, angle_deg, axis='z'
        )
```

---

## Spectral Analysis Integration

Combine with FFT analyzer from `space_field_generator.py`:

```python
from space_field_3d import SpaceField3D
from visualization.space_field_generator import SpectralAnalyzer
import matplotlib.pyplot as plt

# Generate 3D field
field = SpaceField3D()
field.generate_levels(radius=1.0, sides=6, max_levels=3, pattern="CC")

# Render to 2D for FFT
fig, ax = plt.subplots()
# ... project 3D to 2D ...

# Analyze
analyzer = SpectralAnalyzer(fig, ax)
metrics = analyzer.analyze()

print(f"Dominant frequency: {metrics['dominant_freq']}")
print(f"Fractal estimate: {metrics['fractal_estimate']:.3f}")
```

---

## Comparison: Ruby vs Python

| Feature | Ruby (SketchUp) | Python (This Port) |
|---------|----------------|-------------------|
| Geometry Engine | ✅ | ✅ (Exact match) |
| Multiplier | ✅ | ✅ (Identical) |
| Origin Calc | ✅ | ✅ (Identical) |
| CC Pattern | ✅ | ✅ |
| MSC Pattern | ✅ | ✅ |
| Batch Gen | ✅ | ✅ |
| 3D Visualization | SketchUp UI | Plotly (web) |
| Export Format | .skp | .html, .json |
| Performance | Native | Python (slower) |

**Result:** Geometric output is **mathematically identical**. Visualization differs (SketchUp vs web).

---

## Examples

### Symbolic Geometry (Paper 1 Validation)

```bash
# Sacred geometry (low-frequency dominant)
python space_field_3d.py --sides 4 --levels 3 --pattern CC --output sacred_4.html
python space_field_3d.py --sides 6 --levels 3 --pattern CC --output sacred_6.html
python space_field_3d.py --sides 12 --levels 2 --pattern CC --output sacred_12.html

# Esoteric (fractal)
python space_field_3d.py --sides 7 --levels 4 --pattern MSC --output esoteric_7.html
python space_field_3d.py --sides 9 --levels 3 --pattern CC --output esoteric_9.html

# Modern logos (high-frequency)
python space_field_3d.py --sides 30 --levels 2 --pattern CC --output modern_30.html
python space_field_3d.py --sides 60 --levels 2 --pattern MSC --output modern_60.html
```

### Cognitive Resonance Test

```bash
# Test if geometric harmony matches perceptual categories
python space_field_3d.py --batch --batch-dir cognitive_test

# Then analyze spectral signatures:
python analyze_batch.py cognitive_test/
```

---

## Next Steps

1. **Add Rotation Animation:**
   - Implement `apply_global_rotation(angle)` 
   - Create animated GIF/video export

2. **Color Palette Integration:**
   - Map Ruby `D_COLORS` to faces
   - Implement `_RGB` parameter parsing

3. **STL/OBJ Export:**
   - For 3D printing
   - Convert face list to mesh format

4. **WebGL Streamer:**
   - Real-time generation
   - Stream to dashboard as KayGee reasons

5. **Spectral Hash Export:**
   - Integrate FFT analyzer
   - Create unique "spectral genome" for each field

---

## Source Code Fidelity

**Ruby methods ported 1:1:**
- ✅ `multiplier(level, sides)`
- ✅ `generate_vertices(center, radius, sides)`
- ✅ `midpoint(v1, v2)`
- ✅ `calculate_next_level_origin(center, radius, sides, level)`
- ✅ `draw_interdimensional_lines(face, pattern)`
- ✅ `generate_base_polygon(...)`
- ✅ `generate_first_level(...)`
- ✅ `generate_levels(...)`
- ✅ `is_valid_dimension(n)`
- ✅ `generate_valid_dimensions()`
- ✅ `max_level_for_dimension(sides, max_polygons)`
- ✅ `batch_generate(...)`

**Mathematical equivalence verified:**
- Origin offsets match Ruby (Level 4 = [0, 7, 0] for sides=4)
- Vertex generation matches (even/odd symmetry preserved)
- Rotation transformations match (angle calculations identical)

---

## License

Original Ruby: © 2025 Primary Design Co. (Alex London)  
Python Port: Open-source for research and KayGee integration

https://primarydesignco.com
