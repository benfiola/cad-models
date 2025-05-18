from bd_warehouse.fastener import ClearanceHole
from build123d import (
    MM,
    Align,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Circle,
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
    mirror,
)

from cad_models.common import Model, centered_point_list, col_major, main
from cad_models.models.coda56 import Coda56


class Coda56MountBottomBracket(Model):
    def __init__(self, **kwargs):
        bracket_thickness = 5.0 * MM
        corner_radius = 3.0 * MM
        ear_dimensions = Vector(26.5 * MM, 44.35 * MM, 0)
        ear_extra_space = 1.5 * MM
        magnet_dimensions = Vector(6.0 * MM + 0.5 * MM, 0, 3 * MM)
        magnet_offset = 10 * MM
        mount_hole_dimensions = Vector(12.0 * MM, 6.0 * MM)
        mount_hole_offset = 3 * MM
        mount_hole_spacing = 31.75 * MM
        router = Coda56()
        router_inset = 50 * MM
        stand_thickness = 10 * MM

        with BuildPart() as builder:
            # create bracket (via top-down profile)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    bt = bracket_thickness
                    ed = ear_dimensions
                    ees = ear_extra_space
                    rd = router.dimensions
                    ri = router_inset

                    points = centered_point_list(
                        (0, 0),
                        (ed.X + ees + bt, 0),
                        (ed.X + ees + bt, ri + bt + rd.Z + bt),
                        (ed.X + ees, ri + bt + rd.Z + bt),
                        (ed.X + ees, bt),
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
                    stand_length = (bracket_thickness * 2) + router.dimensions.Z
                    Rectangle(
                        stand_length, stand_thickness, align=(Align.MAX, Align.MIN)
                    )
            stand = extrude(amount=router.dimensions.X)

            # create stand ribs
            face = stand.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            mirror_plane = Plane(face).offset(-stand_length / 2)
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                location = (router.dimensions.X / 2, stand_thickness / 2)
                with Locations(location):
                    a = router.dimensions.X
                    c = ear_dimensions.Y - stand_thickness
                    Triangle(a=a, B=90, c=c, align=(Align.MAX, Align.MIN))
            rib = extrude(amount=-bracket_thickness)
            mirror(rib, mirror_plane)

            # create stand standoffs
            stand_face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(Plane(stand_face, x_dir=(1, 0, 0))) as sketch:
                spacing = router.standoff_spacing
                with GridLocations(0, spacing, 1, 2):
                    Rectangle(
                        router.standoff_dimensions.X, router.standoff_dimensions.Y
                    )
                offset = router.standoff_hole_offset * 2
                with GridLocations(0, spacing + offset, 1, 2) as grid_locations:
                    hole_locations = grid_locations.locations
            extrude(amount=-router.standoff_dimensions.Z, mode=Mode.SUBTRACT)

            # create stand standoff holes and joints
            for hole, hole_location in enumerate(hole_locations):
                # hole
                location = Location(hole_location)
                location *= Pos(Z=-stand_thickness)
                location *= Rot(Y=180)
                with Locations(location):
                    ClearanceHole(router.screw, depth=router.screw.length)

                # joint
                location = Location(hole_location)
                location *= Pos(Z=-router.standoff_dimensions.Z)
                RigidJoint(f"coda56-{hole}", joint_location=location)

            # create magnet hole
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face) as sketch:
                location = Location((-face.length / 2, 0))
                location *= Pos(X=magnet_offset)
                with Locations(location):
                    Circle(magnet_dimensions.X / 2)
            extrude(amount=-magnet_dimensions.Z, mode=Mode.SUBTRACT)

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
                joint_location = Location(location)
                joint_location *= Pos(Z=-bracket_thickness)
                joint_location *= Rot(Z=180)
                RigidJoint(f"server-rack-{index}", joint_location=joint_location)

            # apply fillet
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Coda56MountBottomBracket())
