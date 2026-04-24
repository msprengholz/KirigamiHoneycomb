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


def test_export_fold_diagram_with_perforations(tmp_path) -> None:
    samples = sample_cross_section(
        lambda x: 0.05 * x + 12,
        lambda x: -0.02 * x,
        domain=(0.0, 20.0),
        cell_size=5.0,
    )
    pattern = compute_fold_pattern(samples)
    output = tmp_path / "diagram_with_perforation.svg"
    perforation_lines = [[(0.0, 5.0), (10.0, 6.0), (20.0, 5.5)]]

    export_fold_diagram(samples, pattern, output, perforation_lines=perforation_lines)

    content = output.read_text(encoding="utf-8")
    assert "dasharray" in content
