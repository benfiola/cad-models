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


class Thinkcentre(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(228 * MM, 26.2 * MM, 117.8 * MM)
        foot_dimensions = Vector(14 * MM, 3.5 * MM)
        foot_offset = 51.16 * MM
        foot_spacing = Vector(162.2 * MM, 65.34 * MM)

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
            location *= Pos(Y=foot_offset)
            with BuildSketch(location):
                with GridLocations(foot_spacing.X, foot_spacing.Y, 2, 2):
                    Circle(foot_dimensions.X / 2)
            extrude(amount=foot_dimensions.Y)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Thinkcentre())
