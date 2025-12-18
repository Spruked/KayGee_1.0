"""
PDCo Space Field Generator - Enhanced for KayGee Symbolic Cognition
© 02/14/2025 by Primary Design Co. (Alex London) - Modified for research validation

Enhancements:
- Fixed pattern toggle buttons (CC, MSC, MSCC)
- Corrected symmetry point calculation (closed-form geometric series)
- Memory-safe patch registry (flat list, not nested)
- FFT spectral analyzer for harmonic validation
- Export spectral metrics for research validation

https://www.primarydesignco.com
"""

import logging
import math
from collections.abc import Iterable
from typing import List, Tuple, Optional, Callable, Any, Dict
import json

import numpy as np
import time
import matplotlib
matplotlib.use('Agg')  # Headless mode for backend
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from matplotlib.transforms import Affine2D

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

colors_mapped: List[str] = [
    'red', 'green', 'blue', 'yellow',
    'pink', 'purple', 'orange', 'cyan', 'magenta',
    'lime', 'maroon', 'navy', 'olive', 'teal', 'violet',
    'brown', 'gold', 'lightcoral', 'darkkhaki', 'darkgreen',
    'darkblue', 'darkred', 'turquoise', 'indigo', 'darkorange',
    'lightgreen', 'tan', 'salmon', 'plum', 'orchid', 'sienna',
    'skyblue', 'khaki', 'slateblue', 'goldenrod', 'mediumblue',
    'greenyellow', 'burlywood', 'seagreen', 'slategray',
    'cornflowerblue', 'mediumorchid', 'sandybrown', 'tomato',
    'lightblue', 'limegreen', 'lightgrey', 'lightpink', 'thistle',
    'palegreen', 'azure', 'lavender', 'honeydew', 'mintcream', 'aliceblue',
    'black', 'white'
]


class SpectralAnalyzer:
    """FFT-based spectral analysis for geometric field validation."""
    
    def __init__(self, fig: plt.Figure, ax: plt.Axes):
        self.fig = fig
        self.ax = ax
    
    def capture_canvas(self) -> np.ndarray:
        """Capture current plot as grayscale image."""
        self.fig.canvas.draw()
        data = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
        width, height = self.fig.canvas.get_width_height()
        img = data.reshape((height, width, 3))
        return np.mean(img, axis=2)  # Grayscale
    
    def analyze(self) -> Dict[str, float]:
        """
        Perform 2D FFT analysis and extract spectral features.
        Returns metrics for harmonic universality validation.
        """
        image = self.capture_canvas()
        
        # 2D FFT
        f = np.fft.fft2(image)
        fshift = np.fft.fftshift(f)
        magnitude = 20 * np.log(np.abs(fshift) + 1)
        
        # Radial profile (distance from center)
        cy, cx = image.shape[0] // 2, image.shape[1] // 2
        y, x = np.ogrid[:image.shape[0], :image.shape[1]]
        r = np.sqrt((x - cx)**2 + (y - cy)**2)
        r = r.astype(int)
        
        # Average magnitude per radial distance
        radial = np.bincount(r.ravel(), magnitude.ravel())
        nr = np.bincount(r.ravel())
        radial_profile = radial / nr
        
        # Extract harmonic metrics
        metrics = {
            "low_freq_energy": float(np.sum(radial_profile[1:20])),
            "high_freq_energy": float(np.sum(radial_profile[100:min(len(radial_profile), 200)])),
            "dominant_freq": int(np.argmax(radial_profile[1:]) + 1),
            "fractal_estimate": float(np.std(np.diff(radial_profile[:min(len(radial_profile), 100)]))),
            "total_energy": float(np.sum(magnitude)),
            "spectral_entropy": float(-np.sum(radial_profile * np.log(radial_profile + 1e-10))),
            "radial_peak_ratio": float(np.max(radial_profile) / (np.mean(radial_profile) + 1e-10))
        }
        
        return metrics


