from build123d import Compound, RigidJoint

from cad_models.common import Assembly, main
from cad_models.models.wall_patch_panel import WallPatchPanel as WallPatchPanelModel
from cad_models.models.wall_patch_panel_bracket import WallPatchPanelBracket


class WallPatchPanel(Assembly):
    def __init__(self):
        panel = WallPatchPanelModel()

        brackets = []
        for index in range(0, 2):
            bracket = WallPatchPanelBracket()
            for position in range(0, 2):
                bracket_joint: RigidJoint = bracket.joints[f"mount-{position}"]
                panel_joint: RigidJoint = panel.joints[f"mount-{index}-{position}"]
                panel_joint.connect_to(bracket_joint)
            brackets.append(bracket)

        super().__init__(None, children=[panel, *brackets])


if __name__ == "__main__":
    main(WallPatchPanel())
