import typing

from build123d import *

from cad_models.common import *


class ProfileCallback(typing.Protocol):
    def __call__(self, p: "Parameters") -> None: ...


@dataclass
class Parameters:
    bracket_depth: float
    profile: ProfileCallback
    bracket_height: float = 1 * U
    center_width: float = 0 * U
    ear_hole_width: float = 12 * MM
    ear_hole_height: float = 6 * MM
    ear_thickness: float = 5 * MM
    ear_width: float = 15 * MM
    interface_width: float = 5 * MM

    @property
    def bracket_width(self) -> float:
        return self.ear_width + self.center_width + self.interface_width


def gigaplus_profile(p: Parameters):
    hole_count = 2
    hole_offset = 18 * MM
    hole_spacing = 20 * MM
    screw_diameter = 3 * MM
    screw_head_diameter = 5

    location = Location((0, 0))
    location *= Pos(X=-p.bracket_depth / 2)
    location *= Pos(X=hole_offset)
    location *= Pos(X=hole_spacing / 2)
    with Locations(location):
        with GridLocations(hole_spacing, hole_spacing, hole_count, hole_count):
            CounterSinkHole(
                screw_diameter / 2, screw_head_diameter / 2, p.interface_width
            )


gigaplus = Parameters(
    bracket_depth=50 * MM,
    interface_width=2 * MM,
    profile=gigaplus_profile,
)


p = gigaplus


with BuildPart() as builder:
    # bracket
    with BuildSketch() as sketch:
        Rectangle(p.bracket_width, p.ear_thickness, align=(Align.MAX, Align.MIN))
        Rectangle(p.interface_width, p.bracket_depth, align=(Align.MAX, Align.MIN))
    extrude(amount=p.bracket_height)

    # ear holes
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(X=-p.bracket_width / 2)
        location *= Pos(X=p.ear_width / 2)
        with Locations(location):
            vertical_spacing = p.bracket_height - (0.5 * IN)
            with GridLocations(0, vertical_spacing, 1, 2):
                SlotOverall(p.ear_hole_width, p.ear_hole_height)
    extrude(amount=-p.ear_thickness, mode=Mode.SUBTRACT)

    # bracket-device interface
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
    with Locations(Plane(face, x_dir=(0, 1, 0))):
        p.profile(p)


main(builder)
