"""Utilities for generating kirigami honeycomb folding line diagrams."""

from .cross_section import (
    CrossSectionSamples,
    sample_cross_section,
    linearize_cross_section,
)
from .fold_pattern import FoldPattern, compute_fold_pattern
from .honeycomb import HexGrid, generate_hex_grid
from .mesh_io import load_mesh, sample_mesh_cross_section
from .viewer import launch_mesh_viewer

__all__ = [
    "CrossSectionSamples",
    "sample_cross_section",
    "linearize_cross_section",
    "FoldPattern",
    "compute_fold_pattern",
    "HexGrid",
    "generate_hex_grid",
    "load_mesh",
    "sample_mesh_cross_section",
    "launch_mesh_viewer",
]
