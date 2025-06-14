from typing import cast

from build123d import (
    Axis,
    BuildPart,
    Location,
    RigidJoint,
    Rot,
    Solid,
    Vector,
    add,
    import_step,
)

from cad_models.common import Model, main
from cad_models.data import data_file


class KeystoneReceiver(Model):
    dimensions: Vector

    def __init__(self, **kwargs):
        solid: Solid = cast(Solid, import_step(data_file("keystone-receiver.step")))
        solid = solid.rotate(Axis.X, 90)

        with BuildPart() as builder:
            add(solid)

            # find faces to calculate size + joint location
            front_face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            bottom_faces = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[:3]

            # create joint
            joint_location = Location(front_face.location_at(0.5, 0.5))
            joint_location *= Rot(Z=90)
            RigidJoint("keystone", to_part=builder.part, joint_location=joint_location)

            super().__init__(builder.part, **kwargs)

        # calculate dimensions from faces
        width = 0.0
        for face in bottom_faces:
            width += face.length
        self.dimensions = Vector(front_face.length, front_face.width, width)


if __name__ == "__main__":
    main(KeystoneReceiver())
