from collections.abc import Iterable

import ocp_vscode
from build123d import (
    IN,
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Compound,
    GridLocations,
    Locations,
    Mode,
    Rectangle,
    Solid,
    Vector,
    VectorLike,
    extrude,
)


class Bracket(Solid):
    def __init__(
        self,
        *,
        bracket_screw_diameter: float,
        bracket_screw_head_dimensions: VectorLike,
        dimensions: VectorLike,
        label: str = "",
        mount_arm_dimensions: VectorLike,
        mount_nut_dimensions: VectorLike,
        mount_nut_offset: float,
        mount_screw_dimensions: VectorLike
    ):
        # convert vectorlikes
        if isinstance(bracket_screw_head_dimensions, Iterable):
            bracket_screw_head_dimensions = Vector(bracket_screw_head_dimensions)
        if isinstance(mount_arm_dimensions, Iterable):
            mount_arm_dimensions = Vector(mount_arm_dimensions)
        if isinstance(mount_nut_dimensions, Iterable):
            mount_nut_dimensions = Vector(mount_nut_dimensions)
        if isinstance(mount_screw_dimensions, Iterable):
            mount_screw_dimensions = Vector(mount_screw_dimensions)

        with BuildPart() as builder:
            # create the base
            with BuildSketch():
                Rectangle(dimensions.X, dimensions.Y)
            extrude(amount=dimensions.Z)
            front_face = builder.faces().sort_by(Axis.Z)[-1]

            # create the bracket hole
            with BuildSketch(front_face):
                Circle(radius=bracket_screw_diameter / 2)
            extrude(amount=-dimensions.Z, mode=Mode.SUBTRACT)
            with BuildSketch(front_face):
                Circle(radius=bracket_screw_head_dimensions.X / 2)
            extrude(amount=-bracket_screw_head_dimensions.Z, mode=Mode.SUBTRACT)

            # create mount arms
            with BuildSketch(front_face):
                spacing = (0.0, dimensions.Y - mount_arm_dimensions.Y)
                with GridLocations(*spacing, 1, 2) as grid_locations:
                    Rectangle(dimensions.X, mount_arm_dimensions.Y)
            arms = extrude(amount=mount_arm_dimensions.Z)

            # create mount screw hole
            front_faces = arms.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-2:]
            for front_face in front_faces:
                with BuildSketch(front_face):
                    Circle(radius=mount_screw_dimensions.X / 2)
                extrude(amount=-mount_screw_dimensions.Z, mode=Mode.SUBTRACT)

            # create mount nut slot
            top_faces = arms.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1::2]
            for top_face in top_faces:
                with BuildSketch(top_face) as sketch:
                    location = (
                        0.0,
                        (-top_face.width / 2)
                        + mount_nut_offset
                        + (mount_nut_dimensions.Z / 2),
                    )
                    with Locations(location) as location:
                        Rectangle(mount_nut_dimensions.X, mount_nut_dimensions.Z)
                # ensure mount slot is centered with screw
                arm_center = mount_arm_dimensions.Y / 2
                nut_center = mount_nut_dimensions.Y / 2
                depth = mount_nut_dimensions.Y + (arm_center - nut_center)
                extrude(amount=-depth, mode=Mode.SUBTRACT)

        super().__init__(builder.part.wrapped, label=label)


class Model(Compound):
    def __init__(self):
        bracket = Bracket(
            # bracket screw is #7 screw
            bracket_screw_diameter=0.182 * IN,
            bracket_screw_head_dimensions=Vector(0.325 * IN, 0 * MM, 0.16 * IN),
            dimensions=Vector(18.0 * MM, 90.0 * MM, 10.0 * MM),
            label="bracket",
            mount_arm_dimensions=Vector(0.0 * MM, 12.0 * MM, 40.0 * MM),
            # mount screw/nut is #10-32
            mount_nut_dimensions=Vector(0.390 * IN, 0.390 * IN, 0.140 * IN),
            mount_nut_offset=2.0 * MM,
            mount_screw_dimensions=Vector(0.206 * IN, 0 * MM, 0.75 * IN),
        )

        return super().__init__([], children=[bracket])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
