from kirigami_honeycomb.cli import build_mesh_viewer_parser


def test_mesh_viewer_parser_defaults() -> None:
    parser = build_mesh_viewer_parser()
    args = parser.parse_args(["dummy.stl"])
    assert args.mesh == "dummy.stl"
    assert args.axis == "x"
    assert args.height_axis == "z"
    assert args.axis_length is None
