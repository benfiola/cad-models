from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    SlotOverall,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class Test(Model):
    def __init__(self, **kwargs):
        # parameters
        lip_thickness = 2 * MM
        thinkcentre_dimensions = Vector(179.5 * MM, 34.5 * MM, 183.5 * MM)
        thinkcentre_foot_dimensions = Vector(16.0 * MM, 7.5 * MM, 2.5 * MM)
        thinkcentre_foot_spacing = Vector(162.5 * MM, 133 * MM)
        thinkcentre_foot_offset = 0.5 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            # create tray
            width = lip_thickness + thinkcentre_dimensions.X + lip_thickness
            depth = lip_thickness + thinkcentre_dimensions.Z + lip_thickness
            with BuildSketch(Plane.XZ):
                thickness = tray_thickness + lip_thickness
                Rectangle(width, thickness, align=(Align.CENTER, Align.MAX))
            extrude(amount=depth)

            # create tray mount
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                Rectangle(
                    thinkcentre_dimensions.X,
                    thinkcentre_dimensions.Z,
                    align=(Align.CENTER, Align.CENTER),
                )
            extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)

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

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Test())
