from build123d import (
    MM,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Circle,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    Vector,
    extrude,
    fillet,
    make_face,
    mirror,
)

from cad_models.common import Model, ServerRackMountBracket, U, main


class Coda56MountBracketTop(Model):
    def __init__(self, **kwargs):
        bracket_thickness = 5.0 * MM
        corner_radius = 3.0 * MM
        dimensions = Vector(32.5 * MM, 1 * U, 242.840 * MM)
        magnet_dimensions = Vector(6.5 * MM, 3 * MM)
        magnet_offset = 10 * MM
        router_dimensions = Vector(52.0 * MM, 204.1 * MM, 178.84 * MM)
        support_hook_length = 50 * MM

        with BuildPart() as builder:
            # create bracket
            bracket = ServerRackMountBracket(dimensions=dimensions, external=True)
            builder.joints.update(bracket.joints)

            # create supports
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[-1]
            location = edge.location_at(1.0)
            location.orientation = face.center_location.orientation
            with BuildSketch(location):
                with BuildLine():
                    bt = bracket_thickness
                    rd = router_dimensions
                    shl = support_hook_length

                    Polyline(
                        (0, 0),
                        (rd.X + bt, 0),
                        (rd.X + bt, -shl),
                        (rd.X, -shl),
                        (rd.X, -bt),
                        (0, -bt),
                        (0, 0),
                    )
                make_face()
            support_arm = extrude(amount=-dimensions.Y)
            mirror_distance = (
                bracket_thickness + router_dimensions.Z + bracket_thickness
            )
            mirror_plane = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
            mirror_plane = mirror_plane.offset(-(mirror_distance) / 2)
            mirror(support_arm, Plane(mirror_plane))

            # find edges to fillet
            bracket_edges = (
                builder.part.edges()
                .filter_by(Axis.Z)
                .group_by(Axis.X)[-1]
                .sort_by(Axis.Y)
            )
            fillet_edges = [bracket_edges[0], bracket_edges[-1]]

            # create magnet hole
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face):
                location = Location((face.length / 2, 0))
                location *= Pos(X=-magnet_offset)
                with Locations(location):
                    Circle(magnet_dimensions.X / 2)
            extrude(amount=-magnet_dimensions.Y, mode=Mode.SUBTRACT)

            # apply fillet
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Coda56MountBracketTop())
