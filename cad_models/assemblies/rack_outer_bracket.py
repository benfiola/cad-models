import ocp_vscode
from build123d import Compound

from cad_models.solids.keystone_receiver import KeystoneReceiver


def create() -> Compound:
    return Compound([], children=[KeystoneReceiver()])


if __name__ == "__main__":
    ocp_vscode.show_object(create())
