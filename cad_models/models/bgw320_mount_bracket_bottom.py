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
from cad_models.models.bgw320 import Bgw320Screw


class Bgw320MountBracketBottom(Model):
    def __init__(self, **kwargs):
        # parameters
        bracket_thickness = 5.0 * MM
        dimensions = Vector(32.5 * MM, 1 * U, 242.840 * MM)
        magnet_dimensions = Vector(6.5 * MM, 3 * MM)
        magnet_offset = 10 * MM
        router_dimensions = Vector(52.0 * MM, 204.1 * MM, 178.84 * MM)
        with BuildPart(mode=Mode.PRIVATE):
            router_screw = Bgw320Screw()
        router_standoff_dimensions = Vector(8.75 * MM, 14.5 * MM, 8.0 * MM)
        router_standoff_hole_offset = 1.75 * MM
        router_standoff_spacing = 130.8 * MM
        stand_thickness = 10 * MM

        with BuildPart() as builder:
            # create bracket
            bracket = ServerRackMountBracket(dimensions=dimensions, external=True)
            builder.joints.update(bracket.joints)

            # create stand base
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            stand_dimensions = Vector(
                router_dimensions.X,
                stand_thickness,
                bracket_thickness + router_dimensions.Z + bracket_thickness,
            )
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
            rib_height = dimensions.Y - stand_thickness
            mirror_plane = Plane(face).offset(-stand_dimensions.Z / 2)
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                location = (face.width / 2, face.length / 2)
                with Locations(location):
                    Triangle(
                        a=face.width, B=90, c=rib_height, align=(Align.MAX, Align.MIN)
                    )
            rib = extrude(amount=-bracket_thickness)
            mirror(rib, mirror_plane)

            # create stand standoffs
            stand_face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[3]
            with BuildSketch(Plane(stand_face, x_dir=(1, 0, 0))) as sketch:
                spacing = router_standoff_spacing
                with GridLocations(0, spacing, 1, 2):
                    Rectangle(
                        router_standoff_dimensions.X, router_standoff_dimensions.Y
                    )
                offset = router_standoff_hole_offset * 2
                with GridLocations(0, spacing + offset, 1, 2) as grid_locations:
                    hole_locations = grid_locations.locations
            extrude(amount=-router_standoff_dimensions.Z, mode=Mode.SUBTRACT)

            # create stand standoff holes and joints
            for hole, hole_location in enumerate(hole_locations):
                # hole
                location = Location(hole_location)
                location *= Pos(Z=-stand_thickness)
                location *= Rot(Y=180)
                with Locations(location):
                    ClearanceHole(router_screw, depth=router_screw.length)

                # joint
                location = Location(hole_location)
                location *= Pos(Z=-router_standoff_dimensions.Z)
                RigidJoint(f"bgw320-{hole}", joint_location=location)

            # create magnet hole
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
            with BuildSketch(face) as sketch:
                location = Location((face.length / 2, 0))
                location *= Pos(X=-magnet_offset)
                with Locations(location):
                    Circle(magnet_dimensions.X / 2)
            extrude(amount=-magnet_dimensions.Y, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Bgw320MountBracketBottom())
