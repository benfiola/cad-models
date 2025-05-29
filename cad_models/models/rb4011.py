from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class RB4011(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(228 * MM, 26.2 * MM, 117.8 * MM)
        feet_diameter = 14 * MM
        feet_height = 3.5 * MM
        feet_spacing = Vector(162.2 * MM, 65.34 * MM)
        feet_offset = 51.16 * MM

        with BuildPart() as builder:
            # create router box
            with BuildSketch(Plane.XZ):
                Rectangle(dimensions.X, dimensions.Y)
            extrude(amount=dimensions.Z)

            # create joint
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.5)
            location *= Rot(X=180)
            location *= Rot(Z=180)
            RigidJoint(f"mount", joint_location=location)

            # create feet
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.0)
            location *= Pos(Y=feet_offset)
            with BuildSketch(location):
                with GridLocations(feet_spacing.X, feet_spacing.Y, 2, 2):
                    Circle(feet_diameter / 2)
            extrude(amount=feet_height)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RB4011())
