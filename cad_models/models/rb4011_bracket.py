from bd_warehouse.fastener import ClearanceHole
from build123d import (
    IN,
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

from cad_models.common import (
    Model,
    ServerRackInterfaceNut,
    U,
    centered_point_list,
    col_major,
    main,
    row_major,
)
from cad_models.models.rb4011_tray import RB4011Tray


class RB4011Bracket(Model):
    def __init__(self, flip_joints: bool = False, **kwargs):
        # parameters
        bracket_dimensions = Vector(0, 1 * U, 0)
        bracket_thickness = 4 * MM
        corner_radius = 3 * MM
        ear_dimensions = Vector(16.25 * MM, 0, 0)
        ear_extra_space = 1.5 * MM
        ear_hole_dimensions = Vector(12 * MM, 6 * MM)
        ear_hole_offset = 3.125 * MM
        ear_hole_spacing = 1 * U - (0.5 * IN)
        interface_thickness = 6 * MM
        with BuildPart(mode=Mode.PRIVATE):
            interface_nut = ServerRackInterfaceNut()
        interface_hole_count = Vector(3, 2)
        with BuildPart(mode=Mode.PRIVATE):
            tray = RB4011Tray()

        # derived values
        interior_width = ((19 * IN) - tray.dimensions.X) / 2
        interior_dimensions = Vector(
            interior_width - ear_extra_space - interface_thickness,
            bracket_dimensions.Y,
            tray.dimensions.Z - bracket_thickness,
        )
        bracket_dimensions.X = (
            ear_dimensions.X
            + ear_extra_space
            + interior_dimensions.X
            + interface_thickness
        )
        bracket_dimensions.Z = interior_dimensions.Z + bracket_thickness
        ear_dimensions.Y = bracket_dimensions.Y
        ear_dimensions.Z = bracket_thickness

        with BuildPart() as builder:
            # create bracket profile (via top-down view)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    bd = bracket_dimensions
                    bt = bracket_thickness
                    ed = ear_dimensions
                    ees = ear_extra_space
                    id = interior_dimensions
                    it = interface_thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, bt),
                        (ed.X + ees + id.X, bt),
                        (ed.X + ees + id.X, bd.Z),
                        (ed.X + ees + id.X + it, bd.Z),
                        (ed.X + ees + id.X + it, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=bracket_dimensions.Y)

            # gather edges to fillet
            fillet_edges = builder.part.edges().filter_by(Axis.Y).sort_by(Axis.X)[:2]

            # create mount holes
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face) as sketch:
                location = Location((face.length / 2, 0))
                location *= Pos(X=-ear_hole_offset)
                location *= Pos(X=-ear_hole_dimensions.X / 2)
                with Locations(location) as loc:
                    with GridLocations(0, ear_hole_spacing, 1, 2) as grid_locs:
                        SlotOverall(ear_hole_dimensions.X, ear_hole_dimensions.Y)
                        mount_hole_locations = grid_locs.locations
            extrude(amount=-bracket_thickness, mode=Mode.SUBTRACT)
            mount_hole_locations = sorted(mount_hole_locations, key=col_major())
            for mount_hole_index, mount_hole_location in enumerate(
                mount_hole_locations
            ):
                location = Location(mount_hole_location)
                location *= Pos(Z=-bracket_thickness)
                location *= Rot(Z=180)
                RigidJoint(f"server-rack-{mount_hole_index}", joint_location=location)

            # create interface holes
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face, mode=Mode.PRIVATE):
                width = face.length
                height = face.width - 2 * bracket_thickness
                x_spacing = width / int(interface_hole_count.X)
                y_spacing = height / int(interface_hole_count.Y)
                with GridLocations(
                    x_spacing,
                    y_spacing,
                    int(interface_hole_count.X),
                    int(interface_hole_count.Y),
                ) as grid_locs:
                    hole_locations = grid_locs.locations
            hole_locations = sorted(
                hole_locations, key=row_major(x_dir=(0, 1, 0), y_dir=(0, 0, -1))
            )
            for hole_index, hole_location in enumerate(hole_locations):
                with Locations(hole_location):
                    ClearanceHole(
                        interface_nut, depth=interface_thickness, captive_nut=True
                    )
                location = Location(hole_location)
                location *= Pos(Z=-interface_thickness)
                location *= Rot(X=180, Z=180)
                if flip_joints:
                    location *= Rot(X=180)
                RigidJoint(f"interface-{hole_index}", joint_location=location)

            # create ribs
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[-2]
            location = Location(edge.position_at(1.0))
            location.orientation = face.center_location.orientation
            with BuildSketch(location):
                Triangle(
                    c=interior_dimensions.Z,
                    a=interior_dimensions.X,
                    B=90,
                    align=(Align.MIN, Align.MIN),
                )
            rib = extrude(amount=-bracket_thickness)
            mirror_plane = face.offset(-interior_dimensions.Y / 2)
            mirror(rib, Plane(mirror_plane))

            # fillet edges
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RB4011Bracket())
