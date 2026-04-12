from build123d import *
from common import *

height = 114.3 * MM
width = 71.12 * MM
depth = 50 * MM
insert_height = 76.2 * MM
insert_width = 44.45 * MM
screw_radius = 2.0 * MM
screw_head_radius = 3.0 * MM
screw_vertical_spacing = 96.8 * MM
wall_thickness_x = 10.0 * MM
wall_thickness_y = 5 * MM
wall_thickness_z = 5 * MM

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

    # screw
    face = Plane(box.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2], x_dir=(1, 0, 0))
    with Locations(face):
        with GridLocations(0, screw_vertical_spacing, 1, 2):
            CounterSinkHole(screw_radius, screw_head_radius, wall_thickness_z)

    # keystone receivers
set_label(box, "Box")

main(box)
