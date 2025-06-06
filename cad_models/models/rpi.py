from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    add,
    extrude,
)

from cad_models.common import Model, main
from cad_models.models.rpi_ssd_bracket import RpiSsdBracket


class RaspberryPi(Model):
    def __init__(self, **kwargs):
        # parameters
        ssd_dimensions = Vector(70 * MM, 100 * MM, 7 * MM)
        rpi_dimensions = Vector(56 * MM, 85 * MM, 18 * MM)
        rpi_joint_offset = 10 * MM

        with BuildPart() as builder:
            # create bracket
            bracket = RpiSsdBracket()
            add(bracket)

            # create ssd
            with BuildPart(mode=Mode.PRIVATE) as ssd_builder:
                with BuildSketch(Plane.XZ):
                    Rectangle(ssd_dimensions.X, ssd_dimensions.Z)
                extrude(amount=ssd_dimensions.Y)
                face = ssd_builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
                location = face.location_at(0.5, 0.5)
                location *= Rot(Y=180)
                RigidJoint("bracket", joint_location=location)

            # attach ssd to bracket and add to model
            ssd = ssd_builder.part
            ssd_joint: RigidJoint = ssd.joints["bracket"]
            bracket_joint: RigidJoint = bracket.joints["ssd"]
            bracket_joint.connect_to(ssd_joint)
            add(ssd)

            # create rpi
            with BuildPart(mode=Mode.PRIVATE) as rpi_builder:
                with BuildSketch(Plane.XZ):
                    Rectangle(rpi_dimensions.X, rpi_dimensions.Z)
                extrude(amount=rpi_dimensions.Y)
                face = rpi_builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
                location = face.location_at(0.5, 0.5)
                location *= Rot(Y=180)
                location *= Pos(Y=-rpi_joint_offset)
                RigidJoint("bracket", joint_location=location)

            # attach rpi to bracket and add to model
            rpi = rpi_builder.part
            rpi_joint: RigidJoint = rpi.joints["bracket"]
            bracket_joint: RigidJoint = bracket.joints["rpi"]
            bracket_joint.connect_to(rpi_joint)
            add(rpi)

            # create mount joint
            face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.5)
            location *= Rot(X=180)
            location *= Rot(Z=180)
            RigidJoint(f"mount", joint_location=location)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(RaspberryPi())
