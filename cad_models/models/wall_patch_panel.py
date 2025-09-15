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
    Rot,
    SlotOverall,
    Text,
    Vector,
    add,
    extrude,
    fillet,
    make_face,
)

from cad_models.common import Model, centered_point_list, col_major, main, row_major
from cad_models.data import data_file
from cad_models.models.keystone_receiver import KeystoneReceiver


class WallPatchPanel(Model):
    def __init__(self, **kwargs):
        # parameters
        corner_radius = 3 * MM
        ear_dimensions = Vector(20 * MM, 0, 5 * MM)
        grid_dimensions = Vector(78 * MM, 82 * MM)
        grid_label_font_depth = 0.5 * MM
        grid_label_font_size = 5 * MM
        grid_label_font_style = "black"
        grid_labels = [
            ["br1-1", "br1-2", "br2-1"],
            ["br2-2", None, None, "lr-1"],
            ["lr-2", "o-1", "o-2"],
        ]
        hole_dimensions = Vector(12 * MM, 6 * MM)
        hole_spacing = Vector(230 * MM, 70 * MM)
        panel_dimensions = Vector(250 * MM, 90 * MM, 11.25 * MM)

        ear_dimensions.Y = panel_dimensions.Y

        with BuildPart() as builder:
            # create panel (as top-down sketch)
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
                top = Location(top)
                top *= Pos(Z=-ear_dimensions.Z)
                top *= Rot(Z=180)
                RigidJoint(f"mount-{index}-0", joint_location=top)
                bottom = Location(bottom)
                bottom *= Pos(Z=-ear_dimensions.Z)
                bottom *= Rot(Z=180)
                RigidJoint(f"mount-{index}-1", joint_location=bottom)

            # create base keystone for cutouts and future attachments
            with BuildPart(mode=Mode.PRIVATE):
                base_keystone = KeystoneReceiver()

            # create keystone cutouts
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            keystone_local_locations = []
            keystone_locations = []
            with BuildSketch(face):
                # calculate row locs
                num_rows = len(grid_labels)
                spacing_y = (grid_dimensions.Y - base_keystone.dimensions.Y) / (
                    num_rows - 1
                )
                with GridLocations(0, spacing_y, 1, num_rows) as grid_locs:
                    row_locs = grid_locs.local_locations
                    row_locs = sorted(row_locs, key=row_major(y_dir=(0, -1, 0)))

                # use row locs, calculate col locs
                for row, row_loc in zip(grid_labels, row_locs):
                    num_cols = len(row)
                    spacing_x = (grid_dimensions.X - base_keystone.dimensions.X) / (
                        num_cols - 1
                    )
                    with Locations(row_loc):
                        with GridLocations(spacing_x, 0, num_cols, 1) as grid_locs:
                            col_local_locs = grid_locs.local_locations
                            col_local_locs = sorted(col_local_locs, key=col_major())
                            keystone_local_locations.append(col_local_locs)
                            col_locs = grid_locs.locations
                            col_locs = sorted(col_locs, key=col_major())
                            keystone_locations.append(col_locs)

                # place cutouts
                with Locations(*keystone_local_locations):
                    Rectangle(base_keystone.dimensions.X, base_keystone.dimensions.Y)
            extrude(amount=-panel_dimensions.Z, mode=Mode.SUBTRACT)

            # attach keystones
            for row, row_locations in enumerate(keystone_locations):
                for col, keystone_location in enumerate(row_locations):
                    joint_location = Location(keystone_location)
                    joint_location *= Rot(Z=180)
                    cutout_joint = RigidJoint(
                        f"keystone-{row}-{col}", joint_location=joint_location
                    )
                    keystone = copy(base_keystone)
                    joint: RigidJoint = keystone.joints["keystone"]
                    cutout_joint.connect_to(joint)
                    add(keystone)

            # create keystone labels
            face = builder.part.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            font_path = data_file(f"overpass-{grid_label_font_style}.ttf")
            with BuildSketch(Plane(face, x_dir=(1, 0, 0))):
                for row, row_locations in enumerate(keystone_local_locations):
                    for col, keystone_location in enumerate(row_locations):
                        label = grid_labels[row][col]
                        if not label:
                            continue
                        location = Location(keystone_location.position)
                        location *= Pos(Y=base_keystone.dimensions.Y / 2)
                        with Locations(location):
                            Text(
                                label,
                                font_path=f"{font_path}",
                                font_size=grid_label_font_size,
                            )
            extrude(amount=-grid_label_font_depth, mode=Mode.SUBTRACT)

            # fillet corners
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


if __name__ == "__main__":
    main(WallPatchPanel())
