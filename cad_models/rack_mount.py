from build123d import *

from cad_models.common import *


@dataclass
class Parameters:
    device_height: float
    device_width: float
    device_depth: float
    hex_count_x: int
    hex_count_y: int
    ear_hole_width = 12 * MM
    ear_hole_height = 6 * MM
    ear_width = 15 * MM
    hex_radius = 3.0 * MM
    hex_spacing = 3.0 * MM

    mount_width = 252 * MM
    mount_height = 1 * U
    mount_thickness = 5 * MM
    mount_lip = 2 * MM
    rack_width = 222 * MM


thinkcentre = Parameters(
    device_width=179 * MM + 1.0 * MM,
    device_height=34.5 * MM,
    device_depth=183 * MM + 1.0 * MM,
    hex_count_x=23,
    hex_count_y=20,
)


p = thinkcentre


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
    tray_width = p.rack_width + (p.mount_thickness * 2)
    tray_depth = p.device_depth + p.mount_thickness
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
    with BuildSketch(Plane(face.without_holes(), x_dir=(-1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(X=-(tray_width) / 2)
        location *= Pos(Y=-p.mount_height / 2)
        with Locations(location):
            Rectangle(tray_width / 2, p.mount_thickness, align=(Align.MIN, Align.MIN))
            Rectangle(p.mount_thickness, p.mount_height, align=(Align.MIN))
        mirror(about=Plane.YZ)
    extrude(amount=tray_depth)

    # tray rib via subtraction
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
    mirror_plane = Plane(face.offset(-tray_width / 2))
    rib_thickness = p.mount_thickness
    with BuildSketch(Plane(face, x_dir=(0, -1, 0))):
        rib_width = tray_depth
        rib_height = p.mount_height - p.mount_thickness
        location = Location((0, 0))
        location *= Pos(Y=p.mount_height / 2)
        location *= Pos(X=tray_depth / 2)
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

    # device tray inset
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[3]
    with BuildSketch(Plane(face.without_holes(), x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(Y=-tray_depth / 2)
        with Locations(location):
            inset_height = p.device_depth
            Rectangle(p.device_width, inset_height, align=(Align.CENTER, Align.MIN))
    extrude(amount=-p.mount_lip, mode=Mode.SUBTRACT)

    # device tray inset hex grid
    face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
    with BuildSketch(face):
        spacing = p.hex_radius + (p.hex_spacing / 2)
        with HexLocations(
            spacing,
            p.hex_count_x,
            p.hex_count_y,
            major_radius=False,
        ):
            RegularPolygon(p.hex_radius, 6, major_radius=False)
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

    # front panel cutout
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    cutout_width = p.device_width
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
        location = Location((0, 0))
        location *= Pos(Y=-p.mount_height / 2)
        location *= Pos(Y=p.mount_thickness)
        with Locations(location):
            Rectangle(cutout_width, p.device_height, align=(Align.CENTER, Align.MIN))
    extrude(amount=-p.mount_thickness, mode=Mode.SUBTRACT)

main(builder)
