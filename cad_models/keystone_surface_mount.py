import copy
import typing

from build123d import *
from common import *
from ocp_vscode.show import show_object

box_width = 150 * MM
box_depth = 50 * MM
box_height = 150 * MM
cover_dovetail_depth = 3 * MM
cover_fillet_radius = 1 * MM
insert_height = 76.2 * MM
insert_width = 44.45 * MM
keystone_left_count = 4
keystone_right_count = 4
keystone_bottom_count = 1
keystone_top_count = 0
keystone_spacing = 3 * MM
screw_radius = 2.0 * MM
screw_head_radius = 3.0 * MM
screw_vertical_spacing = 96.8 * MM
wall_thickness_x = KeystoneReceiver.depth()
wall_thickness_y = KeystoneReceiver.depth()
wall_thickness_z = 5 * MM

with BuildPart() as cover_builder:
    # cover
    inner_height = box_height - (wall_thickness_y)
    inner_width = box_width - (wall_thickness_x * 2)
    with BuildSketch():
        with BuildLine():
            Polyline(
                (0, 0),
                (cover_dovetail_depth + inner_width + cover_dovetail_depth, 0),
                (cover_dovetail_depth + inner_width, -wall_thickness_z),
                (cover_dovetail_depth, -wall_thickness_z),
                (0, 0),
            )
        make_face()
    extrude(amount=inner_height)

    # fillet
    edges = cover_builder.edges().filter_by(Axis.Z).sort_by(Axis.X)
    edges = [edges[0], edges[-1]]
    fillet(edges, cover_fillet_radius)

    # joint
    face = cover_builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    joint_location = Location(face.location_at(0.5, 0.0).position, (0, 0, 0))
    RigidJoint("joint", cover_builder.part, joint_location)

with BuildPart() as box_builder:
    # box
    with BuildSketch(Plane.XZ):
        Rectangle(box_width, box_height)
    extrude(amount=box_depth)

    # shell
    face = box_builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    inner_depth = box_depth - (wall_thickness_z)
    inner_height = box_height - (wall_thickness_y * 2)
    inner_width = box_width - (wall_thickness_x * 2)
    with BuildSketch(face):
        Rectangle(inner_width, inner_height)
    extrude(amount=-inner_depth, mode=Mode.SUBTRACT)

    # cover slot
    face = box_builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
    cover = copy.copy(ensure_part(cover_builder.part))
    joint_location = Location(face.location_at(0.5, 0.0).position, (0, 0, 0))
    joint = RigidJoint("cover", box_builder.part, joint_location)
    joint.connect_to(typing.cast(RigidJoint, cover.joints["joint"]))
    add(cover, mode=Mode.SUBTRACT)

    # insert hole
    face = box_builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2]
    with BuildSketch(face):
        Rectangle(insert_width, insert_height)
    extrude(amount=-wall_thickness_z, mode=Mode.SUBTRACT)

    # screw holes
    face = box_builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2]
    with Locations(face):
        with GridLocations(0, screw_vertical_spacing, 1, 2):
            CounterSinkHole(screw_radius, screw_head_radius, wall_thickness_z)

    # keystone receiver cutouts
    spacing = KeystoneReceiver.height() + keystone_spacing
    keystone_locations: list[Location] = []
    if keystone_left_count:
        face = box_builder.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
        with BuildSketch(Plane(face, x_dir=(0, -1, 0))):
            with GridLocations(0, spacing, 1, keystone_left_count) as grid_locs:
                Rectangle(KeystoneReceiver.width(), KeystoneReceiver.height())
                keystone_locations += grid_locs.locations
        extrude(amount=-wall_thickness_x, mode=Mode.SUBTRACT)
    if keystone_right_count:
        face = box_builder.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
        with BuildSketch(Plane(face, x_dir=(0, 1, 0))):
            with GridLocations(0, spacing, 1, keystone_right_count) as grid_locs:
                Rectangle(KeystoneReceiver.width(), KeystoneReceiver.height())
                keystone_locations += grid_locs.locations
        extrude(amount=-wall_thickness_x, mode=Mode.SUBTRACT)
    if keystone_bottom_count:
        face = box_builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
        with BuildSketch(Plane(face, x_dir=(0, -1, 0))):
            with GridLocations(0, spacing, 1, keystone_bottom_count) as grid_locs:
                Rectangle(KeystoneReceiver.width(), KeystoneReceiver.height())
                keystone_locations += grid_locs.locations
        extrude(amount=-wall_thickness_y, mode=Mode.SUBTRACT)
    if keystone_top_count:
        face = box_builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
        with BuildSketch(Plane(face, x_dir=(0, 1, 0))):
            with GridLocations(0, spacing, 1, keystone_top_count) as grid_locs:
                Rectangle(KeystoneReceiver.width(), KeystoneReceiver.height())
                keystone_locations += grid_locs.locations
        extrude(amount=-wall_thickness_y, mode=Mode.SUBTRACT)

    # keystone receivers
    for index, keystone_location in enumerate(keystone_locations):
        receiver = KeystoneReceiver()
        receiver_joint = typing.cast(RigidJoint, receiver.joints["joint"])
        joint_location = keystone_location * Rot(X=-90)
        joint = RigidJoint(f"keystone-{index}", box_builder.part, joint_location)
        joint.connect_to(receiver_joint)
        add(receiver)


show_object(box_builder.part)
