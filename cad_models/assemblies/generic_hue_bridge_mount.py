from build123d import Color, Compound, RigidJoint

from cad_models.common import main
from cad_models.models.generic_hue_bridge_tray import GenericHueBridgeTray
from cad_models.models.generic_mount_bracket import GenericMountBracket
from cad_models.models.hue_bridge import HueBridge
from cad_models.models.server_rack import ServerRack


class GenericHueBridgeMount(Compound):
    def __init__(self):
        server_rack = ServerRack(u=3, color=Color("black", alpha=0.3))

        left_bracket = GenericMountBracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(bracket_joint)

        left_tray = GenericHueBridgeTray()
        for hole in range(0, 4):
            bracket_joint: RigidJoint = left_bracket.joints[f"interface-{hole}"]
            tray_joint: RigidJoint = left_tray.joints[f"interface-0-{hole}"]
            bracket_joint.connect_to(tray_joint)

        left_bridge = HueBridge(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = left_bridge.joints["mount"]
        tray_joint: RigidJoint = left_tray.joints["bridge"]
        tray_joint.connect_to(bridge_joint)

        middle_tray = GenericHueBridgeTray()
        for hole in range(0, 4):
            existing_tray_joint: RigidJoint = left_tray.joints[f"interface-1-{hole}"]
            new_tray_joint: RigidJoint = middle_tray.joints[f"interface-0-{hole}"]
            existing_tray_joint.connect_to(new_tray_joint)

        middle_bridge = HueBridge(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = middle_bridge.joints["mount"]
        tray_joint: RigidJoint = middle_tray.joints["bridge"]
        tray_joint.connect_to(bridge_joint)

        right_tray = GenericHueBridgeTray()
        for hole in range(0, 4):
            existing_tray_joint: RigidJoint = middle_tray.joints[f"interface-1-{hole}"]
            new_tray_joint: RigidJoint = right_tray.joints[f"interface-0-{hole}"]
            existing_tray_joint.connect_to(new_tray_joint)

        right_bridge = HueBridge(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = right_bridge.joints["mount"]
        tray_joint: RigidJoint = right_tray.joints["bridge"]
        tray_joint.connect_to(bridge_joint)

        right_bracket = GenericMountBracket(flip=True)
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-1-1-{hole}"]
            bracket_joint: RigidJoint = right_bracket.joints[f"server-rack-{1-hole}"]
            rack_joint.connect_to(bracket_joint)

        for hole in range(0, 4):
            bracket_joint: RigidJoint = right_bracket.joints[f"interface-{hole}"]
            tray_joint: RigidJoint = right_tray.joints[f"interface-1-{hole}"]
            bracket_joint.connect_to(tray_joint)

        super().__init__(
            None,
            children=[
                server_rack,
                left_bracket,
                left_tray,
                left_bridge,
                middle_tray,
                middle_bridge,
                right_tray,
                right_bridge,
                right_bracket,
            ],
        )


if __name__ == "__main__":
    main(GenericHueBridgeMount())
