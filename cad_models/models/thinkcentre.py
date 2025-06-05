from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    SlotOverall,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class Thinkcentre(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(179 * MM, 34.5 * MM, 183 * MM)
        foot_dimensions = Vector(15 * MM, 6.5 * MM, 2.5 * MM)
        foot_spacing = Vector(162.5 * MM, 133 * MM)
        foot_offset = 0.5 * MM

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
            location = face.location_at(0.5, 0.5)
            location *= Pos(Y=-foot_offset)
            with BuildSketch(location):
                with GridLocations(foot_spacing.X, foot_spacing.Y, 2, 2):
                    SlotOverall(foot_dimensions.X, foot_dimensions.Y, rotation=90)
            extrude(amount=foot_dimensions.Z)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Thinkcentre())
