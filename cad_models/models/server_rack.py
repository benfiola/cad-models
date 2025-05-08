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
    Plane,
    Pos,
    RigidJoint,
    Solid,
    Vector,
    mirror,
)

from cad_models.common import Model, RackMountScrew, initialize


class ServerRack(Model):
    def __init__(self, **kwargs):
        # parameters
        rack_us = 16
        arm_distance = 19 * IN
        arm_dimensions = Vector(25.0 * MM, 0, 18.11 * IN)
        hole_offset = 3 * MM
        mount_screw = RackMountScrew()

        # derived values
        arm_dimensions.Y = rack_us * 1.75 * IN

        with BuildPart() as builder:
            # create left arm
            location = Pos(-(arm_distance + arm_dimensions.X) / 2, 0, 0)
            with Locations(location):
                # create arm box
                Box(
                    arm_dimensions.X,
                    arm_dimensions.Z,
                    arm_dimensions.Y,
                )

            # create mount holes
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            base = face.location_at(1.0, 0.0)
            base *= Pos(Y=hole_offset)
            base *= Pos(Y=mount_screw.thread_diameter / 2)
            holes = []
            for rack_u in range(rack_us):
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
                left = Location(left.position)
                right = Location(left) * Pos(X=-left.position.X * 2)
                RigidJoint(f"mount-{rack_u}-0-{hole}", joint_location=left)
                RigidJoint(f"mount-{rack_u}-1-{hole}", joint_location=right)

        kwargs["obj"] = builder.part.wrapped
        kwargs["joints"] = builder.part.joints
        super().__init__(builder.part.wrapped, **kwargs)

    def side_mount(self, item: Solid | Compound, rack_u: int):
        for hole in range(0, 2):
            rack_joint: RigidJoint = self.joints[f"mount-{rack_u}-1-{hole}"]
            item_joint: RigidJoint = item.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(item_joint)


if __name__ == "__main__":
    initialize(ServerRack())
