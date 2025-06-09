from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    Vector,
    extrude,
    mirror,
)

from cad_models.common import Model, main


class Test(Model):
    def __init__(self, **kwargs):
        # parameters
        face_thickness = 4 * MM
        cable_diameter = 4.3 * MM
        cable_slot_width = 4.0 * MM
        cable_tray_dimensions = Vector(32.5 * MM, 10 * MM, 145.5 * MM)
        power_supply_tray_dimensions = Vector(65.5 * MM, 4 * MM, 145.5 * MM)
        tray_thickness = 2 * MM

        with BuildPart() as builder:
            # create tray bases
            base_location = Plane.XY.location
            with BuildSketch(base_location):
                # power supply
                width = tray_thickness + power_supply_tray_dimensions.X + tray_thickness
                height = (
                    tray_thickness + power_supply_tray_dimensions.Z + tray_thickness
                )
                Rectangle(width, height, align=Align.MIN)

                location = Location((0, 0))
                location *= Pos(X=tray_thickness)
                location *= Pos(X=power_supply_tray_dimensions.X)
                location *= Pos(X=tray_thickness)
                with Locations(location):
                    width = cable_tray_dimensions.X + tray_thickness
                    height = tray_thickness + cable_tray_dimensions.Z + tray_thickness
                    Rectangle(width, height, align=Align.MIN)
            extrude(amount=-face_thickness)

            # create power supply tray solid
            with BuildSketch(base_location):
                location = Location((0, 0))
                with Locations(location):
                    width = (
                        tray_thickness + power_supply_tray_dimensions.X + tray_thickness
                    )
                    height = (
                        tray_thickness + power_supply_tray_dimensions.Z + tray_thickness
                    )
                    Rectangle(width, height, align=Align.MIN)
            solid = extrude(amount=power_supply_tray_dimensions.Y)

            # create power supply tray cutout
            face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            with BuildSketch(face):
                location = Location((-face.length / 2, -face.width / 2))
                location *= Pos(X=tray_thickness)
                location *= Pos(Y=tray_thickness)
                with Locations(location) as locs:
                    Rectangle(
                        power_supply_tray_dimensions.X,
                        power_supply_tray_dimensions.Z,
                        align=(Align.MIN, Align.MIN),
                    )
            extrude(amount=-power_supply_tray_dimensions.Y, mode=Mode.SUBTRACT)

            # create cable tray solid
            with BuildSketch(base_location):
                location = Location((0, 0))
                location *= Pos(X=tray_thickness)
                location *= Pos(X=power_supply_tray_dimensions.X)
                location *= Pos(X=tray_thickness)
                with Locations(location):
                    width = cable_tray_dimensions.X + tray_thickness
                    height = tray_thickness + cable_tray_dimensions.Z + tray_thickness
                    Rectangle(width, height, align=Align.MIN)
            solid = extrude(amount=cable_tray_dimensions.Y)

            # create cable tray cutout
            face = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            with BuildSketch(face):
                location = Location((-face.length / 2, -face.width / 2))
                location *= Pos(Y=tray_thickness)
                with Locations(location) as locs:
                    Rectangle(
                        cable_tray_dimensions.X,
                        cable_tray_dimensions.Z,
                        align=(Align.MIN, Align.MIN),
                    )
            extrude(amount=-cable_tray_dimensions.Y, mode=Mode.SUBTRACT)

            # create cable tray cable slots
            face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                Circle(cable_diameter / 2)
                Rectangle(
                    cable_slot_width,
                    cable_tray_dimensions.Y,
                    align=(Align.CENTER, Align.MIN),
                )
            solid = extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)
            mirror_plane = Plane(face).offset(
                -((cable_tray_dimensions.Z / 2) + tray_thickness)
            )
            mirror(solid, mirror_plane, mode=Mode.SUBTRACT)
        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Test())
