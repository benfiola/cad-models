from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Plane,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class RB4011(Model):
    r_dimensions: Vector

    def __init__(self, **kwargs):
        # parameters
        # added .5 MM tolerance to X and Z to ensure fitment
        dimensions = Vector(228.5 * MM, 30 * MM, 120.5 * MM)

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

        super().__init__(builder.part, **kwargs)

        self.r_dimensions = dimensions


if __name__ == "__main__":
    main(RB4011())