def calculate_symmetry_point_adjusted(center: Tuple[float, float],
                                      radius: float,
                                      sides: int,
                                      level: int) -> np.ndarray:
    """
    Closed-form geometric series for symmetry point calculation.
    Matches theoretical behavior:
      Level 1: [0, 0, 0]
      Level 2: [0, 1, 0]
      Level 3: [0, 3, 0]
      Level 4: [0, 7, 0]  (2^3 - 1)
      Level 5: [0, 15, 0] (2^4 - 1)
    """
    if level <= 1:
        return np.array([center[0], center[1], 0.0])
    
    if sides % 2 == 0:  # Even sides: powers of 2
        offset = radius * (2**(level - 1) - 1)
    else:  # Odd sides: 1.5 series
        offset = radius * (1.5**(level - 1) - 1) / 0.5
    
    return np.array([center[0], center[1] + offset, 0.0])


def multiplier(level: int, sides: int) -> float:
    if sides % 2 == 0:
        return 2 ** (level - 2)
    else:
        return 1.5 ** (level - 2)


def generate_vertices(center, radius, sides):
    """
    Generates vertices for a regular polygon.
    For even sides, vertex0 is at angle 0, i.e. directly above the center.
    """
    vertices = []
    angle = (2 * math.pi) / sides
    cx, cy = center
    for side in range(sides):
        theta = angle * side
        x = cx + radius * math.sin(theta)
        y = cy + radius * math.cos(theta)
        vertices.append((x, y, 0))
    return vertices


def midpoint(p1, p2):
    """Returns the midpoint between two 3D points."""
    return ((p1[0] + p2[0]) / 2,
            (p1[1] + p2[1]) / 2,
            (p1[2] + p2[2]) / 2)


