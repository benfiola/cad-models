import math
from typing import Any, Iterable, Literal

import ocp_vscode
from bd_warehouse.fastener import HexNut, Nut, PanHeadScrew, Screw, SquareNut
from build123d import (
    IN,
    MM,
    BasePartObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    Compound,
    Face,
    Line,
    Location,
    Locations,
    Mode,
    Part,
    Plane,
    Polyline,
    Pos,
    RadiusArc,
    Rectangle,
    RotationLike,
    Solid,
    Vector,
    VectorLike,
    extrude,
    make_face,
)

U = 1.75 * IN


class Model(Solid):
    """
    Sold is subclassed to:

    * Streamline kwargs processing
    * Help identify user-created models in the project (- useful for building a CLI)
    """

    def __init__(self, item: Solid | Part, **kwargs):
        kwargs["obj"] = item.wrapped
        kwargs["joints"] = item.joints
        super().__init__(**kwargs)


class Iso:
    """
    Constants that help define the various ISO measurement parameters
    """

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


class ServerRackMountScrew(Screw):
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


class ServerRackMountNut(HexNut):
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


class ServerRackInterfaceScrew(PanHeadScrew):
    """
    Screw used to secure the various parts of a rack-mounted assembly.
    """

    def __init__(self, **kwargs):
        kwargs["size"] = "M5-0.8"
        kwargs.setdefault("length", 8 * MM)
        super().__init__(**kwargs)


class ServerRackInterfaceNut(HexNut):
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


class CaptiveNutSlot(BasePartObject):
    """
    Creates a captive nut slot intended to be used in conjuction with a ClearanceHole.
    """

    def __init__(
        self,
        nut: Nut,
        fit: Literal["Close"] | Literal["Normal"] | Literal["Loose"] = "Normal",
        mode: Mode = Mode.SUBTRACT,
        rotation: RotationLike = (0, 0, 0),
        width: float | None = None,
    ):
        locations = Locations._get_context()
        if not locations:
            raise ValueError("not in Locations context")
        build_part = BuildPart._get_context()
        if not build_part:
            raise ValueError("not in BuildPart context")

        clearance = nut.clearance_hole_diameters[fit] - nut.thread_diameter
        if isinstance(nut, HexNut):
            height = nut.nut_diameter * math.sin(math.pi / 3) + clearance
            min_width = nut.nut_diameter + clearance
        elif isinstance(nut, SquareNut):
            height = nut.nut_diameter * math.sqrt(2) / 2 + clearance
            min_width = height + clearance
        else:
            raise NotImplementedError(type(nut))
        if width is None:
            width = build_part.max_dimension

        with BuildPart(mode=Mode.PRIVATE) as builder:
            with BuildSketch():
                location = Location((0, 0))
                location *= Pos(X=-(width - min_width) / 2)
                with Locations(location):
                    Rectangle(width, height)
            extrude(amount=nut.nut_thickness)
        part = builder.part

        super().__init__(
            part,
            mode=mode,
            rotation=rotation,
        )


def row_major(x_dir: VectorLike | None = None, y_dir: VectorLike | None = None):
    """
    A function used as the 'key' kwarg to a sort function that sorts locations in row major order.

    Accepts a VectorLike indicating the x direction and y direction
    For locations:
    A B
    C D

    Will return:
    A B C D
    """
    if x_dir is None:
        x_dir = (1, 0, 0)
    if y_dir is None:
        y_dir = (0, 1, 0)
    x_dir = Vector(*x_dir)
    y_dir = Vector(*y_dir)

    def inner(a: Location):
        pos = a.position
        x = pos.dot(x_dir)
        y = pos.dot(y_dir)
        return y, x

    return inner


def col_major(x_dir: VectorLike | None = None, y_dir: VectorLike | None = None):
    """
    A function used as the 'key' kwarg to a sort function that sorts locations in col major order.

    Accepts a VectorLike indicating the x direction and y direction
    For locations:
    A B
    C D

    Will return:
    A B C D
    """
    if x_dir is None:
        x_dir = (1, 0, 0)
    if y_dir is None:
        y_dir = (0, 1, 0)
    x_dir = Vector(*x_dir)
    y_dir = Vector(*y_dir)

    def inner(a: Location):
        pos = a.position
        x = pos.dot(x_dir)
        y = pos.dot(y_dir)
        return x, y

    return inner


def centered_point_list(*points: tuple[float, float]) -> Iterable[tuple[float, float]]:
    """
    Takes a list of points used to construct a Polyline and centers them.

    This allows you to construct Polyline shapes oriented arbitrarily around the origin (for easy construction),
    and center them in a second pass via this method.
    """
    min_x = math.inf
    min_y = math.inf
    max_x = -math.inf
    max_y = -math.inf
    for x, y in points:
        max_x = max(x, max_x)
        max_y = max(y, max_y)
        min_x = min(x, min_x)
        min_y = min(y, min_y)
    offset_x = (max_x - min_x) / 2
    offset_y = (max_y - min_y) / 2
    to_return = []
    for point in points:
        to_return.append((point[0] - offset_x, point[1] - offset_y))
    return to_return


def main(model: Solid | Compound):
    """
    Used as the entrypoint for build123d scripts.

    Often is invoked at the bottom of a user-created module
    """
    ocp_vscode.set_defaults(reset_camera=ocp_vscode.Camera.KEEP)
    ocp_vscode.show(model)
