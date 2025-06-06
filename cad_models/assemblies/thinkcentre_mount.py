from build123d import Color, Compound, RigidJoint

from cad_models.common import Assembly, main
from cad_models.models.server_rack import ServerRack
from cad_models.models.thinkcentre import Thinkcentre
from cad_models.models.thinkcentre_bracket import ThinkcentreBracket
from cad_models.models.thinkcentre_bracket_power import ThinkcentreBracketPower
from cad_models.models.thinkcentre_tray import ThinkcentreTray


class ThinkcentreMount(Assembly):
    def __init__(self):
        server_rack = ServerRack(u=3, color=Color("black", alpha=0.3))

        left_bracket = ThinkcentreBracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(bracket_joint)

        right_bracket = ThinkcentreBracketPower()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-1-{hole}"]
            bracket_joint: RigidJoint = right_bracket.joints[f"server-rack-{1-hole}"]
            rack_joint.connect_to(bracket_joint)

        tray = ThinkcentreTray()
        for hole in range(0, 6):
            tray_joint: RigidJoint = tray.joints[f"interface-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)
        for hole in range(0, 6):
            tray_joint: RigidJoint = tray.joints[f"interface-1-{hole}"]
            hole += 3
            hole %= 6
            bracket_joint: RigidJoint = right_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)

        thinkcentre = Thinkcentre(color=Color("white", alpha=0.7))
        thinkcentre_joint: RigidJoint = thinkcentre.joints["mount"]
        tray_joint: RigidJoint = tray.joints["thinkcentre"]
        tray_joint.connect_to(thinkcentre_joint)

        super().__init__(
            None, children=[server_rack, left_bracket, right_bracket, tray, thinkcentre]
        )


if __name__ == "__main__":
    main(ThinkcentreMount())
