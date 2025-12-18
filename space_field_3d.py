"""
PDCo Space Field 3D Generator - Python Port
Ported from SketchUp Ruby Extension by Alex London (Primary Design Co.)
© 2025 - Faithful implementation of recursive harmonic geometry

Original Ruby: https://primarydesignco.com
Python Port: For KayGee symbolic cognition visualization

Features:
- Exact geometric series matching Ruby implementation
- CC (Corners Connected) and MSC (Mid Sides Connected) patterns
- Batch generation with automatic level optimization
- Interactive 3D visualization with Plotly
- Export to multiple formats (STL, OBJ, JSON)
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import json
import time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Color palette matching Ruby D_COLORS
COLORS = {
    "B": (0, 0, 255),        # Blue
    "Bl": (0, 0, 0),         # Black
    "Br": (165, 42, 42),     # Brown
    "C": (0, 100, 100),      # Cyan
    "G": (0, 255, 0),        # Green
    "Gr": (128, 128, 128),   # Gray
    "L": (191, 255, 0),      # Lime
    "Lb": (173, 216, 230),   # Light Blue
    "Ly": (255, 255, 224),   # Light Yellow
    "O": (255, 165, 0),      # Orange
    "P": (128, 0, 128),      # Purple
    "Pi": (255, 192, 203),   # Pink
    "R": (255, 0, 0),        # Red
    "S": (192, 192, 192),    # Silver
    "W": (255, 255, 255),    # White
    "Y": (255, 255, 0)       # Yellow
}


@dataclass
class Vertex3D:
    """3D vertex with position"""
    x: float
    y: float
    z: float = 0.0
    
    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)
    
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])


@dataclass
class Face:
    """Polygon face with vertices and color"""
    vertices: List[Vertex3D]
    color: Optional[str] = None
    pattern_type: Optional[str] = None
    level: int = 0
    
    def get_center(self) -> Vertex3D:
        """Calculate face centroid"""
        x = sum(v.x for v in self.vertices) / len(self.vertices)
        y = sum(v.y for v in self.vertices) / len(self.vertices)
        z = sum(v.z for v in self.vertices) / len(self.vertices)
        return Vertex3D(x, y, z)


class SpaceField3D:
    """
    3D Space Field Generator
    Mirrors Ruby SketchUp extension geometry engine
    WITH complex phasor implementation from JS visualizer
    """
    
    def __init__(self):
        self.faces: List[Face] = []
        self.edges: List[Tuple[Vertex3D, Vertex3D]] = []
        self.level_groups: List[List[Face]] = []
        self.emergent_rotation = True  # Golden-ratio phase damping toggle
        self.global_angle = 0.0  # For PLL animation
        self.rotation_speed = 0.01  # Radians per frame
        self.phase_damping = 0.3  # PLL proportional control
        
    @staticmethod
    def multiplier(level: int, sides: int) -> float:
        """
        Scaling factor for level calculation
        Matches Ruby: def self.multiplier(level, sides)
        
        Even sides: powers of 2 (2^(level-2))
        Odd sides: 1.5 series (1.5^(level-2))
        """
        if sides % 2 == 0:
            return 2 ** (level - 2)
        else:
            return 1.5 ** (level - 2)
    
    @staticmethod
    def generate_vertices(center: Vertex3D, radius: float, sides: int) -> List[Vertex3D]:
        """
        Generate regular polygon vertices
        Matches Ruby: def self.generate_vertices(center_point, radius, sides)
        
        For even sides: vertex 0 at angle 0 (top)
        For odd sides: offset by half slice for symmetry
        """
        vertices = []
        angle = (2 * math.pi) / sides
        
        for side in range(sides):
            if sides % 2 == 0:
                # Even sides - vertex at top
                theta = angle * side
                x = center.x + radius * math.sin(theta)
                y = center.y + radius * math.cos(theta)
            else:
                # Odd sides - offset for symmetry
                theta = angle * side - (angle / 2)
                x = center.x + radius * math.sin(theta)
                y = center.y + radius * math.cos(theta)
            
            vertices.append(Vertex3D(x, y, center.z))
        
        return vertices
    
    @staticmethod
    def midpoint(v1: Vertex3D, v2: Vertex3D) -> Vertex3D:
        """
        Calculate midpoint between two vertices
        Matches Ruby: def self.midpoint(vertex1, vertex2)
        """
        return Vertex3D(
            (v1.x + v2.x) / 2.0,
            (v1.y + v2.y) / 2.0,
            (v1.z + v2.z) / 2.0
        )
    
    @staticmethod
    def calculate_next_level_origin(center: Vertex3D, radius: float, sides: int, level: int) -> Vertex3D:
        """
        Calculate origin point for next recursion level
        Matches Ruby: def self.calculate_next_level_origin(center_point, radius, sides, level)
        
        This is THE CORE FUNCTION that creates the recursive drift pattern.
        
        For even sides: uses first vertex as origin
        For odd sides: uses midpoint of first edge as origin
        
        The offset grows geometrically based on level.
        """
        # Calculate scaling factor
        scaling_factor = SpaceField3D.multiplier(level, sides)
        corner_adjusted = radius * scaling_factor
        
        # Generate vertices at this level's scale
        verts = SpaceField3D.generate_vertices(center, corner_adjusted, sides)
        
        # Determine origin for next level
        if sides % 2 == 1:
            # Odd sides: midpoint of first edge
            origin = SpaceField3D.midpoint(verts[0], verts[1])
        else:
            # Even sides: first vertex
            origin = verts[0]
        
        logging.debug(f"Level {level} origin: ({origin.x:.4f}, {origin.y:.4f})")
        return origin
    
    @staticmethod
    def calculate_symmetry_point_phasor(center: Vertex3D, radius: float, sides: int, level: int, 
                                       emergent: bool = True) -> Vertex3D:
        """
        Complex phasor implementation from JS visualizer
        
        This is the ROSETTA STONE - treats geometry as signal processing:
        center + magnitude * e^(i*phase)
        
        Where:
        - magnitude = sum of geometric series (harmonic accumulation)
        - phase = π/sides * 0.618 (golden-ratio damped rotation)
        
        When emergent=True: applies golden-ratio phase offset
        When emergent=False: pure vertical offset (locked mode)
        
        Result: frequency-domain arithmetic rendered as geometry
        """
        if level <= 1:
            return center
        
        # Accumulate harmonic magnitude
        total_magnitude = 0.0
        for l in range(2, level + 1):
            mult = 2 ** (l - 2) if sides % 2 == 0 else 1.5 ** (l - 2)
            total_magnitude += radius * mult
        
        # Golden-ratio phase damping (Euler's formula: magnitude * e^(i*phase))
        phase = (math.pi / sides) * 0.618 if emergent else 0.0
        
        offset_x = total_magnitude * math.cos(phase)
        offset_y = total_magnitude * math.sin(phase)
        
        return Vertex3D(
            center.x + offset_x,
            center.y + offset_y,
            center.z
        )
    
    def draw_interdimensional_lines(self, face_vertices: List[Vertex3D], pattern: str) -> List[Tuple[Vertex3D, Vertex3D]]:
        """
        Generate pattern lines within polygon
        Matches Ruby: def self.draw_interdimensional_lines(face, pattern)
        
        CC (Corners Connected): Connect vertex 0 to all others in first half
        MSC (Mid Sides Connected): Connect midpoints of edges
        """
        lines = []
        
        if pattern == "CC":
            # Corners Connected - connect vertex 0 to first half of vertices
            for j in range(1, len(face_vertices) // 2 + 1):
                lines.append((face_vertices[0], face_vertices[j]))
        
        elif pattern == "MSC":
            # Mid Sides Connected - connect midpoints
            midpoints = []
            for i in range(len(face_vertices) // 2 + 1):
                mp = self.midpoint(face_vertices[i], face_vertices[(i + 1) % len(face_vertices)])
                midpoints.append(mp)
            
            for j in range(1, len(midpoints)):
                lines.append((midpoints[0], midpoints[j]))
        
        return lines
    
    def generate_base_polygon(self, center: Vertex3D, radius: float, sides: int, pattern: Optional[str] = None) -> Face:
        """
        Generate base level polygon with pattern
        """
        vertices = self.generate_vertices(center, radius, sides)
        face = Face(vertices=vertices, pattern_type=pattern, level=0)
        
        # Add pattern lines if specified
        if pattern:
            pattern_lines = self.draw_interdimensional_lines(vertices, pattern)
            self.edges.extend(pattern_lines)
        
        self.faces.append(face)
        return face
    
    def rotate_vertices(self, vertices: List[Vertex3D], center: Vertex3D, angle_deg: float, axis: str = 'z') -> List[Vertex3D]:
        """
        Rotate vertices around center point
        Matches Ruby rotation transformations
        """
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        rotated = []
        for v in vertices:
            # Translate to origin
            dx = v.x - center.x
            dy = v.y - center.y
            
            if axis == 'z':
                # Rotate around Z axis
                new_x = cos_a * dx - sin_a * dy
                new_y = sin_a * dx + cos_a * dy
                rotated.append(Vertex3D(new_x + center.x, new_y + center.y, v.z))
            else:
                rotated.append(v)  # No rotation for other axes yet
        
        return rotated
    
    def copy_and_rotate_face(self, face: Face, center: Vertex3D, angle_deg: float) -> Face:
        """
        Copy face and rotate around center
        Matches Ruby component copy + rotation transform
        """
        rotated_verts = self.rotate_vertices(face.vertices, center, angle_deg)
        new_face = Face(
            vertices=rotated_verts,
            color=face.color,
            pattern_type=face.pattern_type,
            level=face.level
        )
        
        # Rotate pattern edges too
        if face.pattern_type:
            pattern_lines = self.draw_interdimensional_lines(rotated_verts, face.pattern_type)
            self.edges.extend(pattern_lines)
        
        return new_face
    
    def generate_first_level(self, base_face: Face, center: Vertex3D, sides: int) -> List[Face]:
        """
        Generate first level by rotating base polygon around center
        Matches Ruby: generate_first_level_polygon
        
        Creates 'sides' copies rotated by 360/sides degrees
        """
        first_level_faces = [base_face]
        angle_step = 360.0 / sides
        
        for i in range(1, sides):
            angle = angle_step * i
            rotated_face = self.copy_and_rotate_face(base_face, center, angle)
            rotated_face.level = 1
            self.faces.append(rotated_face)
            first_level_faces.append(rotated_face)
        
        logging.info(f"Generated first level: {len(first_level_faces)} faces")
        return first_level_faces
    
    def generate_levels(self, radius: float, sides: int, max_levels: int, pattern: str = "CC") -> None:
        """
        Main recursive level generation
        Matches Ruby: def self.generate_levels(radius, sides, levels, pattern, colors)
        
        This is the HEART of the space field generator.
        """
        logging.info(f"Generating space field: {sides} sides, {max_levels} levels, pattern={pattern}")
        start_time = time.time()
        
        # Level 0: Base polygon
        center = Vertex3D(0, 0, 0)
        base_face = self.generate_base_polygon(center, radius, sides, pattern)
        
        # Level 1: Rotate base around center
        level_1_faces = self.generate_first_level(base_face, center, sides)
        self.level_groups.append(level_1_faces)
        
        if max_levels < 2:
            return
        
        # Levels 2+: Recursive expansion
        current_level_faces = level_1_faces.copy()
        origin = center
        
        for level in range(2, max_levels + 1):
            level_start = time.time()
            
            # Calculate new origin using geometric series
            origin = self.calculate_next_level_origin(origin, radius, sides, level)
            
            new_level_faces = []
            angle_step = 360.0 / sides
            
            # For each existing face group, create rotated copies around new origin
            for i in range(sides):
                angle = angle_step * i
                
                for face in current_level_faces:
                    # Copy and rotate around new origin
                    rotated_face = self.copy_and_rotate_face(face, origin, angle)
                    rotated_face.level = level
                    self.faces.append(rotated_face)
                    new_level_faces.append(rotated_face)
            
            self.level_groups.append(new_level_faces)
            current_level_faces = new_level_faces
            
            elapsed = time.time() - level_start
            logging.info(f"Level {level} generated: {len(new_level_faces)} faces in {elapsed:.3f}s")
        
        total_time = time.time() - start_time
        logging.info(f"✅ Generation complete: {len(self.faces)} total faces in {total_time:.3f}s")
    
    def generate_levels_phasor(self, radius: float, sides: int, max_levels: int, 
                              pattern: str = "CC", use_emergent: bool = True) -> None:
        """
        Phasor-based recursive generation (JS visualizer method)
        
        Uses complex phasor for origin calculation instead of geometric vertex offset.
        This creates the "emergent rotation" effect seen in the live JS visualizer.
        
        When use_emergent=True: golden-ratio damped spiral
        When use_emergent=False: locked vertical expansion
        """
        logging.info(f"Generating space field (PHASOR): {sides} sides, {max_levels} levels, "
                    f"pattern={pattern}, emergent={use_emergent}")
        start_time = time.time()
        
        # Level 0: Base polygon
        center = Vertex3D(0, 0, 0)
        base_face = self.generate_base_polygon(center, radius, sides, pattern)
        
        # Level 1: Rotate base around center
        level_1_faces = self.generate_first_level(base_face, center, sides)
        self.level_groups.append(level_1_faces)
        
        if max_levels < 2:
            return
        
        # Levels 2+: Phasor-based recursive expansion
        current_level_faces = level_1_faces.copy()
        origin = center
        
        for level in range(2, max_levels + 1):
            level_start = time.time()
            
            # Calculate new origin using complex phasor (ROSETTA STONE)
            origin = self.calculate_symmetry_point_phasor(origin, radius, sides, level, use_emergent)
            
            new_level_faces = []
            angle_step = 360.0 / sides
            
            # For each existing face group, create rotated copies around new origin
            for i in range(sides):
                angle = angle_step * i
                
                for face in current_level_faces:
                    # Copy and rotate around new origin
                    rotated_face = self.copy_and_rotate_face(face, origin, angle)
                    rotated_face.level = level
                    self.faces.append(rotated_face)
                    new_level_faces.append(rotated_face)
            
            self.level_groups.append(new_level_faces)
            current_level_faces = new_level_faces
            
            elapsed = time.time() - level_start
            logging.info(f"Level {level} (phasor) generated: {len(new_level_faces)} faces in {elapsed:.3f}s")
        
        total_time = time.time() - start_time
        logging.info(f"✅ Phasor generation complete: {len(self.faces)} total faces in {total_time:.3f}s")
    
    def visualize_plotly(self, title: str = "PDCo Space Field 3D") -> go.Figure:
        """
        Create interactive 3D visualization with Plotly
        """
        fig = go.Figure()
        
        # Add faces as mesh
        for level_idx, level_faces in enumerate(self.level_groups):
            # Sample faces to avoid overload (take every Nth face)
            sample_rate = max(1, len(level_faces) // 500)
            sampled_faces = level_faces[::sample_rate]
            
            for face in sampled_faces:
                # Extract vertex coordinates
                x = [v.x for v in face.vertices] + [face.vertices[0].x]
                y = [v.y for v in face.vertices] + [face.vertices[0].y]
                z = [v.z for v in face.vertices] + [face.vertices[0].z]
                
                # Face as line loop
                fig.add_trace(go.Scatter3d(
                    x=x, y=y, z=z,
                    mode='lines',
                    line=dict(color=f'rgba({100 + level_idx * 30},{150},{255 - level_idx * 30},0.3)', width=1),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Add pattern edges
        if self.edges:
            sample_rate = max(1, len(self.edges) // 1000)
            for edge in self.edges[::sample_rate]:
                fig.add_trace(go.Scatter3d(
                    x=[edge[0].x, edge[1].x],
                    y=[edge[0].y, edge[1].y],
                    z=[edge[0].z, edge[1].z],
                    mode='lines',
                    line=dict(color='rgba(255,100,100,0.5)', width=2),
                    showlegend=False,
                    hoverinfo='skip'
                ))
        
        # Layout
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='data',
                bgcolor='rgba(0,0,0,1)'
            ),
            showlegend=False,
            paper_bgcolor='black',
            font=dict(color='white')
        )
        
        return fig
    
    def export_json(self, filepath: str) -> None:
        """Export geometry to JSON"""
        data = {
            "faces": [
                {
                    "vertices": [v.to_tuple() for v in face.vertices],
                    "level": face.level,
                    "pattern": face.pattern_type
                }
                for face in self.faces
            ],
            "edges": [
                [e[0].to_tuple(), e[1].to_tuple()]
                for e in self.edges
            ],
            "metadata": {
                "total_faces": len(self.faces),
                "total_edges": len(self.edges),
                "levels": len(self.level_groups)
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logging.info(f"Exported to {filepath}")
    
    def calculate_spectral_signature(self, sides: int, levels: int) -> dict:
        """
        Calculate spectral metrics for cognitive resonance streaming
        
        This is the CLOSED-LOOP CONNECTION to KayGee's reasoning engine:
        - dominantFreq: Harmonic frequency (sides^levels / geometric series)
        - phaseCoherence: Current rotation lock state (cos(global_angle))
        
        When phaseCoherence → 1.0: Perfect harmonic alignment
        When phaseCoherence < 0.5: Cognitive turbulence
        """
        # Dominant frequency calculation (harmonic accumulation)
        # Formula from JS visualizer: sides^(levels-1) / 2^(levels-2)
        if levels <= 1:
            dominant_freq = sides
        else:
            numerator = sides ** (levels - 1)
            denominator = 2 ** (levels - 2)
            dominant_freq = numerator / denominator
        
        # Phase coherence (PLL lock indicator)
        phase_coherence = abs(math.cos(self.global_angle))
        
        # Spectral width (uncertainty measure)
        spectral_width = sides * levels  # Simple metric: more dimensions = wider spectrum
        
        return {
            "timestamp": time.time(),
            "levels": levels,
            "sides": sides,
            "dominantFreq": dominant_freq,
            "phaseCoherence": phase_coherence,
            "spectralWidth": spectral_width,
            "globalAngle": self.global_angle,
            "emergentMode": self.emergent_rotation
        }
    
    def update_animation_state(self, delta_time: float = 0.016) -> None:
        """
        Update PLL animation state
        
        Mirrors JS animate() loop:
        globalAngle += rotationSpeed * (emergent ? phase_damping : 1.0)
        
        This is the PHASE-LOCKED OSCILLATOR - prevents runaway rotation
        """
        damping = self.phase_damping if self.emergent_rotation else 1.0
        self.global_angle += self.rotation_speed * damping
        
        # Wrap angle to [0, 2π]
        self.global_angle = self.global_angle % (2 * math.pi)


# ============================================================================
# BATCH GENERATOR (Mirrors Ruby batch_generate)
# ============================================================================

class BatchGenerator:
    """
    Batch generator matching Ruby extension functionality
    Automatically determines optimal levels for each dimension
    """
    
    @staticmethod
    def is_valid_dimension(n: int) -> bool:
        """
        Check if dimension produces terminating decimal for 360/n
        Matches Ruby: def self.is_valid_dimension(n)
        """
        num = 360
        den = n
        g = math.gcd(num, den)
        num //= g
        den //= g
        
        # Check if denominator only has factors of 2 and 5
        while den % 2 == 0:
            den //= 2
        while den % 5 == 0:
            den //= 5
        
        return den == 1
    
    @staticmethod
    def generate_valid_dimensions(min_dim: int = 3, max_dim: int = 360) -> List[int]:
        """
        Generate all valid dimensions in range
        Matches Ruby: def self.generate_valid_dimensions
        """
        valid = []
        for n in range(min_dim, max_dim + 1):
            if BatchGenerator.is_valid_dimension(n):
                valid.append(n)
        return valid
    
    @staticmethod
    def max_level_for_dimension(sides: int, max_outer_polygons: int = 500_000) -> int:
        """
        Calculate maximum safe level based on face count
        Matches Ruby: def self.max_level_for_dimension(sides, max_outer_polygons)
        
        outer_gons = sides^level
        Find largest level where sides^level <= max_outer_polygons
        """
        level = 1
        while True:
            outer_gons = sides ** level
            if outer_gons > max_outer_polygons:
                break
            level += 1
        return level - 1
    
    @staticmethod
    def batch_generate(output_dir: str = "output", start_pct: float = 0, end_pct: float = 100, 
                       patterns: List[str] = ["CC"], visualize: bool = False) -> None:
        """
        Batch generate space fields for multiple dimensions
        Matches Ruby: def self.batch_generate
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        valid_dims = BatchGenerator.generate_valid_dimensions()
        total_dims = len(valid_dims)
        
        # Select dimension range based on percentages
        start_idx = int(total_dims * (start_pct / 100.0))
        end_idx = int(total_dims * (end_pct / 100.0))
        selected_dims = valid_dims[start_idx:end_idx]
        
        logging.info(f"Batch generation: {len(selected_dims)} dimensions, patterns: {patterns}")
        
        total_generated = 0
        start_time = time.time()
        
        for sides in selected_dims:
            max_level = BatchGenerator.max_level_for_dimension(sides)
            dim_angle = 360.0 / sides
            
            logging.info(f"Dimension {sides} (angle: {dim_angle:.2f}°): max level {max_level}")
            
            for pattern in patterns:
                # Generate parameter string matching Ruby format
                param_str = f"O{sides}{pattern}xx{max_level}"
                
                # Generate space field
                field = SpaceField3D()
                field.generate_levels(radius=1.0, sides=sides, max_levels=max_level, pattern=pattern)
                
                # Export JSON
                json_path = output_path / f"{param_str}.json"
                field.export_json(str(json_path))
                
                # Optional visualization
                if visualize and total_generated < 5:  # Only visualize first few
                    fig = field.visualize_plotly(title=param_str)
                    html_path = output_path / f"{param_str}.html"
                    fig.write_html(str(html_path))
                    logging.info(f"  Visualization saved: {html_path}")
                
                total_generated += 1
        
        elapsed = time.time() - start_time
        logging.info(f"✅ Batch complete: {total_generated} fields generated in {elapsed:.1f}s")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution matching Ruby UI flow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDCo Space Field 3D Generator")
    parser.add_argument("--sides", type=int, default=4, help="Number of polygon sides (dimension)")
    parser.add_argument("--levels", type=int, default=3, help="Recursion depth")
    parser.add_argument("--pattern", type=str, default="CC", choices=["CC", "MSC"], help="Pattern type")
    parser.add_argument("--radius", type=float, default=1.0, help="Base radius")
    parser.add_argument("--output", type=str, default="space_field.html", help="Output HTML file")
    parser.add_argument("--batch", action="store_true", help="Run batch generation")
    parser.add_argument("--batch-dir", type=str, default="output", help="Batch output directory")
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch mode
        BatchGenerator.batch_generate(
            output_dir=args.batch_dir,
            start_pct=0,
            end_pct=10,  # Generate first 10% of dimensions
            patterns=["CC", "MSC"],
            visualize=True
        )
    else:
        # Single generation mode
        logging.info("="*70)
        logging.info("PDCo Space Field 3D Generator - Python Port")
        logging.info("="*70)
        
        field = SpaceField3D()
        field.generate_levels(
            radius=args.radius,
            sides=args.sides,
            max_levels=args.levels,
            pattern=args.pattern
        )
        
        # Create visualization
        param_str = f"O{args.sides}{args.pattern}xx{args.levels}"
        fig = field.visualize_plotly(title=f"Space Field: {param_str}")
        fig.write_html(args.output)
        
        logging.info(f"✅ Visualization saved to: {args.output}")
        logging.info(f"   Open in browser to interact")
        
        # Export JSON too
        json_path = args.output.replace('.html', '.json')
        field.export_json(json_path)


if __name__ == "__main__":
    main()
