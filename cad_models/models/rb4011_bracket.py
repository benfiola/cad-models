from bd_warehouse.fastener import ClearanceHole
from build123d import (
    MM,
    Align,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    GridLocations,
    Keep,
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
    RackInterfaceNut,
    centered_point_list,
    col_major,
    main,
    row_major,
)


class RB4011Bracket(Model):
    def __init__(self, **kwargs):
        # parameters
        bracket_thickness = 4 * MM
        corner_radius = 3 * MM
        dimensions = Vector(150 * MM, 0, 100 * MM)
        ear_dimensions = Vector(28.0 * MM, 44.35 * MM, 0)
        ear_hole_dimensions = Vector(12 * MM, 6 * MM)
        ear_hole_spacing = 31.75 * MM
        inner_bracket_thickness = 6 * MM
        interface_nut = RackInterfaceNut()
        interface_hole_count = Vector(4, 2)
        interface_hole_spacing = Vector(20 * MM, 20 * MM)

        # derived values
        dimensions.Y = ear_dimensions.Y
        ear_dimensions.Z = bracket_thickness

        with BuildPart() as builder:
            # create bracket profile (via top-down view)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    bt = bracket_thickness
                    d = dimensions
                    ed = ear_dimensions
                    ibt = inner_bracket_thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, bt),
                        (ed.X + d.X, bt),
                        (ed.X + d.X, bt + d.Z),
                        (ed.X + d.X + ibt, bt + d.Z),
                        (ed.X + d.X + ibt, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=dimensions.Y)

            fillet_edges = builder.part.edges().filter_by(Axis.Y).sort_by(Axis.Y)[:2]

            # create bracket ribs
            split_plane = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
            split_plane = split_plane.offset(-ear_dimensions.X)
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            faces = face.split(split_plane, keep=Keep.BOTH)
            face = faces.faces().sort_by(Axis.X)[-1]
            split_plane = split_plane.offset(-dimensions.X)
            faces = face.split(split_plane, keep=Keep.BOTH)
            face = faces.faces().sort_by(Axis.X)[0]
            mirror_plane = Plane(face).offset(-(dimensions.Y / 2))
            with BuildSketch(face) as sketch:
                location = Location((0, -(bracket_thickness / 2)))
                with Locations(location):
                    Triangle(
                        a=dimensions.X,
                        b=dimensions.Z,
                        C=90,
                        align=(Align.CENTER, Align.MIN),
                        rotation=180,
                    )
            solid = extrude(amount=-bracket_thickness)
            mirror(solid, mirror_plane)

            # create interface holes
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face, mode=Mode.PRIVATE) as sketch:
                count = interface_hole_count
                spacing = interface_hole_spacing
                with GridLocations(
                    spacing.X, spacing.Y, int(count.X), int(count.Y)
                ) as grid_locations:
                    interface_hole_locations = grid_locations.locations
            interface_hole_locations = sorted(
                interface_hole_locations,
                key=row_major(x_dir=(0, 1, 0), y_dir=(0, 0, -1)),
            )
            for index, interface_hole_location in enumerate(interface_hole_locations):
                x = index % interface_hole_count.X
                y = index / interface_hole_count.X
                location = interface_hole_location
                with Locations(location):
                    ClearanceHole(interface_nut, captive_nut=True)
                location = Location(interface_hole_location)
                location *= Rot(X=180)
                RigidJoint(f"interface-{x}-{y}", joint_location=interface_hole_location)

            # create ear holes and joints
            split_plane = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
            split_plane = split_plane.offset(-ear_dimensions.X)
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            faces = face.split(split_plane, keep=Keep.BOTH)
            face = faces.faces().sort_by(Axis.X)[0]
            with BuildSketch(face):
                with GridLocations(0.0, ear_hole_spacing, 1, 2) as grid_locations:
                    SlotOverall(ear_hole_dimensions.X, ear_hole_dimensions.Y)
                    ear_hole_locations = grid_locations.locations
            extrude(amount=-ear_dimensions.Z, mode=Mode.SUBTRACT)
            locations = sorted(ear_hole_locations, key=col_major(y_dir=(0, 0, -1)))
            for index, location in enumerate(locations):
                joint_location = Location(location)
                joint_location *= Pos(Z=-bracket_thickness)
                joint_location *= Rot(Z=180)
                RigidJoint(f"server-rack-{index}", joint_location=joint_location)

            # fillet edges
            fillet(fillet_edges, corner_radius)
        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RB4011Bracket())
