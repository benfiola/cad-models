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
    SlotOverall,
    Vector,
    extrude,
)

from cad_models.common import Model, ServerRackMountBlank, U, main


class GenericHueBridgeTray(Model):
    def __init__(self, **kwargs):
        # parameters
        bridge_dimensions = Vector(91.4 * MM, 26 * MM, 91.4 * MM)
        bridge_foot_spacing = Vector(65.24 * MM, 66.82 * MM)
        bridge_foot_dimensions = Vector(8.5 * MM, 17.0 * MM, 0.9 * MM)
        bridge_peg_shaft_dimensions = Vector(4.5 * MM, 2.2 * MM)
        bridge_peg_head_dimensions = Vector(8.5 * MM, 1.8 * MM)
        bridge_peg_spacing = 49.5 * MM
        bridge_slide_distance = 8 * MM
        dimensions = Vector(145.03 * MM, 1 * U, 154 * MM)
        hex_grid_count = Vector(13, 13)
        hex_grid_radius = 3 * MM
        hex_grid_spacing = 0.5 * MM
        interface_holes = Vector(2, 2)
        lip_thickness = 2.0 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            # create blank
            blank = ServerRackMountBlank(
                dimensions=dimensions, interface_holes=interface_holes
            )
            builder.joints.update(blank.joints)

            # create tray
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            depth = bridge_dimensions.Z + bridge_slide_distance + lip_thickness
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
                        bridge_dimensions.X,
                        bridge_dimensions.Z + bridge_slide_distance,
                        align=(Align.CENTER, Align.MIN),
                    )
            tray_mount = extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)
            face = tray_mount.faces().sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.0)
            location *= Pos(Y=bridge_dimensions.Z / 2)
            location *= Pos(Y=bridge_slide_distance)
            location *= Rot(Y=180)
            RigidJoint(f"hue-bridge", joint_location=location)

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

            # create feet standoffs
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            location = face.location_at(0.5, 0.0)
            location *= Pos(Y=bridge_dimensions.Z / 2)
            location *= Pos(Y=bridge_slide_distance / 2)
            with BuildSketch(location):
                with GridLocations(bridge_foot_spacing.X, bridge_foot_spacing.Y, 2, 2):
                    width = bridge_foot_dimensions.X + lip_thickness
                    length = bridge_foot_dimensions.Y * MM + lip_thickness
                    SlotOverall(length, width, rotation=90)
            extrude(amount=-tray_thickness)
            with BuildSketch(location):
                with GridLocations(bridge_foot_spacing.X, bridge_foot_spacing.Y, 2, 2):
                    SlotOverall(
                        bridge_foot_dimensions.Y, bridge_foot_dimensions.X, rotation=90
                    )
            extrude(amount=-bridge_foot_dimensions.Z, mode=Mode.SUBTRACT)

            # create mount pegs
            with BuildSketch(location, mode=Mode.PRIVATE):
                with GridLocations(0, bridge_peg_spacing, 1, 2) as grid_locs:
                    front, back = grid_locs.local_locations
            with BuildSketch(location) as build_sketch:
                with Locations(back):
                    Circle(bridge_peg_head_dimensions.X / 2)
            sketch = build_sketch.sketch
            extrude(amount=-tray_thickness)
            height = bridge_peg_shaft_dimensions.Y + bridge_peg_head_dimensions.Y
            extrude(sketch, amount=height)
            with BuildSketch(location):
                with Locations(front):
                    Circle(bridge_peg_head_dimensions.X / 2)
            extrude(amount=-tray_thickness)
            with BuildSketch(location):
                with Locations(front):
                    Circle(bridge_peg_shaft_dimensions.X / 2)
            solid = extrude(amount=bridge_peg_shaft_dimensions.Y)
            face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                Circle(bridge_peg_head_dimensions.X / 2)
            extrude(amount=bridge_peg_head_dimensions.Y)

            # create face cutout
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                location = Location((0, face.width / 2))
                location *= Pos(Y=-(tray_thickness + lip_thickness))
                width = bridge_dimensions.X - (lip_thickness * 2)
                height = bridge_dimensions.Y - (lip_thickness * 2)
                with Locations(location):
                    Rectangle(width, height, align=(Align.CENTER, Align.MAX))
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericHueBridgeTray())
