from build123d import (
    MM,
    BuildPart,
    BuildSketch,
    Location,
    Rectangle,
    RigidJoint,
    Solid,
    Vector,
    extrude,
)

from cad_models.common import initialize


class MT6000(Solid):
    m_dimensions: Vector

    def __init__(self, **kwargs):
        # dimensions of the underside of the router where the mount holes are
        dimensions = Vector(217.46 * MM, 33.84 * MM, 131.92 * MM)

        hole_depth = 5.4 * MM
        hole_diameter = 11.28 * MM
        hole_slot_dimensions = Vector(4 * MM, 6 * MM)
        hole_spacing = 179.20 * MM

        with BuildPart() as builder:
            with BuildSketch():
                Rectangle(5, 5)
            extrude(amount=5)

            location = Location((0, 0, 0))
            RigidJoint(f"mount-0", joint_location=location)
            RigidJoint(f"mount-1", joint_location=location)

        kwargs["obj"] = builder.part.wrapped
        kwargs["joints"] = builder.joints
        super().__init__(**kwargs)

        self.m_dimensions = dimensions


if __name__ == "__main__":
    initialize(MT6000())
