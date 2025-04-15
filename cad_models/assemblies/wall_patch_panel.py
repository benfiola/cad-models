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
    Plane,
    Rectangle,
    RigidJoint,
    Solid,
    Vector,
    VectorLike,
    extrude,
)

from cad_models.compounds.keystone_receiver import KeystoneReceiver


class Panel(Solid):
    def __init__(
        self,
        *,
        dimensions: VectorLike,
        edge_chamfer: float,
        keystone_count: tuple[int, int],
        keystone_spacing: VectorLike,
        mount_dimensions: VectorLike,
        mount_spacing: VectorLike,
        label: str = "",
    ):
        base_keystone = KeystoneReceiver()

        # convert VectorLikes into Vectors
        if isinstance(dimensions, Iterable):
            dimensions = Vector(*dimensions)
        if isinstance(keystone_spacing, Iterable):
            keystone_spacing = Vector(*keystone_spacing)
        if isinstance(mount_dimensions, Iterable):
            mount_dimensions = Vector(*mount_dimensions)
        if isinstance(mount_spacing, Iterable):
            mount_spacing = Vector(*mount_spacing)

        # validate keystone grid will fit panel dimensions
        keystone_size = base_keystone.bounding_box().size
        min_x = (
            (keystone_size.X + keystone_spacing.X) * keystone_count[0]
        ) + keystone_spacing.X
        min_y = (
            (keystone_size.Y + keystone_spacing.Y) * keystone_count[1]
        ) + keystone_spacing.Y
        if min_x > dimensions.X or min_y > dimensions.Y:
            raise ValueError(
                f"panel cannot fit {keystone_count} keystones with {keystone_spacing} spacing"
            )

        with BuildPart() as panel:
            # create panel
            with BuildSketch():
                Rectangle(dimensions.X, dimensions.Y)
            base_panel = extrude(amount=dimensions.Z)

            # chamfer panel edges

            # create keystone cutouts
            panel_front = Plane(panel.faces().sort_by(Axis.Z)[0])
            cutout_dimensions = base_keystone.bounding_box().size
            with BuildSketch(panel_front):
                with GridLocations(
                    cutout_dimensions.X + keystone_spacing.X,
                    cutout_dimensions.Y + keystone_spacing.Y,
                    *keystone_count,
                ):
                    Rectangle(cutout_dimensions.X, cutout_dimensions.Y)
            cutouts = extrude(amount=-dimensions.Z, mode=Mode.SUBTRACT)

            # create joints from cutout faces
            total_keystones = keystone_count[0] * keystone_count[1]
            cutout_faces = cutouts.faces().sort_by(Axis.Z)[:total_keystones]
            for index, face in enumerate(cutout_faces):
                joint_location = Location(face.center_location.position)
                RigidJoint(f"keystone-cutout-{index}", joint_location=joint_location)

        super().__init__(panel.part.wrapped, joints=panel.joints, label=label)


def create() -> Compound:
    keystone_count = (3, 3)
    panel = Panel(
        edge_chamfer=3.0 * MM,
        dimensions=(250.0 * MM, 96.0 * MM, 4.0 * MM),
        keystone_count=keystone_count,
        keystone_spacing=Vector(4.0 * MM, 4.0 * MM, 0.0 * MM),
        mount_dimensions=Vector(6.0 * MM, 4.0 * MM, 0.0 * MM),
        mount_spacing=Vector(1.0 * MM, 2.0 * MM, 0.0 * MM),
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
