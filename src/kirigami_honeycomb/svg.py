"""SVG export helpers for fold line diagrams."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import svgwrite

from .cross_section import CrossSectionSamples
from .fold_pattern import FoldPattern


DEFAULT_STROKE = svgwrite.rgb(10, 10, 16, "%")


def _line(dwg: svgwrite.Drawing, start: tuple[float, float], end: tuple[float, float]) -> svgwrite.shapes.Line:
    return dwg.line(start=start, end=end, stroke=DEFAULT_STROKE, stroke_width=0.5)


def _polyline(
    dwg: svgwrite.Drawing,
    points: Iterable[tuple[float, float]],
    *,
    stroke: str = "#2e7",
) -> svgwrite.shapes.Polyline:
    return dwg.polyline(points=points, stroke=stroke, fill="none", stroke_width=0.6)


def export_fold_diagram(samples: CrossSectionSamples, pattern: FoldPattern, output: Path) -> None:
    """Write a simple SVG visualisation of the fold pattern."""

    x, upper, lower = samples.as_tuple()
    width = pattern.length
    min_lower = min(lower)
    max_upper = max(upper)
    height = max_upper - min_lower
    padding = samples.cell_size

    dwg = svgwrite.Drawing(size=(width + padding * 2, height + padding * 2))

    def _transform(xi: float, yi: float) -> tuple[float, float]:
        return padding + xi, padding + height - (yi - min_lower)

    upper_points = [_transform(xi, yi) for xi, yi in zip(x, upper)]
    lower_points = [_transform(xi, yi) for xi, yi in zip(x, lower)]
    dwg.add(_polyline(dwg, upper_points, stroke="#0a6"))
    dwg.add(_polyline(dwg, lower_points, stroke="#c41"))

    for position in pattern.a_positions:
        start = (padding + position, padding)
        end = (padding + position, padding + height)
        dwg.add(_line(dwg, start=start, end=end))

    for position in pattern.b_positions:
        start = (padding + position, padding)
        end = (padding + position, padding + height)
        dwg.add(_line(dwg, start=start, end=end))

    output.parent.mkdir(parents=True, exist_ok=True)
    dwg.saveas(str(output))
