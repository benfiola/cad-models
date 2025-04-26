import ocp_vscode
from bd_warehouse.fastener import ClearanceHole
from build123d import (
    BuildPart,
    BuildSketch,
    Compound,
    Location,
    Locations,
    Rectangle,
    Solid,
    extrude,
)

from cad_models.common import ServerRackNut, ServerRackScrew, WallAnchorScrew


class Part(Solid):
    def __init__(self):
        srs = ServerRackScrew()
        srn = ServerRackNut()
        was = WallAnchorScrew()
        fit = "Close"

        with BuildPart() as builder:
            with BuildSketch():
                Rectangle(50.0, 15.0)
            extrude(amount=20.0)
            with Locations(Location((-10.0, 0.0, 20.0))):
                ClearanceHole(srs, fit)
            with Locations(Location((-10.0, 0.0, srn.nut_thickness))) as l:
                ClearanceHole(srn, fit, captive_nut=True)
            with Locations(Location((5.0, 0.0, 20.0))):
                ClearanceHole(was, fit)
        super().__init__(builder.part.wrapped)


class Model(Compound):
    def __init__(self):
        super().__init__([], children=[Part()])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
