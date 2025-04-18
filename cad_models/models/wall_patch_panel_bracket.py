from collections.abc import Iterable

import ocp_vscode
from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    GridLocations,
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
        arm_dimensions: VectorLike,
        dimensions: VectorLike,
        label: str = "",
        mount_hole_offset: VectorLike,
    ):
        """ """
        # convert VectorLikes
        if isinstance(arm_dimensions, Iterable):
            arm_dimensions = Vector(*arm_dimensions)
        if isinstance(dimensions, Iterable):
            dimensions = Vector(*dimensions)
        if isinstance(mount_hole_offset, Iterable):
            mount_hole_offset = Vector(*mount_hole_offset)

        with BuildPart() as part:
            with BuildSketch():
                Rectangle(dimensions.X, dimensions.Y)
            base = extrude(amount=dimensions.Z)

            front = base.faces().filter_by(Axis.Z)[1]
            with BuildSketch(front):
                with GridLocations(0, front.width - arm_dimensions.Y, 1, 2):
                    Rectangle(arm_dimensions.X, arm_dimensions.Y)
            extrude(amount=arm_dimensions.Z - base.height)

        super().__init__(part.wrapped, label=label)


class Model(Compound):
    def __init__(self):
        bracket = Bracket(
            arm_dimensions=Vector(10 * MM, 10 * MM, 80 * MM),
            dimensions=Vector(10 * MM, 100 * MM, 10.0 * MM),
            mount_hole_offset=Vector(2.0 * MM, 2.0 * MM),
            label="bracket",
        )
        return super().__init__([], children=[bracket])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
