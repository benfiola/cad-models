from build123d import Color, Compound

from cad_models.common import initialize
from cad_models.models.mt6000 import MT6000
from cad_models.models.mt6000_mount import MT6000MountTopBracket
from cad_models.models.server_rack import ServerRack


class MT6000Mount(Compound):
    def __init__(self):
        server_rack = ServerRack(color=Color("black", alpha=0.3))
        bracket = MT6000MountTopBracket()
        server_rack.side_mount(bracket, 3)

        mt6000 = MT6000(color=Color("white", alpha=0.7))
        bracket.mount(mt6000)

        super().__init__(None, children=[server_rack, bracket])


if __name__ == "__main__":
    initialize(MT6000Mount())
