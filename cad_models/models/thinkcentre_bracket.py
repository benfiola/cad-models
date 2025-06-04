from copy import copy

from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Location,
    Mode,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    add,
    extrude,
)

from cad_models.common import Model, ServerRackMountBracket, U, main
from cad_models.models.keystone_receiver import KeystoneReceiver


class ThinkcentreBracket(Model):
    def __init__(
        self,
        flipped_joints: bool = False,
        keystone_receivers: bool = True,
        power_supply_tray: bool = False,
        **kwargs,
    ):
        # parameters
        dimensions = Vector(145.8 * MM, 1 * U, 189 * MM)
        face_thickness = 4 * MM
        with BuildPart(mode=Mode.PRIVATE):
            base_keystone = KeystoneReceiver()
        keystone_spacing = 25 * MM
        interface_holes = Vector(3, 2)

        with BuildPart() as builder:
            # create bracket
            bracket = ServerRackMountBracket(
                dimensions=dimensions,
                interface_holes=interface_holes,
                flipped_joints=flipped_joints,
            )
            builder.joints.update(bracket.joints)

            if keystone_receivers:
                # create keystone cutouts
                face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
                with BuildSketch(face):
                    with GridLocations(keystone_spacing, 0, 2, 1) as grid_locs:
                        keystone_locations = grid_locs.locations
                        Rectangle(
                            base_keystone.dimensions.X, base_keystone.dimensions.Y
                        )
                extrude(amount=-face_thickness, mode=Mode.SUBTRACT)

                # attach keystone receivers to cutouts
                for index, keystone_location in enumerate(keystone_locations):
                    joint_location = Location(keystone_location)
                    joint_location *= Rot(Z=180)
                    cutout_joint = RigidJoint(
                        f"keystone-{index}", joint_location=joint_location
                    )
                    keystone = copy(base_keystone)
                    joint: RigidJoint = keystone.joints["keystone"]
                    cutout_joint.connect_to(joint)
                    add(keystone)

            if power_supply_tray:
                pass

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(ThinkcentreBracket())
