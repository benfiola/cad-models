from build123d import MM, BuildPart, Vector

from cad_models.common import Model, ServerRackMountBracket, U, main


class GenericBracket(Model):
    def __init__(self, flipped_joints: bool = False, **kwargs):
        # parameters
        dimensions = Vector(23.75, 1 * U, 154 * MM)
        interface_holes = Vector(2, 2)

        with BuildPart() as builder:
            # create bracket
            bracket = ServerRackMountBracket(
                dimensions=dimensions,
                interface_holes=interface_holes,
                flipped_joints=flipped_joints,
            )
            builder.joints.update(bracket.joints)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericBracket())
