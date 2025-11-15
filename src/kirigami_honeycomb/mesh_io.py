"""Mesh ingestion utilities for kirigami honeycomb workflows."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import numpy as np
import trimesh

from .cross_section import CrossSectionSamples


AxisName = Literal["x", "y", "z"]

__all__ = ["load_mesh", "sample_mesh_cross_section"]


def load_mesh(path: str | Path, *, process: bool = True) -> trimesh.Trimesh:
    """Load a mesh from *path* using :mod:`trimesh`.

    Parameters
    ----------
    path:
        Location of the mesh file. Any format supported by ``trimesh`` may be
        supplied (e.g. OBJ, STL, PLY).
    process:
        Forwarded to :func:`trimesh.load`, enabling optional mesh processing
        such as normal generation and face merging.
    """

    mesh = trimesh.load_mesh(path, process=process)
    if isinstance(mesh, trimesh.Scene):  # pragma: no cover - defensive guard
        mesh = mesh.dump().sum()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Unsupported mesh type: {type(mesh)!r}")
    if mesh.is_empty:
        raise ValueError("Loaded mesh does not contain any geometry")
    return mesh


def sample_mesh_cross_section(
    mesh_or_path: trimesh.Trimesh | str | Path,
    *,
    axis: AxisName = "x",
    height_axis: AxisName = "z",
    spacing: float | None = None,
    cell_size: float = 20.0,
) -> CrossSectionSamples:
    """Slice a mesh into a :class:`CrossSectionSamples` representation.

    The mesh is sliced by planes orthogonal to ``axis``. For each slice the
    minimum and maximum coordinates along ``height_axis`` are captured to form
    the lower and upper envelope of the cross section.
    """

    mesh = load_mesh(mesh_or_path) if not isinstance(mesh_or_path, trimesh.Trimesh) else mesh_or_path

    axis_index = _axis_index(axis)
    height_index = _axis_index(height_axis)
    if axis_index == height_index:
        raise ValueError("axis and height_axis must refer to different dimensions")

    if cell_size <= 0:
        raise ValueError("cell_size must be greater than zero")
    if spacing is None:
        spacing = cell_size / 2.0
    if spacing <= 0:
        raise ValueError("spacing must be greater than zero")

    bounds = mesh.bounds
    start = bounds[0, axis_index]
    end = bounds[1, axis_index]
    if not np.isfinite(start) or not np.isfinite(end):
        raise ValueError("Mesh bounds must be finite")

    coordinates = _build_coordinates(start, end, spacing)
    if coordinates.size < 2:
        raise ValueError("Mesh extent along the selected axis is too small for the requested spacing")

    origin = mesh.centroid
    normal = np.zeros(3)
    normal[axis_index] = 1.0
    heights = coordinates - origin[axis_index]
    sections = mesh.section_multiplane(plane_origin=origin, plane_normal=normal, heights=heights)

    lower = np.full(coordinates.shape, np.nan, dtype=float)
    upper = np.full(coordinates.shape, np.nan, dtype=float)

    for index, section in enumerate(sections):
        if section is None or section.vertices.size == 0:
            continue
        vertices = _section_vertices_to_3d(section)
        upper[index] = float(np.max(vertices[:, height_index]))
        lower[index] = float(np.min(vertices[:, height_index]))

    lower = _interpolate_missing(lower, coordinates)
    upper = _interpolate_missing(upper, coordinates)

    if np.any(upper < lower):
        raise ValueError("Derived upper envelope dips below the lower envelope; check mesh orientation")

    return CrossSectionSamples(coordinates, upper, lower, cell_size)


def _axis_index(axis: AxisName) -> int:
    mapping = {"x": 0, "y": 1, "z": 2}
    try:
        return mapping[axis]
    except KeyError as exc:  # pragma: no cover - validated by typing
        raise ValueError(f"Unsupported axis '{axis}'") from exc


def _build_coordinates(start: float, end: float, spacing: float) -> np.ndarray:
    if end <= start:
        raise ValueError("Mesh bounds are degenerate along the slicing axis")
    epsilon = spacing * 1e-9
    return np.arange(start, end + epsilon, spacing, dtype=float)


def _interpolate_missing(values: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
    mask = np.isfinite(values)
    if mask.all():
        return values

    valid_indices = np.flatnonzero(mask)
    if valid_indices.size == 0:
        raise ValueError("No valid cross-section slices were produced from the mesh")

    interpolated = np.interp(coordinates, coordinates[valid_indices], values[valid_indices])
    return interpolated


def _section_vertices_to_3d(section: trimesh.path.Path2D | trimesh.path.Path3D) -> np.ndarray:
    vertices = section.vertices
    if vertices.ndim != 2:
        raise ValueError("Unexpected vertex array dimensionality for section output")
    if vertices.shape[1] == 3:
        return vertices

    if "to_3D" not in section.metadata:
        raise ValueError("Section data lacks the transformation to world coordinates")

    zeros = np.zeros((vertices.shape[0], 1), dtype=vertices.dtype)
    homogenous = np.hstack([vertices, zeros])
    return trimesh.transform_points(homogenous, section.metadata["to_3D"])

