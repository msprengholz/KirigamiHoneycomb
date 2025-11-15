from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
import trimesh

from kirigami_honeycomb.mesh_io import sample_mesh_cross_section


def test_sample_mesh_cross_section_box_returns_constant_envelope() -> None:
    mesh = trimesh.creation.box(extents=(40.0, 20.0, 30.0))

    samples = sample_mesh_cross_section(mesh, axis="x", height_axis="z", spacing=10.0, cell_size=20.0)

    assert samples.x[0] == pytest.approx(-20.0)
    assert samples.x[-1] == pytest.approx(20.0)
    assert np.allclose(samples.lower, -15.0)
    assert np.allclose(samples.upper, 15.0)


def test_sample_mesh_cross_section_from_path(tmp_path: Path) -> None:
    mesh = trimesh.creation.box(extents=(30.0, 20.0, 20.0))
    rotation = trimesh.transformations.rotation_matrix(math.radians(30), (1.0, 0.0, 0.0))
    mesh.apply_transform(rotation)

    mesh_path = tmp_path / "wedge.stl"
    mesh.export(mesh_path)

    samples = sample_mesh_cross_section(
        mesh_path,
        axis="y",
        height_axis="z",
        spacing=5.0,
        cell_size=10.0,
    )

    assert samples.cell_size == pytest.approx(10.0)
    assert samples.x.size >= 5
    assert np.all(np.diff(samples.x) > 0)
    # The rotation should create a gradient in the height envelope along the slicing axis.
    assert samples.upper.max() > samples.upper.min()
    assert samples.lower.max() > samples.lower.min()
