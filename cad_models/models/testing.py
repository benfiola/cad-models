import ocp_vscode
from build123d import Compound

from cad_models.fastener import ServerRackScrew


class Model(Compound):
    def __init__(self):
        super().__init__([], children=[ServerRackScrew()])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
