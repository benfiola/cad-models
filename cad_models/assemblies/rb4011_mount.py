from build123d import Color, Compound, RigidJoint

from cad_models.common import main
from cad_models.models.rb4011 import RB4011
from cad_models.models.rb4011_bracket import RB4011Bracket
from cad_models.models.rb4011_tray import RB4011Tray
from cad_models.models.server_rack import ServerRack


class Coda56Mount(Compound):
    def __init__(self):
        server_rack = ServerRack(u=3, color=Color("black", alpha=0.3))

        left_bracket = RB4011Bracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(bracket_joint)

        right_bracket = RB4011Bracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-1-{hole}"]
            bracket_joint: RigidJoint = right_bracket.joints[f"server-rack-{1-hole}"]
            rack_joint.connect_to(bracket_joint)

        tray = RB4011Tray()
        for hole in range(0, 8):
            tray_joint: RigidJoint = tray.joints[f"interface-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)
        for hole in range(0, 8):
            tray_joint: RigidJoint = tray.joints[f"interface-1-{hole}"]
            hole += 4
            hole %= 8
            bracket_joint: RigidJoint = right_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)

        router = RB4011(color=Color("white", alpha=0.7))
        router_joint: RigidJoint = router.joints["mount"]
        tray_joint: RigidJoint = tray.joints["router"]
        tray_joint.connect_to(router_joint)

        super().__init__(
            None, children=[server_rack, left_bracket, right_bracket, tray, router]
        )


if __name__ == "__main__":
    main(Coda56Mount())
