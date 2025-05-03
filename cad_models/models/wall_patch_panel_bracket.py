from collections.abc import Iterable

import ocp_vscode
from bd_warehouse.fastener import ClearanceHole, Nut, Screw
from build123d import (
    MM,
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Compound,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    RigidJoint,
    Solid,
    Vector,
    VectorLike,
    extrude,
    make_face,
)

from cad_models.common import (
    RackMountNut,
    RackMountScrew,
    WallScrew,
    captive_nut_slot_dimensions,
    centered_point_list,
)


class WallPatchPanelBracket(Solid):
    def __init__(
        self,
        *,
        bracket_screw: Screw,
        dimensions: VectorLike,
        label: str = "",
        mount_arm_profile: VectorLike,
        mount_nut: Nut,
        mount_nut_offset: float,
        mount_screw: Screw,
    ):
        """
        :param bracket_screw: the screw securing the bracket to the wall
        :param dimensions: the dimensions of the bracket base
        :param label: the label for the produced solid
        :param mount_arm_depth: the depth of the arms extending from the bracket base.  this is in addition to the depth of the bracket base
        :param mount_nut: the captive nut used to secure the mount screw to the bracket
        :param mount_nut_offset: the distance from the edge of the mount arm to place the mount captive nut slot
        :param mount_screw: the screw securing the 'other' object to the bracket
        """
        if isinstance(dimensions, Iterable):
            dimensions = Vector(dimensions)
        if isinstance(mount_arm_profile, Iterable):
            mount_arm_profile = Vector(*mount_arm_profile)

        with BuildPart() as builder:
            # create the bracket
            with BuildSketch(Plane.YZ):
                with BuildLine():
                    # side profile of the bracket
                    d = dimensions
                    map = mount_arm_profile
                    # design polyline where bottom left is origin for readability
                    Polyline(
                        centered_point_list(
                            (0, 0),
                            (d.Z + map.X, 0),
                            (d.Z + map.X, d.Y),
                            (0, d.Y),
                            (0, d.Y - map.Y),
                            (map.X, d.Y - map.Y),
                            (map.X, map.Y),
                            (0, map.Y),
                            (0, 0),
                        )
                    )
                make_face()
            extrude(amount=dimensions.X)

            # create the bracket hole
            front_face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[2]
            location = front_face.location_at(0.5, 0.5)
            with Locations(location):
                ClearanceHole(bracket_screw)

            arm_faces = (
                builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[:2].sort_by(Axis.Z)
            )
            for arm_face in arm_faces:
                location = arm_face.location_at(0.5, 0.5)
                with Locations(location):
                    # create mount screw hole
                    ClearanceHole(
                        mount_screw, depth=mount_screw.length, counter_sunk=False
                    )

                    # create mount joint
                    joint_label = "mount-top"
                    if arm_faces[0] == arm_face:
                        joint_label = "mount-bottom"
                    joint_location = Location(arm_face.position_at(0.5, 0.5))
                    RigidJoint(joint_label, joint_location=joint_location)

                # create mount nut slot
                top = arm_face.location_at(0.0, 0.5)
                top *= Pos(Z=-mount_nut_offset)
                slot_dimensions = captive_nut_slot_dimensions(mount_nut)
                extra_height = (arm_face.length - slot_dimensions.Y) / 2
                with Locations(top):
                    Box(
                        length=slot_dimensions.Y + extra_height,
                        width=slot_dimensions.X,
                        height=mount_nut.nut_thickness,
                        mode=Mode.SUBTRACT,
                        align=(Align.MIN, Align.CENTER, Align.CENTER),
                    )

        super().__init__(builder.part.wrapped, joints=builder.joints, label=label)


class Model(Compound):
    def __init__(self):
        bracket = WallPatchPanelBracket(
            bracket_screw=WallScrew(),
            dimensions=(18.0 * MM, 90.0 * MM, 12.0 * MM),
            label="bracket",
            mount_arm_profile=(90.0 * MM, 12.0 * MM),
            mount_nut=RackMountNut(),
            mount_nut_offset=4.0 * MM,
            mount_screw=RackMountScrew(),
        )

        return super().__init__([], children=[bracket])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
