from pathlib import Path

from build123d import Axis, Location, RigidJoint, Solid, import_step

step_file = Path(__file__).parent.joinpath("keystone_receiver.step")


class KeystoneReceiver(Solid):
    def __init__(self, label: str = ""):
        solid = import_step(step_file)
        front_face = solid.faces().sort_by(Axis.Z)[0]
        joint = RigidJoint(
            "keystone",
            to_part=solid,
            joint_location=Location(front_face.center_location.position),
        )
        super().__init__(solid.wrapped, joints={joint.label: joint}, label=label)
