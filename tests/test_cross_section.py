import pytest

np = pytest.importorskip("numpy")

from kirigami_honeycomb.cross_section import linearize_cross_section, sample_cross_section


def test_sample_cross_section_includes_domain_end():
    upper = lambda x: 0.5 * np.asarray(x)
    lower = lambda x: np.zeros_like(np.asarray(x))
    samples = sample_cross_section(upper, lower, domain=(0.0, 10.0), cell_size=4.0)
    assert isinstance(samples.x, np.ndarray)
    assert samples.x[-1] == pytest.approx(10.0)
    assert samples.upper.shape == samples.x.shape
    assert samples.lower.shape == samples.x.shape


def test_linearize_cross_section_matches_manual_result():
    def upper(x):
        arr = np.asarray(x, dtype=float)
        return arr**2

    def lower(x):
        arr = np.asarray(x, dtype=float)
        return np.sin(arr)

    samples = sample_cross_section(upper, lower, domain=(0.0, 4.0), cell_size=2.0)
    linear = linearize_cross_section(samples)

    expected_upper = samples.upper.copy()
    for index in range(1, expected_upper.size - 1, 2):
        expected_upper[index] = (samples.upper[index - 1] + samples.upper[index + 1]) / 2.0

    expected_lower = samples.lower.copy()
    for index in range(2, expected_lower.size - 1, 2):
        expected_lower[index] = (samples.lower[index - 1] + samples.lower[index + 1]) / 2.0

    np.testing.assert_allclose(linear.upper, expected_upper)
    np.testing.assert_allclose(linear.lower, expected_lower)
