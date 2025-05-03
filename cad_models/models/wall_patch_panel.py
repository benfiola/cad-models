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
    Location,
    Locations,
    Mode,
    Plane,
    Pos,
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

from cad_models.common import (
    GridLocations,
    RackMountNut,
    RackMountScrew,
    WallScrew,
    col_major,
    row_major,
    to_planar_locations,
)
from cad_models.models.keystone_receiver import KeystoneReceiver
from cad_models.models.wall_patch_panel_bracket import WallPatchPanelBracket


class Panel(Solid):
    def __init__(
        self,
        *,
        corner_radius: float | None,
        keystone_count: tuple[int, int],
        keystone_grid_dimensions: VectorLike,
        keystone_text: list[list[str | None]],
        keystone_text_depth: float,
        keystone_text_size: float,
        keystone_text_style: FontStyle,
        label: str = "",
        mount_hole_dimensions: VectorLike,
        mount_hole_offset: VectorLike,
        panel_dimensions: VectorLike,
    ):
        """
        :param corner_radius: the fillet radius for the panel corners
        :param keystone_count: an (x, y) tuple indicating the number of keystones along the x and y axes
        :param keystone_grid_dimensions: the dimensions for the centered keystone grid relative to the overall panel
        :param keystone_text: the physical text label (or None, if none) to add to each keystone.  list is in column order.
        :param keystone_text_depth: the emboss depth of the keystone text labels
        :param keystone_text_size: the size of the keystone text labels in mm
        :param keystone_text_style: the style of the keystone text labels
        :param label: the label to give the resulting solid
        :param mount_hole_dimensions: the dimensions for the panel mount holes
        :param mount_hole_offset: the distance of the mount holes from the corners of the panel
        :param panel_dimensions: the dimensions for the whole panel
        """
        if isinstance(keystone_grid_dimensions, Iterable):
            keystone_grid_dimensions = Vector(*keystone_grid_dimensions)
        if isinstance(mount_hole_dimensions, Iterable):
            mount_hole_dimensions = Vector(*mount_hole_dimensions)
        if isinstance(mount_hole_offset, Iterable):
            mount_hole_offset = Vector(*mount_hole_offset)
        if isinstance(panel_dimensions, Iterable):
            panel_dimensions = Vector(*panel_dimensions)

        with BuildPart(mode=Mode.PRIVATE):
            base_keystone = KeystoneReceiver()
            keystone_size = base_keystone.kr_dimensions

        with BuildPart() as builder:
            with BuildSketch(Plane.XZ):
                # create panel
                rectangle = Rectangle(panel_dimensions.X, panel_dimensions.Y)

                # create mount holes
                spacing = Vector(rectangle.width, rectangle.rectangle_height)
                spacing -= mount_hole_offset * 2
                spacing -= mount_hole_dimensions
                with GridLocations(
                    spacing.X, spacing.Y, 2, 2
                ) as mount_hole_grid_location:
                    SlotOverall(
                        mount_hole_dimensions.X,
                        mount_hole_dimensions.Y,
                        mode=Mode.SUBTRACT,
                    )

                # create keystone cutouts
                spacing = keystone_grid_dimensions
                with GridLocations.area_grid(
                    area=keystone_grid_dimensions,
                    grid=keystone_count,
                    item=keystone_size,
                ) as keystone_grid_location:
                    Rectangle(keystone_size.X, keystone_size.Y, mode=Mode.SUBTRACT)
            panel = extrude(amount=panel_dimensions.Z)
            front_face = panel.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]

            keystone_grid_locations = sorted(
                keystone_grid_location.locations, key=row_major
            )
            keystone_locations = to_planar_locations(
                Plane(front_face), keystone_grid_locations
            )
            keystones: list[KeystoneReceiver] = []
            for index, keystone_location in enumerate(keystone_locations):
                x = int(index / keystone_count[1])
                y = index % keystone_count[1]

                # create cutout joint
                location = Location(keystone_location.position)
                cutout_joint = RigidJoint(f"keystone-{x}-{y}", joint_location=location)

                # create keystone
                keystone = copy(base_keystone)
                keystone.label = f"keystone-{x}-{y}"
                keystones.append(keystone)
                keystone_joint: RigidJoint = keystone.joints["keystone"]

                # attach keystone to cutout
                cutout_joint.connect_to(keystone_joint)
                add(keystone)

            front_face = builder.faces().sort_by(SortBy.AREA)[-2:].sort_by(Axis.Y)[0]
            with BuildSketch(front_face) as sketch:
                for index, keystone_location in enumerate(keystone_grid_locations):
                    x = int(index / keystone_count[1])
                    y = index % keystone_count[1]

                    # create keystone label
                    ks_label = keystone_text[x][y]
                    if ks_label is None:
                        continue
                    location = Location(keystone_location)
                    location *= Pos(Y=keystone.kr_dimensions.Y / 2)
                    with Locations(location):
                        Text(
                            ks_label,
                            font_size=keystone_text_size,
                            font_style=keystone_text_style,
                        )
            extrude(amount=-keystone_text_depth, mode=Mode.SUBTRACT)

            mount_hole_locations = to_planar_locations(
                Plane(front_face),
                sorted(mount_hole_grid_location.locations, key=col_major),
            )
            mount_hole_locations = zip(
                mount_hole_locations[::2], mount_hole_locations[1::2]
            )
            for index, (top, bottom) in enumerate(mount_hole_locations):
                # create mount joint
                RigidJoint(f"mount-{index}-top", joint_location=top)
                RigidJoint(f"mount-{index}-bottom", joint_location=bottom)

            # fillet corners
            corners = builder.edges().filter_by(Axis.Y).sort_by(SortBy.DISTANCE)[-4:]
            fillet(corners, radius=corner_radius)

        super().__init__(builder.part.wrapped, joints=builder.joints, label=label)


class Model(Compound):
    def __init__(self):
        panel = Panel(
            corner_radius=3.0 * MM,
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
            panel_dimensions=(250.0 * MM, 90.0 * MM, 4.0 * MM),
            label="panel",
        )

        brackets = []
        for index in range(0, 2):
            bracket = WallPatchPanelBracket(
                bracket_screw=WallScrew(),
                dimensions=(18.0 * MM, 90.0 * MM, 10.0 * MM),
                label=f"bracket-{index}",
                mount_arm_profile=(90.0 * MM, 12.0 * MM),
                mount_nut=RackMountNut(),
                mount_nut_offset=4.0 * MM,
                mount_screw=RackMountScrew(),
            )
            for pos in ["bottom", "top"]:
                bracket_joint: RigidJoint = bracket.joints[f"mount-{pos}"]
                panel_joint: RigidJoint = panel.joints[f"mount-{index}-{pos}"]
                panel_joint.connect_to(bracket_joint)
            brackets.append(bracket)

        super().__init__(
            [],
            children=[panel, *brackets],
            label=f"wall-patch-panel",
        )


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
