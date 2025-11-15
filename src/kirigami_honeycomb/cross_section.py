"""Sampling utilities for kirigami honeycomb cross sections."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Iterable, Tuple

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]
CurveFunction = Callable[[ArrayLike], ArrayLike]


@dataclass(frozen=True)
class CrossSectionSamples:
    """Discretised representation of upper and lower cross-section curves."""

    x: FloatArray
    upper: FloatArray
    lower: FloatArray
    cell_size: float

    def __post_init__(self) -> None:
        x = _ensure_vector(self.x, name="x")
        upper = _ensure_vector(self.upper, name="upper")
        lower = _ensure_vector(self.lower, name="lower")

        if x.shape != upper.shape or x.shape != lower.shape:
            raise ValueError("x, upper, and lower arrays must share the same length.")

        object.__setattr__(self, "x", x)
        object.__setattr__(self, "upper", upper)
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "cell_size", float(self.cell_size))

    def as_tuple(self) -> Tuple[Tuple[float, ...], Tuple[float, ...], Tuple[float, ...]]:
        """Return tuple copies of the discretised sample sequences."""

        return (
            tuple(float(value) for value in self.x.tolist()),
            tuple(float(value) for value in self.upper.tolist()),
            tuple(float(value) for value in self.lower.tolist()),
        )


def _ensure_vector(values: ArrayLike, *, name: str) -> FloatArray:
    """Coerce *values* into a 1-D floating-point numpy array."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    return array


def _validate_domain(domain: Tuple[float, float]) -> Tuple[float, float]:
    start, end = float(domain[0]), float(domain[1])
    if not math.isfinite(start) or not math.isfinite(end):
        raise ValueError("Domain boundaries must be finite values.")
    if end <= start:
        raise ValueError("Upper domain boundary must be greater than the lower boundary.")
    return start, end


def _evaluate_function(func: CurveFunction, values: FloatArray) -> FloatArray:
    """Evaluate *func* against *values* with graceful fallbacks."""

    try:
        result = func(values)
    except TypeError:
        result = _evaluate_with_fallback(func, values)
    else:
        result = np.asarray(result, dtype=float)
        if result.shape == ():
            result = np.full_like(values, float(result))
        elif result.shape != values.shape:
            # Some users may return Python lists even when the length is correct.
            result = np.asarray(list(result), dtype=float)
    if result.shape != values.shape:
        raise ValueError("Cross-section functions must return values matching the number of samples.")
    if not np.all(np.isfinite(result)):
        raise ValueError("Cross-section functions must return finite values.")
    return result


def _evaluate_with_fallback(func: CurveFunction, values: FloatArray) -> FloatArray:
    try:
        result = func(values.tolist())
    except TypeError:
        result_list: Iterable[float] = (float(func(float(v))) for v in values)
        return np.fromiter(result_list, dtype=float, count=values.size)
    else:
        result = np.asarray(result, dtype=float)
        if result.shape != values.shape:
            result = np.asarray(list(result), dtype=float)
        return result


def sample_cross_section(
    upper: CurveFunction,
    lower: CurveFunction,
    *,
    domain: Tuple[float, float],
    cell_size: float,
) -> CrossSectionSamples:
    """Sample the cross section described by the provided functions."""

    if cell_size <= 0:
        raise ValueError("cell_size must be greater than zero.")

    start, end = _validate_domain(domain)
    half_step = cell_size / 2.0
    if half_step <= 0:
        raise ValueError("cell_size must be greater than zero.")

    epsilon = half_step * 1e-9
    x_values = np.arange(start, end + epsilon, half_step, dtype=float)

    upper_samples = _evaluate_function(upper, x_values)
    lower_samples = _evaluate_function(lower, x_values)

    return CrossSectionSamples(x_values, upper_samples, lower_samples, float(cell_size))


def linearize_cross_section(samples: CrossSectionSamples) -> CrossSectionSamples:
    """Apply the foldable linear approximation described by Saito et al."""

    if samples.x.size < 3:
        raise ValueError("At least three samples are required for linearisation.")

    upper = samples.upper.copy()
    lower = samples.lower.copy()

    for index in range(1, upper.size - 1, 2):
        upper[index] = (samples.upper[index - 1] + samples.upper[index + 1]) / 2.0

    for index in range(2, lower.size - 1, 2):
        lower[index] = (samples.lower[index - 1] + samples.lower[index + 1]) / 2.0

    return CrossSectionSamples(samples.x.copy(), upper, lower, samples.cell_size)
