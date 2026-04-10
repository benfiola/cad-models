from build123d import *
from common import *

with BuildPart() as plate:
    with BuildSketch():
        Rectangle(1.0, 1.0)
    extrude(amount=1.0)
set_label(plate, "Plate")

with BuildPart() as cover:
    with BuildSketch():
        Rectangle(2.0, 2.0)
    extrude(amount=0.5)
set_label(cover, "Cover")

main(plate, cover)
