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


class MT6000MountBracket(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(32.5 * MM, 1 * U, 246.460 * MM)
        magnet_dimensions = Vector(6.5 * MM, 3 * MM)
        magnet_offset = 10 * MM
        modem_dimensions = Vector(217.46 * MM, 33.84 * MM, 131.92 * MM)
        modem_peg_depth = 5.4 * MM
        modem_peg_head_diameter = 9 * MM
        modem_peg_shaft_diameter = 3 * MM
        modem_hole_spacing = Vector(180 * MM, 0)

        with BuildPart() as builder:
            bracket = ServerRackMountBracket(dimensions=dimensions, external=True)
            builder.joints.update(bracket.joints)

            # create modem mounts
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            location = face.location_at(0.0, 0.5)
            location *= Pos(Y=modem_dimensions.X / 2)
            with BuildSketch(location):
                spacing = modem_hole_spacing.X
                with GridLocations(0, spacing, 1, 2) as grid_locations:
                    Circle(modem_peg_shaft_diameter / 2)
                    post_locations = grid_locations.locations
            solids = extrude(amount=modem_peg_depth / 2)
            faces = solids.faces().filter_by(Axis.X).sort_by(Axis.X)[-2:]
            for face in faces:
                with BuildSketch(face):
                    Circle(modem_peg_head_diameter / 2)
                extrude(amount=modem_peg_depth / 2)

            # create joints
            post_locations = sorted(post_locations, key=row_major(x_dir=(0, 1, 0)))
            for hole, post_location in enumerate(post_locations):
                location = Location(post_location.position)
                location *= Pos(X=modem_peg_depth)
                location *= Rot(Z=90)
                RigidJoint(f"mt6000-{hole}", joint_location=location)

            # create magnet hole
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face) as sketch:
                location = Location((face.length / 2, 0))
                location *= Pos(X=-magnet_offset)
                with Locations(location):
                    Circle(magnet_dimensions.X / 2)
            extrude(amount=-magnet_dimensions.Y, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(MT6000MountBracket())
