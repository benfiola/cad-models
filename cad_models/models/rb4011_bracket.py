from build123d import IN, MM, BuildPart, Mode, Vector

from cad_models.common import Model, ServerRackMountBracket, U, main
from cad_models.models.rb4011_tray import RB4011Tray


class RB4011Bracket(Model):
    def __init__(self, flipped_joints: bool = False, **kwargs):
        interface_holes = Vector(3, 2)
        with BuildPart(mode=Mode.PRIVATE):
            tray = RB4011Tray()

        dimensions = Vector(
            ((19 * IN - tray.dimensions.X) / 2) - 6.0 * MM, 1 * U, tray.dimensions.Z
        )
        with BuildPart() as builder:
            bracket = ServerRackMountBracket(
                interface_holes=interface_holes,
                flipped_joints=flipped_joints,
                interior_dimensions=dimensions,
            )
            builder.joints.update(bracket.joints)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RB4011Bracket())
