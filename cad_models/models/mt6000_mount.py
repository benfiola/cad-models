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
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, ServerRackMountBracket, U, main, row_major
from cad_models.models.mt6000 import MT6000


class MT6000MountTopBracket(Model):
    def __init__(self, **kwargs):
        # parameters
        bracket_height = 1 * U
        magnet_dimensions = Vector(6.0 * MM + 0.5, 0, 3 * MM)
        magnet_offset = 10 * MM
        modem = MT6000()
        modem_inset = 25 * MM

        # derived data
        magnet_dimensions.Y = magnet_dimensions.X
        interior_dimensions = (0, bracket_height, modem_inset + modem.dimensions.X)

        with BuildPart() as builder:
            bracket = ServerRackMountBracket(
                external=True, interior_dimensions=interior_dimensions
            )
            builder.joints.update(bracket.joints)

            # create modem mounts
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            location = face.location_at(0.0, 0.5)
            location *= Pos(Y=modem.dimensions.X / 2)
            with BuildSketch(location):
                spacing = modem.hole_spacing.X
                with GridLocations(0, spacing, 1, 2) as grid_locations:
                    Circle(modem.peg_shaft_diameter / 2)
                    post_locations = grid_locations.locations
            solids = extrude(amount=modem.peg_depth / 2)
            faces = solids.faces().filter_by(Axis.X).sort_by(Axis.X)[-2:]
            for face in faces:
                with BuildSketch(face):
                    Circle(modem.peg_top_diameter / 2)
                extrude(amount=modem.peg_depth / 2)

            # create joints
            post_locations = sorted(post_locations, key=row_major(x_dir=(0, 1, 0)))
            for hole, post_location in enumerate(post_locations):
                location = Location(post_location.position)
                location *= Pos(X=modem.peg_depth)
                location *= Rot(Z=90)
                RigidJoint(f"mt6000-{hole}", joint_location=location)

            # create magnet hole
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face) as sketch:
                location = Location((-face.length / 2, 0))
                location *= Pos(X=magnet_offset)
                with Locations(location):
                    Circle(magnet_dimensions.X / 2)
            extrude(amount=-magnet_dimensions.Z, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(MT6000MountTopBracket())
