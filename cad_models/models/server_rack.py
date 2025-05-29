from enum import Enum

from bd_warehouse.fastener import ClearanceHole
from build123d import (
    IN,
    MM,
    Align,
    Axis,
    Box,
    BuildPart,
    Location,
    Locations,
    Plane,
    Pos,
    RigidJoint,
    Rot,
    Vector,
    mirror,
)

from cad_models.common import Model, ServerRackMountScrew, main


class Mount(Enum):
    Both = "both"
    Left = "left"
    Right = "right"


class ServerRack(Model):
    def __init__(self, u: int = 16, **kwargs):
        # parameters
        arm_distance = 476.02 * MM
        arm_dimensions = Vector(26.5 * MM, u * 1.75 * IN, 18.11 * IN)
        hole_offset = 5 * MM
        mount_screw = ServerRackMountScrew()

        with BuildPart() as builder:
            # create left arm
            location = Pos(-arm_distance / 2, 0, 0)
            with Locations(location):
                # create arm box
                Box(
                    arm_dimensions.X,
                    arm_dimensions.Z,
                    arm_dimensions.Y,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                )

            # create mount holes
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            base = face.location_at(1.0, 1.0)
            base *= Pos(Y=-hole_offset)
            base *= Pos(Y=-(mount_screw.thread_diameter / 2))
            holes = []
            for rack_u in range(u):
                holes.extend([base * Pos(X=0.25 * IN), base * Pos(X=1.50 * IN)])
                base *= Pos(X=1.75 * IN)
            with Locations(holes) as locations:
                ClearanceHole(
                    mount_screw,
                    counter_sunk=False,
                    depth=mount_screw.length,
                )
                hole_locations = locations.locations

            # create right-arm
            left_arm = builder.part
            mirror(left_arm, Plane.YZ)

            # create joints
            for index, left in enumerate(hole_locations):
                rack_u = int(index / 2)
                hole = index % 2
                left = Location(left)
                left *= Rot(Z=90)
                RigidJoint(f"mount-{rack_u}-0-{hole}", joint_location=left)
                right = Location(left)
                right *= Pos(X=-left.position.X * 2)
                right *= Rot(Z=180)
                RigidJoint(f"mount-{rack_u}-1-{hole}", joint_location=right)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(ServerRack())
