import argparse
import copy
import pathlib
import sys
from dataclasses import dataclass
from typing import ClassVar

from build123d import (
    Align,
    Axis,
    BasePartObject,
    BuildPart,
    Compound,
    Location,
    Mode,
    Part,
    RigidJoint,
    Rotation,
    Solid,
    export_step,
    import_step,
)
from ocp_vscode.show import show_object

from cad_models.data import get_data_file


def ensure_part(part: Part | None) -> Part:
    if part is None:
        raise ValueError(f"part is none")
    return part


class KeystoneReceiver(BasePartObject):
    _applies_to = [BuildPart._tag]
    _solid: ClassVar[Solid | None] = None

    @classmethod
    def get_solid(cls) -> Solid:
        if not cls._solid:
            step_file = get_data_file("keystone-receiver.step")
            solid = import_step(step_file)
            if not isinstance(solid, Solid):
                raise TypeError(solid)
            face = solid.faces().sort_by(Axis.Z)[-1]
            joint_location = Location(face.center_location)
            RigidJoint("joint", solid, joint_location)
            cls._solid = solid
        return copy.copy(cls._solid)

    @classmethod
    def depth(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            solid = cls.get_solid()
        return solid.bounding_box().size.Y

    @classmethod
    def height(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            solid = cls.get_solid()
        return solid.bounding_box().size.Z

    @classmethod
    def width(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            solid = cls.get_solid()
        return solid.bounding_box().size.X

    def __init__(
        self,
        rotation: Rotation | tuple[float, float, float] = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
    ):
        solid = self.get_solid()
        super().__init__(solid, rotation, align, mode)


@dataclass
class Args:
    export: pathlib.Path | None
    ocp: bool = False


def main(compound: Compound):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocp", default=False, action="store_true")
    parser.add_argument("--export", default=None, type=pathlib.Path)
    args = Args(**vars(parser.parse_args(sys.argv[1:])))

    if args.ocp:
        show_object(compound)

    if args.export:
        if args.export.suffix == ".step":
            export_step(compound, args.export)
        else:
            raise ValueError(f"unknown export extension: {args.export}")

    if args.ocp:
        show_object(compound)

    if args.export:
        if args.export.suffix == ".step":
            export_step(compound, args.export)
        else:
            raise ValueError(f"unknown export extension: {args.export}")
