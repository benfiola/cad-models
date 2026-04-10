from build123d import *
from common import main

with BuildPart() as part:
    with BuildSketch():
        Rectangle(1.0, 1.0)
    extrude(amount=1.0)


main(part)
