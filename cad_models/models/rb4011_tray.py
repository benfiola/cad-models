from bd_warehouse.fastener import ClearanceHole
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
    Vector,
    extrude,
    make_face,
    mirror,
)

from cad_models.common import (
    Model,
    ServerRackInterfaceScrew,
    U,
    centered_point_list,
    main,
    row_major,
)
from cad_models.models.rb4011 import RB4011


class RB4011Tray(Model):
    dimensions: Vector

    def __init__(self, **kwargs):
        interface_holes = Vector(3, 2)
        with BuildPart(mode=Mode.PRIVATE):
            interface_screw = ServerRackInterfaceScrew()
        interface_thickness = 6 * MM
        lip_thickness = 2 * MM
        with BuildPart(mode=Mode.PRIVATE):
            router = RB4011()
        router_tolerance = 0.5 * MM
        tray_thickness = 4.0 * MM

        # derived values
        router_dimensions = Vector(
            router.dimensions.X + router_tolerance,
            router.dimensions.Y + router_tolerance,
            router.dimensions.Z + router_tolerance,
        )
        interior_dimensions = Vector(
            router_dimensions.X,
            (1 * U - tray_thickness),
            router_dimensions.Z + lip_thickness,
        )
        tray_dimensions = Vector(
            interface_thickness + interior_dimensions.X + interface_thickness,
            interior_dimensions.Y + tray_thickness,
            interior_dimensions.Z + tray_thickness,
        )

        with BuildPart() as builder:
            # create blank
            with BuildSketch(Plane.XY):
                with BuildLine():
                    id = interior_dimensions
                    it = interface_thickness
                    td = tray_dimensions
                    tt = tray_thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, td.Z),
                        (it, td.Z),
                        (it, tt),
                        (it + id.X, tt),
                        (it + id.X, td.Z),
                        (td.X, td.Z),
                        (td.X, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=tray_dimensions.Y)

            # create interface holes
            left = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(left, mode=Mode.PRIVATE):
                width = left.length
                height = left.width - 2 * tray_thickness
                x_spacing = width / int(interface_holes.X)
                y_spacing = height / int(interface_holes.Y)
                with GridLocations(
                    x_spacing,
                    y_spacing,
                    int(interface_holes.X),
                    int(interface_holes.Y),
                ) as grid_locs:
                    left_hole_locations = grid_locs.locations
            left_hole_locations = sorted(
                left_hole_locations,
                key=row_major(x_dir=(0, 1, 0), y_dir=(0, 0, -1)),
            )
            mirror_plane = Plane(left).offset(interior_dimensions.X / 2)
            for hole_index, left_hole_location in enumerate(left_hole_locations):
                right_hole_location = Location(left_hole_location)
                right_hole_location *= Pos(Z=interior_dimensions.X)
                with Locations(left_hole_location):
                    hole = ClearanceHole(interface_screw, depth=interface_thickness)
                mirror(hole, mirror_plane, mode=Mode.SUBTRACT)
                location = Location(left_hole_location)
                location *= Pos(Z=-interface_thickness)
                RigidJoint(f"interface-0-{hole_index}", joint_location=location)
                location = Location(right_hole_location)
                location *= Pos(Z=interface_thickness)
                RigidJoint(f"interface-1-{hole_index}", joint_location=location)

            # create tray
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            with BuildSketch(face):
                thickness = tray_thickness + lip_thickness
                location = Location((0, face.width / 2))
                with Locations(location):
                    Rectangle(face.length, thickness, align=(Align.CENTER, Align.MAX))
            extrude(amount=interior_dimensions.Z)

            # create tray mount
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                with Locations(location):
                    Rectangle(
                        router_dimensions.X,
                        router_dimensions.Z,
                        align=(Align.CENTER, Align.MIN),
                    )
            tray_mount = extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)
            face = tray_mount.faces().sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.5)
            location *= Rot(Y=180)
            RigidJoint(f"rb4011", joint_location=location)

            # create face cutout
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                location = Location((0, face.width / 2))
                location *= Pos(Y=-(tray_thickness + lip_thickness))
                width = router_dimensions.X - (lip_thickness * 2)
                height = router_dimensions.Y - (lip_thickness * 2)
                with Locations(location):
                    Rectangle(width, height, align=(Align.CENTER, Align.MAX))
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)

        self.dimensions = tray_dimensions


if __name__ == "__main__":
    main(RB4011Tray())
