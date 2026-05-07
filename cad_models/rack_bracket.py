from build123d import *
from build123d import Part

from cad_models.common import *
from cad_models.common import Part


class Device:
    p: "Parameters"
    bracket_depth: float
    interface_width: float

    def interface(self) -> Part:
        raise NotImplementedError()


@dataclass
class Parameters:
    device: Device
    bracket_height: float = 1 * U
    center_width: float = 0 * U
    ear_hole_width: float = 12 * MM
    ear_hole_height: float = 6 * MM
    ear_thickness: float = 5 * MM
    ear_width: float = 15 * MM

    def __post_init__(self):
        self.device.p = self

    @property
    def bracket_width(self) -> float:
        return self.ear_width + self.center_width + self.device.interface_width


class Gigaplus(Device):
    bracket_depth = 50 * MM
    interface_width = 2 * MM

    hole_count = 2
    hole_offset = 18 * MM
    hole_spacing = 20 * MM
    screw_diameter = 3 * MM
    screw_head_diameter = 5 * MM

    def interface(self) -> Part:
        with BuildPart(mode=Mode.PRIVATE) as builder:
            location = Location((0, 0))
            location *= Pos(X=-self.p.ear_thickness / 2)
            location *= Pos(X=-self.bracket_depth / 2)
            location *= Pos(X=self.hole_offset)
            location *= Pos(X=self.hole_spacing / 2)
            with Locations(location):
                with GridLocations(
                    self.hole_spacing,
                    self.hole_spacing,
                    self.hole_count,
                    self.hole_count,
                ):
                    CounterSinkHole(
                        self.screw_diameter / 2,
                        self.screw_head_diameter / 2,
                        self.interface_width,
                        mode=Mode.ADD,
                    )
        return require(builder.part)


def builder_fn(p: Parameters):
    with BuildPart() as builder:
        # bracket
        with BuildSketch():
            Rectangle(p.bracket_width, p.ear_thickness, align=(Align.MAX, Align.MIN))
            Rectangle(
                p.device.interface_width,
                p.device.bracket_depth,
                align=(Align.MAX, Align.MIN),
            )
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
        face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
        with Locations(Plane(face, x_dir=(0, 1, 0))):
            interface = p.device.interface()
            add(interface, mode=Mode.SUBTRACT)
    return builder


main(builder_fn, {"gigaplus": Parameters(device=Gigaplus())})
