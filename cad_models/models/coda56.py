from bd_warehouse.fastener import ClearanceHole, CounterSunkScrew, Screw
from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Location,
    Locations,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class RouterScrew(CounterSunkScrew):
    def __init__(self, **kwargs):
        super().__init__(
            size="M2.5-0.45", length=6 * MM, fastener_type="iso7046", **kwargs
        )


class Coda56(Model):
    c_dimensions: Vector
    screw: Screw
    standoff_dimensions: Vector
    standoff_hole_offset: float
    standoff_spacing: float

    def __init__(self, **kwargs):
        # added .5 MM tolerance
        dimensions = Vector(52.0 * MM, 204.6 * MM, 178.84 * MM)
        screw = RouterScrew()
        # added .5 MM tolerance
        standoff_dimensions = Vector(9.25 * MM, 15.0 * MM, 8.5 * MM)
        standoff_spacing = 130.8 * MM
        standoff_hole_offset = 1.75 * MM

        with BuildPart() as builder:
            # create router
            with BuildSketch(Plane.XZ):
                Rectangle(dimensions.X, dimensions.Y)
            extrude(amount=dimensions.Z)

            # create standoffs
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            with BuildSketch(face) as sketch:
                spacing = standoff_spacing
                with GridLocations(0, spacing, 1, 2) as locations:
                    Rectangle(standoff_dimensions.X, standoff_dimensions.Y)
            extrude(amount=standoff_dimensions.Z)

            # create screw holes and joints
            faces = (
                builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[:2].sort_by(Axis.Y)
            )
            offsets = [Pos(Y=-standoff_hole_offset), Pos(Y=standoff_hole_offset)]
            for index, (face, offset) in enumerate(zip(faces, offsets)):
                location = face.location_at(0.5, 0.5)
                location *= offset
                with Locations(location):
                    ClearanceHole(screw, depth=screw.length, counter_sunk=False)
                location = Location(location)
                location *= Rot(Y=180)
                RigidJoint(f"mount-{index}", joint_location=location)

        super().__init__(builder.part, **kwargs)

        self.c_dimensions = dimensions
        self.screw = screw
        self.standoff_dimensions = standoff_dimensions
        self.standoff_hole_offset = standoff_hole_offset
        self.standoff_spacing = standoff_spacing


if __name__ == "__main__":
    main(Coda56())
