from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Location,
    Locations,
    Mode,
    Pos,
    Rectangle,
    RigidJoint,
    SlotOverall,
    Solid,
    Vector,
    extrude,
)

from cad_models.common import initialize


class MT6000(Solid):
    m_dimensions: Vector
    hole_depth: float
    hole_diameter: float
    hole_slot_dimensions: Vector
    hole_spacing: Vector

    def __init__(self, **kwargs):
        # dimensions of the underside of the router where the mount holes are
        dimensions = Vector(217.46 * MM, 33.84 * MM, 131.92 * MM)

        hole_depth = 5.4 * MM
        hole_diameter = 11.28 * MM
        # TODO: fix hole slot math to make sense
        hole_slot_dimensions = Vector(4 * MM, 6.5 * MM)
        hole_spacing = Vector(179.20 * MM, 0)

        with BuildPart() as builder:
            # create router box
            # TODO: make this actually look like the router
            with BuildSketch():
                Rectangle(dimensions.X, dimensions.Y)
            extrude(amount=dimensions.Z)

            # create mount holes
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
            with BuildSketch(face) as sketch:
                with GridLocations(hole_spacing.X, 0, 2, 1) as grid_locations:
                    Circle(hole_diameter / 2)
                    hole_locations = grid_locations.locations
                offsets = [
                    Pos(Y=hole_slot_dimensions.Y),
                    Pos(Y=-hole_slot_dimensions.Y),
                ]
                for location in offsets:
                    with Locations(location):
                        with GridLocations(hole_spacing.X, 0, 2, 1):
                            SlotOverall(
                                hole_slot_dimensions.Y + (hole_slot_dimensions.X / 2),
                                hole_slot_dimensions.X,
                                rotation=270,
                            )
            extrude(amount=-hole_depth, mode=Mode.SUBTRACT)

            # create joints
            for hole, hole_location in enumerate(hole_locations):
                location = Location(hole_location.position)
                location *= Pos(Y=-hole_depth)
                RigidJoint(f"mount-{hole}", joint_location=location)

        kwargs["obj"] = builder.part.wrapped
        kwargs["joints"] = builder.joints
        super().__init__(**kwargs)

        self.hole_depth = hole_depth
        self.hole_diameter = hole_diameter
        self.hole_slot_dimensions = hole_slot_dimensions
        self.hole_spacing = hole_spacing
        self.m_dimensions = dimensions


if __name__ == "__main__":
    initialize(MT6000())
