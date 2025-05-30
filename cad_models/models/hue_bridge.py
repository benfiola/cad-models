from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Mode,
    Plane,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class HueBridge(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(91.82 * MM, 26.9 * MM, 89.42 * MM)
        foot_spacing = Vector(65.24 * MM, 66.82 * MM)
        foot_dimensions = Vector(7.5 * MM, 0.9 * MM)
        mount_dimensions = Vector(9.2 * MM, 4.2 * MM)
        mount_spacing = 41.4 * MM

        with BuildPart() as builder:
            # create bridge box
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
            with BuildSketch(face):
                with GridLocations(foot_spacing.X, foot_spacing.Y, 2, 2):
                    Circle(foot_dimensions.X / 2)
            extrude(amount=foot_dimensions.Y)

            # create mounts
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-2]
            with BuildSketch(face):
                with GridLocations(0, mount_spacing, 1, 2):
                    Circle(mount_dimensions.X / 2)
            extrude(amount=-mount_dimensions.Y, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(HueBridge())
