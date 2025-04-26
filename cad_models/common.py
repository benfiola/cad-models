from typing import Literal

from bd_warehouse.fastener import HexNut, PanHeadScrew, Screw
from build123d import (
    IN,
    MM,
    BuildLine,
    BuildSketch,
    Face,
    Line,
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


class WallAnchorScrew(PanHeadScrew):
    cm_size = "0.151-16"
    cm_diameter = cm_size.split("-")[0]

    countersink_profile = Screw.default_countersink_profile
    # #7 isn't listed in bd_warehouses known imperial sizes - use inches for diameter
    fastener_data = {
        f"{cm_size}": {
            f"asme_b_18.6.3:{Iso.HeadDiameter}": "0.296",
            f"asme_b_18.6.3:{Iso.HeadHeight}": "0.089",
            f"asme_b_18.6.3:{Iso.HeadRadius}": "0.049",
            f"asme_b_18.6.3:{Iso.SlotDepth}": "0.054",
            f"asme_b_18.6.3:{Iso.SlotWidth}": "0.048",
        },
    }
    clearance_hole_data = {
        cm_diameter: {"Close": 0.168 * IN, "Normal": 0.190 * IN, "Loose": 0.205 * IN}
    }

    def __init__(self, **kwargs):
        kwargs["size"] = self.cm_size
        kwargs["length"] = 1.125 * IN
        kwargs["fastener_type"] = "asme_b_18.6.3"
        super().__init__(**kwargs)


class WallAnchorNut(HexNut):
    def __init__(self):
        pass


class ServerRackScrew(Screw):
    cm_size = "#10-32"

    countersink_profile = Screw.default_countersink_profile
    fastener_data = {
        cm_size: {
            f"asme_b_18.6.3:{Iso.HeadDiameter}": "0.456",
            f"asme_b_18.6.3:{Iso.HeadHeight}": "0.132",
            f"asme_b_18.6.3:{Iso.HeadRadius}": "0.283",
            f"asme_b_18.6.3:{Iso.SlotDepth}": "0.068",
            f"asme_b_18.6.3:{Iso.SlotWidth}": "0.070",
        }
    }
    head_recess = Screw.default_head_recess

    def __init__(self, **kwargs):
        kwargs["size"] = self.cm_size
        kwargs["length"] = (5 / 8 * IN) + (1.6 * MM)
        kwargs["fastener_type"] = "asme_b_18.6.3"
        super().__init__(**kwargs)

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


class ServerRackNut(HexNut):
    cm_size = "#10-32"

    fastener_data = {
        cm_size: {
            f"asme_b_18.2.2:s": "0.375",
            f"asme_b_18.2.2:m": "0.130",
        }
    }

    def __init__(self, **kwargs):
        kwargs["size"] = self.cm_size
        kwargs["fastener_type"] = "asme_b_18.2.2"
        super().__init__(**kwargs)
