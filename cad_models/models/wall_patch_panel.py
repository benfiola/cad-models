from collections.abc import Iterable
from copy import copy

import ocp_vscode
from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    FontStyle,
    GridLocations,
    Location,
    Locations,
    Mode,
    Rectangle,
    RigidJoint,
    SlotOverall,
    Solid,
    SortBy,
    Text,
    Vector,
    VectorLike,
    add,
    extrude,
    fillet,
)

from cad_models.common import RackMountNut, RackMountScrew, WallScrew
from cad_models.models.keystone_receiver import KeystoneReceiver
from cad_models.models.wall_patch_panel_bracket import WallPatchPanelBracket


class Panel(Solid):
    def __init__(
        self,
        *,
        corner_radius: float,
        dimensions: VectorLike,
        keystone_count: tuple[int, int],
        keystone_grid_dimensions: VectorLike,
        keystone_text: list[list[str | None]],
        keystone_text_depth: float,
        keystone_text_size: float,
        keystone_text_style: FontStyle,
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
        :param keystone_text_style: the style of the keystone text labels
        :param label: the label to give the resulting solid
        :param mount_hole_dimensions: the dimensions for the panel mount holes
        :param mount_hole_offset: the distance of the mount holes from the corners of the panel
        """
        base_keystone = KeystoneReceiver()

        if isinstance(dimensions, Iterable):
            dimensions = Vector(*dimensions)
        if isinstance(keystone_grid_dimensions, Iterable):
            keystone_grid_dimensions = Vector(*keystone_grid_dimensions)
        if isinstance(mount_hole_dimensions, Iterable):
            mount_hole_dimensions = Vector(*mount_hole_dimensions)
        if isinstance(mount_hole_offset, Iterable):
            mount_hole_offset = Vector(*mount_hole_offset)

        base_keystone = KeystoneReceiver()
        keystone_size = base_keystone.bounding_box().size

        with BuildPart() as builder:
            with BuildSketch():
                # create panel
                Rectangle(dimensions.X, dimensions.Y)

                # create mount holes
                offset = 2 * Vector(mount_hole_offset)
                spacing = dimensions.sub(mount_hole_dimensions.add(offset))
                spacing = spacing.to_tuple()[:2]
                with GridLocations(*spacing, 2, 2) as mount_hole_grid_locations:
                    SlotOverall(*mount_hole_dimensions.to_tuple(), mode=Mode.SUBTRACT)

                # create keystone cutouts
                min_grid_size = Vector(keystone_size)
                min_grid_size.X *= keystone_count[0]
                min_grid_size.Y *= keystone_count[1]
                extra_space = keystone_grid_dimensions.sub(min_grid_size)
                extra_space.X /= keystone_count[0]
                extra_space.Y /= keystone_count[1]
                spacing = keystone_size.add(extra_space).to_tuple()[:2]
                # NOTE: .01 is subtracted to remove seam between attached component and cutout
                size = keystone_size.sub((0.01, 0.01, 0.0))
                with GridLocations(
                    *spacing, *keystone_count
                ) as keystone_grid_locations:
                    Rectangle(size.X, size.Y, mode=Mode.SUBTRACT)

            extrude(amount=dimensions.Z)

            def col_order(loc: Location):
                pos = loc.to_tuple()
                return pos

            def row_order(location: Location):
                pos = location.position.to_tuple()
                return -pos[1], pos[0]

            # create mount hole joint
            locations = list(sorted(mount_hole_grid_locations.locations, key=col_order))
            locations = zip(locations[0::2], locations[1::2])
            for index, (top, bottom) in enumerate(locations):
                top.position += (0.0, 0.0, dimensions.Z)
                bottom.position += (0.0, 0.0, dimensions.Z)
                top.orientation += (180.0, 0.0, 0.0)
                bottom.orientation += (180.0, 0.0, 0.0)
                RigidJoint(f"mount-hole-{index}-top", joint_location=top)
                RigidJoint(f"mount-hole-{index}-bottom", joint_location=bottom)

            keystones: list[KeystoneReceiver] = []
            for index, location in enumerate(
                sorted(keystone_grid_locations, key=row_order)
            ):
                # create keystone cutout joint
                x = int(index / keystone_count[1])
                y = index % keystone_count[1]
                cutout_joint = RigidJoint(
                    f"keystone-cutout-{x}-{y}", joint_location=location
                )

                # create keystone
                keystone = copy(base_keystone)
                keystone.label = f"keystone-{x}-{y}"
                keystones.append(keystone)

                # attach keystone to joint
                keystone_joint: RigidJoint = keystone.joints["keystone"]
                cutout_joint.connect_to(keystone_joint)
                add(keystone)

            # create labels
            front = builder.faces().sort_by(SortBy.AREA)[-2:].sort_by(Axis.Y)[0]
            with BuildSketch(front) as sketch:
                for x, y_labels in enumerate(keystone_text):
                    for y, ks_label in enumerate(y_labels):
                        if ks_label is None:
                            continue
                        original = builder.joints[
                            f"keystone-cutout-{x}-{y}"
                        ].location.position
                        location = original.add((0, -keystone_size.Y / 2, 0))
                        with Locations(location):
                            Text(
                                ks_label,
                                font_size=keystone_text_size,
                                font_style=keystone_text_style,
                            )
            extrude(amount=-keystone_text_depth, mode=Mode.SUBTRACT)

            # fillet corners
            corners = builder.edges().filter_by(Axis.Z).sort_by(SortBy.DISTANCE)[-4:]
            fillet(corners, radius=corner_radius)

        super().__init__(builder.part.wrapped, joints=builder.joints, label=label)


class Model(Compound):
    def __init__(self):
        panel = Panel(
            corner_radius=3.0 * MM,
            dimensions=(250.0 * MM, 90.0 * MM, 4.0 * MM),
            keystone_count=(3, 3),
            keystone_grid_dimensions=(60.0 * MM, 82.0 * MM),
            keystone_text=[
                ["br1-1", "br1-2", "br2-1"],
                ["br2-2", None, "lr-1"],
                ["lr-2", "o-1", "o-2"],
            ],
            keystone_text_depth=0.5 * MM,
            keystone_text_size=5.0 * MM,
            keystone_text_style=FontStyle.BOLD,
            mount_hole_dimensions=(12.0 * MM, 6.0 * MM),
            mount_hole_offset=(3.0 * MM, 3.0 * MM),
            label="panel",
        )

        brackets = []
        for index in range(0, 2):
            bracket = WallPatchPanelBracket(
                bracket_screw=WallScrew(),
                dimensions=(18.0 * MM, 90.0 * MM, 10.0 * MM),
                label=f"bracket-{index}",
                mount_arm_dimensions=(18.0 * MM, 12.0 * MM, 90.0 * MM),
                mount_nut=RackMountNut(),
                mount_nut_offset=4.0 * MM,
                mount_screw=RackMountScrew(),
            )
            for pos in ["bottom", "top"]:
                bracket_joint = bracket.joints[f"mount-{pos}"]
                panel_joint = panel.joints[f"mount-hole-{index}-{pos}"]
                panel_joint.connect_to(bracket_joint)
            brackets.append(bracket)

        super().__init__(
            [],
            children=[panel, *brackets],
            label=f"wall-patch-panel",
        )


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
