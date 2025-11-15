# Kirigami Honeycomb FLDs

A tool for converting arbitrary geometry into kirigami honeycomb folding line diagrams (FLD). This projects is still in its early stages.

![fcurves](docs/imgs/f_curves.png "Function curves")
![hexmesh](docs/imgs/hexmesh.png "Honeycomb 3D mesh")
![fld](docs/imgs/fld.png "Folding line diagram")

## Prior Work

The idea is based on two publications from Saito et al.:

- Saito, K., Pellegrino, S., Nojima, T., 2014. Manufacture of Arbitrary Cross-Section Composite Honeycomb Cores Based on Origami Techniques. Journal of Mechanical Design 136, 051011. https://doi.org/10.1115/1.4026824
- Saito, K., Fujimoto, A., Okabe, Y., 2016. Design of a 3D Wing Honeycomb Core Based on Origami Techniques, in: Volume 5B: 40th Mechanisms and Robotics Conference. Presented at the ASME 2016 International Design Engineering Technical Conferences and Computers and Information in Engineering Conference, American Society of Mechanical Engineers, Charlotte, North Carolina, USA, p. V05BT07A026. https://doi.org/10.1115/DETC2016-60419

The first paper explains how arbitrary cross sections can be converted to kirigami folding line diagrams. It can be accessed [here](https://core.ac.uk/download/pdf/33110081.pdf). In the second, this idea is further developed to morph the honeycomb cells to also cover 3D shapes.

Sadly, no source code has been published alongside. The mathematical description of the algorithm inside both papers is not correct to my understanding. Therefore, I have written my own implementation of the simplified algorithm (see paper; zero slit width; linear cross section approximation, but always foldable) based on the provided examples and (quite excellent) figures.

## The Idea Behind

I have been looking for a way to build larger structures of freeform geometry. While 3D printers work well for tiny parts they are limited by their build volume. Manufacturing kirigami patterns with a laser cutter allows larger structures that still can be made at home with relatively few and cheap tools. In the end, this tool should allow to load a geometry mesh and provide the corresponding folding line diagram that matches the input geometry as close as possible when folded. While the goal is pretty clear, the process to get there is not.

## Vision for the Tool

The long-term objective of the project remains identical to the original research notes. To stay aligned with that vision we continue to track the following high-level capabilities:

- load any geometry and process it into a FLD
- overcome the limitation that the arbitrarily shaped cross section is fixed along the third axis
  - add perforated lines to remove additional material so the resulting pattern produces the desired geometry
- split the FLD into multiple parts that can be joined back together after folding
  - this is needed because laser cutters are limited in the sheet size they can work on
  - the FLD approximates the outer curves of the mesh
  - inner cavities should also be drawn on the FLD as perforations that can be removed after folding and gluing

## Defining the Process

The roadmap towards the target experience is still evolving. The current open questions mainly revolve around whether the tooling should remain a standalone application or grow into a Blender add-on. Regardless of the delivery vehicle, the workflow we want to enable is:

- Load geometry from external file
- Partition the mesh into multiple zones, depending on manufacturing constraints (maximum size of sheets)
  - have the user select some parameters:
    - manually define zones
    - direction of folding
    - honeycomb cell size
    - controls for the following steps...
- In each zone determine the upper and lower curve (hull of projection); right now this is defined by two functions
- Sample functions in honeycomb cell size steps
  - build a linear approximation (this is needed to obtain a foldable end result!)
  - add offset so that original geometry is definitely inside the linear approximation
- Calculate FLD parameters and create first iteration FLD (no cavities nor perforation lines for exact outer hull)
- Build 3D honeycomb mesh of the FLD
- Intersect the real geometry with the honeycomb mesh
- Transform intersection points (optimally polylines) from 3D onto 2D FLD
  - create perforation lines

## Getting Started

The repository now ships as an installable Python package. The tooling lives in
`kirigami_honeycomb` under `src/` and provides reusable functions as well as a
small command line interface for experiments. Install the project in a virtual
environment together with the development tools. The numerical routines depend
on `numpy` for efficient vectorised sampling and fold calculations, so make sure
your environment can compile binary wheels on your platform:

```bash
pip install -e .[dev]
```

### Command Line Interface

Use the `kirigami-fld` entry point to generate a fold line diagram (FLD) from
analytic upper and lower cross-section expressions:

```bash
kirigami-fld "0.002*x**2 - 0.4*x + 40" "10*sin(2*pi*x/200)" output.svg --domain 0 200 --cell-size 20 --linearise
```

The command samples the provided expressions, applies the optional foldable
linearisation, computes the fold pattern and writes a simple SVG visualisation.

### Python API

The package exposes composable building blocks that encapsulate the cleaned up
implementation from the research papers:

```python
from kirigami_honeycomb import (
    sample_cross_section,
    linearize_cross_section,
    compute_fold_pattern,
    generate_hex_grid,
)

samples = sample_cross_section(upper, lower, domain=(0, 200), cell_size=20)
samples = linearize_cross_section(samples)
pattern = compute_fold_pattern(samples)
grid = generate_hex_grid(cell_size=20, width=pattern.length, length=200)
```

Each function is unit tested and documented to serve as a stable foundation for
future work such as 3D mesh morphing and perforation line placement.

### Running the Tests

Execute the automated checks with `pytest`:

```bash
pytest
```

## License

MIT, see LICENSE file
