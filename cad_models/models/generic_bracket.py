from build123d import MM, BuildPart, Vector

from cad_models.common import Model, ServerRackMountBracket, U, main


class GenericBracket(Model):
    def __init__(self, flipped_joints: bool = False, **kwargs):
        interface_holes = Vector(2, 2)

        interior_dimensions = (0, 1 * U, 150 * MM)
        with BuildPart() as builder:
            bracket = ServerRackMountBracket(
                interface_holes=interface_holes,
                flipped_joints=flipped_joints,
                interior_dimensions=interior_dimensions,
            )
            builder.joints.update(bracket.joints)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(GenericBracket())
