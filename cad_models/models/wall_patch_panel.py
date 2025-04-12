import ocp_vscode
from build123d import Compound

from cad_models.utils import import_external_model


def create() -> Compound:
    left = import_external_model("reinforced-patch-panel-left.stl")
    return Compound([], children=[left])


if __name__ == "__main__":
    ocp_vscode.show_object(create())
