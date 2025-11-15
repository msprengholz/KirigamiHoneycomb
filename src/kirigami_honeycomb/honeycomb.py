"""Generate the underlying hexagonal grid used by the honeycomb core."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from numpy.typing import NDArray


FloatGrid = NDArray[np.float64]


@dataclass(frozen=True)
class HexGrid:
    """Vertices of a hexagonal grid aligned with the fold pattern."""

    x: FloatGrid
    y: FloatGrid
    cell_size: float

    def __post_init__(self) -> None:
        x = np.asarray(self.x, dtype=float)
        y = np.asarray(self.y, dtype=float)
        if x.shape != y.shape:
            raise ValueError("x and y grids must have matching shapes.")
        if x.ndim != 2:
            raise ValueError("HexGrid coordinates must be two-dimensional.")
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
        object.__setattr__(self, "cell_size", float(self.cell_size))

    @property
    def shape(self) -> Tuple[int, int]:
        if self.x.size == 0:
            return (0, 0)
        return self.x.shape


def generate_hex_grid(
    *,
    cell_size: float,
    width: float,
    length: float,
) -> HexGrid:
    """Generate a hexagonal grid covering the requested extent."""

    if cell_size <= 0:
        raise ValueError("cell_size must be positive.")
    if width <= 0 or length <= 0:
        raise ValueError("width and length must be positive.")

    half_step_length = cell_size / 2.0
    half_step_width = cell_size / math.sqrt(3.0)

    num_width = int(math.floor(width / half_step_width)) + 2
    num_length = int(math.floor(length / half_step_length)) + 2

    column_indices = np.arange(num_width, dtype=float)
    row_indices = np.arange(num_length, dtype=float)

    x_coords = np.tile(column_indices * half_step_width, (num_length, 1))
    x_coords[1::2] += half_step_width / 2.0

    y_coords = np.repeat((row_indices * half_step_length)[:, np.newaxis], num_width, axis=1)

    return HexGrid(x_coords, y_coords, float(cell_size))
