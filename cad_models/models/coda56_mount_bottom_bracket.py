from bd_warehouse.fastener import ClearanceHole, CounterSunkScrew
from build123d import (
    MM,
    Align,
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
    Rectangle,
    RigidJoint,
    Rot,
    SlotOverall,
    Triangle,
    Vector,
    extrude,
    fillet,
    make_face,
)

from cad_models.common import Model, centered_point_list, col_major, initialize


class RouterScrew(CounterSunkScrew):
    def __init__(self, **kwargs):
        super().__init__(
            size="M2.5-0.45", length=6 * MM, fastener_type="iso7046", **kwargs
        )


class Coda56MountBottomBracket(Model):
    def __init__(self, **kwargs):
        # derived values
        bracket_thickness = 5.0 * MM
        corner_radius = 3.0 * MM
        ear_dimensions = Vector(28.0 * MM, 41.35 * MM, 0)
        mount_hole_dimensions = Vector(12.0 * MM, 6.0 * MM)
        mount_hole_offset = 3 * MM
        mount_hole_spacing = 31.75 * MM
        router_dimensions = Vector(51.5 * MM, 171 * MM, 171 * MM)
        router_inset = 50 * MM
        stand_screw = RouterScrew()
        stand_thickness = 10 * MM
        stand_standoff_dimensions = Vector(9 * MM, 18 * MM, 9 * MM)

        with BuildPart() as builder:
            # create bracket (via top-down profile)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    bt = bracket_thickness
                    ed = ear_dimensions
                    rd = router_dimensions
                    ri = router_inset

                    points = centered_point_list(
                        (0, 0),
                        (ed.X + bt, 0),
                        (ed.X + bt, ri + bt + rd.Z + bt),
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
            fillet_edges = [*ear_edges]

            # create stand base
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            with BuildSketch(face):
                location = Location((0, 0))
                location *= Pos(X=face.length / 2, Y=-face.width / 2)
                with Locations(location):
                    width = (bracket_thickness * 2) + router_dimensions.Z
                    Rectangle(width, stand_thickness, align=(Align.MAX, Align.MIN))
            stand = extrude(amount=router_dimensions.X)

            # create stand ribs
            face = stand.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            front_plane = Plane(face, x_dir=(1, 0, 0))
            back_plane = front_plane.offset(-(router_dimensions.Y + bracket_thickness))
            for plane in [front_plane, back_plane]:
                with BuildSketch(plane):
                    location = (router_dimensions.X / 2, stand_thickness / 2)
                    with Locations(location):
                        a = router_dimensions.X
                        c = ear_dimensions.Y - stand_thickness
                        Triangle(a=a, B=90, c=c, align=(Align.MAX, Align.MIN))
                extrude(amount=-bracket_thickness)

            # create stand standoffs
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as sketch:
                spacing = router_dimensions.Z
                spacing -= stand_standoff_dimensions.Y
                with GridLocations(0, spacing, 1, 2) as grid_locations:
                    Rectangle(stand_standoff_dimensions.X, stand_standoff_dimensions.Y)
                    standoff_locations = grid_locations.locations
            extrude(amount=-stand_standoff_dimensions.Z, mode=Mode.SUBTRACT)

            # create stand standoff holes
            for standoff_location in standoff_locations:
                location = Location(standoff_location)
                location *= Pos(Z=-stand_thickness)
                location *= Rot(Y=180)
                with Locations(location):
                    ClearanceHole(stand_screw, depth=stand_screw.length)

            # create mount holes and joints
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                location = Location((0, 0))
                location *= Pos(X=-face.length / 2)
                location *= Pos(X=mount_hole_offset)
                location *= Pos(X=mount_hole_dimensions.X / 2)
                with Locations(location):
                    with GridLocations(0.0, mount_hole_spacing, 1, 2) as grid_locations:
                        SlotOverall(mount_hole_dimensions.X, mount_hole_dimensions.Y)
                        hole_locations = grid_locations.locations
            extrude(amount=-bracket_thickness, mode=Mode.SUBTRACT)
            locations = sorted(hole_locations, key=col_major(y_dir=(0, 0, -1)))
            for index, location in enumerate(locations):
                joint_location = Location(location.position) * Pos(Y=bracket_thickness)
                RigidJoint(f"mount-{index}", joint_location=joint_location)

            # apply fillet
            fillet(fillet_edges, corner_radius)

        kwargs["obj"] = builder.part.wrapped
        kwargs["joints"] = builder.part.joints
        super().__init__(builder.part.wrapped, **kwargs)


if __name__ == "__main__":
    initialize(Coda56MountBottomBracket())
