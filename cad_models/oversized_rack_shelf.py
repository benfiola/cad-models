import math

from build123d import *

from cad_models.common import *


@dataclass
class Parameters:
    device_height: float
    device_width: float
    device_depth: float
    ear_hole_width: float = 12 * MM
    ear_hole_height: float = 6 * MM
    ear_width: float = 15 * MM
    hex_radius: float = 3.0 * MM
    hex_spacing: float = 3.0 * MM
    mount_width: float = 252 * MM
    mount_height: float = 1 * U
    mount_thickness: float = 5 * MM
    mount_lip: float = 2 * MM
    oversize_taper_offset: float = 10 * MM
    oversize_taper_length: float = 10 * MM
    rack_width: float = 222 * MM


rb4011 = Parameters(
    device_height=26 * MM,
    device_width=227.7 * MM + 1.0 * MM,
    device_depth=117.7 * MM + 1.0 * MM,
)


p = rb4011


with BuildPart() as builder:
    inner_width = p.mount_width - (p.ear_width * 2)

    # front panel
    with BuildSketch(Plane.XZ):
        Rectangle(p.mount_width, p.mount_height)
    extrude(amount=p.mount_thickness)

    # ear holes
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
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
    oversize_top_width = (tray_width - p.rack_width) + (p.mount_thickness * 2)
    tray_depth = p.device_depth + p.mount_thickness + p.oversize_taper_offset
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
                oversize_top_width / 2,
                p.mount_thickness,
                align=(Align.MIN, Align.MAX),
            )
        mirror(about=Plane.YZ)
    extrude(amount=tray_depth)

    # tray rib via subtraction
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
    mirror_plane = Plane(face.offset(-tray_width / 2))
    rib_thickness = oversize_top_width
    with BuildSketch(Plane(face, x_dir=(0, -1, 0))):
        rib_width = tray_depth - (
            (p.oversize_taper_offset * 2) + p.oversize_taper_length
        )
        rib_height = p.mount_height - p.mount_thickness
        location = Location((0, 0))
        location *= Pos(Y=p.mount_height / 2)
        location *= Pos(X=tray_depth / 2)
        location *= Pos(X=-((p.oversize_taper_offset * 2) + p.oversize_taper_length))
        with Locations(location):
            Triangle(
                C=90,
                a=rib_width,
                b=rib_height,
                align=(Align.MIN, Align.MIN),
                rotation=180,
            )
    extruded = extrude(amount=-rib_thickness, mode=Mode.SUBTRACT)
    mirror(extruded, about=mirror_plane, mode=Mode.SUBTRACT)

    # oversize tray cutouts
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
    mirror_plane = Plane(face.offset(tray_width / 2))
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
    edge = face.edges().filter_by(Axis.Y).sort_by(Axis.X)[1]
    location = edge.location_at(1.0)
    with BuildSketch(
        Plane(location.position, x_dir=(0, -1, 0), z_dir=face.normal_at())
    ):
        taper_width = (oversize_top_width / 2) - p.mount_thickness
        location = Location((0, 0))
        with Locations(location):
            Rectangle(
                p.oversize_taper_offset, taper_width, align=(Align.MAX, Align.MIN)
            )
        location = Location((0, 0))
        location *= Pos(X=-p.oversize_taper_offset)
        with Locations(location):
            Triangle(
                C=90,
                a=p.oversize_taper_length,
                b=taper_width,
                align=(Align.MAX, Align.MIN),
            )
    extruded = extrude(amount=-p.mount_height, mode=Mode.SUBTRACT)
    mirror(extruded, about=mirror_plane, mode=Mode.SUBTRACT)

    # device tray inset
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[3]
    with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(Y=-tray_depth / 2)
        location *= Pos(Y=p.oversize_taper_offset / 2)
        with Locations(location):
            inset_height = p.device_depth + (p.oversize_taper_offset / 2)
            Rectangle(p.device_width, inset_height, align=(Align.CENTER, Align.MIN))
    extrude(amount=-p.mount_lip, mode=Mode.SUBTRACT)

    # device tray inset hex grid
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
    with BuildSketch(face):
        spacing = p.hex_radius + (p.hex_spacing / 2)
        hex_count_x = int(p.device_width / (math.sqrt(3) * spacing))
        hex_count_y = int(p.device_depth / (2 * spacing))
        with HexLocations(
            spacing,
            hex_count_x,
            hex_count_y,
            major_radius=False,
        ):
            RegularPolygon(p.hex_radius, 6, major_radius=False)
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

    # front panel cutout
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    cutout_width = p.rack_width
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(Y=-p.mount_height / 2)
        location *= Pos(Y=p.mount_thickness)
        with Locations(location):
            Rectangle(cutout_width, p.device_height, align=(Align.CENTER, Align.MIN))
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

main(builder)
