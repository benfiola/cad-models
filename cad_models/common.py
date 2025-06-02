import math
from typing import Any, Iterable, Literal

import ocp_vscode
from bd_warehouse.fastener import (
    ClearanceHole,
    HexNut,
    Nut,
    PanHeadScrew,
    Screw,
    SquareNut,
)
from build123d import (
    IN,
    MM,
    Align,
    Axis,
    BasePartObject,
    BuildLine,
    BuildPart,
    BuildSketch,
    Compound,
    Face,
    GridLocations,
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
    RigidJoint,
    Rot,
    RotationLike,
    SlotOverall,
    Solid,
    Triangle,
    Vector,
    VectorLike,
    extrude,
    fillet,
    make_face,
    mirror,
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


class ServerRackMountBracket(BasePartObject):
    def __init__(
        self,
        dimensions: VectorLike,
        ribs: bool = True,
        interface_holes: VectorLike | None = None,
        external: bool = False,
        flipped_joints: bool = False,
        **kwargs,
    ):
        dimensions = Vector(dimensions)
        if interface_holes is not None:
            interface_holes = Vector(interface_holes)

        corner_radius = 3 * MM
        ear_dimensions = Vector(16.25 * MM, 0, 0)
        if external:
            ear_dimensions.X = 26.5 * MM
        ear_extra_space = 1.5 * MM
        ear_hole_dimensions = Vector(12 * MM, 6 * MM)
        ear_hole_offset = 3.125 * MM
        if external:
            ear_hole_offset = 3 * MM
        ear_hole_spacing = dimensions.Y - (0.5 * IN)
        with BuildPart(mode=Mode.PRIVATE):
            interface_nut = ServerRackInterfaceNut()
        interface_thickness = 6 * MM
        thickness = 4 * MM

        interior_dimensions = Vector(
            dimensions.X - (ear_dimensions.X + interface_thickness),
            dimensions.Y,
            dimensions.Z - thickness,
        )

        with BuildPart() as builder:
            # create bracket profile (via top-down view)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    d = dimensions
                    ed = ear_dimensions
                    ees = ear_extra_space
                    id = interior_dimensions
                    it = interface_thickness
                    t = thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, t),
                        (ed.X + id.X, t),
                        (ed.X + id.X, d.Z),
                        (ed.X + id.X + it, d.Z),
                        (ed.X + id.X + it, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=dimensions.Y)

            # gather edges to fillet
            fillet_edges = builder.part.edges().filter_by(Axis.Y).sort_by(Axis.X)[:2]

            # create mount holes
            face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(face) as sketch:
                location = Location((face.length / 2, 0))
                location *= Pos(X=-ear_hole_offset)
                location *= Pos(X=-ear_hole_dimensions.X / 2)
                with Locations(location) as loc:
                    with GridLocations(0, ear_hole_spacing, 1, 2) as grid_locs:
                        SlotOverall(ear_hole_dimensions.X, ear_hole_dimensions.Y)
                        mount_hole_locations = grid_locs.locations
            extrude(amount=-thickness, mode=Mode.SUBTRACT)
            mount_hole_locations = sorted(mount_hole_locations, key=col_major())
            for mount_hole_index, mount_hole_location in enumerate(
                mount_hole_locations
            ):
                location = Location(mount_hole_location)
                location *= Pos(Z=-thickness)
                if not external:
                    location *= Rot(Z=180)
                RigidJoint(f"server-rack-{mount_hole_index}", joint_location=location)

            # create interface holes
            if interface_holes:
                face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
                with BuildSketch(face, mode=Mode.PRIVATE):
                    width = face.length
                    height = face.width - 2 * thickness
                    x_spacing = width / int(interface_holes.X)
                    y_spacing = height / int(interface_holes.Y)
                    with GridLocations(
                        x_spacing,
                        y_spacing,
                        int(interface_holes.X),
                        int(interface_holes.Y),
                    ) as grid_locs:
                        hole_locations = grid_locs.locations
                hole_locations = sorted(
                    hole_locations, key=row_major(x_dir=(0, 1, 0), y_dir=(0, 0, -1))
                )
                for hole_index, hole_location in enumerate(hole_locations):
                    with Locations(hole_location):
                        ClearanceHole(
                            interface_nut, depth=interface_thickness, captive_nut=True
                        )
                    location = Location(hole_location)
                    location *= Pos(Z=-interface_thickness)
                    location *= Rot(X=180, Z=180)
                    if flipped_joints:
                        location *= Rot(X=180)
                    RigidJoint(f"interface-{hole_index}", joint_location=location)

            # create ribs
            rib_width = interior_dimensions.X - ear_extra_space
            if rib_width > 0 and ribs:
                face = builder.faces().filter_by(Axis.Z).sort_by(Axis.Z)[0]
                edge = face.edges().filter_by(Axis.X).sort_by(Axis.Y)[-2]
                location = Location(edge.position_at(1.0))
                location.orientation = face.center_location.orientation
                with BuildSketch(location):
                    Triangle(
                        c=interior_dimensions.Z,
                        a=rib_width,
                        B=90,
                        align=(Align.MIN, Align.MIN),
                    )
                rib = extrude(amount=-thickness)
                mirror_plane = face.offset(-interior_dimensions.Y / 2)
                mirror(rib, Plane(mirror_plane))

            # fillet edges
            fillet(fillet_edges, corner_radius)

        super().__init__(builder.part, **kwargs)


