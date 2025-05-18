from build123d import IN, MM, BuildPart, Vector

from cad_models.common import Model, ServerRackMountBlank, U, main


class GenericBlank(Model):
    interface_holes: Vector
    interior_dimensions: Vector

    def __init__(self, **kwargs):
        interface_holes = Vector(2, 2)

        total_space = ((19 * IN) - (6.0 * MM + 6.0 * MM)) / 3
        interior_dimensions = Vector(total_space - 12.0 * MM, 1 * U, 150 * MM)

        with BuildPart() as builder:
            bracket = ServerRackMountBlank(
                interface_holes=interface_holes,
                interior_dimensions=interior_dimensions,
            )
            builder.joints.update(bracket.joints)

        super().__init__(builder.part, **kwargs)

        self.interior_dimensions = interior_dimensions
        self.interface_holes = interface_holes


if __name__ == "__main__":
    main(GenericBlank())
