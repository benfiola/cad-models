from build123d import Color, Compound, RigidJoint

from cad_models.common import main
from cad_models.models.rb4011_bracket import RB4011Bracket
from cad_models.models.server_rack import ServerRack


class Coda56Mount(Compound):
    def __init__(self):
        server_rack = ServerRack(color=Color("black", alpha=0.3))

        left_bracket = RB4011Bracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-3-0-{hole}"]
            item_joint: RigidJoint = left_bracket.joints[f"server-rack-{hole}"]
            rack_joint.connect_to(item_joint)

        right_bracket = RB4011Bracket()
        for hole in range(0, 2):
            rack_joint: RigidJoint = server_rack.joints[f"mount-3-1-{hole}"]
            item_joint: RigidJoint = right_bracket.joints[f"server-rack-{1-hole}"]
            rack_joint.connect_to(item_joint)

        super().__init__(None, children=[server_rack, left_bracket, right_bracket])


if __name__ == "__main__":
    main(Coda56Mount())
