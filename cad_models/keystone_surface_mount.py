import typing

<<<<<<< Updated upstream
from bd_warehouse import *
=======
>>>>>>> Stashed changes
from build123d import *
from common import *
from ocp_vscode.show import show_object

<<<<<<< Updated upstream
cover_dovetail_depth = 3 * MM
insert_height = 76.2 * MM
insert_width = 44.45 * MM
keystone_count = 5
keystone_vertical_spacing = 3 * MM
=======
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
>>>>>>> Stashed changes
screw_radius = 2.0 * MM
screw_head_radius = 3.0 * MM
screw_vertical_spacing = 96.8 * MM
wall_thickness_x = KeystoneReceiver.depth()
<<<<<<< Updated upstream
wall_thickness_y = 5 * MM
wall_thickness_z = 5 * MM
depth = 50 * MM
height = max(
    114 * MM,
    (keystone_count * KeystoneReceiver.height())
    + (keystone_vertical_spacing * (keystone_count + 2)),
)
width = 71.12 * MM


class Cover(BasePartObject):
    _applies_to = [BuildPart._tag]

    def __init__(
        self,
        *,
        rotation: Rotation | tuple[float, float, float] = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as builder:
            inner_height = height - (wall_thickness_y)
            with BuildSketch():
                with BuildLine():
                    inner_width = width - (wall_thickness_x * 2)
                    Polyline(
                        (0, 0),
                        (cover_dovetail_depth + inner_width + cover_dovetail_depth, 0),
                        (cover_dovetail_depth + inner_width, wall_thickness_z),
                        (cover_dovetail_depth, wall_thickness_z),
                        (0, 0),
                    )
                make_face()
            extrude(amount=inner_height)
        part = ensure_part(builder.part)
        part.location *= Rot(Z=180)

        face = part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        joint_location = face.location_at(0.5, 0.0)
        RigidJoint("joint", part, joint_location)

        super().__init__(part, rotation, align, mode)


class MountBox(BasePartObject):
    _applies_to = [BuildPart._tag]

    def __init__(
        self,
        rotation: Rotation | tuple[float, float, float] = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
    ):
        with BuildPart() as builder:
            # box
            with BuildSketch():
                Rectangle(width, depth)
            extrude(amount=height)

            # box shell
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            inner_depth = depth - wall_thickness_z
            with BuildSketch(face):
                inner_width = width - (wall_thickness_x * 2)
                inner_height = height - (wall_thickness_y * 2)
                Rectangle(inner_width, inner_height)
            extrude(amount=-inner_depth, mode=Mode.SUBTRACT)

            # cover slot
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            joint_location = face.location_at(0.5, 0.0)
            joint = RigidJoint("cover", builder.part, joint_location)
            cover = Cover()
            joint.connect_to(typing.cast(RigidJoint, cover.joints["joint"]))
            add(cover, mode=Mode.SUBTRACT)

            # insert hole
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2]
            with BuildSketch(face):
                Rectangle(insert_width, insert_height)
            extrude(amount=-wall_thickness_z, mode=Mode.SUBTRACT)

            # screw holes
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-2]
            with Locations(face):
                with GridLocations(0, screw_vertical_spacing, 1, 2):
                    CounterSinkHole(screw_radius, screw_head_radius, wall_thickness_z)

        part = ensure_part(builder.part)
        super().__init__(part, rotation, align, mode)


cover = Cover()
cover.label = "Cover"
box = MountBox()
box.label = "Box"
compound = Compound(children=[box, cover])
main(compound)
=======
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
        joint_location = Location(keystone_location) * Rot(X=-90)
        joint = RigidJoint(f"keystone-{index}", box_builder.part, joint_location)
        joint.connect_to(receiver_joint)
        print("here")

show_object(box_builder.part)
>>>>>>> Stashed changes
