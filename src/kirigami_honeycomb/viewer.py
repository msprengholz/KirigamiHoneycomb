"""Simple 3D viewer for inspecting mesh slicing directions."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh

AXES = {"x": np.array([1.0, 0.0, 0.0]), "y": np.array([0.0, 1.0, 0.0]), "z": np.array([0.0, 0.0, 1.0])}


def _ensure_mesh(mesh_or_path: trimesh.Trimesh | trimesh.Scene | str | Path) -> trimesh.Trimesh:
    if isinstance(mesh_or_path, (str, Path)):
        mesh = trimesh.load_mesh(mesh_or_path)
    else:
        mesh = mesh_or_path
    if isinstance(mesh, trimesh.Scene):
        geom = [g for g in mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not geom:
            raise ValueError("Scene does not contain any mesh geometry")
        mesh = trimesh.util.concatenate(geom)
    if not isinstance(mesh, trimesh.Trimesh):  # pragma: no cover - defensive
        raise TypeError("Unsupported mesh type")
    return mesh


def launch_mesh_viewer(
    mesh_or_path: trimesh.Trimesh | trimesh.Scene | str | Path,
    *,
    axis: str = "x",
    height_axis: str = "z",
    axis_length: float | None = None,
) -> None:
    """Display the mesh with highlighted slicing and height directions."""

    mesh = _ensure_mesh(mesh_or_path)
    vertices = mesh.vertices
    faces = mesh.faces
    if axis not in AXES or height_axis not in AXES:
        raise ValueError("Axis and height_axis must be one of 'x', 'y', or 'z'")

    centroid = vertices.mean(axis=0)
    extents = mesh.extents
    if axis_length is None:
        axis_length = float(np.max(extents))

    figure = plt.figure()
    ax = figure.add_subplot(111, projection="3d")
    tris = Poly3DCollection(vertices[faces], alpha=0.4, facecolor="#4c72b0", linewidths=0.1)
    tris.set_edgecolor("k")
    ax.add_collection3d(tris)
    ax.auto_scale_xyz(vertices[:, 0], vertices[:, 1], vertices[:, 2])

    def _plot_axis(direction: np.ndarray, color: str, label: str) -> None:
        points = np.vstack([
            centroid - direction * axis_length * 0.5,
            centroid + direction * axis_length * 0.5,
        ])
        ax.plot(points[:, 0], points[:, 1], points[:, 2], color=color, linewidth=3, label=label)
        ax.text(
            points[-1, 0],
            points[-1, 1],
            points[-1, 2],
            label,
            color=color,
            fontsize=12,
            weight="bold",
        )

    _plot_axis(AXES[axis], "#dd8452", f"slicing axis ({axis})")
    _plot_axis(AXES[height_axis], "#55a868", f"height axis ({height_axis})")

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.legend(loc="upper right")
    ax.set_title("Mesh slicing direction preview")
    plt.tight_layout()
    plt.show()


__all__ = ["launch_mesh_viewer"]
