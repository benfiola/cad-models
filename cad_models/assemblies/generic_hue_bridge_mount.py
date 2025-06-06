from build123d import Color, RigidJoint

from cad_models.common import Assembly, main
from cad_models.models.generic_bracket import GenericBracket
from cad_models.models.generic_hue_bridge_tray import GenericHueBridgeTray
from cad_models.models.hue_bridge import HueBridge
from cad_models.models.server_rack import ServerRack


class GenericHueBridgeMount(Assembly):
    def __init__(self):
        server_rack = ServerRack(u=3, color=Color("black", alpha=0.3))

        left_bracket = GenericBracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(bracket_joint)

        right_bracket = GenericBracket(flipped_joints=True)
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-1-{hole}"]
            bracket_joint: RigidJoint = right_bracket.joints[f"server-rack-{1-hole}"]
            rack_joint.connect_to(bracket_joint)

        tray_1 = GenericHueBridgeTray()
        for hole in range(0, 4):
            tray_joint: RigidJoint = tray_1.joints[f"interface-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)
        bridge_1 = HueBridge(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = bridge_1.joints["mount"]
        tray_joint: RigidJoint = tray_1.joints["hue-bridge"]
        tray_joint.connect_to(bridge_joint)

        tray_3 = GenericHueBridgeTray()
        for hole in range(0, 4):
            tray_joint: RigidJoint = tray_3.joints[f"interface-1-{hole}"]
            hole += 2
            hole %= 4
            bracket_joint: RigidJoint = right_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)
        bridge_3 = HueBridge(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = bridge_3.joints["mount"]
        tray_joint: RigidJoint = tray_3.joints["hue-bridge"]
        tray_joint.connect_to(bridge_joint)

        tray_2 = GenericHueBridgeTray()
        for hole in range(0, 4):
            existing_tray_joint: RigidJoint = tray_1.joints[f"interface-1-{hole}"]
            new_tray_joint: RigidJoint = tray_2.joints[f"interface-0-{hole}"]
            existing_tray_joint.connect_to(new_tray_joint)
        bridge_2 = HueBridge(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = bridge_2.joints["mount"]
        tray_joint: RigidJoint = tray_2.joints["hue-bridge"]
        tray_joint.connect_to(bridge_joint)

        super().__init__(
            None,
            children=[
                server_rack,
                left_bracket,
                right_bracket,
                tray_1,
                bridge_1,
                tray_2,
                bridge_2,
                tray_3,
                bridge_3,
            ],
        )


if __name__ == "__main__":
    main(GenericHueBridgeMount())
