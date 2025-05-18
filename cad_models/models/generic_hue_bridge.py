from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Location,
    Locations,
    Mode,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, ServerRackMountBlank, main
from cad_models.models.generic_blank import GenericBlank
from cad_models.models.hue_bridge import HueBridge


class GenericHueBridge(Model):
    dimensions: Vector

    def __init__(self, **kwargs):
        with BuildPart(mode=Mode.PRIVATE):
            bridge = HueBridge()
        bridge_tolerance = 0.5 * MM
        with BuildPart(mode=Mode.PRIVATE):
            generic_blank = GenericBlank()
        lip_thickness = 2.0 * MM
        tray_thickness = 4.0 * MM

        # derived values
        bridge_dimensions = Vector(
            bridge.dimensions.X + bridge_tolerance,
            bridge.dimensions.Y,
            bridge.dimensions.Z + bridge_tolerance,
        )
        tray_depth = bridge_dimensions.Z + lip_thickness

        with BuildPart() as builder:
            blank = ServerRackMountBlank(
                interface_holes=generic_blank.interface_holes,
                interior_dimensions=generic_blank.interior_dimensions,
            )
            builder.joints.update(blank.joints)

            # create tray
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[1]
            with BuildSketch(face):
                thickness = tray_thickness + lip_thickness
                location = Location((0, face.width / 2))
                with Locations(location):
                    Rectangle(face.length, thickness, align=(Align.CENTER, Align.MAX))
            extrude(amount=tray_depth)

            # create tray mount
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                location = Location((0, -face.width / 2))
                with Locations(location):
                    Rectangle(
                        bridge_dimensions.X,
                        bridge_dimensions.Z,
                        align=(Align.CENTER, Align.MIN),
                    )
            tray_mount = extrude(amount=-lip_thickness, mode=Mode.SUBTRACT)
            face = tray_mount.faces().sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.5)
            location *= Rot(Y=180)
            RigidJoint(f"hue-bridge", joint_location=location)

            # create face cutout
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                location = Location((0, face.width / 2))
                location *= Pos(Y=-(tray_thickness + lip_thickness))
                width = bridge_dimensions.X - (lip_thickness * 2)
                height = bridge_dimensions.Y - (lip_thickness * 2)
                with Locations(location):
                    Rectangle(width, height, align=(Align.CENTER, Align.MAX))
            extrude(amount=-tray_thickness, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)

        self.dimensions = blank.dimensions


if __name__ == "__main__":
    main(GenericHueBridge())
