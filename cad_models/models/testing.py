import ocp_vscode
from build123d import Compound

from cad_models.fastener import ServerRackScrew, WallAnchorScrew


class Model(Compound):
    def __init__(self):
        fit = "Loose"
        screw = WallAnchorScrew()
        profile = screw.countersink_profile(fit)
        screw_2 = ServerRackScrew()
        profile_2 = screw_2.countersink_profile(fit)
        super().__init__([], children=[screw])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
