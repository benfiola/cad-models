from collections.abc import Iterable

import ocp_vscode
from bd_warehouse.fastener import ClearanceHole, CounterSunkScrew, Screw
from build123d import (
    MM,
    Align,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Compound,
    Locations,
    Mode,
    Plane,
    Polyline,
    Pos,
    Rectangle,
    SlotOverall,
    Solid,
    Vector,
    VectorLike,
    extrude,
    fillet,
    make_face,
    mirror,
)

from cad_models.common import centered_point_list


class RouterScrew(CounterSunkScrew):
    def __init__(self, **kwargs):
        super().__init__(
            size="M2.5-0.45", length=6 * MM, fastener_type="iso7046", **kwargs
        )


class Coda56MountBottomBracket(Solid):
    def __init__(
        self,
        *,
        corner_radius: float,
        ear_dimensions: VectorLike,
        label: str = "",
        mount_hole_dimensions: VectorLike,
        mount_hole_offset: VectorLike,
        stand_dimensions: VectorLike,
        stand_inset: float,
        stand_screw: Screw,
        stand_standoff_dimensions: VectorLike,
    ):
        if isinstance(ear_dimensions, Iterable):
            ear_dimensions = Vector(*ear_dimensions)
        if isinstance(mount_hole_dimensions, Iterable):
            mount_hole_dimensions = Vector(*mount_hole_dimensions)
        if isinstance(mount_hole_offset, Iterable):
            mount_hole_offset = Vector(*mount_hole_offset)
        if isinstance(stand_dimensions, Iterable):
            stand_dimensions = Vector(*stand_dimensions)
        if isinstance(stand_standoff_dimensions, Iterable):
            stand_standoff_dimensions = Vector(*stand_standoff_dimensions)

        with BuildPart() as builder:
            with BuildSketch(Plane.XY):
                # create the arm
                with BuildLine():
                    ed = ear_dimensions
                    sd = stand_dimensions
                    si = stand_inset

                    Polyline(
                        centered_point_list(
                            (0, 0),
                            (0, ed.Z + si + sd.Y),
                            (ed.Z, ed.Z + si + sd.Y),
                            (ed.Z, ed.Z),
                            (ed.Z + ed.X, ed.Z),
                            (ed.Z + ed.X, 0),
                            (0, 0),
                        )
                    )
                make_face()
            bracket = extrude(amount=ear_dimensions.Y)

            # find corners for final fillet
            corners = bracket.edges().filter_by(
                lambda shape: shape.length == ear_dimensions.Z
            )

            arm_face = bracket.faces().filter_by(Axis.X).sort_by(Axis.X)[0]
            with BuildSketch(arm_face):
                # create the stand
                location = Vector(arm_face.length, arm_face.width) / 2
                with Locations(location):
                    Rectangle(
                        stand_dimensions.Y,
                        stand_dimensions.Z,
                        align=(Align.MAX, Align.MAX),
                    )
            stand = extrude(amount=stand_dimensions.X)

            top_stand_face = stand.faces().filter_by(Axis.Z).sort_by(Axis.Z)[-1]
            with BuildSketch(top_stand_face) as sketch:
                # create the standoffs
                location = Vector(top_stand_face.length, 0) / 2
                with Locations(location):
                    standoff = Rectangle(
                        stand_standoff_dimensions.Y,
                        stand_standoff_dimensions.X,
                        align=(Align.MAX, Align.CENTER),
                    )
                mirror(standoff, Plane.YZ)
            standoff = extrude(amount=-stand_standoff_dimensions.Z, mode=Mode.SUBTRACT)

            standoff_faces = standoff.faces().filter_by(Axis.Z).sort_by(Axis.Z)[:2]
            for standoff_face in standoff_faces:
                # create the standoff clearance holes
                offset = stand_dimensions.Z - stand_standoff_dimensions.Z
                location = standoff_face.location_at(0.5, 0.5)
                location *= Pos(Z=offset)
                with Locations(location):
                    ClearanceHole(stand_screw, depth=stand_screw.length)

            ear_face = builder.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
            with BuildSketch(ear_face):
                # create mount holes
                location = Vector(-ear_face.length, -ear_face.width) / 2
                location += mount_hole_offset

                with Locations(location):
                    slot = SlotOverall(
                        mount_hole_dimensions.X,
                        mount_hole_dimensions.Y,
                        align=(Align.MIN, Align.MIN),
                    )
                mirror(slot, Plane.XZ)
            extrude(amount=-ear_dimensions.Z, mode=Mode.SUBTRACT)

            # fillet corners
            fillet(corners, radius=corner_radius)

        super().__init__(builder.part.wrapped, joints=builder.joints, label=label)


class Model(Compound):
    def __init__(self):
        # coda56 router dimensions: (170.942, 170.942, 51.562)
        bracket = Coda56MountBottomBracket(
            corner_radius=3.0 * MM,
            ear_dimensions=(25.0 * MM, 41.35 * MM, 6.0 * MM),
            mount_hole_dimensions=(12.0 * MM, 6.0 * MM),
            mount_hole_offset=(3.0 * MM, 3.0 * MM),
            stand_dimensions=(52 * MM, 152 * MM, 12.0 * MM),
            stand_inset=(50 * MM),
            stand_screw=RouterScrew(),
            stand_standoff_dimensions=(9.0 * MM, 18.4 * MM, 9.2 * MM),
        )
        return super().__init__([], children=[bracket])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
