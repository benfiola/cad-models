import ocp_vscode
from build123d import Compound


def create() -> Compound:
    return Compound([], children=[])


if __name__ == "__main__":
    ocp_vscode.show_object(create())