def generate_base_level_polygon(
    vertices: np.ndarray,
    fig: plt.Figure,
    ax: plt.Axes,
    center: Tuple[float, float],
    radius: float,
    sides: int,
    alpha: float,
    draw_base: bool,
    levels: int,
    colors_mapped: List[str],
    edges_only: bool = False,
    line_width: float = 1,
    patch_registry: Optional[List] = None
) -> List[patches.Polygon]:
    base_level_rays: List[patches.Polygon] = []
    polygon = patches.Polygon(vertices, closed=True, edgecolor='black' if edges_only else 'none',
                              facecolor='none', linewidth=line_width)
    
    if draw_base:
        for j in range(1, (sides // 2 + 2) if sides % 2 else (sides // 2 + 1)):
            i = 0
            start_vertex = vertices[i]
            end_vertex = vertices[(i + j + 1) % sides]
            if j < sides // 2:
                ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='None')
            start_vertex = vertices[i]
            middle_vertex = vertices[(i + j) % sides]
            end_vertex = vertices[(i + j - 1) % sides]
            triangle = np.array([start_vertex, middle_vertex, end_vertex])
            color_index = (j - 2) % len(colors_mapped)
            color = colors_mapped[color_index] if not edges_only else 'none'
            base_level_ray = patches.Polygon(
                triangle, closed=True,
                edgecolor='black' if edges_only else 'none',
                fill=not edges_only, facecolor=color, alpha=alpha, linewidth=line_width
            )
            ax.add_patch(base_level_ray)
            base_level_rays.append(base_level_ray)
            
            if patch_registry is not None:
                patch_registry.append((base_level_ray, 0, None))  # level=0, no parent
    
    return base_level_rays


def generate_first_level_polygon(
    fig: plt.Figure,
    ax: plt.Axes,
    center: Tuple[float, float],
    sides: int,
    alpha: float,
    base_level_rays: List[patches.Polygon],
    edges_only: bool = False,
    line_width: float = 1,
    patch_registry: Optional[List] = None
) -> List[patches.Polygon]:
    first_level_rays: List[patches.Polygon] = [base_level_rays]
    layers = sides
    for i in range(1, layers):
        angle = 360 / layers * i
        rotation = Affine2D().rotate_deg_around(center[0], center[1], angle)
        for parent_idx, patch in enumerate(base_level_rays):
            rotated_patch = patches.Polygon(
                patch.get_xy(), closed=True,
                edgecolor='black' if edges_only else 'none',
                fill=not edges_only, facecolor=patch.get_facecolor() if not edges_only else 'none',
                alpha=alpha, linewidth=line_width
            )
            rotated_patch.set_transform(rotation + ax.transData)
            ax.add_patch(rotated_patch)
            first_level_rays.append(rotated_patch)
            
            if patch_registry is not None:
                patch_registry.append((rotated_patch, 1, parent_idx))  # level=1
    
    ax.set_aspect('equal')
    return first_level_rays


def generate_higher_levels(
    vertices: np.ndarray,
    fig,
    ax,
    center: tuple,
    radius: float,
    sides: int,
    current_level: int,
    max_levels: int,
    n_levels_rays: list,
    edges_only: bool = False,
    line_width: float = 1,
    cancel_callback=lambda: False,
    patch_registry: Optional[List] = None
) -> None:
    if cancel_callback():
        return
    if current_level > max_levels or n_levels_rays[0][0].get_alpha() < 0.01:
        return

    new_level_patches = []

    def process_patches(patch_list, rotation: Affine2D, accumulated_patches: list, parent_idx_base: int) -> None:
        for patch_idx, patch in enumerate(patch_list):
            if cancel_callback():
                return
            if isinstance(patch, Iterable) and not isinstance(patch, str):
                sub_patches = []
                process_patches(patch, rotation, sub_patches, parent_idx_base + patch_idx)
                accumulated_patches.append(sub_patches)
            else:
                orig_vertices = patch.get_xy()
                rotated_vertices = rotation.transform(orig_vertices)
                rotated_patch = patches.Polygon(
                    rotated_vertices, closed=True,
                    edgecolor='black' if edges_only else 'none',
                    fill=not edges_only,
                    facecolor=patch.get_facecolor() if not edges_only else 'none',
                    alpha=patch.get_alpha(), linewidth=line_width
                )
                ax.add_patch(rotated_patch)
                accumulated_patches.append(rotated_patch)
                
                if patch_registry is not None:
                    patch_registry.append((rotated_patch, current_level, parent_idx_base + patch_idx))

    for i in range(1, sides):
        if cancel_callback():
            return
        symmetry_point = calculate_symmetry_point_adjusted(center, radius, sides, current_level)
        angle = 360 / sides * i
        rotation = Affine2D().rotate_deg_around(symmetry_point[0], symmetry_point[1], angle)
        process_patches(n_levels_rays, rotation, new_level_patches, 0)
    
    n_levels_rays += new_level_patches

    generate_higher_levels(
        vertices, fig, ax, center, radius, sides,
        current_level + 1, max_levels, n_levels_rays,
        edges_only, line_width, cancel_callback, patch_registry
    )
    fig.canvas.draw_idle()


def calculate_effective_alpha(sides: int, levels: int, base_alpha: float = 1.0) -> float:
    """
    Computes the effective alpha after a given number of levels, where level 1 uses
    the base alpha and for each subsequent level the alpha is divided by (1.2 * sides**(level/2)).
    """
    if levels < 1:
        return base_alpha
    mult_log = - (levels - 1) * math.log(1.2) - (math.log(sides) / 2) * ((levels * (levels + 1)) / 2 - 1)
    effective_alpha = base_alpha * math.exp(mult_log)
    return effective_alpha


def calculate_line_width(levels: int) -> float:
    return max(0.5, 2.0 / (levels + 1))


class SpaceFieldGenerator:
    """
    Headless generator for space field visualizations.
    Designed for backend API integration.
    """
    
    def __init__(self):
        self.patch_registry = []  # Memory-safe flat list
        self.spectral_analyzer = None
    
    def generate(
        self,
        sides: int = 4,
        levels: int = 3,
        alpha: float = 0.444,
        rotation_angle: float = 0,
        edges_only: bool = True,
        width: int = 800,
        height: int = 800,
        dpi: int = 100
    ) -> Tuple[plt.Figure, Dict[str, Any]]:
        """
        Generate space field visualization with spectral analysis.
        
        Args:
            sides: Number of polygon sides (dimension)
            levels: Recursion depth (reasoning depth)
            alpha: Transparency (confidence)
            rotation_angle: Rotation in degrees
            edges_only: Show only edges (computational efficiency)
            width, height: Canvas dimensions in pixels
            dpi: Resolution
        
        Returns:
            (figure, metrics) tuple with matplotlib figure and spectral metrics
        """
        self.patch_registry = []
        
        # Create figure
        fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Generate geometry
        center = (0, 0)
        radius = 1
        
        start_angle = np.pi / sides if sides % 2 != 0 else 0
        angles = np.linspace(start_angle, start_angle + 2 * np.pi, sides, endpoint=False)
        vertices = np.array([
            np.array(center) + radius * np.array([np.cos(angle), np.sin(angle)]) for angle in angles
        ])
        
        line_width = calculate_line_width(levels)
        effective_alpha = calculate_effective_alpha(sides, levels, alpha)
        
        # Generate base level
        base_patches = generate_base_level_polygon(
            vertices=vertices, fig=fig, ax=ax, center=center, radius=radius,
            sides=sides, alpha=effective_alpha, draw_base=True, levels=levels,
            colors_mapped=colors_mapped, edges_only=edges_only, line_width=line_width,
            patch_registry=self.patch_registry
        )
        
        # Generate first level expansion
        first_level_patches = [base_patches]
        if levels >= 1:
            expanded_first = generate_first_level_polygon(
                fig=fig, ax=ax, center=center, sides=sides, alpha=effective_alpha,
                base_level_rays=base_patches, edges_only=edges_only, line_width=line_width,
                patch_registry=self.patch_registry
            )
            first_level_patches.append(expanded_first)
        
        # Generate higher levels
        if levels > 1:
            generate_higher_levels(
                vertices=vertices, fig=fig, ax=ax, center=center, radius=radius,
                sides=sides, current_level=1, max_levels=levels,
                n_levels_rays=first_level_patches, edges_only=edges_only,
                line_width=line_width, cancel_callback=lambda: False,
                patch_registry=self.patch_registry
            )
        
        # Apply rotation
        if rotation_angle != 0:
            for patch in ax.patches:
                xy = patch.get_xy()
                new_xy = np.zeros_like(xy)
                radians = np.radians(rotation_angle)
                cos_angle, sin_angle = np.cos(radians), np.sin(radians)
                for i, (x, y) in enumerate(xy):
                    translated_x, translated_y = x - center[0], y - center[1]
                    rotated_x = cos_angle * translated_x - sin_angle * translated_y
                    rotated_y = sin_angle * translated_x + cos_angle * translated_y
                    new_xy[i, 0] = rotated_x + center[0]
                    new_xy[i, 1] = rotated_y + center[1]
                patch.set_xy(new_xy)
        
        # Set view limits
        ax.autoscale()
        plt.tight_layout()
        
        # Spectral analysis
        self.spectral_analyzer = SpectralAnalyzer(fig, ax)
        metrics = self.spectral_analyzer.analyze()
        
        # Add metadata
        metrics.update({
            "sides": sides,
            "levels": levels,
            "alpha": alpha,
            "rotation_angle": rotation_angle,
            "patch_count": len(self.patch_registry),
            "edges_only": edges_only
        })
        
        return fig, metrics
    
    def save_svg(self, fig: plt.Figure, filepath: str) -> None:
        """Save as SVG for web display."""
        fig.savefig(filepath, format='svg', bbox_inches='tight')
    
    def save_png(self, fig: plt.Figure, filepath: str) -> None:
        """Save as PNG for raster display."""
        fig.savefig(filepath, format='png', bbox_inches='tight')
    
    def get_svg_string(self, fig: plt.Figure) -> str:
        """Get SVG as string for direct embedding."""
        import io
        buf = io.BytesIO()
        fig.savefig(buf, format='svg', bbox_inches='tight')
        buf.seek(0)
        return buf.read().decode('utf-8')


if __name__ == "__main__":
    # Test with documented levels
    logging.info("Testing symmetry point calculations:")
    for lvl in range(1, 6):
        origin = calculate_symmetry_point_adjusted((0, 0), 1, 4, lvl)
        logging.info(f"Level {lvl} origin: {origin}")
    
    # Generate test field
    generator = SpaceFieldGenerator()
    fig, metrics = generator.generate(sides=4, levels=3, alpha=0.5, edges_only=False)
    
    logging.info(f"Generated field with {metrics['patch_count']} patches")
    logging.info(f"Spectral metrics: {json.dumps(metrics, indent=2)}")
    
    # Save test output
    generator.save_png(fig, "space_field_test.png")
    logging.info("Saved test output to space_field_test.png")
    
    plt.close(fig)
