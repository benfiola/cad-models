from build123d import *
from common import *

keystone_count = 5
keystone_vertical_spacing = 3 * MM
insert_height = 76.2 * MM
insert_width = 44.45 * MM
screw_radius = 2.0 * MM
screw_head_radius = 3.0 * MM
screw_vertical_spacing = 96.8 * MM
wall_thickness_x = 10.0 * MM
wall_thickness_y = 5 * MM
wall_thickness_z = 5 * MM
height = max(
    114.3 * MM, keystone_count * (KeystoneReceiver.height() + keystone_vertical_spacing)
)
width = 71.12 * MM
depth = 50 * MM

with BuildPart() as box:
    # initial box
    with BuildSketch(Plane.XZ):
        Rectangle(width, height)
    extrude(amount=depth)

    # box shell
    face = Plane(box.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0], x_dir=(1, 0, 0))
    inner_width = width - (wall_thickness_x * 2)
    inner_height = height - (wall_thickness_y * 2)
    inner_depth = depth - wall_thickness_z
    with BuildSketch(face):
        Rectangle(inner_width, inner_height)
    extrude(amount=-inner_depth, mode=Mode.SUBTRACT)

    # insert hole
    face = Plane(box.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2], x_dir=(1, 0, 0))
    with BuildSketch(face):
        Rectangle(insert_width, insert_height)
    extrude(amount=-wall_thickness_z, mode=Mode.SUBTRACT)

    # screw holes
    face = Plane(box.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2], x_dir=(1, 0, 0))
    with Locations(face):
        with GridLocations(0, screw_vertical_spacing, 1, 2):
            CounterSinkHole(screw_radius, screw_head_radius, wall_thickness_z)

    # keystone receivers
    face = Plane(box.faces().filter_by(Axis.X).sort_by(Axis.X)[0], x_dir=(0, -1, 0))
    mirror_plane = face.offset(width / 2)
    with Locations(face):
        spacing = keystone_vertical_spacing + KeystoneReceiver.height()
        with GridLocations(0, spacing, 1, keystone_count):
            KeystoneReceiver(align=(Align.CENTER, Align.CENTER, Align.MAX))
set_label(box, "Box")

main(box)
