from build123d import (
    MM,
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Locations,
    Mode,
    Plane,
    Pos,
    Rectangle,
    RigidJoint,
    Rot,
    SlotOverall,
    Vector,
    extrude,
)

from cad_models.common import Model, main


class HueBridge(Model):
    def __init__(self, **kwargs):
        # parameters
        dimensions = Vector(91.82 * MM, 26.9 * MM, 89.42 * MM)
        foot_spacing = Vector(65.24 * MM, 66.82 * MM)
        foot_dimensions = Vector(7.5 * MM, 0.9 * MM)
        mount_slot_outer_width = 9.2 * MM
        mount_slot_inner_width = 5.0 * MM
        mount_slot_length = 17 * MM
        mount_slot_depth = 4.2 * MM
        mount_spacing = 41.4 * MM

        with BuildPart() as builder:
            # create bridge box
            with BuildSketch(Plane.XZ):
                Rectangle(dimensions.X, dimensions.Y)
            extrude(amount=dimensions.Z)

            # create joint
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            location = face.location_at(0.5, 0.5)
            location *= Rot(X=180)
            location *= Rot(Z=180)
            RigidJoint(f"mount", joint_location=location)

            # create feet
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
            with BuildSketch(face):
                with GridLocations(foot_spacing.X, foot_spacing.Y, 2, 2):
                    Circle(foot_dimensions.X / 2)
            extrude(amount=foot_dimensions.Y)

            # create mounts
            face = builder.part.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-2]
            with BuildSketch(face):
                with GridLocations(0, mount_spacing, 1, 2) as grid_locs:
                    back, front = grid_locs.local_locations
                with Locations(back):
                    SlotOverall(mount_slot_length, mount_slot_outer_width, rotation=90)
                with Locations(front):
                    SlotOverall(mount_slot_length, mount_slot_inner_width, rotation=90)
                front *= Pos(Y=-mount_slot_length / 2)
                with Locations(front):
                    Circle(mount_slot_outer_width / 2, align=(Align.CENTER, Align.MIN))
            extrude(amount=-mount_slot_depth, mode=Mode.SUBTRACT)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(HueBridge())
