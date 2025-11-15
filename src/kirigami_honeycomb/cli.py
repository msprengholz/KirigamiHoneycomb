"""Command line interface for generating kirigami honeycomb FLDs."""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Callable

import numpy as np

from .cross_section import linearize_cross_section, sample_cross_section
from .fold_pattern import compute_fold_pattern
from .svg import export_fold_diagram

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


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

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
