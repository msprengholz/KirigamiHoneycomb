"""Command line interface for generating kirigami honeycomb FLDs."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Callable

import numpy as np

from .cross_section import linearize_cross_section, sample_cross_section
from .fold_pattern import compute_fold_pattern
from .gui import launch_cut_editor
from .mesh_io import sample_mesh_perforation_lines
from .svg import export_fold_diagram
from .viewer import launch_mesh_viewer

FunctionFactory = Callable[[float], float]


def _parse_function(expression: str) -> FunctionFactory:
    """Create a math-aware lambda from the provided expression."""

    allowed_names = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
    allowed_names.update({"np": np, "numpy": np})

    def func(x: float) -> float:
        return eval(expression, {"__builtins__": {}}, {**allowed_names, "x": x})

    return func


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upper", help="Expression describing the upper cross-section curve")
    parser.add_argument("lower", help="Expression describing the lower cross-section curve")
    parser.add_argument("output", help="Path to the SVG file that will be generated")
    parser.add_argument("--domain", nargs=2, type=float, metavar=("START", "END"), default=(0.0, 200.0))
    parser.add_argument("--cell-size", type=float, default=20.0, help="Honeycomb cell size in millimetres")
    parser.add_argument(
        "--linearise",
        action="store_true",
        help="Apply the foldable linear approximation before computing the fold pattern",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch an interactive cut editor before exporting the SVG.",
    )
    parser.add_argument(
        "--perforation-mesh",
        help="Optional mesh path used to derive perforation guide lines for 3D-aware output.",
    )
    parser.add_argument(
        "--perforation-axis",
        choices=("x", "y", "z"),
        default="x",
        help="Slicing axis used for deriving perforation lines from --perforation-mesh.",
    )
    parser.add_argument(
        "--perforation-height-axis",
        choices=("x", "y", "z"),
        default="z",
        help="Height axis used for deriving perforation lines from --perforation-mesh.",
    )
    parser.add_argument(
        "--perforation-spacing",
        type=float,
        default=None,
        help="Slice spacing for deriving perforations (defaults to cell_size/2).",
    )
    return parser


def build_mesh_viewer_parser() -> argparse.ArgumentParser:
    """Build parser for standalone mesh slicing direction preview."""

    parser = argparse.ArgumentParser(description="Launch a 3D mesh viewer for slicing setup.")
    parser.add_argument("mesh", help="Path to the mesh file to preview")
    parser.add_argument("--axis", choices=("x", "y", "z"), default="x", help="Slicing axis")
    parser.add_argument("--height-axis", choices=("x", "y", "z"), default="z", help="Height axis")
    parser.add_argument("--axis-length", type=float, default=None, help="Optional axis overlay length")
    return parser


def main(argv: list[str] | None = None) -> None:
    if argv and len(argv) > 0 and argv[0] == "view-mesh":
        viewer_args = build_mesh_viewer_parser().parse_args(argv[1:])
        launch_mesh_viewer(
            viewer_args.mesh,
            axis=viewer_args.axis,
            height_axis=viewer_args.height_axis,
            axis_length=viewer_args.axis_length,
        )
        return

    parser = build_parser()
    args = parser.parse_args(argv)

    upper = _parse_function(args.upper)
    lower = _parse_function(args.lower)

    samples = sample_cross_section(upper, lower, domain=tuple(args.domain), cell_size=args.cell_size)
    if args.linearise:
        samples = linearize_cross_section(samples)
    pattern = compute_fold_pattern(samples)
    output = Path(args.output)
    perforation_lines = None
    if args.perforation_mesh:
        perforation_lines = sample_mesh_perforation_lines(
            args.perforation_mesh,
            axis=args.perforation_axis,
            height_axis=args.perforation_height_axis,
            spacing=args.perforation_spacing,
            cell_size=args.cell_size,
        )
    if args.gui:
        launch_cut_editor(samples, pattern, output=output, perforation_lines=perforation_lines)
    else:
        export_fold_diagram(samples, pattern, output, perforation_lines=perforation_lines)


if __name__ == "__main__":  # pragma: no cover
    main()
