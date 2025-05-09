from build123d import (
    MM,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    RigidJoint,
    SlotOverall,
    Vector,
    extrude,
    fillet,
    make_face,
)

from cad_models.common import Model, centered_point_list, col_major, initialize
from cad_models.models.coda56 import Coda56


class Coda56MountTopBracket(Model):
    def __init__(self, **kwargs):
        # parameters
        bracket_thickness = 5.0 * MM
        corner_radius = 3.0 * MM
        ear_dimensions = Vector(28.0 * MM, 44.35 * MM, 0)
        hole_dimensions = Vector(12.0 * MM, 6.0 * MM)
        hole_offset = 3 * MM
        hole_spacing = 31.75 * MM
        hook_length = 50 * MM
        router = Coda56()
        router_inset = 50 * MM

        with BuildPart() as builder:
            # create bracket (via top-down profile)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    bt = bracket_thickness
                    ed = ear_dimensions
                    hl = hook_length
                    rd = router.c_dimensions
                    ri = router_inset

                    points = centered_point_list(
                        (0, 0),
                        (ed.X + bt, 0),
                        (ed.X + bt, ri),
                        (ed.X + bt + rd.X + bt, ri),
                        (ed.X + bt + rd.X + bt, ri + bt + hl),
                        (ed.X + bt + rd.X, ri + bt + hl),
                        (ed.X + bt + rd.X, ri + bt),
                        (ed.X + bt, ri + bt),
                        (ed.X + bt, ri + bt + rd.Z),
                        (ed.X + bt + rd.X, ri + bt + rd.Z),
                        (ed.X + bt + rd.X, ri + bt + rd.Z - hl),
                        (ed.X + bt + rd.X + bt, ri + bt + rd.Z - hl),
                        (ed.X + bt + rd.X + bt, ri + bt + rd.Z + bt),
                        (ed.X, ri + bt + rd.Z + bt),
                        (ed.X, bt),
                        (0, bt),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=ear_dimensions.Y)

            # find edges to fillet
            ear_edges = builder.part.edges().filter_by(Axis.Y).sort_by(Axis.X)[:2]
            bracket_edges = (
                builder.part.edges()
                .filter_by(Axis.Z)
                .sort_by(Axis.X)[-4:]
                .sort_by(Axis.Y)
            )
            fillet_edges = [*ear_edges, bracket_edges[0], bracket_edges[-1]]

            # create mount holes and joints
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                location = Location((0, 0))
                location *= Pos(X=-face.length / 2)
                location *= Pos(X=hole_offset)
                location *= Pos(X=hole_dimensions.X / 2)
                with Locations(location):
                    with GridLocations(0.0, hole_spacing, 1, 2) as grid_locations:
                        SlotOverall(hole_dimensions.X, hole_dimensions.Y)
                        hole_locations = grid_locations.locations
            extrude(amount=-bracket_thickness, mode=Mode.SUBTRACT)
            locations = sorted(hole_locations, key=col_major(y_dir=(0, 0, -1)))
            for index, location in enumerate(locations):
                joint_location = Location(location)
                joint_location *= Pos(Z=-bracket_thickness)
                RigidJoint(f"server-rack-{index}", joint_location=joint_location)

            # apply fillet
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    initialize(Coda56MountTopBracket())
