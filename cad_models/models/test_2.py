from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    GridLocations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    add,
    extrude,
)

from cad_models.common import Model, main
from cad_models.models.keystone_receiver import KeystoneReceiver


class Test2(Model):
    def __init__(self, **kwargs):
        with BuildPart(mode=Mode.PRIVATE):
            base_receiver = KeystoneReceiver()

        depths = [0.0 * MM, 0.5 * MM, 1.0 * MM, 1.5 * MM]
        padding = 5 * MM
        thickness = 5 * MM

        with BuildPart() as builder:
            # create base
            width = base_receiver.dimensions.X * len(depths)
            width += (len(depths) + 1) * padding
            height = base_receiver.dimensions.Y + (padding * 2)
            with BuildSketch(Plane.XZ):
                Rectangle(width, height)
            extrude(amount=thickness)

            # create keystone receiver cutouts and store locations
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[-1]
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                spacing = base_receiver.dimensions.X + padding
                with GridLocations(spacing, 0, len(depths), 1) as grid_locs:
                    locations = grid_locs.locations
                    Rectangle(base_receiver.dimensions.X, base_receiver.dimensions.Y)
            extrude(amount=-thickness, mode=Mode.SUBTRACT)

            # create receivers and connect to panel
            for index, location in enumerate(locations):
                receiver = KeystoneReceiver(taper_fix_depth=depths[index])
                location *= Pos(Z=-thickness)
                location *= Rot(Y=180)
                location *= Rot(Z=180)
                test_joint = RigidJoint(f"{index}", joint_location=location)
                keystone_joint: RigidJoint = receiver.joints["keystone"]
                test_joint.connect_to(keystone_joint)
                add(receiver)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Test2())
