from build123d import Color, Compound, RigidJoint

from cad_models.common import main
from cad_models.models.generic_bracket import GenericBracket
from cad_models.models.generic_rpi_tray import GenericRpiTray
from cad_models.models.rpi import RaspberryPi
from cad_models.models.server_rack import ServerRack


class GenericRpiMount(Compound):
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

        tray_1 = GenericRpiTray()
        for hole in range(0, 4):
            tray_joint: RigidJoint = tray_1.joints[f"interface-0-{hole}"]
            bracket_joint: RigidJoint = left_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)
        rpi_1 = RaspberryPi(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = rpi_1.joints["mount"]
        tray_joint: RigidJoint = tray_1.joints["rpi"]
        tray_joint.connect_to(bridge_joint)

        tray_3 = GenericRpiTray()
        for hole in range(0, 4):
            tray_joint: RigidJoint = tray_3.joints[f"interface-1-{hole}"]
            hole += 2
            hole %= 4
            bracket_joint: RigidJoint = right_bracket.joints[f"interface-{hole}"]
            bracket_joint.connect_to(tray_joint)
        rpi_3 = RaspberryPi(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = rpi_3.joints["mount"]
        tray_joint: RigidJoint = tray_3.joints["rpi"]
        tray_joint.connect_to(bridge_joint)

        tray_2 = GenericRpiTray()
        for hole in range(0, 4):
            existing_tray_joint: RigidJoint = tray_1.joints[f"interface-1-{hole}"]
            new_tray_joint: RigidJoint = tray_2.joints[f"interface-0-{hole}"]
            existing_tray_joint.connect_to(new_tray_joint)
        rpi_2 = RaspberryPi(color=Color("white", alpha=0.7))
        bridge_joint: RigidJoint = rpi_2.joints["mount"]
        tray_joint: RigidJoint = tray_2.joints["rpi"]
        tray_joint.connect_to(bridge_joint)

        super().__init__(
            None,
            children=[
                server_rack,
                left_bracket,
                right_bracket,
                tray_1,
                rpi_1,
                tray_2,
                rpi_2,
                tray_3,
                rpi_3,
            ],
        )


if __name__ == "__main__":
    main(GenericRpiMount())
