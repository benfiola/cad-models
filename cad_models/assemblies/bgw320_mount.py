from build123d import Color, RigidJoint

from cad_models.common import Assembly, main
from cad_models.models.bgw320 import Bgw320
from cad_models.models.bgw320_mount_bracket_bottom import Bgw320MountBracketBottom
from cad_models.models.bgw320_mount_bracket_top import Bgw320MountBracketTop
from cad_models.models.server_rack import ServerRack


class Bgw320Mount(Assembly):
    def __init__(self):
        server_rack = ServerRack(u=6, color=Color("black", alpha=0.3))

        top_bracket = Bgw320MountBracketTop()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-1-{hole}"]
            item_joint: RigidJoint = top_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(item_joint)

        bottom_bracket = Bgw320MountBracketBottom()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-4-1-{hole}"]
            item_joint: RigidJoint = bottom_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(item_joint)

        bgw = Bgw320(color=Color("white", alpha=0.7))
        for hole in range(0, 2):
            bracket_joint: RigidJoint = bottom_bracket.joints[f"bgw320-{hole}"]
            bgw_joint: RigidJoint = bgw.joints[f"mount-{hole}"]
            bracket_joint.connect_to(bgw_joint)

        super().__init__(None, children=[server_rack, bgw, top_bracket, bottom_bracket])


if __name__ == "__main__":
    main(Bgw320Mount())
