from build123d import Color, RigidJoint

from cad_models.common import Assembly, main
from cad_models.models.wall_slat_canvas_hanger import (
    WallSlatCanvasHanger as WallSlatCanvasHangerModel,
)
from cad_models.models.wall_slats import WallSlats


class WallSlatCanvasHanger(Assembly):
    def __init__(self):
        slats = WallSlats(color=Color("black", alpha=0.3))

        slat_joint: RigidJoint = slats.joints[f"slat-space-0"]
        left_hanger = WallSlatCanvasHangerModel()
        hanger_joint: RigidJoint = left_hanger.joints["mount"]
        slat_joint.connect_to(hanger_joint)

        slat_joint: RigidJoint = slats.joints[f"slat-space-2"]
        right_hanger = WallSlatCanvasHangerModel()
        hanger_joint: RigidJoint = right_hanger.joints["mount"]
        slat_joint.connect_to(hanger_joint)

        super().__init__(None, children=[slats, left_hanger, right_hanger])


if __name__ == "__main__":
    main(WallSlatCanvasHanger())
