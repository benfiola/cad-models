from bd_warehouse.fastener import ClearanceHole
from build123d import (
    IN,
    MM,
    Axis,
    Box,
    BuildPart,
    Compound,
    Location,
    Locations,
    Pos,
    RigidJoint,
    Solid,
    Vector,
)

from cad_models.common import RackMountScrew


class ServerRack(Solid):
    def __init__(self):
        rack_us = 16
        dimensions = Vector(25.0 * MM, 0, 21 * IN)
        hole_offset = 3 * MM
        mount_screw = RackMountScrew()

        dimensions.Y = rack_us * 1.75 * IN

        with BuildPart() as builder:
            Box(dimensions.X, dimensions.Z, dimensions.Y)

            # create mount holes p
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            base_location = face.location_at(1.0, 0.0)
            base_location *= Pos(Y=hole_offset)
            base_location *= Pos(Y=mount_screw.thread_diameter / 2)
            for index in range(rack_us):
                positions = {
                    "top": base_location * Pos(X=0.25 * IN),
                    "bottom": base_location * Pos(X=1.50 * IN),
                }
                for position, location in positions.items():
                    # hole
                    with Locations(location):
                        ClearanceHole(
                            mount_screw, counter_sunk=False, depth=mount_screw.length
                        )

                    # joint
                    joint_location = Location(location.position)
                    RigidJoint(
                        f"mount-{index}-{position}", joint_location=joint_location
                    )
                base_location *= Pos(X=1.75 * IN)

        super().__init__(builder.part.wrapped, joints=builder.part.joints)

    def side_mount(self, item: Solid | Compound, u: int):
        for position in ["top", "bottom"]:
            rack_joint: RigidJoint = self.joints[f"mount-{u}-{position}"]
            item_joint: RigidJoint = item.joints[f"mount-{position}"]
            rack_joint.connect_to(item_joint)
