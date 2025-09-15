from build123d import (
    IN,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class WallSlats(Model):
    def __init__(self, num_slats: int = 4, slat_height: float = 48 * IN, **kwargs):
        foam_thickness = 0.3 * IN
        slat_dimensions = Vector(1.1 * IN, slat_height, 0.5 * IN)
        slat_spacing = 0.5 * IN

        foam_dimensions = Vector(
            ((slat_dimensions.X * num_slats) + (slat_spacing * (num_slats - 1))),
            slat_dimensions.Y,
            foam_thickness,
        )

        with BuildPart() as builder:
            # foam backing
            with BuildSketch(Plane.XZ):
                Rectangle(foam_dimensions.X, foam_dimensions.Y)
            solid = extrude(amount=foam_dimensions.Z)

            # slats
            face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                spacing = slat_dimensions.X + slat_spacing
                with GridLocations(spacing, 0, num_slats, 1) as grid_locs:
                    Rectangle(slat_dimensions.X, slat_dimensions.Y)
                    locations = grid_locs.locations
            extrude(amount=slat_dimensions.Z)

            # slat space joints
            offset = (slat_dimensions.X + slat_spacing) / 2
            for index, location in enumerate(locations[: num_slats - 1]):
                location *= Pos(X=offset)
                location *= Rot(X=-90, Z=180)
                label = f"slat-space-{index}"
                RigidJoint(joint_location=location, label=label)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(WallSlats())
