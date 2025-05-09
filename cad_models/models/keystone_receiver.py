from typing import cast

from build123d import Axis, Location, RigidJoint, Rot, Solid, Vector, import_step

from cad_models.common import Model, initialize
from cad_models.data import data_file


class KeystoneReceiver(Model):
    kr_dimensions: Vector

    def __init__(self, **kwargs):
        solid: Solid = cast(Solid, import_step(data_file("keystone-receiver.step")))
        solid = solid.rotate(Axis.X, 90)

        # find faces to calculate size + joint location
        front_face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        bottom_faces = solid.faces().filter_by(Axis.Z).sort_by(Axis.Z)[:3]

        # create joint
        joint_location = Location(front_face.location_at(0.5, 0.5))
        joint_location *= Rot(Z=90)
        RigidJoint("keystone", to_part=solid, joint_location=joint_location)

        super().__init__(solid, **kwargs)

        # calculate dimensions from faces
        width = 0.0
        for face in bottom_faces:
            width += face.length
        self.kr_dimensions = Vector(front_face.length, front_face.width, width)


if __name__ == "__main__":
    initialize(KeystoneReceiver())
