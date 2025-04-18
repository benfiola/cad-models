import ocp_vscode
from build123d import Compound


class Model(Compound):
    def __init__(self):
        super().__init__([], children=[])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
