import math
from typing import Any, Literal

from bd_warehouse.fastener import HexNut, Nut, PanHeadScrew, Screw
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
    Vector,
    make_face,
)


class Iso:
    HeadDiameter: Literal["dk"] = "dk"
    HeadHeight: Literal["k"] = "k"
    HeadRadius: Literal["rf"] = "rf"
    NutWidth: Literal["s"] = "s"
    NutHeight: Literal["m"] = "m"
    SlotDepth: Literal["t"] = "t"
    SlotWidth: Literal["n"] = "n"


class WallScrew(PanHeadScrew):
    """
    Screw used in conjunction with wall anchors to secure an assembly to the wall.
    """

    cm_size = "0.151-16"
    cm_diameter = cm_size.split("-")[0]

    countersink_profile = Screw.default_countersink_profile
    # #7 isn't listed in bd_warehouses known imperial sizes - use inches for diameter
    fastener_data = {
        f"{cm_size}": {
            f"custom:{Iso.HeadDiameter}": "0.311",
            f"custom:{Iso.HeadHeight}": "0.089",
            f"custom:{Iso.HeadRadius}": "0.049",
            f"custom:{Iso.SlotDepth}": "0.054",
            f"custom:{Iso.SlotWidth}": "0.048",
        },
    }
    clearance_hole_data = {
        cm_diameter: {"Close": 0.168 * IN, "Normal": 0.190 * IN, "Loose": 0.205 * IN}
    }

    def __init__(self, **kwargs):
        kwargs["size"] = self.cm_size
        kwargs["length"] = 1.125 * IN
        kwargs["fastener_type"] = "custom"
        super().__init__(**kwargs)


class RackMountScrew(Screw):
    """
    Screw used to secure a rack-mounted assembly to the rack mount itself
    """

    cm_size = "#10-32"

    countersink_profile = Screw.default_countersink_profile
    fastener_data: Any = {
        cm_size: {
            f"custom:{Iso.HeadDiameter}": "0.456",
            f"custom:{Iso.HeadHeight}": "0.132",
            f"custom:{Iso.HeadRadius}": "0.283",
            f"custom:{Iso.SlotDepth}": "0.068",
            f"custom:{Iso.SlotWidth}": "0.070",
        }
    }
    head_recess = Screw.default_head_recess

    def __init__(self, **kwargs):
        kwargs["size"] = self.cm_size
        kwargs["length"] = (5 / 8 * IN) + (1.6 * MM)
        kwargs["fastener_type"] = "custom"
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


class RackMountNut(HexNut):
    """
    Nut used to secure a rack-mounted assembly to the rack mount itself
    """

    cm_size = "#10-32"

    fastener_data = {
        cm_size: {
            f"custom:{Iso.NutWidth}": "0.375",
            f"custom:{Iso.NutHeight}": "0.130",
        }
    }

    def __init__(self, **kwargs):
        kwargs["size"] = self.cm_size
        kwargs["fastener_type"] = "custom"
        super().__init__(**kwargs)


class RackInterfaceScrew(PanHeadScrew):
    """
    Screw used to secure the various parts of a rack-mounted assembly.
    """

    def __init__(self, **kwargs):
        kwargs["size"] = "M5-0.8"
        kwargs.setdefault("length", 8 * MM)
        super().__init__(**kwargs)


class RackInterfaceNut(HexNut):
    """
    Nut used to secure the various parts of a rack-mounted assembly.
    """

    cm_size = "M5-0.8"

    fastener_data = {
        cm_size: {f"custom:{Iso.NutHeight}": "3.900", f"custom:{Iso.NutWidth}": "8.000"}
    }

    def __init__(self, **kwargs):
        kwargs["size"] = "M5-0.8"
        kwargs["fastener_type"] = "custom"
        super().__init__(**kwargs)


def captive_nut_slot_dimensions(
    nut: Nut, fit: Literal["Close"] | Literal["Normal"] | Literal["Loose"] = "Normal"
) -> Vector:
    """
    Snippet taken from bd_warehouse.fasteners._make_fastener_hole.

    Calculates and returns the width and height of a captive nut slot - which is effectively the width and height of a nut's clearance hole.
    """
    clearance = nut.clearance_hole_diameters[fit] - nut.thread_diameter
    if isinstance(nut, HexNut):
        rect_width = nut.nut_diameter + clearance
        rect_height = nut.nut_diameter * math.sin(math.pi / 3) + clearance
    return Vector(X=rect_width, Y=rect_height)
