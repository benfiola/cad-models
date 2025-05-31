from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Rectangle,
    RigidJoint,
    Rot,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class Test(Model):
    def __init__(self, **kwargs):
        # parameters
        bridge_dimensions = Vector(91.4 * MM, 26 * MM, 90.6 * MM)
        bridge_foot_spacing = Vector(65.24 * MM, 66.82 * MM)
        bridge_foot_dimensions = Vector(8.5 * MM, 0.9 * MM)
        bridge_peg_dimensions = Vector(8.2 * MM, 3.2 * MM)
        bridge_peg_spacing = 41.4 * MM
        lip_thickness = 2.0 * MM
        tray_thickness = 4.0 * MM

        with BuildPart() as builder:
            # create tray
            width = lip_thickness + bridge_dimensions.X + lip_thickness
            depth = bridge_dimensions.Z + lip_thickness
            with BuildSketch(Plane.XZ):
                thickness = tray_thickness + lip_thickness
                location = Location((0, width / 2))
                with Locations(location):
                    Rectangle(width, thickness, align=(Align.CENTER, Align.MAX))
            extrude(amount=depth)

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

            # create feet standoffs
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[1]
            with BuildSketch(face):
                with GridLocations(bridge_foot_spacing.X, bridge_foot_spacing.Y, 2, 2):
                    Circle((bridge_foot_dimensions.X + lip_thickness) / 2)
            extrude(amount=-tray_thickness)
            with BuildSketch(face):
                with GridLocations(bridge_foot_spacing.X, bridge_foot_spacing.Y, 2, 2):
                    Circle(bridge_foot_dimensions.X / 2)
            extrude(amount=-bridge_foot_dimensions.Y, mode=Mode.SUBTRACT)

            # create mount pegs
            with BuildSketch(face) as build_sketch:
                with GridLocations(0, bridge_peg_spacing, 2, 2):
                    Circle((bridge_peg_dimensions.X) / 2)
            sketch = build_sketch.sketch
            extrude(amount=-tray_thickness)
            extrude(sketch, amount=bridge_peg_dimensions.Y)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(Test())
