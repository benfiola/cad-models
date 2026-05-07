from build123d import *
from common import *


@dataclass
class Parameters:
    adapter_width: float = 70 * MM
    adapter_height: float = 100 * MM
    adapter_thickness: float = 5 * MM
    adapter_fillet_radius: float = 2 * MM
    ssd_spacing_x: float = 62.0 * MM
    ssd_spacing_y: float = 77.0 * MM
    ssd_offset_y: float = -2.5 * MM
    standoff_spacing_x: float = 49 * MM
    standoff_spacing_y: float = 58 * MM
    standoff_offset_y: float = -5.5 * MM


def builder_fn(p: Parameters):
    with BuildPart() as builder:
        # adapter
        with BuildSketch():
            Rectangle(p.adapter_width, p.adapter_height)
        extrude(amount=p.adapter_thickness)

        # ssd holes
        face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
        plane = Plane(face.position, x_dir=(1, 0, 0), z_dir=(face.normal_at()))
        location = Location(plane)
        location *= Pos(Y=p.ssd_offset_y)
        with Locations(Plane(face, x_dir=(1, 0, 0))):
            with GridLocations(p.ssd_spacing_x, p.ssd_spacing_y, 2, 2):
                Cylinder(2, 1, mode=Mode.SUBTRACT)

        # standoff holes
        face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
        plane = Plane(face.position, x_dir=(1, 0, 0), z_dir=face.normal_at())
        location = Location(plane)
        location *= Pos(Y=p.standoff_offset_y)
        with Locations(location):
            with GridLocations(p.standoff_spacing_x, p.standoff_spacing_y, 2, 2):
                Cylinder(2, 1, mode=Mode.SUBTRACT)

        # fillet
        edges = builder.edges().filter_by(Axis.Z)
        fillet(edges, p.adapter_fillet_radius)

    return builder


main(builder_fn, Parameters())
