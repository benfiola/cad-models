from bd_warehouse.fastener import ClearanceHole
from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    Triangle,
    Vector,
    extrude,
    mirror,
)

from cad_models.common import Model, ServerRackMountBracket, U, main
from cad_models.models.coda56 import Coda56


class Coda56MountBottomBracket(Model):
    def __init__(self, **kwargs):
        bracket_height = 1 * U
        bracket_thickness = 5.0 * MM
        magnet_dimensions = Vector(6.0 * MM + 0.5 * MM, 0, 3 * MM)
        magnet_offset = 10 * MM
        router = Coda56()
        router_inset = 50 * MM
        stand_thickness = 10 * MM

        router_dimensions = Vector(
            router.dimensions.X + 0.5 * MM,
            router.dimensions.Y,
            router.dimensions.Z + 0.5 * MM,
        )
        stand_dimensions = Vector(
            router_dimensions.X,
            stand_thickness,
            bracket_thickness + router_dimensions.Z + bracket_thickness,
        )
        rib_height = bracket_height - stand_thickness
        interior_dimensions = Vector(
            0, bracket_height, router_inset + stand_dimensions.Z
        )

        with BuildPart() as builder:
            bracket = ServerRackMountBracket(
                external=True, interior_dimensions=interior_dimensions
            )
            builder.joints.update(bracket.joints)

            # create stand base
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            with BuildSketch(face):
                location = Location((0, 0))
                location *= Pos(X=-face.length / 2, Y=face.width / 2)
                with Locations(location) as locs:
                    Rectangle(
                        stand_dimensions.Z,
                        stand_dimensions.Y,
                        align=(Align.MIN, Align.MAX),
                    )
            stand = extrude(amount=stand_dimensions.X)

            # create stand ribs
            face = stand.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            mirror_plane = Plane(face).offset(-stand_dimensions.Z / 2)
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                location = (router.dimensions.X / 2, stand_thickness / 2)
                with Locations(location):
                    Triangle(
                        a=face.width, B=90, c=rib_height, align=(Align.MAX, Align.MIN)
                    )
            rib = extrude(amount=-bracket_thickness)
            mirror(rib, mirror_plane)

            # create stand standoffs
            stand_face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[3]
            with BuildSketch(Plane(stand_face, x_dir=(1, 0, 0))) as sketch:
                spacing = router.standoff_spacing
                with GridLocations(0, spacing, 1, 2):
                    Rectangle(
                        router.standoff_dimensions.X, router.standoff_dimensions.Y
                    )
                offset = router.standoff_hole_offset * 2
                with GridLocations(0, spacing + offset, 1, 2) as grid_locations:
                    hole_locations = grid_locations.locations
            extrude(amount=-router.standoff_dimensions.Z, mode=Mode.SUBTRACT)

            # create stand standoff holes and joints
            for hole, hole_location in enumerate(hole_locations):
                # hole
                location = Location(hole_location)
                location *= Pos(Z=-stand_thickness)
                location *= Rot(Y=180)
                with Locations(location):
                    ClearanceHole(router.screw, depth=router.screw.length)

                # joint
                location = Location(hole_location)
                location *= Pos(Z=-router.standoff_dimensions.Z)
                RigidJoint(f"coda56-{hole}", joint_location=location)

            # create magnet hole
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face) as sketch:
                location = Location((-face.length / 2, 0))
                location *= Pos(X=magnet_offset)
                with Locations(location):
                    Circle(magnet_dimensions.X / 2)
            extrude(amount=-magnet_dimensions.Z, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Coda56MountBottomBracket())
