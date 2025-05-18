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
from cad_models.models.coda56 import Coda56


class Coda56MountTopBracket(Model):
    def __init__(self, **kwargs):
        bracket_height = 1 * U
        bracket_thickness = 5.0 * MM
        corner_radius = 3.0 * MM
        magnet_dimensions = Vector(6.0 * MM + 0.5 * MM, 0, 3.0 * MM)
        magnet_offset = 10 * MM
        router = Coda56()
        router_inset = 50 * MM
        support_hook_length = 50 * MM

        router_dimensions = Vector(
            router.dimensions.X + 0.5 * MM,
            router.dimensions.Y,
            router.dimensions.Z + 0.5 * MM,
        )
        support_dimensions = Vector(
            router_dimensions.X + bracket_thickness,
            bracket_height,
            bracket_thickness + router_dimensions.Z + bracket_thickness,
        )
        interior_dimensions = Vector(
            0, bracket_height, router_inset + support_dimensions.Z
        )
        with BuildPart() as builder:
            bracket = ServerRackMountBracket(
                external=True, interior_dimensions=interior_dimensions
            )
            builder.joints.update(bracket.joints)

            # create supports
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[-1]
            location = edge.location_at(1.0)
            location.orientation = face.center_location.orientation
            with BuildSketch(location):
                with BuildLine():
                    bt = bracket_thickness
                    sd = support_dimensions
                    shl = support_hook_length
                    Polyline(
                        (0, 0),
                        (sd.X, 0),
                        (sd.X, -shl),
                        (sd.X - bt, -shl),
                        (sd.X - bt, -bt),
                        (0, -bt),
                        (0, 0),
                    )
                make_face()
            support_arm = extrude(amount=-support_dimensions.Y)
            mirror_plane = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
            mirror_plane = mirror_plane.offset(-support_dimensions.Z / 2)
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
                location = Location((-face.length / 2, 0))
                location *= Pos(X=magnet_offset)
                with Locations(location):
                    Circle(magnet_dimensions.X / 2)
            extrude(amount=-magnet_dimensions.Z, mode=Mode.SUBTRACT)

            # apply fillet
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Coda56MountTopBracket())
