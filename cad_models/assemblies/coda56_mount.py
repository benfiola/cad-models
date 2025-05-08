from build123d import Color, Compound

from cad_models.common import initialize
from cad_models.models.coda56 import Coda56
from cad_models.models.coda56_mount_bottom_bracket import Coda56MountBottomBracket
from cad_models.models.coda56_mount_top_bracket import Coda56MountTopBracket
from cad_models.models.server_rack import ServerRack


class Coda56Mount(Compound):
    def __init__(self):
        server_rack = ServerRack(color=Color("black", alpha=0.3))
        top_bracket = Coda56MountTopBracket()
        server_rack.side_mount(top_bracket, 3)
        bottom_bracket = Coda56MountBottomBracket()
        server_rack.side_mount(bottom_bracket, 6)

        coda = Coda56(color=Color("white", alpha=0.7))
        bottom_bracket.mount(coda)

        super().__init__(
            None, children=[server_rack, coda, top_bracket, bottom_bracket]
        )


if __name__ == "__main__":
    initialize(Coda56Mount())
