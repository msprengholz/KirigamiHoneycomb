# Kirigami Honeycomb

A tool for converting arbitrary geometry into kirigami honeycomb folding line diagrams. This projects is still in its early stages.

## Prior Work

The idea is based on two publication from Saito et al.:

Saito, K., Pellegrino, S., Nojima, T., 2014. Manufacture of Arbitrary Cross-Section Composite Honeycomb Cores Based on Origami Techniques. Journal of Mechanical Design 136, 051011. https://doi.org/10.1115/1.4026824

Saito, K., Fujimoto, A., Okabe, Y., 2016. Design of a 3D Wing Honeycomb Core Based on Origami Techniques, in: Volume 5B: 40th Mechanisms and Robotics Conference. Presented at the ASME 2016 International Design Engineering Technical Conferences and Computers and Information in Engineering Conference, American Society of Mechanical Engineers, Charlotte, North Carolina, USA, p. V05BT07A026. https://doi.org/10.1115/DETC2016-60419

The former can be accessed freely [here](https://core.ac.uk/download/pdf/33110081.pdf).

Sadly, no source code has been published alongside. The mathematical description of the algorithm inside both papers is not correct to my understanding. Therefore, I have written my own implementation of the simplified algorithm (explained in detail below) based on the provided examples and (quite excellent) figures.
