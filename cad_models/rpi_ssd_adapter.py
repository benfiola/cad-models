from bd_warehouse.fastener import *
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
    ssd_screw_size: str = "M3-0.5"
    standoff_spacing_x: float = 49 * MM
    standoff_spacing_y: float = 58 * MM
    standoff_offset_y: float = -5.5 * MM
    standoff_diameter: float = 5 * MM
    standoff_nut_size: str = "M3-0.5-H3-D5"
    standoff_nut_depth: float = 3 * MM


def builder_fn(p: Parameters):
    with BuildPart(mode=Mode.PRIVATE):
        screw = PanHeadScrew(p.ssd_screw_size, p.adapter_thickness)
        nut = HeatSetNut(
            p.standoff_nut_size, fastener_type=typing.cast(typing.Any, "AE-SamZhihui")
        )

    with BuildPart() as builder:
        # adapter
        with BuildSketch():
            Rectangle(p.adapter_width, p.adapter_height)
        extrude(amount=p.adapter_thickness)

        # ssd holes
        face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
        plane = Plane(face.center(), x_dir=(1, 0, 0), z_dir=(face.normal_at()))
        location = Location(plane)
        location *= Pos(Y=p.ssd_offset_y)
        with Locations(location):
            with GridLocations(p.ssd_spacing_x, p.ssd_spacing_y, 2, 2):
                ClearanceHole(screw)

        # standoff holes
        face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
        plane = Plane(
            face.without_holes().center(), x_dir=(1, 0, 0), z_dir=face.normal_at()
        )
        location = Location(plane)
        location *= Pos(Y=p.standoff_offset_y)
        with Locations(location):
            # NOTE: depth seems to be 'in addition to' nut depth, but also needs to be > 0.
            with GridLocations(p.standoff_spacing_x, p.standoff_spacing_y, 2, 2):
                InsertHole(nut, depth=0.0001 * MM)

        # fillet
        edges = builder.edges().filter_by(Axis.Z)
        fillet(edges, p.adapter_fillet_radius)

    return builder


main(builder_fn, Parameters())
