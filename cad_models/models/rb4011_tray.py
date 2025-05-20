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
from cad_models.models.rb4011 import RB4011


class RB4011Tray(Model):
    dimensions: Vector

    def __init__(self, **kwargs):
        hex_grid_count = Vector(34, 15)
        hex_grid_radius = 3 * MM
        hex_grid_spacing = 0.5 * MM
        interface_holes = Vector(3, 2)
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
        router_feet_diameter = router.feet_diameter + router_tolerance
        interior_dimensions = Vector(
            router_dimensions.X,
            1 * U,
            router_dimensions.Z + lip_thickness,
        )

        with BuildPart() as builder:
            blank = ServerRackMountBlank(
                interface_holes=interface_holes, interior_dimensions=interior_dimensions
            )
            builder.joints.update(blank.joints)

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
            location *= Pos(Y=router.feet_offset)
            with BuildSketch(location):
                with GridLocations(router.feet_spacing.X, router.feet_spacing.Y, 2, 2):
                    Circle((router_feet_diameter + lip_thickness) / 2)
            extrude(amount=-tray_thickness)
            with BuildSketch(location):
                with GridLocations(router.feet_spacing.X, router.feet_spacing.Y, 2, 2):
                    Circle(router_feet_diameter / 2)
            extrude(amount=-router.feet_height, mode=Mode.SUBTRACT)

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

        self.dimensions = blank.dimensions


if __name__ == "__main__":
    main(RB4011Tray())
