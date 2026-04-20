import typing

from build123d import *
from common import *


@dataclass
class Parameters:
    ear_hole_width = 12 * MM
    ear_hole_height = 6 * MM
    ear_hole_horizontal_offset = 3 * MM
    ear_thickness = 5 * MM
    ear_width = 20 * MM
    panel_width = 254 * MM
    panel_height = 1 * U
    panel_thickness = KeystoneReceiver.depth()
    keystone_count = 8
    keystone_spacing = 3 * MM


p = Parameters()

with BuildPart() as builder:
    inner_width = p.panel_width - (p.ear_width * 2)

    # profile
    with BuildSketch():
        with BuildLine():
            Polyline(
                (0, 0),
                (0, p.ear_thickness),
                (p.ear_width, p.ear_thickness),
                (p.ear_width, p.panel_thickness),
                (p.ear_width + inner_width, p.panel_thickness),
                (p.ear_width + inner_width, p.ear_thickness),
                (p.ear_width + inner_width + p.ear_width, p.ear_thickness),
                (p.ear_width + inner_width + p.ear_width, 0),
                (0, 0),
            )
        make_face()
    extrude(amount=p.panel_height)

    # ear holes
    face = builder.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
    mirror_plane = Plane(face.offset(-p.panel_width / 2))
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
        horizontal_offset = p.ear_hole_horizontal_offset + (p.ear_hole_width / 2)
        location = Location((0, 0))
        location *= Pos(X=-p.panel_width / 2)
        location *= Pos(X=horizontal_offset)
        with Locations(location):
            vertical_spacing = p.panel_height - (0.5 * IN)
            with GridLocations(0, vertical_spacing, 1, 2):
                SlotOverall(p.ear_hole_width, p.ear_hole_height)
    extruded = extrude(amount=-p.ear_thickness, mode=Mode.SUBTRACT)
    mirror(extruded, mirror_plane, mode=Mode.SUBTRACT)

    # keystone cutouts
    face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
    keystone_locations = []
    with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
        horizontal_spacing = KeystoneReceiver.width() + (
            max(0, inner_width - (KeystoneReceiver.width() * p.keystone_count))
            / p.keystone_count
        )
        with GridLocations(horizontal_spacing, 0, p.keystone_count, 1) as grid_locs:
            Rectangle(KeystoneReceiver.width(), KeystoneReceiver.height())
            for location in grid_locs.locations:
                keystone_location = location * Rot(X=-90)
                keystone_locations.append(keystone_location)
    extrude(amount=-p.panel_thickness, mode=Mode.SUBTRACT)

    # keystone receivers
    for index, joint_location in enumerate(keystone_locations):
        with BuildPart(mode=Mode.PRIVATE):
            receiver = KeystoneReceiver()
        receiver_joint = typing.cast(RigidJoint, receiver.joints["joint"])
        joint = RigidJoint(f"keystone-{index}", builder.part, joint_location)
        joint.connect_to(receiver_joint)
        add(receiver)

main(builder)
