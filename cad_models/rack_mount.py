from build123d import *
from build123d import BuildPart
from common import *

from cad_models.common import BuildPart


@dataclass
class Device:
    width: float
    height: float
    depth: float


class RB4011(Device):
    def __init__(self):
        super().__init__(width=227.7 * MM, height=26 * MM, depth=117.7 * MM)


@dataclass
class Parameters:
    device_height = 26 * MM
    device_width = 227.7 * MM
    device_depth = 117.7 * MM
    ear_hole_width = 12 * MM
    ear_hole_height = 6 * MM
    ear_width = 15 * MM
    mount_width = 252 * MM
    mount_height = 1 * U
    mount_oversize_taper_offset = 10 * MM
    mount_oversize_taper_length = 10 * MM
    mount_thickness = 5 * MM
    mount_lip = 2 * MM
    rack_width = 222 * MM
    rib_depth = 10 * MM


p = Parameters()


with BuildPart() as builder:
    inner_width = p.mount_width - (p.ear_width * 2)

    # front panel
    with BuildSketch(Plane.XZ):
        Rectangle(p.mount_width, p.mount_height)
    extruded = extrude(amount=p.mount_thickness)

    # ear holes
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
        location = Location((0, 0))
        location *= Pos(X=-(inner_width + p.ear_width) / 2)
        with Locations(location):
            vertical_spacing = p.mount_height - (0.5 * IN)
            with GridLocations(0, vertical_spacing, 1, 2):
                SlotOverall(p.ear_hole_width, p.ear_hole_height)
        mirror(about=Plane.YZ)
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

    # tray
    tray_width = p.device_width + (p.mount_thickness * 2)
    tray_rack_width_difference = (tray_width - p.rack_width) + (p.mount_thickness * 2)
    tray_depth = p.device_depth + p.mount_thickness
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
    with BuildSketch(Plane(face.without_holes(), x_dir=(-1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(X=-(tray_width) / 2)
        location *= Pos(Y=-p.mount_height / 2)
        with Locations(location):
            Rectangle(tray_width / 2, p.mount_thickness, align=(Align.MIN, Align.MIN))
            Rectangle(p.mount_thickness, p.mount_height, align=(Align.MIN))
        location *= Pos(Y=p.mount_height)
        with Locations(location):
            Rectangle(
                tray_rack_width_difference / 2,
                p.mount_thickness,
                align=(Align.MIN, Align.MAX),
            )
        mirror(about=Plane.YZ)
    extrude(amount=tray_depth)

    # oversize tray subtraction
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
    mirror_plane = Plane(face.offset(-tray_width / 2))
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
    edge = face.edges().filter_by(Axis.Y).sort_by(Axis.X)[1]
    location = edge.location_at(1.0)
    with BuildSketch(
        Plane(location.position, x_dir=(0, -1, 0), z_dir=face.normal_at())
    ) as sketch:
        taper_width = (tray_rack_width_difference / 2) - p.mount_thickness
        location = Location((0, 0))
        with Locations(location):
            Rectangle(
                p.mount_oversize_taper_offset, taper_width, align=(Align.MAX, Align.MIN)
            )
        location = Location((0, 0))
        location *= Pos(X=-p.mount_oversize_taper_offset)
        with Locations(location):
            Triangle(
                C=90,
                a=p.mount_oversize_taper_length,
                b=taper_width,
                align=(Align.MAX, Align.MIN),
            )
    sketch_face = sketch.face
    extruded = extrude(amount=-p.mount_height, mode=Mode.SUBTRACT)
    mirror(extruded, about=mirror_plane, mode=Mode.SUBTRACT)

    # tray rib
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
    with BuildSketch(Plane(face, x_dir=(0, -1, 0))):
        location = Location((0, 0))
        location *= Pos(Y=p.mount_height / 2)
        location *= Pos(X=(tray_depth / 2))
        with Locations(location) as locs:
            testing = locs.locations[0]
    print("here")

main(builder)