class ServerRackMountBlank(BasePartObject):
    def __init__(
        self,
        dimensions: VectorLike,
        interface_holes: VectorLike | None = None,
        interface_hole_captive_nut: bool = False,
        **kwargs,
    ):
        dimensions = Vector(dimensions)
        if interface_holes is not None:
            interface_holes = Vector(interface_holes)

        with BuildPart(mode=Mode.PRIVATE):
            interface_nut = ServerRackInterfaceNut()
            interface_screw = ServerRackInterfaceScrew()

        interface_thickness = 6 * MM
        thickness = 4 * MM

        interior_dimensions = Vector(
            dimensions.X - (interface_thickness + interface_thickness),
            dimensions.Y,
            dimensions.Z - thickness,
        )

        with BuildPart() as builder:
            # create bracket profile (via top-down view)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    d = dimensions
                    id = interior_dimensions
                    it = interface_thickness
                    t = thickness

                    points = centered_point_list(
                        (0, 0),
                        (0, d.Z),
                        (it, d.Z),
                        (it, t),
                        (it + id.X, t),
                        (it + id.X, d.Z),
                        (d.X, d.Z),
                        (d.X, 0),
                        (0, 0),
                    )
                    Polyline(*points)
                make_face()
            extrude(amount=dimensions.Y)

            # create interface holes
            if interface_holes:
                face = builder.part.faces().filter_by(Axis.X).sort_by(Axis.X)[1]
                with BuildSketch(face, mode=Mode.PRIVATE):
                    width = face.length
                    height = face.width - 2 * thickness
                    x_spacing = width / int(interface_holes.X)
                    y_spacing = height / int(interface_holes.Y)
                    with GridLocations(
                        x_spacing,
                        y_spacing,
                        int(interface_holes.X),
                        int(interface_holes.Y),
                    ) as grid_locs:
                        hole_locations = grid_locs.locations
                hole_locations = sorted(
                    hole_locations, key=row_major(x_dir=(0, 1, 0), y_dir=(0, 0, -1))
                )
                mirror_plane = Plane(face.offset(interior_dimensions.X / 2))
                for hole_index, hole_location in enumerate(hole_locations):
                    with Locations(hole_location):
                        if interface_hole_captive_nut:
                            hole = ClearanceHole(
                                interface_nut,
                                captive_nut=True,
                                depth=interface_thickness,
                            )
                        else:
                            hole = ClearanceHole(
                                interface_screw,
                                depth=interface_thickness,
                            )
                    mirror(hole, mirror_plane, mode=Mode.SUBTRACT)
                    location = Location(hole_location)
                    location *= Pos(Z=-interface_thickness)
                    RigidJoint(f"interface-0-{hole_index}", joint_location=location)
                    location *= Pos(Z=dimensions.X)
                    RigidJoint(f"interface-1-{hole_index}", joint_location=location)

        super().__init__(builder.part, **kwargs)


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
