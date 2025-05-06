from copy import copy

from build123d import (
    MM,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    GridLocations,
    Location,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    Rectangle,
    RigidJoint,
    SlotOverall,
    Solid,
    Text,
    Vector,
    add,
    extrude,
    fillet,
    make_face,
)

from cad_models.common import centered_point_list, col_major, initialize, row_major
from cad_models.data import data_file
from cad_models.models.keystone_receiver import KeystoneReceiver


class WallPatchPanel(Solid):
    def __init__(self):
        # parameters
        corner_radius = 3 * MM
        ear_dimensions = Vector(20 * MM, 0, 5 * MM)
        grid_count = Vector(3.0, 3.0)
        grid_dimensions = Vector(60 * MM, 82 * MM)
        grid_label_font_depth = 0.5 * MM
        grid_label_font_size = 5 * MM
        grid_label_font_style = "black"
        grid_labels = [
            ["br1-1", "br1-2", "br2-1"],
            ["br2-2", None, "lr-1"],
            ["lr-2", "o-1", "o-2"],
        ]
        hole_dimensions = Vector(12 * MM, 6 * MM)
        hole_spacing = Vector(230 * MM, 70 * MM)
        panel_dimensions = Vector(250 * MM, 90 * MM, 11.25 * MM)

        ear_dimensions.Y = panel_dimensions.Y

        with BuildPart() as builder:
            # create panel
            with BuildSketch(Plane.XY):
                with BuildLine():
                    pd = panel_dimensions
                    ed = ear_dimensions
                    points = centered_point_list(
                        (0, 0),
                        (0, ed.Z),
                        (ed.X, ed.Z),
                        (ed.X, pd.Z),
                        (pd.X - ed.X, pd.Z),
                        (pd.X - ed.X, ed.Z),
                        (pd.X, ed.Z),
                        (pd.X, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=panel_dimensions.Y)

            # save corners for final fillet
            fillet_edges = builder.part.edges().filter_by(Axis.Y).sort_by(Axis.Y)[:4]

            # create mount holes and joints
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face):
                with GridLocations(
                    hole_spacing.X, hole_spacing.Y, 2, 2
                ) as grid_locations:
                    SlotOverall(hole_dimensions.X, hole_dimensions.Y)
                    mount_hole_locations = grid_locations.locations
            extrude(amount=-ear_dimensions.Z, mode=Mode.SUBTRACT)
            locations = sorted(mount_hole_locations, key=col_major())
            pairs = zip(locations[::2], locations[1::2])
            for index, (top, bottom) in enumerate(pairs):
                top = Location(top.position) * Pos(Y=ear_dimensions.Z)
                bottom = Location(bottom.position) * Pos(Y=ear_dimensions.Z)
                RigidJoint(f"mount-{index}-top", joint_location=top)
                RigidJoint(f"mount-{index}-bottom", joint_location=bottom)

            # create base keystone for cutouts and future attachments
            with BuildPart(mode=Mode.PRIVATE):
                base_keystone = KeystoneReceiver()

            # create keystone cutouts
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face) as grid_sketch:
                spacing = Vector(grid_dimensions)
                spacing.X /= grid_count.X
                spacing.Y /= grid_count.Y
                with GridLocations(
                    spacing.X, spacing.Y, int(grid_count.X), int(grid_count.Y)
                ) as grid_locations:
                    Rectangle(base_keystone.kr_length, base_keystone.kr_height)
                    keystone_locations = grid_locations.locations
                    keystone_local_locations = grid_locations.local_locations
            extrude(amount=-panel_dimensions.Z, mode=Mode.SUBTRACT)

            # attach keystones
            locations = sorted(keystone_locations, key=row_major(y_dir=(0, 0, -1)))
            for index, keystone_location in enumerate(locations):
                x = int(index / grid_count.Y)
                y = index % int(grid_count.Y)
                joint_location = Location(keystone_location.position)
                cutout_joint = RigidJoint(
                    f"keystone-{x}-{y}", joint_location=joint_location
                )
                keystone = copy(base_keystone)
                joint: RigidJoint = keystone.joints["keystone"]
                cutout_joint.connect_to(joint)
                add(keystone)

            # create keystone labels
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            font_path = data_file(f"overpass-{grid_label_font_style}.ttf")
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))) as text_sketch:
                locations = sorted(
                    keystone_local_locations, key=row_major(y_dir=(0, -1, 0))
                )
                for index, keystone_location in enumerate(locations):
                    x = int(index / grid_count.Y)
                    y = index % int(grid_count.Y)
                    label = grid_labels[y][x]
                    if not label:
                        continue
                    location = Location(keystone_location.position)
                    location *= Pos(Y=base_keystone.kr_height / 2)
                    with Locations(location):
                        Text(
                            label,
                            font_path=f"{font_path}",
                            font_size=grid_label_font_size,
                        )
            extrude(amount=-grid_label_font_depth, mode=Mode.SUBTRACT)

            # fillet corners
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part.wrapped, joints=builder.part.joints)


if __name__ == "__main__":
    initialize(WallPatchPanel())
