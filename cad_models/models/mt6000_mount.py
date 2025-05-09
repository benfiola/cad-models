from build123d import (
    MM,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Circle,
    GridLocations,
    Keep,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    RigidJoint,
    Rot,
    SlotOverall,
    Vector,
    extrude,
    fillet,
    make_face,
)

from cad_models.common import Model, centered_point_list, col_major, initialize
from cad_models.models.mt6000 import MT6000


class MT6000MountTopBracket(Model):
    def __init__(self, **kwargs):
        # parameters
        bracket_thickness = 5.0 * MM
        corner_radius = 3.0 * MM
        ear_dimensions = Vector(28.0 * MM, 44.35 * MM, 0)
        hole_dimensions = Vector(12.0 * MM, 6.0 * MM)
        hole_offset = 3 * MM
        hole_spacing = 31.75 * MM
        modem = MT6000()
        modem_inset = 25 * MM

        with BuildPart() as builder:
            # create bracket (via top-down profile)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    bt = bracket_thickness
                    ed = ear_dimensions
                    md = modem.m_dimensions
                    mi = modem_inset

                    points = centered_point_list(
                        (0, 0),
                        (ed.X + bt, 0),
                        (ed.X + bt, bt + mi + md.X),
                        (ed.X, bt + mi + md.X),
                        (ed.X, bt),
                        (0, bt),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=ear_dimensions.Y)

            # find edges to fillet
            ear_edges = builder.part.edges().filter_by(Axis.Y).sort_by(Axis.X)[:2]
            fillet_edges = [*ear_edges]

            # create modem mounts
            ear_face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[-1]
            plane = ear_face.offset(-modem_inset)
            faces = face.split(plane, keep=Keep.BOTH)
            face = faces.faces().sort_by(Axis.Y)[1]
            with BuildSketch(face):
                spacing = modem.hole_spacing.X
                with GridLocations(spacing, 0, 2, 1) as grid_locations:
                    Circle(modem.peg_shaft_diameter / 2)
                    post_locations = grid_locations.locations
            solids = extrude(amount=modem.peg_depth / 2)
            faces = solids.faces().filter_by(Axis.X).sort_by(Axis.X)[-2:]
            for face in faces:
                with BuildSketch(face):
                    Circle(modem.peg_top_diameter / 2)
                extrude(amount=modem.peg_depth / 2)

            # create joints
            for hole, post_location in enumerate(post_locations):
                location = Location(post_location.position)
                location *= Pos(X=modem.peg_depth)
                # TODO: set correct orientation of all joints in project
                location *= Rot(Z=90)
                RigidJoint(f"mt6000-{hole}", joint_location=location)

            # create mount holes and joints
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                location = Location((0, 0))
                location *= Pos(X=-face.length / 2)
                location *= Pos(X=hole_offset)
                location *= Pos(X=hole_dimensions.X / 2)
                with Locations(location):
                    with GridLocations(0.0, hole_spacing, 1, 2) as grid_locations:
                        SlotOverall(hole_dimensions.X, hole_dimensions.Y)
                        hole_locations = grid_locations.locations
            extrude(amount=-bracket_thickness, mode=Mode.SUBTRACT)
            locations = sorted(hole_locations, key=col_major(y_dir=(0, 0, -1)))
            for index, location in enumerate(locations):
                joint_location = Location(location.position) * Pos(Y=bracket_thickness)
                RigidJoint(f"server-rack-{index}", joint_location=joint_location)

            # apply fillet
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)

    def mount(self, mt: MT6000):
        for hole in range(0, 2):
            mount_joint: RigidJoint = self.joints[f"mt6000-{hole}"]
            mount_location = mount_joint.location
            mt_joint: RigidJoint = mt.joints[f"mount-{hole}"]
            mt_location = mt_joint.location
            mount_joint.connect_to(mt_joint)


if __name__ == "__main__":
    initialize(MT6000MountTopBracket())
