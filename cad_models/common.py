import argparse
import copy
import pathlib
import sys
from dataclasses import dataclass
from typing import ClassVar

from build123d import (
    Align,
    BasePartObject,
    BuildPart,
    Compound,
    Location,
    Mode,
    Part,
    Rot,
    RotationLike,
    Solid,
    export_step,
    import_step,
)
from build123d.topology.utils import tuplify
from ocp_vscode.show import show_object

from cad_models.data import get_data_file


def get_part(build_part: BuildPart) -> Part:
    if build_part.part is None:
        raise ValueError("part is None")
    return build_part.part


def set_label(build_part: BuildPart, label: str):
    if not build_part.part:
        raise ValueError("inner part is None")
    build_part.part.label = label


class KeystoneReceiver(BasePartObject):
    _base_solid: ClassVar[Solid | None] = None
    _applies_to = [BuildPart._tag]

    @classmethod
    def get_solid(cls) -> Solid:
        if not cls._base_solid:
            step_file = get_data_file("keystone-receiver.step")
            imported = import_step(step_file)
            if not isinstance(imported, Solid):
                raise TypeError(imported)
            center = Location(imported.bounding_box().center())
            imported.relocate(center)
            imported.location *= Rot(X=270)
            cls._base_solid = imported
        solid = copy.copy(cls._base_solid)
        return solid

    @classmethod
    def height(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            solid = cls.get_solid()
        return solid.bounding_box().size.Y

    @classmethod
    def width(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            solid = cls.get_solid()
        return solid.bounding_box().size.X

    @classmethod
    def depth(cls) -> float:
        with BuildPart(mode=Mode.PRIVATE):
            solid = cls.get_solid()
        return solid.bounding_box().size.Z

    def __init__(
        self,
        rotation: RotationLike = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
    ):
        solid = self.get_solid()
        super().__init__(
            part=solid, rotation=rotation, align=tuplify(align, 3), mode=mode
        )
        print("here")


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
