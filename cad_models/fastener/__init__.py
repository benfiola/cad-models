from typing import Literal

from bd_warehouse.fastener import Screw
from build123d import (
    IN,
    MM,
    BuildLine,
    BuildSketch,
    Face,
    Line,
    Mode,
    Plane,
    Polyline,
    RadiusArc,
    make_face,
)


class Iso:
    HeadDiameter: Literal["dk"] = "dk"
    HeadHeight: Literal["k"] = "k"
    HeadRadius: Literal["rf"] = "rf"
    SlotDepth: Literal["t"] = "t"
    SlotWidth: Literal["n"] = "n"


class ServerRackScrew(Screw):
    countersink_profile = Screw.default_countersink_profile
    fastener_data = {
        "#10-32": {
            f"asme_b_18.6.3:{Iso.HeadDiameter}": "0.456",
            f"asme_b_18.6.3:{Iso.HeadHeight}": "0.132",
            f"asme_b_18.6.3:{Iso.HeadRadius}": "0.283",
            f"asme_b_18.6.3:{Iso.SlotDepth}": "0.068",
            f"asme_b_18.6.3:{Iso.SlotWidth}": "0.070",
        }
    }
    head_recess = Screw.default_head_recess

    def __init__(self):
        super().__init__(
            size="#10-32",
            length=(5 / 8 * IN) + (1.6 * MM),
            fastener_type="asme_b_18.6.3",
            hand="right",
            simple=True,
            rotation=(0, 0, 0),
            align=None,
            mode=Mode.ADD,
        )

    def head_profile(self) -> Face:
        head_diameter = self.screw_data[Iso.HeadDiameter]
        head_height = self.screw_data[Iso.HeadHeight]
        head_radius = self.screw_data[Iso.HeadRadius]
        slot_width = self.screw_data[Iso.SlotWidth]

        with BuildSketch(Plane.XZ) as profile:
            with BuildLine():
                l1 = Polyline((0, 0), (0, head_height), (slot_width / 2, head_height))
                l2 = RadiusArc(l1 @ 1, (head_diameter / 2, 0), head_radius)
                Line(l2 @ 1, l1 @ 0)
            make_face()

        return profile.sketch.face()
