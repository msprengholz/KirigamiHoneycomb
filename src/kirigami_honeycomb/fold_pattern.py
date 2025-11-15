"""Computation of fold line positions for kirigami honeycomb diagrams."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .cross_section import CrossSectionSamples


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class FoldPattern:
    """Fold line positions for the a and b slit series."""

    a_positions: FloatArray
    b_positions: FloatArray
    offsets: FloatArray

    def __post_init__(self) -> None:
        a_positions = np.asarray(self.a_positions, dtype=float).reshape(-1)
        b_positions = np.asarray(self.b_positions, dtype=float).reshape(-1)
        offsets = np.asarray(self.offsets, dtype=float).reshape(-1)

        object.__setattr__(self, "a_positions", a_positions)
        object.__setattr__(self, "b_positions", b_positions)
        object.__setattr__(self, "offsets", offsets)

    @property
    def length(self) -> float:
        """Total extent of the pattern in the width direction."""

        if self.a_positions.size == 0:
            return 0.0
        return float(self.a_positions[-1])


def compute_fold_pattern(samples: CrossSectionSamples) -> FoldPattern:
    """Compute fold line positions for the provided cross-section samples."""

    upper = samples.upper
    lower = samples.lower
    if upper.size != lower.size:
        raise ValueError("Upper and lower samples must have the same length.")
    if upper.size < 2:
        raise ValueError("At least two sample points are required to compute a fold pattern.")

    num = upper.size
    delta = upper - lower

    a_positions = np.zeros(num + 1, dtype=float)
    for index in range(1, num + 1):
        k = index if index % 2 == 0 else index - 1
        if k >= num:
            k = num - 1
        a_positions[index] = a_positions[index - 1] + delta[k]

    b_positions = np.zeros(num, dtype=float)
    for index in range(1, num):
        k = index - 1 if index % 2 == 0 else index
        if k >= num:
            k = num - 1
        b_positions[index] = b_positions[index - 1] + delta[k]

    if num >= 2:
        offset = lower[1] - lower[0]
        b_positions = b_positions + offset
        offsets = np.array([offset], dtype=float)
    else:
        offsets = np.array([], dtype=float)

    return FoldPattern(a_positions, b_positions, offsets)
