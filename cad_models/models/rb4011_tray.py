from build123d import MM, BuildPart, Vector

from cad_models.common import Model, RackInterfaceScrew, main
from cad_models.models.rb4011 import RB4011


class RB4011Tray(Model):
    def __init__(self, **kwargs):
        bracket_thickness = 4.0 * MM
        dimensions = Vector(236 * MM, 44.35 * MM, 128 * MM)
        router = RB4011()
        interface_hole_count = Vector(4, 2)
        interface_hole_spacing = Vector(20 * MM, 20 * MM)
        interface_screw = RackInterfaceScrew()

        with BuildPart() as builder:
            # make base tray
            pass

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RB4011Tray())
