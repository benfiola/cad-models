from build123d import MM, BuildPart, Vector

from cad_models.common import Model, ServerRackMountBlank, U, main


class GenericBlank(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(145.03 * MM, 1 * U, 154 * MM)
        interface_holes = Vector(2, 2)

        with BuildPart() as builder:
            # create blank
            bracket = ServerRackMountBlank(
                dimensions=dimensions, interface_holes=interface_holes
            )
            builder.joints.update(bracket.joints)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericBlank())
