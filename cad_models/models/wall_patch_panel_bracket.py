from bd_warehouse.fastener import ClearanceHole
from build123d import (
    MM,
    Align,
    Axis,
    Box,
    BuildLine,
    BuildPart,
    BuildSketch,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    RigidJoint,
    Rot,
    Vector,
    extrude,
    make_face,
)

from cad_models.common import (
    Model,
    RackMountNut,
    RackMountScrew,
    WallScrew,
    captive_nut_slot_dimensions,
    centered_point_list,
    main,
)


class WallPatchPanelBracket(Model):
    def __init__(self, **kwargs):
        # parameters
        arm_dimensions = Vector(0, 20 * MM, 90 * MM)
        base_dimensions = Vector(20 * MM, 0, 12 * MM)
        mount_hole_spacing = 70 * MM
        mount_slot_offset = 5 * MM
        mount_nut = RackMountNut()
        mount_screw = RackMountScrew()
        wall_screw = WallScrew()

        # derived values
        arm_dimensions.X = base_dimensions.X
        base_dimensions.Y = mount_hole_spacing + arm_dimensions.Y

        with BuildPart() as builder:
            # create bracket (via side profile)
            with BuildSketch(Plane.YZ):
                with BuildLine():
                    ad = arm_dimensions
                    bd = base_dimensions

                    points = centered_point_list(
                        (0, 0),
                        (0, ad.Y),
                        (ad.Z - bd.Z, ad.Y),
                        (ad.Z - bd.Z, bd.Y - ad.Y),
                        (0, bd.Y - ad.Y),
                        (0, bd.Y),
                        (ad.Z, bd.Y),
                        (ad.Z, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            bracket = extrude(amount=base_dimensions.X)

            # create wall hole
            face = bracket.faces().filter_by(Axis.Y).sort_by(Axis.Y)[2]
            location = face.location_at(0.5, 0.5)
            with Locations(location):
                ClearanceHole(wall_screw)

            # create mount holes + slots
            slot_dimensions = captive_nut_slot_dimensions(mount_nut)
            faces = (
                bracket.faces()
                .filter_by(Axis.Y)
                .sort_by(Axis.Y)[:2]
                .sort_by(Axis.Z, reverse=True)
            )
            for index, face in enumerate(faces):
                # hole
                location = face.location_at(0.5, 0.5)
                with Locations(location):
                    ClearanceHole(
                        mount_screw, counter_sunk=False, depth=mount_screw.length
                    )

                # joint
                location = Location(face.location_at(0.5, 0.5))
                location *= Rot(Z=90)
                RigidJoint(f"mount-{index}", joint_location=location)

                # slot
                location = face.location_at(0.5, 0.5)
                location *= Pos(X=slot_dimensions.X / 2)
                location *= Pos(X=-arm_dimensions.Y)
                location *= Pos(Z=-mount_slot_offset)
                with Locations(location):
                    Box(
                        arm_dimensions.Y,
                        slot_dimensions.Y,
                        slot_dimensions.Z,
                        align=(Align.MIN, Align.CENTER, Align.CENTER),
                        mode=Mode.SUBTRACT,
                    )

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(WallPatchPanelBracket())
