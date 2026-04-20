import typing

from build123d import *
from build123d import BuildPart
from common import *

from cad_models.common import BuildPart


class RackItem(typing.Protocol):
    def faceplate_profile(self) -> None: ...
    def shelf_profile(self) -> None: ...


class ThinkCentre(RackItem):
    def faceplate_profile(self) -> None:
        pass

    def shelf_profile(self) -> None:
        pass


@dataclass
class Parameters:
    items: list[RackItem]
    ear_hole_width = 12 * MM
    ear_hole_height = 6 * MM
    ear_hole_horizontal_offset = 3 * MM
    ear_width = 20 * MM
    rackmount_width = 254 * MM
    rackmount_height = 1 * U
    rackmount_thickness = 5 * MM


thinkcentre = Parameters(items=[ThinkCentre()])

p = thinkcentre

with BuildPart() as builder:
    # front panel
    with BuildSketch(Plane.XZ):
        Rectangle(p.rackmount_width, p.rackmount_height)
    extrude(amount=p.rackmount_thickness)

    # ear holes
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
    mirror_plane = Plane(face.offset(-p.rackmount_width / 2))
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
        horizontal_offset = p.ear_hole_horizontal_offset + (p.ear_hole_width / 2)
        location = Location((0, 0))
        location *= Pos(X=-p.rackmount_width / 2)
        location *= Pos(X=horizontal_offset)
        with Locations(location):
            vertical_spacing = p.rackmount_height - (0.5 * IN)
            with GridLocations(0, vertical_spacing, 1, 2):
                SlotOverall(p.ear_hole_width, p.ear_hole_height)
    extruded = extrude(amount=-p.rackmount_thickness, mode=Mode.SUBTRACT)
    mirror(extruded, mirror_plane, mode=Mode.SUBTRACT)

main(builder)
