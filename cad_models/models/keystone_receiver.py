from pathlib import Path

import ocp_vscode
from build123d import Axis, Compound, Location, RigidJoint, Solid, Vector, import_step

step_file = Path(__file__).parent.joinpath("keystone_receiver.step")


class KeystoneReceiver(Solid):
    kr_dimensions: Vector

    def __init__(self, label: str = ""):
        solid: Solid = import_step(step_file)
        solid = solid.rotate(Axis.X, 270.0)

        # find faces to calculate size + joint location
        front_face = solid.faces().sort_by(Axis.Y)[0]
        bottom_face = solid.faces().sort_by(Axis.Z)[0]

        # create joint
        joint_location = Location(front_face.position_at(0.5, 0.5))
        joint = RigidJoint(
            "keystone",
            to_part=solid,
            joint_location=joint_location,
        )

        super().__init__(solid.wrapped, joints={joint.label: joint}, label=label)

        # store size (calculated from faces)
        size = Vector(front_face.length, front_face.width, bottom_face.width)
        self.kr_dimensions = size


class Model(Compound):
    def __init__(self):
        receiver = KeystoneReceiver()
        super().__init__([], children=[receiver])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
