from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Pos,
    Rectangle,
    Vector,
    extrude,
)

from cad_models.common import Model, ServerRackMountBlank, U, main


class GenericBlank(Model):
    def __init__(self, interface_hole_captive_nut: bool = False, **kwargs):
        # parameters
        dimensions = Vector(145.03 * MM, 1 * U, 154 * MM)
        interface_holes = Vector(2, 2)
        support_dimensions = Vector(20 * MM, 4 * MM)
        support_spacing = 67 * MM

        with BuildPart() as builder:
            # create blank
            bracket = ServerRackMountBlank(
                dimensions=dimensions,
                interface_holes=interface_holes,
                interface_hole_captive_nut=interface_hole_captive_nut,
            )
            builder.joints.update(bracket.joints)

            # create supports
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0)
            location *= Pos(Y=dimensions.Z / 2)
            with BuildSketch(location):
                with GridLocations(0, support_spacing, 1, 3):
                    Rectangle(face.length, support_dimensions.X)
            extrude(amount=-support_dimensions.Y)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericBlank())
