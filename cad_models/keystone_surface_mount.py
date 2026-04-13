import typing

from bd_warehouse import *
from build123d import *
from common import *

cover_dovetail_depth = 3 * MM
insert_height = 76.2 * MM
insert_width = 44.45 * MM
keystone_count = 5
keystone_vertical_spacing = 3 * MM
screw_radius = 2.0 * MM
screw_head_radius = 3.0 * MM
screw_vertical_spacing = 96.8 * MM
wall_thickness_x = KeystoneReceiver.depth()
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
