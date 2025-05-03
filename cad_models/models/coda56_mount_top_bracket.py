from collections.abc import Iterable

import ocp_vscode
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


class Coda56MountTopBracket(Solid):
    def __init__(
        self,
        *,
        arm_dimensions: VectorLike,
        arm_hook_length: VectorLike,
        arm_inset: float,
        corner_radius: float,
        ear_dimensions: VectorLike,
        label: str = "",
        mount_hole_dimensions: VectorLike,
        mount_hole_offset: VectorLike,
    ):
        if isinstance(arm_dimensions, Iterable):
            arm_dimensions = Vector(*arm_dimensions)
        if isinstance(ear_dimensions, Iterable):
            ear_dimensions = Vector(*ear_dimensions)
        if isinstance(mount_hole_dimensions, Iterable):
            mount_hole_dimensions = Vector(*mount_hole_dimensions)
        if isinstance(mount_hole_offset, Iterable):
            mount_hole_offset = Vector(*mount_hole_offset)

        with BuildPart() as builder:
            # create the bracket
            with BuildSketch(Plane.XY):
                # produce a top-down sketch of the bracket
                with BuildLine():
                    ad = arm_dimensions
                    ed = ear_dimensions
                    ahl = arm_hook_length
                    ai = arm_inset

                    Polyline(
                        centered_point_list(
                            (0, (ed.Z + ad.Y + ad.Z) - ahl),
                            (0, ed.Z + ad.Y + ad.Z),
                            (ad.Z + ad.X + ad.Z, ed.Z + ad.Y + ad.Z),
                            (ad.Z + ad.X + ad.Z, ed.Z),
                            (ad.Z + ad.X + ad.Z + ed.X, ed.Z),
                            (ad.Z + ad.X + ad.Z + ed.X, 0),
                            (ad.Z + ad.X, 0),
                            (ad.Z + ad.X, ai),
                            (0, ai),
                            (0, ai + ahl + ad.Z),
                            (ad.Z, ai + ahl + ad.Z),
                            (ad.Z, ai + ad.Z),
                            (ad.Z + ad.X, ai + ad.Z),
                            (ad.Z + ad.X, ed.Z + ad.Y),
                            (ad.Z, ed.Z + ad.Y),
                            (ad.Z, (ed.Z + ad.Y + ad.Z) - ahl),
                            (0, (ed.Z + ad.Y + ad.Z) - ahl),
                        )
                    )
                make_face()
            bracket = extrude(amount=ear_dimensions.Y)

            # find corners for final fillet
            corners = bracket.edges().filter_by(
                lambda shape: shape.length == ear_dimensions.Z
            )

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
        bracket = Coda56MountTopBracket(
            arm_dimensions=(52 * MM, (171.5 + 50.0) * MM, 6.0 * MM),
            arm_hook_length=(25.0 * MM),
            arm_inset=(50 * MM),
            corner_radius=3.0 * MM,
            ear_dimensions=(25.0 * MM, 41.35 * MM, 6.0 * MM),
            mount_hole_dimensions=(12.0 * MM, 6.0 * MM),
            mount_hole_offset=(3.0 * MM, 3.0 * MM),
        )
        return super().__init__([], children=[bracket])


if __name__ == "__main__":
    ocp_vscode.show_object(Model())
