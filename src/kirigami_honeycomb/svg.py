"""Export helpers for fold line diagrams."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import svgwrite

from .cross_section import CrossSectionSamples
from .fold_pattern import FoldPattern


DEFAULT_STROKE = svgwrite.rgb(10, 10, 16, "%")


def export_fold_diagram(samples: CrossSectionSamples, pattern: FoldPattern, output: Path) -> None:
    """Write the fold pattern to *output*, inferring the format from its suffix."""

    suffix = output.suffix.lower()
    if suffix == ".png":
        _export_png(samples, pattern, output)
    else:
        _export_svg(samples, pattern, output)


def _diagram_bounds(samples: CrossSectionSamples, pattern: FoldPattern) -> tuple[
    Sequence[float],
    Sequence[float],
    Sequence[float],
    float,
    float,
    float,
    float,
]:
    x, upper, lower = samples.as_tuple()
    width = pattern.length
    min_lower = min(lower)
    max_upper = max(upper)
    height = max_upper - min_lower
    padding = samples.cell_size
    return x, upper, lower, width, min_lower, height, padding


def _line(dwg: svgwrite.Drawing, start: tuple[float, float], end: tuple[float, float]) -> svgwrite.shapes.Line:
    return dwg.line(start=start, end=end, stroke=DEFAULT_STROKE, stroke_width=0.5)


def _polyline(
    dwg: svgwrite.Drawing,
    points: Iterable[tuple[float, float]],
    *,
    stroke: str = "#2e7",
) -> svgwrite.shapes.Polyline:
    return dwg.polyline(points=points, stroke=stroke, fill="none", stroke_width=0.6)


def _export_svg(samples: CrossSectionSamples, pattern: FoldPattern, output: Path) -> None:
    x, upper, lower, width, min_lower, height, padding = _diagram_bounds(samples, pattern)
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


def _export_png(samples: CrossSectionSamples, pattern: FoldPattern, output: Path) -> None:
    """Render the fold diagram as a bitmap for environments without SVG viewing."""

    import matplotlib  # Imported lazily to avoid the Agg backend unless needed.

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    x, upper, lower, width, min_lower, height, padding = _diagram_bounds(samples, pattern)

    fig_width = max(width, 1.0) / 25.4  # convert millimetres to inches
    fig_height = max(height, 1.0) / 25.4
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=300)

    ax.plot(x, upper, color="#0a6", linewidth=1.4, label="upper envelope")
    ax.plot(x, lower, color="#c41", linewidth=1.4, label="lower envelope")

    for position in pattern.a_positions:
        ax.axvline(position, color="#222", linewidth=0.8, linestyle="-", alpha=0.6)

    for position in pattern.b_positions:
        ax.axvline(position, color="#555", linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_xlim(min(x), max(x))
    ax.set_ylim(min_lower - padding * 0.5, min_lower + height + padding * 0.5)
    ax.set_xlabel("slice direction (mm)")
    ax.set_ylabel("height (mm)")
    ax.legend(loc="upper right", frameon=False)
    ax.grid(True, linestyle=":", linewidth=0.4, alpha=0.6)
    fig.tight_layout()

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)
