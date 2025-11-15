"""Command line interface for generating kirigami honeycomb FLDs."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Callable

import numpy as np

from .cross_section import linearize_cross_section, sample_cross_section
from .fold_pattern import compute_fold_pattern
from .mesh_io import sample_mesh_cross_section
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
    return parser


def build_mesh_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Slice a mesh into a fold pattern")
    parser.add_argument("mesh", help="Path to the mesh to slice (OBJ, STL, PLY, ...)")
    parser.add_argument("output", help="Path to the SVG file that will be generated")
    parser.add_argument("--axis", choices=("x", "y", "z"), default="x", help="Axis along which to slice the mesh")
    parser.add_argument(
        "--height-axis",
        choices=("x", "y", "z"),
        default="z",
        help="Axis representing the cross-section height envelope",
    )
    parser.add_argument(
        "--spacing",
        type=float,
        default=None,
        help="Spacing between mesh slicing planes (defaults to half the cell size)",
    )
    parser.add_argument("--cell-size", type=float, default=20.0, help="Honeycomb cell size in millimetres")
    parser.add_argument(
        "--linearise",
        action="store_true",
        help="Apply the foldable linear approximation before computing the fold pattern",
    )
    return parser


def build_mesh_viewer_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview mesh slicing directions")
    parser.add_argument("mesh", help="Path to the mesh to visualise")
    parser.add_argument("--axis", choices=("x", "y", "z"), default="x")
    parser.add_argument("--height-axis", choices=("x", "y", "z"), default="z")
    parser.add_argument(
        "--axis-length",
        type=float,
        default=None,
        help="Optional length for the highlighted axes (defaults to mesh diagonal)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args_list = list(argv) if argv is not None else None

    if args_list and args_list[0] == "mesh":
        mesh_parser = build_mesh_parser()
        mesh_args = mesh_parser.parse_args(args_list[1:])
        samples = sample_mesh_cross_section(
            mesh_args.mesh,
            axis=mesh_args.axis,
            height_axis=mesh_args.height_axis,
            spacing=mesh_args.spacing,
            cell_size=mesh_args.cell_size,
        )
        if mesh_args.linearise:
            samples = linearize_cross_section(samples)
        pattern = compute_fold_pattern(samples)
        output = Path(mesh_args.output)
        export_fold_diagram(samples, pattern, output)
        return

    if args_list and args_list[0] == "viewer":
        viewer_parser = build_mesh_viewer_parser()
        viewer_args = viewer_parser.parse_args(args_list[1:])
        launch_mesh_viewer(
            viewer_args.mesh,
            axis=viewer_args.axis,
            height_axis=viewer_args.height_axis,
            axis_length=viewer_args.axis_length,
        )
        return

    parser = build_parser()
    args = parser.parse_args(args_list)

    upper = _parse_function(args.upper)
    lower = _parse_function(args.lower)

    samples = sample_cross_section(upper, lower, domain=tuple(args.domain), cell_size=args.cell_size)
    if args.linearise:
        samples = linearize_cross_section(samples)
    pattern = compute_fold_pattern(samples)
    output = Path(args.output)
    export_fold_diagram(samples, pattern, output)


if __name__ == "__main__":  # pragma: no cover
    main()
