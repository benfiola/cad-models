from build123d import Color, Compound

from cad_models.common import initialize
from cad_models.models.mt6000_mount_top_bracket import MT6000MountTopBracket
from cad_models.models.mt6000_mount_bottom_bracket import MT6000MountBottomBracket
from cad_models.models.server_rack import ServerRack


class MT6000Mount(Compound):
    def __init__(self):
        server_rack = ServerRack(color=Color("black", alpha=0.3))
        top_bracket = MT6000MountTopBracket()
        server_rack.side_mount(top_bracket, 3)
        bottom_bracket = MT6000MountBottomBracket()
        server_rack.side_mount(bottom_bracket, 5)
        super().__init__(None, children=[server_rack, top_bracket, bottom_bracket])


if __name__ == "__main__":
    initialize(MT6000Mount())
