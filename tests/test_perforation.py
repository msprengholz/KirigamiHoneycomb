from __future__ import annotations

import numpy as np
import pytest
import trimesh

from kirigami_honeycomb.mesh_io import sample_mesh_perforation_lines


def test_sample_mesh_perforation_lines_returns_lines_for_curved_mesh() -> None:
    mesh = trimesh.creation.icosphere(subdivisions=2, radius=10.0)

    lines = sample_mesh_perforation_lines(mesh, axis="x", height_axis="z", spacing=2.0, cell_size=4.0)

    assert isinstance(lines, list)
    assert len(lines) > 0
    first = lines[0]
    assert len(first) >= 2
    assert all(len(point) == 2 for point in first)
    assert np.all(np.isfinite(np.asarray(first)))


def test_sample_mesh_perforation_lines_rejects_invalid_max_lines() -> None:
    mesh = trimesh.creation.box(extents=(10.0, 10.0, 10.0))
    with pytest.raises(ValueError, match="max_lines must be greater than zero"):
        sample_mesh_perforation_lines(mesh, max_lines=0)
