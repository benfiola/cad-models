from build123d import MM, BuildPart, Vector

from cad_models.common import Model, ServerRackBlank, U, main
from cad_models.models.rb4011 import RB4011


class RB4011Tray(Model):
    def __init__(self, **kwargs):
        router_dimensions = RB4011().dimensions
        interface_holes = Vector(3, 2)
        lip_thickness = 2 * MM
        tolerance = 0.5 * MM
        tray_thickness = 4.0 * MM

        # derived values
        tray_dimensions = Vector(
            router_dimensions.X + tolerance, 1 * U, router_dimensions.Z + tolerance
        )

        with BuildPart() as builder:
            blank = ServerRackBlank(
                dimensions=tray_dimensions,
                interface_holes=interface_holes,
            )

        super().__init__(builder.part, **kwargs)

        self.dimensions = tray_dimensions


if __name__ == "__main__":
    main(RB4011Tray())
