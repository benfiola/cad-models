from build123d import MM, BuildPart, Vector

from cad_models.common import Model, ServerRackMountBracket, U, main


class RB4011Bracket(Model):
    def __init__(self, flipped_joints: bool = False, **kwargs):
        # parameters
        dimensions = Vector(121.05 * MM, 1 * U, 124.3 * MM)
        interface_holes = Vector(3, 2)

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
    main(RB4011Bracket())
