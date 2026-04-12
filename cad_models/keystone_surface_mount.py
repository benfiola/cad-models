from build123d import *
from common import *

cover_dovetail_depth = 3 * MM
keystone_count = 5
keystone_vertical_spacing = 3 * MM
insert_height = 76.2 * MM
insert_width = 44.45 * MM
screw_radius = 2.0 * MM
screw_head_radius = 3.0 * MM
screw_vertical_spacing = 96.8 * MM
wall_thickness_x = KeystoneReceiver.depth()
wall_thickness_y = 5 * MM
wall_thickness_z = 5 * MM
height = max(
    114.3 * MM,
    keystone_count * (KeystoneReceiver.height() + (keystone_vertical_spacing + 2)),
)
width = 71.12 * MM
depth = 50 * MM

with BuildPart() as builder:
    # cover
    with BuildSketch(Plane.XY) as sketch:
        inner_width = width - (wall_thickness_x * 2)
        with BuildLine() as line:
            Polyline(
                (0, 0),
                (cover_dovetail_depth + inner_width + cover_dovetail_depth, 0),
                (cover_dovetail_depth + inner_width, wall_thickness_z),
                (cover_dovetail_depth, wall_thickness_z),
                (0, 0),
            )
        make_face()
    extrude(amount=height - wall_thickness_y)
cover = get_part(builder)
cover.label = "Cover"

with BuildPart() as builder:
    # initial box
    with BuildSketch(Plane.XZ):
        Rectangle(width, height)
    extrude(amount=depth)

    # box shell
    face = Plane(builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0], x_dir=(1, 0, 0))
    inner_width = width - (wall_thickness_x * 2)
    inner_height = height - (wall_thickness_y * 2)
    inner_depth = depth - wall_thickness_z
    with BuildSketch(face):
        Rectangle(inner_width, inner_height)
    extrude(amount=-inner_depth, mode=Mode.SUBTRACT)

    # cover slot

    # insert hole
    face = Plane(builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2], x_dir=(1, 0, 0))
    with BuildSketch(face):
        Rectangle(insert_width, insert_height)
    extrude(amount=-wall_thickness_z, mode=Mode.SUBTRACT)

    # screw holes
    face = Plane(builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2], x_dir=(1, 0, 0))
    with Locations(face):
        with GridLocations(0, screw_vertical_spacing, 1, 2):
            CounterSinkHole(screw_radius, screw_head_radius, wall_thickness_z)

    # keystone receivers
    face = Plane(builder.faces().filter_by(Axis.X).sort_by(Axis.X)[0], x_dir=(0, -1, 0))
    mirror_plane = face.offset(-width / 2)
    cutouts = []
    receivers = []
    with Locations(face) as face:
        spacing = keystone_vertical_spacing + KeystoneReceiver.height()
        with GridLocations(0, spacing, 1, keystone_count):
            cutouts += Box(
                KeystoneReceiver.width(),
                KeystoneReceiver.height(),
                wall_thickness_x,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT,
            )
            receivers += KeystoneReceiver(align=(Align.CENTER, Align.CENTER, Align.MAX))
    mirror(cutouts, mirror_plane, mode=Mode.SUBTRACT)
    mirror(receivers, mirror_plane)
box = get_part(builder)
box.label = "Box"

compound = Compound(children=[box, cover])

main(compound)
