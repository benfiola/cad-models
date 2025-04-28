from collections.abc import Iterable

import ocp_vscode
from bd_warehouse.fastener import ClearanceHole, Nut, Screw
from build123d import (
    MM,
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Compound,
    GridLocations,
    Locations,
    Mode,
    Pos,
    Rectangle,
    Solid,
    Vector,
    VectorLike,
    extrude,
)

from cad_models.common import (
    RackMountNut,
    RackMountScrew,
    WallScrew,
    captive_nut_slot_dimensions,
)


class Bracket(Solid):
    def __init__(
        self,
        *,
        bracket_screw: Screw,
        dimensions: VectorLike,
        label: str = "",
        mount_arm_dimensions: VectorLike,
        mount_nut: Nut,
        mount_nut_offset: float,
        mount_screw: Screw,
    ):
        """
        :param bracket_screw: the screw securing the bracket to the wall
        :param dimensions: the dimensions of the bracket base
        :param label: the label for the produced solid
        :param mount_arm_dimensions: the dimensions of the arms extending from the bracket base.  the depth of the arms is in addition to the depth of the bracket base
        :param mount_nut: the captive nut used to secure the mount screw to the bracket
        :param mount_nut_offset: the distance from the edge of the mount arm to place the mount captive nut slot
        :param mount_screw: the screw securing the 'other' object to the bracket
        """
        # convert vectorlikes
        if isinstance(dimensions, Iterable):
            dimensions = Vector(dimensions)
        if isinstance(mount_arm_dimensions, Iterable):
            mount_arm_dimensions = Vector(mount_arm_dimensions)

        with BuildPart() as builder:
            # create the base
            with BuildSketch():
                Rectangle(dimensions.X, dimensions.Y)
            extrude(amount=dimensions.Z)
            front_face = builder.faces().sort_by(Axis.Z)[-1]

            # create the bracket hole
            with Locations(front_face.location):
                ClearanceHole(bracket_screw)

            # create mount arms
            with BuildSketch(front_face):
                spacing = (0.0, dimensions.Y - mount_arm_dimensions.Y)
                with GridLocations(*spacing, 1, 2) as grid_locations:
                    Rectangle(mount_arm_dimensions.X, mount_arm_dimensions.Y)
            arms = extrude(amount=mount_arm_dimensions.Z)

            front_faces = arms.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-2:]
            for front_face in front_faces:
                # create mount screw hole
                with Locations(front_face.location):
                    ClearanceHole(
                        mount_screw, depth=mount_screw.length, counter_sunk=False
                    )

                # create mount nut slot
                top = front_face.location * Pos(
                    Y=front_face.width / 2, Z=-mount_nut_offset
                )
                slot_dimensions = captive_nut_slot_dimensions(mount_nut)
                extra_height = (front_face.width - slot_dimensions.Y) / 2
                with Locations(top):
                    Box(
                        length=slot_dimensions.X,
                        width=slot_dimensions.Y + extra_height,
                        height=mount_nut.nut_thickness,
                        mode=Mode.SUBTRACT,
                        align=(Align.CENTER, Align.MAX, Align.MAX),
                    )

        super().__init__(builder.part.wrapped, label=label)


class Model(Compound):
    def __init__(self):
        bracket = Bracket(
            bracket_screw=WallScrew(),
            dimensions=Vector(18.0 * MM, 90.0 * MM, 10.0 * MM),
            label="bracket",
            mount_arm_dimensions=(18.0 * MM, 16.0 * MM, 90.0 * MM),
            mount_nut=RackMountNut(),
            mount_nut_offset=4.0 * MM,
            mount_screw=RackMountScrew(),
        )

        return super().__init__(
            [], children=[bracket], label="wall-patch-panel-bracket"
        )


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
