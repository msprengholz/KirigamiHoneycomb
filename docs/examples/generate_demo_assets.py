"""Generate a sample mesh and folding line diagram for documentation."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from kirigami_honeycomb import compute_fold_pattern, sample_mesh_cross_section
from kirigami_honeycomb.svg import export_fold_diagram


def _wave_height(x: float, y: float, length: float, width: float) -> float:
    """Smooth height field resembling a gently twisted wing panel."""

    wave_x = np.sin(2.0 * np.pi * x / length)
    wave_y = np.cos(np.pi * y / width)
    return 12.0 * wave_x * wave_y + 6.0 * np.sin(np.pi * x / (length / 3.0))


def build_wave_panel_mesh(
    *,
    length: float = 240.0,
    width: float = 90.0,
    thickness: float = 8.0,
    segments_x: int = 60,
    segments_y: int = 18,
) -> trimesh.Trimesh:
    """Create a closed mesh with a wavy upper surface."""

    xs = np.linspace(0.0, length, segments_x + 1)
    ys = np.linspace(-width / 2.0, width / 2.0, segments_y + 1)

    grid_w = segments_y + 1

    top_vertices = []
    bottom_vertices = []
    for x in xs:
        for y in ys:
            z = _wave_height(x, y, length, width)
            top_vertices.append((x, y, z))
            bottom_vertices.append((x, y, z - thickness))

    top_vertices = np.asarray(top_vertices, dtype=float)
    bottom_vertices = np.asarray(bottom_vertices, dtype=float)
    vertices = np.vstack([top_vertices, bottom_vertices])

    faces: list[list[int]] = []

    def quad(a: int, b: int, c: int, d: int, *, flip: bool = False) -> None:
        if flip:
            faces.append([a, c, b])
            faces.append([b, c, d])
        else:
            faces.append([a, b, c])
            faces.append([b, d, c])

    for ix in range(segments_x):
        for iy in range(segments_y):
            i0 = ix * grid_w + iy
            i1 = i0 + 1
            i2 = i0 + grid_w
            i3 = i2 + 1
            quad(i0, i1, i2, i3)  # top surface
            quad(
                i0 + top_vertices.shape[0],
                i2 + top_vertices.shape[0],
                i1 + top_vertices.shape[0],
                i3 + top_vertices.shape[0],
                flip=True,
            )  # bottom surface

    def side_strip(indices: list[int]) -> None:
        for idx in range(len(indices) - 1):
            top_a = indices[idx]
            top_b = indices[idx + 1]
            bottom_a = top_a + top_vertices.shape[0]
            bottom_b = top_b + top_vertices.shape[0]
            quad(top_a, top_b, bottom_a, bottom_b)

    leading_edge = [iy for iy in range(grid_w)]
    trailing_edge = [segments_x * grid_w + iy for iy in range(grid_w)]
    span_min = [ix * grid_w for ix in range(segments_x + 1)]
    span_max = [ix * grid_w + (grid_w - 1) for ix in range(segments_x + 1)]

    side_strip(leading_edge)
    side_strip(trailing_edge)
    side_strip(span_min)
    side_strip(span_max)

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces, dtype=np.int64), process=True)
    mesh.remove_duplicate_faces()
    mesh.remove_unreferenced_vertices()
    return mesh


def main() -> None:
    root = Path(__file__).parent
    mesh_path = root / "wave_panel_demo.stl"
    svg_path = root / "wave_panel_demo.svg"
    png_path = root / "wave_panel_demo.png"

    mesh = build_wave_panel_mesh()
    mesh.export(mesh_path)

    samples = sample_mesh_cross_section(mesh, axis="x", height_axis="z", cell_size=20.0)
    pattern = compute_fold_pattern(samples)
    export_fold_diagram(samples, pattern, svg_path)
    export_fold_diagram(samples, pattern, png_path)

    print(f"Wrote sample mesh to {mesh_path.relative_to(Path.cwd())}")
    print(f"Wrote fold diagram to {svg_path.relative_to(Path.cwd())}")
    print(f"Wrote PNG preview to {png_path.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
