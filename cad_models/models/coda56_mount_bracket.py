from collections.abc import Iterable

import ocp_vscode
from bd_warehouse.fastener import ClearanceHole, Nut
from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    Locations,
    Mode,
    Pos,
    Rectangle,
    SlotOverall,
    Solid,
    Vector,
    VectorLike,
    cos,
    degrees,
    extrude,
    mirror,
    sin,
)

from cad_models.common import RackInterfaceNut, captive_nut_slot_dimensions


class RackOuterBracket(Solid):
    def __init__(
        self,
        *,
        arm_dimensions: VectorLike,
        ear_dimensions: VectorLike,
        interface_hole_offset: float,
        interface_hole_spacing: float,
        interface_nut: Nut,
        label: str = "",
        mount_hole_dimensions: VectorLike,
        mount_hole_offset: VectorLike,
    ):
        if isinstance(arm_dimensions, Iterable):
            arm_dimensions = Vector(*arm_dimensions)
        if isinstance(ear_dimensions, Iterable):
            ear_dimensions = Vector(*ear_dimensions)
        if isinstance(mount_hole_dimensions, Iterable):
            mount_hole_dimensions = Vector(*mount_hole_dimensions)
        if isinstance(mount_hole_offset, Iterable):
            mount_hole_offset = Vector(*mount_hole_offset)

        with BuildPart() as builder:
            # create the mount ear
            with BuildSketch():
                Rectangle(ear_dimensions.X, ear_dimensions.Y)
            mount_ear = extrude(amount=ear_dimensions.Z)

            # create mount ear holes
            front_face = mount_ear.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            with BuildSketch(front_face):
                location = Vector(front_face.length, front_face.width)
                location /= 2
                location.Z = 0.0
                location -= mount_hole_offset
                location -= mount_hole_dimensions / 2
                with Locations(location):
                    mount_hole = SlotOverall(
                        mount_hole_dimensions.X,
                        mount_hole_dimensions.Y,
                    )
                mirror(mount_hole)
            extrude(amount=-ear_dimensions.Z, mode=Mode.SUBTRACT)

            # create mount arm
            back_face = mount_ear.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(back_face):
                location = Vector(-back_face.length)
                location /= 2
                location.Z = 0
                with Locations(location):
                    Rectangle(
                        arm_dimensions.X,
                        arm_dimensions.Y,
                        align=(Align.MIN, Align.CENTER),
                    )
            arm = extrude(amount=(arm_dimensions.Z - ear_dimensions.Z))

            # create interface nut clearance holes
            slot_size = captive_nut_slot_dimensions(interface_nut)
            arm_face = arm.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            right = arm_face.center_location
            right *= Pos(X=arm_face.width / 2)
            right *= Pos(X=-interface_hole_offset)
            right *= Pos(X=-slot_size.X / 2)
            spacing = Vector(
                (interface_hole_spacing + slot_size.X) * sin(degrees(60)),
                (interface_hole_spacing + slot_size.Y) * cos(degrees(60)),
            )
            top = right * Pos(X=-spacing.X, Y=spacing.Y)
            bottom = right * Pos(X=-spacing.X, Y=-spacing.Y)
            with Locations(right, top, bottom):
                ClearanceHole(interface_nut, captive_nut=True)

        super().__init__(builder.part.wrapped, joints=builder.joints, label=label)


class Model(Compound):
    def __init__(self):
        bracket = RackOuterBracket(
            arm_dimensions=(6.0 * MM, 41.35 * MM, 118.0 * MM),
            ear_dimensions=(31.0 * MM, 41.35 * MM, 6.0 * MM),
            interface_hole_offset=3.0 * MM,
            interface_hole_spacing=11.5 * MM,
            interface_nut=RackInterfaceNut(),
            mount_hole_dimensions=(12.0 * MM, 6.0 * MM),
            mount_hole_offset=(3.0 * MM, 3.0 * MM),
        )
        return super().__init__([], children=[bracket])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
