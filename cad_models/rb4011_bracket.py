from build123d import *
from build123d import BuildPart
from common import *

from cad_models.common import BuildPart


@dataclass
class Parameters:
    bracket_depth = 64 * MM
    bracket_height = 1 * U
    bracket_thickness = 5 * MM
    bracket_width = 37 * MM
    ear_hole_width = 12 * MM
    ear_hole_height = 6 * MM
    ear_hole_horizontal_offset = 3 * MM
    ear_width = 20 * MM


p = Parameters()

with BuildPart() as builder:
    # bracket
    with BuildSketch(Plane.XZ):
        Rectangle(p.bracket_width, p.bracket_height)
    extrude(amount=p.bracket_thickness)

    # ear holes
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
        horizontal_offset = p.ear_hole_horizontal_offset + (p.ear_hole_width / 2)
        location = Location((0, 0))
        location *= Pos(X=-p.bracket_width / 2)
        location *= Pos(X=horizontal_offset)
        with Locations(location):
            vertical_spacing = p.bracket_height - (0.5 * IN)
            with GridLocations(0, vertical_spacing, 1, 2):
                SlotOverall(p.ear_hole_width, p.ear_hole_height)
    extruded = extrude(amount=-p.bracket_thickness, mode=Mode.SUBTRACT)

main(builder)
