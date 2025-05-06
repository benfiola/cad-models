from typing import cast

from build123d import Axis, Location, RigidJoint, Solid, import_step

from cad_models.common import initialize
from cad_models.data import data_file


class KeystoneReceiver(Solid):
    kr_length: float
    kr_height: float
    kr_width: float

    def __init__(self, label: str = ""):
        solid: Solid = cast(Solid, import_step(data_file("keystone-receiver.step")))
        solid = solid.rotate(Axis.X, 90)

        # find faces to calculate size + joint location
        front_face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        bottom_faces = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[:3]

        # create joint
        joint_location = Location(front_face.position_at(0.5, 0.5))
        joint = RigidJoint(
            "keystone",
            to_part=solid,
            joint_location=joint_location,
        )

        super().__init__(solid.wrapped, joints={joint.label: joint}, label=label)

        # calculate dimensions from faces
        self.kr_length = front_face.length
        self.kr_height = front_face.width
        width = 0.0
        for face in bottom_faces:
            width += face.length
        self.kr_width = width


if __name__ == "__main__":
    initialize(KeystoneReceiver())
