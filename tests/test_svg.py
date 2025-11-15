from kirigami_honeycomb.cross_section import sample_cross_section
from kirigami_honeycomb.fold_pattern import compute_fold_pattern
from kirigami_honeycomb.svg import export_fold_diagram


def test_export_fold_diagram_png(tmp_path) -> None:
    samples = sample_cross_section(
        lambda x: 0.1 * x + 20,
        lambda x: -0.05 * x,
        domain=(0.0, 40.0),
        cell_size=10.0,
    )
    pattern = compute_fold_pattern(samples)
    output = tmp_path / "diagram.png"

    export_fold_diagram(samples, pattern, output)

    assert output.exists()
    assert output.stat().st_size > 0
