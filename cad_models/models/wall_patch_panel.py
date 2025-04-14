from copy import copy

import ocp_vscode
from build123d import (
    MM,
    Axis,
    BuildPart,
    BuildSketch,
    Compound,
    GridLocations,
    Location,
    Mode,
    Rectangle,
    extrude,
)

from cad_models.utils import import_external_model


def create() -> Compound:
    panel = (250.0 * MM, 4.0 * MM, 96.0 * MM)
    keystone_num = (3, 3)
    keystone_spacing = 4.0 * MM
    keystone_receiver = import_external_model("keystone-receiver.stl")

    keystone_locations = []
    with BuildPart() as part:
        # initial panel
        with BuildSketch():
            Rectangle(panel[0], panel[1])
        panel_part = extrude(amount=panel[2])

        # keystone cutouts
        cutout_face = panel_part.faces().sort_by(Axis.Y, reverse=True)[0]
        cutout_size = keystone_receiver.bounding_box().size
        cutout_size = (cutout_size.X, cutout_size.Z)
        with BuildSketch(cutout_face):
            with GridLocations(
                cutout_size[0] + keystone_spacing,
                cutout_size[1] + keystone_spacing,
                *keystone_num
            ) as cutout_grid_locations:
                Rectangle(*cutout_size)
        result = extrude(amount=-panel[1], mode=Mode.SUBTRACT)

    # add keystones
    keystones: list[Compound] = []
    center_location = cutout_face.center_location
    for relative_location in cutout_grid_locations.locations:
        keystone: Compound = copy(keystone_receiver)
        location = Location()

        keystone.locate(location)
        keystones.append(keystone)

    return Compound([], children=[part.part, *keystones])


if __name__ == "__main__":
    ocp_vscode.show_object(create())
