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
    Mode,
    Rectangle,
    RigidJoint,
    SlotOverall,
    Solid,
    SortBy,
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

        with BuildPart() as builder:
            with BuildSketch():
                # create panel
                Rectangle(dimensions.X, dimensions.Y)

                # create mount holes
                spacing = (
                    dimensions.X - (mount_hole_dimensions.X + mount_hole_offset.X),
                    dimensions.Y - (mount_hole_dimensions.Y + mount_hole_offset.Y),
                )
                with GridLocations(*spacing, 2, 2):
                    SlotOverall(*mount_hole_dimensions.to_tuple(), mode=Mode.SUBTRACT)

                # create keystone cutouts
                size = base_keystone.bounding_box().size
                min_grid_size = Vector(
                    size.X * keystone_count[0], size.Y * keystone_count[1]
                )
                extra_space = Vector(
                    (keystone_grid_dimensions.X - min_grid_size.X)
                    / (keystone_count[0] + 1),
                    (keystone_grid_dimensions.Y - min_grid_size.Y)
                    / (keystone_count[1] + 1),
                )
                spacing = (
                    size.X + extra_space.X,
                    size.Y + extra_space.Y,
                )
                with GridLocations(*spacing, *keystone_count) as keystone_locations:
                    Rectangle(size.X, size.Y, mode=Mode.SUBTRACT)
            extrude(amount=dimensions.Z)

            def row_order(location: Location):
                pos = location.position.to_tuple()
                return pos[1], pos[0]

            for index, location in enumerate(sorted(keystone_locations, key=row_order)):
                x = int(index / keystone_count[1])
                y = index % keystone_count[1]
                RigidJoint(f"keystone-cutout-{x}-{y}", joint_location=location)

            # fillet corners
            corners = builder.edges().filter_by(Axis.Z).sort_by(SortBy.DISTANCE)[-4:]
            fillet(corners, radius=corner_radius)

        super().__init__(builder.part.wrapped, joints=builder.joints, label=label)


def create() -> Compound:
    keystone_count = (3, 3)
    panel = Panel(
        corner_radius=4.0 * MM,
        dimensions=(250.0 * MM, 100.0 * MM, 4.0 * MM),
        keystone_count=keystone_count,
        keystone_grid_dimensions=(64 * MM, 100.0 * MM),
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
        keystone_text_size=5.0 * MM,
        mount_hole_dimensions=Vector(12.0 * MM, 6.0 * MM),
        mount_hole_offset=Vector(1.0 * MM, 3.0 * MM),
        label="panel",
    )

    base_keystone = KeystoneReceiver()
    keystones: list[KeystoneReceiver] = []
    for x in range(0, keystone_count[0]):
        for y in range(0, keystone_count[1]):
            # create keystone
            keystone = copy(base_keystone)
            keystone.label = f"keystone-{x}-{y}"
            keystones.append(keystone)

            # attach keystone to panel
            keystone_joint: Joint = keystone.joints["keystone"]
            cutout_joint: Joint = panel.joints[f"keystone-cutout-{x}-{y}"]
            cutout_joint.connect_to(keystone_joint)

    return Compound([], children=[panel, *keystones])


if __name__ == "__main__":
    ocp_vscode.show_object(create())
