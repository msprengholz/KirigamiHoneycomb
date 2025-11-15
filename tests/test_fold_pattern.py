import pytest

np = pytest.importorskip("numpy")

from kirigami_honeycomb.cross_section import CrossSectionSamples
from kirigami_honeycomb.fold_pattern import compute_fold_pattern


def test_fold_pattern_reproduces_reference_values():
    x = np.linspace(0.0, 8.0, 5)
    upper = np.array([10.0, 9.0, 8.0, 7.0, 6.0])
    lower = np.array([0.0, 1.0, 0.0, 1.0, 0.0])
    samples = CrossSectionSamples(x=x, upper=upper, lower=lower, cell_size=4.0)

    pattern = compute_fold_pattern(samples)

    # Reference data computed from the legacy script.
    expected_a = np.array([0.0, 10.0, 18.0, 26.0, 32.0, 38.0])
    expected_b = np.array([1.0, 9.0, 17.0, 23.0, 29.0])
    np.testing.assert_allclose(pattern.a_positions, expected_a)
    np.testing.assert_allclose(pattern.b_positions, expected_b)
    np.testing.assert_allclose(pattern.offsets, np.array([1.0]))
