from bd_warehouse.fastener import ClearanceHole, Screw
from build123d import (
    IN,
    MM,
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
    Vector,
    extrude,
    fillet,
    make_face,
)

from cad_models.common import (
    Model,
    ServerRackInterfaceNut,
    ServerRackInterfaceScrew,
    centered_point_list,
    col_major,
    main,
    row_major,
)


class GenericMountBracket(Model):
    available_width: float
    bracket_dimensions: Vector
    bracket_thickness: float
    interface_hole_count: Vector
    interface_hole_spacing: Vector
    interface_screw: Screw
    interface_thickness: float

    def __init__(self, flip: bool = False, **kwargs):
        # parameters
        bracket_dimensions = Vector(0, 44.35 * MM, 125 * MM)
        bracket_inset = 5 * MM
        bracket_thickness = 4 * MM
        corner_radius = 3 * MM
        ear_dimensions = Vector(15 * MM, 0, 0)
        ear_hole_dimensions = Vector(12 * MM, 6 * MM)
        ear_hole_spacing = 31.75 * MM
        interface_thickness = 6 * MM
        interface_nut = ServerRackInterfaceNut()
        interface_hole_count = Vector(2, 2)
        interface_hole_spacing = Vector(60 * MM, 20 * MM)

        # derived values
        bracket_dimensions.X = bracket_thickness
        ear_dimensions.Y = bracket_dimensions.Y
        ear_dimensions.Z = bracket_thickness

        with BuildPart() as builder:
            # create bracket profile (via top-down view)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    bd = bracket_dimensions
                    bi = bracket_inset
                    bt = bracket_thickness
                    ed = ear_dimensions
                    it = interface_thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, bt),
                        (ed.X + bi, bt),
                        (ed.X + bi, bd.Z),
                        (ed.X + bi + it, bd.Z),
                        (ed.X + bi + it, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=bracket_dimensions.Y)

            fillet_edges = builder.part.edges().filter_by(Axis.Y).sort_by(Axis.Y)[:2]

            # create interface holes
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face, mode=Mode.PRIVATE) as sketch:
                count = interface_hole_count
                spacing = interface_hole_spacing
                with GridLocations(
                    spacing.X, spacing.Y, int(count.X), int(count.Y)
                ) as grid_locations:
                    interface_hole_locations = grid_locations.locations
            y_dir = (0, 0, -1)
            if flip:
                y_dir = (0, 0, 1)
            interface_hole_locations = sorted(
                interface_hole_locations,
                key=row_major(x_dir=(0, 1, 0), y_dir=y_dir),
            )
            for hole, interface_hole_location in enumerate(interface_hole_locations):
                location = interface_hole_location
                with Locations(location):
                    ClearanceHole(interface_nut, captive_nut=True)
                location = Location(interface_hole_location)
                location *= Pos(Z=-interface_thickness)
                if flip:
                    location *= Rot(X=180)
                RigidJoint(f"interface-{hole}", joint_location=location)

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
            ear_hole_locations = sorted(
                ear_hole_locations, key=col_major(y_dir=(0, 0, -1))
            )
            for index, ear_hole_location in enumerate(ear_hole_locations):
                location = Location(ear_hole_location)
                location *= Pos(Z=-bracket_thickness)
                location *= Rot(Z=180)
                RigidJoint(f"server-rack-{index}", joint_location=location)

            # fillet edges
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)

        self.available_width = (
            (19 * IN) - (bracket_inset * 2) - (interface_thickness * 2)
        )
        self.bracket_dimensions = bracket_dimensions
        self.bracket_thickness = bracket_thickness
        self.interface_hole_count = interface_hole_count
        self.interface_hole_spacing = interface_hole_spacing
        self.interface_screw = ServerRackInterfaceScrew()
        self.interface_thickness = interface_thickness


if __name__ == "__main__":
    main(GenericMountBracket())
