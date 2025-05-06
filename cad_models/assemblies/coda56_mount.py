from build123d import Compound

from cad_models.common import initialize
from cad_models.models.coda56_mount_bottom_bracket import Coda56MountBottomBracket
from cad_models.models.coda56_mount_top_bracket import Coda56MountTopBracket
from cad_models.models.server_rack import ServerRack


class Coda56Mount(Compound):
    def __init__(self):
        server_rack = ServerRack()
        top_bracket = Coda56MountTopBracket()
        server_rack.side_mount(top_bracket, 3)
        bottom_bracket = Coda56MountBottomBracket()
        server_rack.side_mount(bottom_bracket, 6)
        super().__init__(None, children=[server_rack, top_bracket, bottom_bracket])


if __name__ == "__main__":
    initialize(Coda56Mount())
