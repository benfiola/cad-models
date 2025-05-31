from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    HexLocations,
    Location,
    Locations,
    Mode,
    Pos,
    Rectangle,
    RegularPolygon,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, ServerRackMountBlank, U, main


class RB4011Tray(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(240.5 * MM, 1 * U, 124.3 * MM)
        hex_grid_count = Vector(34, 15)
        hex_grid_radius = 3 * MM
        hex_grid_spacing = 0.5 * MM
        interface_holes = Vector(3, 2)
        lip_thickness = 2 * MM
        router_dimensions = Vector(228.5 * MM, 26.7 * MM, 118.3 * MM)
        router_foot_dimensions = Vector(15 * MM, 3.5 * MM)
        router_foot_spacing = Vector(162.2 * MM, 65.34 * MM)
        router_foot_offset = 51.16 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            blank = ServerRackMountBlank(
                dimensions=dimensions, interface_holes=interface_holes
            )
            builder.joints.update(blank.joints)

            # create tray
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            depth = router_dimensions.Z + lip_thickness
            with BuildSketch(face):
                thickness = tray_thickness + lip_thickness
                location = Location((0, face.width / 2))
                with Locations(location):
                    Rectangle(face.length, thickness, align=(Align.CENTER, Align.MAX))
            extrude(amount=depth)

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

            # create hex grid
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                with HexLocations(
                    hex_grid_radius + hex_grid_spacing,
                    int(hex_grid_count.X),
                    int(hex_grid_count.Y),
                ):
                    RegularPolygon(hex_grid_radius, 6)
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

            # create feet cutouts
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            location = face.location_at(0.5, 0.0)
            location *= Pos(Y=router_foot_offset)
            with BuildSketch(location):
                with GridLocations(router_foot_spacing.X, router_foot_spacing.Y, 2, 2):
                    Circle((router_foot_dimensions.X + lip_thickness) / 2)
            extrude(amount=-tray_thickness)
            with BuildSketch(location):
                with GridLocations(router_foot_spacing.X, router_foot_spacing.Y, 2, 2):
                    Circle(router_foot_dimensions.X / 2)
            extrude(amount=-router_foot_dimensions.Y, mode=Mode.SUBTRACT)

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


if __name__ == "__main__":
    main(RB4011Tray())
