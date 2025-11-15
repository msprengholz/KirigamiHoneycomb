"""Utilities for generating kirigami honeycomb folding line diagrams."""

from .cross_section import (
    CrossSectionSamples,
    sample_cross_section,
    linearize_cross_section,
)
from .fold_pattern import FoldPattern, compute_fold_pattern
from .honeycomb import HexGrid, generate_hex_grid

__all__ = [
    "CrossSectionSamples",
    "sample_cross_section",
    "linearize_cross_section",
    "FoldPattern",
    "compute_fold_pattern",
    "HexGrid",
    "generate_hex_grid",
]
