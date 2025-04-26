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

from cad_models.common import (
    RackInterfaceNut,
    RackInterfaceScrew,
    RackMountNut,
    RackMountScrew,
    WallScrew,
)


class Part(Solid):
    def __init__(self):
        rms = RackMountScrew()
        rmn = RackMountNut()
        ws = WallScrew()
        ris = RackInterfaceScrew()
        rin = RackInterfaceNut()
        fit = "Close"

        with BuildPart() as builder:
            with BuildSketch():
                Rectangle(50.0, 15.0)
            extrude(amount=20.0)
            with Locations(Location((-15.0, 0.0, 20.0))):
                ClearanceHole(rms, fit)
            with Locations(Location((-15.0, 0.0, rmn.nut_thickness))) as l:
                ClearanceHole(rmn, fit, captive_nut=True)
            with Locations(Location((0.0, 0.0, 20.0))):
                ClearanceHole(ws, fit)
            with Locations(Location((15.0, 0.0, 20.0))):
                ClearanceHole(ris, fit)
            with Locations(Location((15.0, 0.0, rin.nut_thickness))):
                ClearanceHole(rin, fit, captive_nut=True)
        super().__init__(builder.part.wrapped)


class Model(Compound):
    def __init__(self):
        super().__init__([], children=[Part()])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
