"""Interactive GUI utilities for adjusting FLD cut placement."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseEvent, PickEvent
from matplotlib.lines import Line2D
from matplotlib.widgets import Button

from .cross_section import CrossSectionSamples
from .fold_pattern import FoldPattern
from .svg import export_fold_diagram


class _CutLineEditor:
    def __init__(
        self,
        ax: plt.Axes,
        *,
        a_positions: np.ndarray,
        b_positions: np.ndarray,
        y_range: tuple[float, float],
    ) -> None:
        self.ax = ax
        self._a_positions = a_positions.copy()
        self._b_positions = b_positions.copy()
        self._selected: tuple[str, int] | None = None
        y_min, y_max = y_range
        self._a_lines = [ax.plot([x, x], [y_min, y_max], color="black", lw=0.6, picker=5)[0] for x in a_positions]
        self._b_lines = [ax.plot([x, x], [y_min, y_max], color="#666", lw=0.6, ls="--", picker=5)[0] for x in b_positions]

    def on_pick(self, event: PickEvent) -> None:
        artist = event.artist
        for index, line in enumerate(self._a_lines):
            if artist is line:
                self._selected = ("a", index)
                return
        for index, line in enumerate(self._b_lines):
            if artist is line:
                self._selected = ("b", index)
                return

    def on_motion(self, event: MouseEvent) -> None:
        if self._selected is None or event.xdata is None or event.inaxes is not self.ax:
            return
        family, index = self._selected
        x = float(event.xdata)
        if family == "a":
            self._a_positions[index] = x
            self._a_lines[index].set_xdata([x, x])
        else:
            self._b_positions[index] = x
            self._b_lines[index].set_xdata([x, x])
        self.ax.figure.canvas.draw_idle()

    def on_release(self, _: MouseEvent) -> None:
        self._selected = None

    @property
    def a_positions(self) -> np.ndarray:
        return np.sort(self._a_positions)

    @property
    def b_positions(self) -> np.ndarray:
        return np.sort(self._b_positions)


def launch_cut_editor(
    samples: CrossSectionSamples,
    pattern: FoldPattern,
    *,
    output: str | Path,
    perforation_lines: list[list[tuple[float, float]]] | None = None,
) -> FoldPattern:
    """Launch an interactive editor that lets users drag cut lines horizontally."""

    x = samples.x
    y_min = float(np.min(samples.lower))
    y_max = float(np.max(samples.upper))

    fig, ax = plt.subplots(figsize=(10, 5))
    plt.subplots_adjust(bottom=0.2)
    ax.plot(x, samples.upper, color="#0a6", lw=1.2, label="upper")
    ax.plot(x, samples.lower, color="#c41", lw=1.2, label="lower")
    if perforation_lines:
        for line in perforation_lines:
            xs = [p[0] for p in line]
            ys = [p[1] for p in line]
            ax.plot(xs, ys, color="#e67e22", lw=0.8, ls=":", label="perforation")
    ax.set_title("Drag vertical lines to adjust cut placement")
    ax.set_xlabel("Cross-section coordinate")
    ax.set_ylabel("Height")
    ax.set_xlim(float(np.min(x)), float(np.max(x)))
    ax.set_ylim(y_min, y_max)

    editor = _CutLineEditor(
        ax,
        a_positions=pattern.a_positions,
        b_positions=pattern.b_positions,
        y_range=(y_min, y_max),
    )
    fig.canvas.mpl_connect("pick_event", editor.on_pick)
    fig.canvas.mpl_connect("motion_notify_event", editor.on_motion)
    fig.canvas.mpl_connect("button_release_event", editor.on_release)

    save_ax = fig.add_axes([0.8, 0.05, 0.16, 0.08])
    save_button = Button(save_ax, "Save SVG")

    target = Path(output)

    def _save(_: object) -> None:
        updated = FoldPattern(editor.a_positions, editor.b_positions, pattern.offsets)
        export_fold_diagram(
            samples,
            updated,
            target,
            perforation_lines=perforation_lines,
        )

    save_button.on_clicked(_save)
    plt.show()

    return FoldPattern(editor.a_positions, editor.b_positions, pattern.offsets)


__all__ = ["launch_cut_editor"]
