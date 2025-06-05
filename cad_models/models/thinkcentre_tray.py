from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
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
    SlotOverall,
    Vector,
    extrude,
)

from cad_models.common import Model, ServerRackMountBlank, U, main


class ThinkcentreTray(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(191.5 * MM, 1 * U, 189.5 * MM)
        hex_grid_count = Vector(26, 24)
        hex_grid_radius = 3 * MM
        hex_grid_spacing = 0.5 * MM
        interface_holes = Vector(3, 2)
        lip_thickness = 2 * MM
        thinkcentre_dimensions = Vector(179.5 * MM, 34.5 * MM, 183.5 * MM)
        thinkcentre_foot_dimensions = Vector(16.0 * MM, 7.5 * MM, 2.5 * MM)
        thinkcentre_foot_spacing = Vector(162.5 * MM, 133 * MM)
        thinkcentre_foot_offset = 0.5 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            blank = ServerRackMountBlank(
                dimensions=dimensions, interface_holes=interface_holes
            )
            builder.joints.update(blank.joints)

            # create tray
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            depth = thinkcentre_dimensions.Z + lip_thickness
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
                        thinkcentre_dimensions.X,
                        thinkcentre_dimensions.Z,
                        align=(Align.CENTER, Align.MIN),
                    )
            tray_mount = extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)
            face = tray_mount.faces().sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.5)
            location *= Rot(Y=180)
            RigidJoint(f"thinkcentre", joint_location=location)

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
            with BuildSketch(face, mode=Mode.PRIVATE):
                location = Location((0, -thinkcentre_foot_offset))
                with Locations(location):
                    with GridLocations(
                        thinkcentre_foot_spacing.X, thinkcentre_foot_spacing.Y, 2, 2
                    ) as grid_locs:
                        locations = grid_locs.local_locations
            with BuildSketch(face):
                with Locations(*locations):
                    width = thinkcentre_foot_dimensions.X + lip_thickness
                    length = thinkcentre_foot_dimensions.Y + lip_thickness
                    SlotOverall(width, length, rotation=90)
            extrude(amount=-tray_thickness)
            with BuildSketch(face):
                with Locations(*locations):
                    SlotOverall(
                        thinkcentre_foot_dimensions.X,
                        thinkcentre_foot_dimensions.Y,
                        rotation=90,
                    )
            extrude(amount=-thinkcentre_foot_dimensions.Z, mode=Mode.SUBTRACT)

            # create face cutout
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                location = Location((0, face.width / 2))
                location *= Pos(Y=-(tray_thickness + lip_thickness))
                width = thinkcentre_dimensions.X - (lip_thickness * 2)
                height = thinkcentre_dimensions.Y - (lip_thickness * 2)
                with Locations(location):
                    Rectangle(width, height, align=(Align.CENTER, Align.MAX))
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(ThinkcentreTray())
