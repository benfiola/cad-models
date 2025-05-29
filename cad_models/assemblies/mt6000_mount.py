from build123d import Color, Compound, RigidJoint

from cad_models.common import main
from cad_models.models.mt6000 import MT6000
from cad_models.models.mt6000_mount import MT6000MountBracket
from cad_models.models.server_rack import ServerRack


class MT6000Mount(Compound):
    def __init__(self):
        server_rack = ServerRack(u=3, color=Color("black", alpha=0.3))

        bracket = MT6000MountBracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-1-{hole}"]
            bracket_joint: RigidJoint = bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(bracket_joint)

        mt6000 = MT6000(color=Color("white", alpha=0.7))
        for hole in range(0, 2):
            bracket_joint: RigidJoint = bracket.joints[f"mt6000-{hole}"]
            mt6000_joint: RigidJoint = mt6000.joints[f"mount-{hole}"]
            bracket_joint.connect_to(mt6000_joint)

        super().__init__(None, children=[server_rack, bracket, mt6000])


if __name__ == "__main__":
    main(MT6000Mount())
