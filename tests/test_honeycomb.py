import math

import pytest

np = pytest.importorskip("numpy")

from kirigami_honeycomb.honeycomb import generate_hex_grid


def test_generate_hex_grid_returns_expected_shape():
    grid = generate_hex_grid(cell_size=20.0, width=100.0, length=80.0)
    assert isinstance(grid.x, np.ndarray)
    assert grid.shape == grid.x.shape
    hs_w = 20.0 / math.sqrt(3.0)
    offset = grid.x[1, 0] - grid.x[0, 0]
    assert offset == pytest.approx(hs_w / 2.0)


def test_generate_hex_grid_spacing():
    cell_size = 10.0
    grid = generate_hex_grid(cell_size=cell_size, width=30.0, length=30.0)
    hs_w = cell_size / math.sqrt(3.0)
    hs_l = cell_size / 2.0

    first_row_diffs = np.diff(grid.x[0])
    first_col_diffs = np.diff(grid.y[:, 0])

    np.testing.assert_allclose(first_row_diffs, np.full_like(first_row_diffs, hs_w))
    np.testing.assert_allclose(first_col_diffs, np.full_like(first_col_diffs, hs_l))
