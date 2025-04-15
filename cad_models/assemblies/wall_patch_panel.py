from collections.abc import Iterable
from copy import copy

import ocp_vscode
from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    GridLocations,
    Joint,
    Location,
    Locations,
    Mode,
    Rectangle,
    RigidJoint,
    SlotOverall,
    Solid,
    Text,
    Vector,
    VectorLike,
    extrude,
    fillet,
)

from cad_models.solids.keystone_receiver import KeystoneReceiver


class Panel(Solid):
    def __init__(
        self,
        *,
        corner_radius: float,
        dimensions: VectorLike,
        keystone_count: tuple[int, int],
        keystone_grid_dimensions: VectorLike,
        keystone_text: list[str | None],
        keystone_text_depth: float,
        keystone_text_size: float,
        label: str = "",
        mount_hole_dimensions: VectorLike,
        mount_hole_offset: VectorLike,
    ):
        """
        :param corner_radius: the fillet radius for the panel corners
        :param dimensions: the dimensions for the whole panel
        :param keystone_count: an (x, y) tuple indicating the number of keystones along the x and y axes
        :param keystone_grid_dimensions: the dimensions for the centered keystone grid relative to the overall panel
        :param keystone_text: the physical text label (or None, if none) to add to each keystone.  list is in column order.
        :param keystone_text_depth: the emboss depth of the keystone text labels
        :param keystone_text_size: the size of the keystone text labels in mm
        :param label: the label to give the resulting solid
        :param mount_hole_dimensions: the dimensions for the panel mount holes
        :param mount_hole_offset: the distance of the mount holes from the corners of the panel
        """
        base_keystone = KeystoneReceiver()

        # convert VectorLikes into Vectors
        if isinstance(dimensions, Iterable):
            dimensions = Vector(*dimensions)
        if isinstance(keystone_grid_dimensions, Iterable):
            keystone_grid_dimensions = Vector(*keystone_grid_dimensions)
        if isinstance(mount_hole_dimensions, Iterable):
            mount_hole_dimensions = Vector(*mount_hole_dimensions)
        if isinstance(mount_hole_offset, Iterable):
            mount_hole_offset = Vector(*mount_hole_offset)

        # calculate keystone spacing
        keystone_size = base_keystone.bounding_box().size
        keystones_size = Vector(
            keystone_size.X * keystone_count[0],
            keystone_size.Y * keystone_count[1],
        )
        keystone_spacing = Vector(
            (keystone_grid_dimensions.X - keystones_size.X) / (keystone_count[0] + 1),
            (keystone_grid_dimensions.Y - keystones_size.Y) / (keystone_count[1] + 1),
        )

        with BuildPart() as panel:
            # create panel
            with BuildSketch():
                Rectangle(dimensions.X, dimensions.Y)
            base_panel = extrude(amount=dimensions.Z)
            panel_front = base_panel.faces().sort_by(Axis.Z)[0]

            # create mount holes
            with BuildSketch(panel_front):
                with GridLocations(
                    (
                        panel_front.length
                        - (mount_hole_dimensions.X + mount_hole_offset.X)
                    ),
                    (
                        panel_front.width
                        - (mount_hole_dimensions.Y + mount_hole_offset.Y)
                    ),
                    2,
                    2,
                ):
                    SlotOverall(
                        width=mount_hole_dimensions.X, height=mount_hole_dimensions.Y
                    )
            extrude(amount=-dimensions.Z, mode=Mode.SUBTRACT)

            # create keystone labels
            with BuildSketch(panel_front) as sketch:
                grid_locations = GridLocations(
                    keystone_size.X + keystone_spacing.X,
                    keystone_size.Y + keystone_spacing.Y,
                    *keystone_count,
                )
                for index, location in enumerate(grid_locations.locations):
                    text = keystone_text[index]
                    if text is None:
                        continue
                    text_location = Location(
                        (
                            location.position.X,
                            (
                                location.position.Y
                                + ((keystone_size.Y + keystone_spacing.Y) / 2)
                            ),
                            location.position.Z,
                        )
                    )
                    with Locations(text_location):
                        Text(text, font_size=keystone_text_size)
            extrude(amount=-keystone_text_depth, mode=Mode.SUBTRACT)

            # create keystone cutouts
            with BuildSketch(panel_front):
                with GridLocations(
                    keystone_size.X + keystone_spacing.X,
                    keystone_size.Y + keystone_spacing.Y,
                    *keystone_count,
                ):
                    Rectangle(keystone_size.X, keystone_size.Y)
            cutouts = extrude(amount=-dimensions.Z, mode=Mode.SUBTRACT)

            # create joints from cutout faces
            total_keystones = keystone_count[0] * keystone_count[1]
            cutout_faces = cutouts.faces().sort_by(Axis.Z)[:total_keystones]
            for index, face in enumerate(cutout_faces):
                joint_location = Location(face.center_location.position)
                RigidJoint(f"keystone-cutout-{index}", joint_location=joint_location)

            # fillet corners
            corners = base_panel.edges().filter_by(Axis.Z)
            fillet(corners, radius=corner_radius)

        super().__init__(panel.part.wrapped, joints=panel.joints, label=label)


def create() -> Compound:
    keystone_count = (3, 3)
    panel = Panel(
        corner_radius=3.0 * MM,
        dimensions=(250.0 * MM, 100.0 * MM, 4.0 * MM),
        keystone_count=keystone_count,
        keystone_grid_dimensions=(80 * MM, 100.0 * MM),
        keystone_text=[
            "br1-1",
            "br2-2",
            "lr-2",
            "br1-2",
            None,
            "o-1",
            "br2-1",
            "lr-1",
            "o-2",
        ],
        keystone_text_depth=1.0 * MM,
        keystone_text_size=4.0 * MM,
        mount_hole_dimensions=Vector(12.0 * MM, 8.0 * MM),
        mount_hole_offset=Vector(1.0 * MM, 3.0 * MM),
        label="panel",
    )

    # keystones
    base_keystone = KeystoneReceiver()
    keystones: list[KeystoneReceiver] = []
    for _ in range(0, keystone_count[0] * keystone_count[1]):
        keystone = copy(base_keystone)
        keystone.label = f"keystone-{len(keystones)}"
        keystones.append(keystone)

    # connect keystones <-> panel cutouts
    for index, keystone in enumerate(keystones):
        keystone_joint: Joint = keystone.joints["keystone"]
        cutout_joint: Joint = panel.joints[f"keystone-cutout-{index}"]
        cutout_joint.connect_to(keystone_joint)

    return Compound([], children=[panel, *keystones])


if __name__ == "__main__":
    ocp_vscode.show_object(create())
