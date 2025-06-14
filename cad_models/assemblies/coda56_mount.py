from build123d import Color, RigidJoint

from cad_models.common import Assembly, main
from cad_models.models.coda56 import Coda56
from cad_models.models.coda56_mount_bracket_bottom import Coda56MountBracketBottom
from cad_models.models.coda56_mount_bracket_top import Coda56MountBracketTop
from cad_models.models.server_rack import ServerRack


class Coda56Mount(Assembly):

    def __init__(self):
        server_rack = ServerRack(u=6, color=Color("black", alpha=0.3))

        top_bracket = Coda56MountBracketTop()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-1-{hole}"]
            item_joint: RigidJoint = top_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(item_joint)

        bottom_bracket = Coda56MountBracketBottom()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-4-1-{hole}"]
            item_joint: RigidJoint = bottom_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(item_joint)

        coda = Coda56(color=Color("white", alpha=0.7))
        for hole in range(0, 2):
            bracket_joint: RigidJoint = bottom_bracket.joints[f"coda56-{hole}"]
            coda_joint: RigidJoint = coda.joints[f"mount-{hole}"]
            bracket_joint.connect_to(coda_joint)

        super().__init__(
            None, children=[server_rack, coda, top_bracket, bottom_bracket]
        )


if __name__ == "__main__":
    main(Coda56Mount())
