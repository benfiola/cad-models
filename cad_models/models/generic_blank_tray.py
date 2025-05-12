from bd_warehouse.fastener import ClearanceHole
from build123d import (
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
    Vector,
    extrude,
    make_face,
)

from cad_models.common import Model, centered_point_list, main, row_major
from cad_models.models.generic_mount_bracket import GenericMountBracket


class GenericBlankTray(Model):
    def __init__(self, **kwargs):
        # parameters
        bracket = GenericMountBracket()

        # derived data
        interface_hole_count = bracket.interface_hole_count
        interface_hole_spacing = bracket.interface_hole_spacing
        interface_screw = bracket.interface_screw
        interface_thickness = bracket.interface_thickness
        tray_dimensions = Vector(
            bracket.available_width / 3,
            bracket.bracket_dimensions.Y,
            bracket.bracket_dimensions.Z,
        )
        tray_thickness = bracket.bracket_thickness

        with BuildPart() as builder:
            # create bracket profile (via top-down view)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    it = interface_thickness
                    td = tray_dimensions
                    tt = tray_thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, td.Z),
                        (it, td.Z),
                        (it, tt),
                        (td.X - it, tt),
                        (td.X - it, td.Z),
                        (td.X, td.Z),
                        (td.X, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=tray_dimensions.Y)

            # create interface holes
            faces = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1:3]
            for side, face in enumerate(faces):
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
                for hole, interface_hole_location in enumerate(
                    interface_hole_locations
                ):
                    location = interface_hole_location
                    with Locations(location):
                        ClearanceHole(interface_screw, depth=interface_screw.length)
                    location = Location(interface_hole_location)
                    location *= Pos(Z=-interface_thickness)
                    if side == 0:
                        location *= Rot(X=180)
                        location *= Rot(Z=180)
                    RigidJoint(f"interface-{side}-{hole}", joint_location=location)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericBlankTray())
