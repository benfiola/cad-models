import argparse
import copy
import pathlib
import sys
from dataclasses import dataclass

from build123d import (
    Align,
    BasePartObject,
    BuildPart,
    Compound,
    Mode,
    RotationLike,
    Solid,
    export_step,
    import_step,
)
from build123d.topology.utils import tuplify
from ocp_vscode.show import show_all

from cad_models.data import get_data_file


def set_label(build_part: BuildPart, label: str):
    if not build_part.part:
        raise ValueError("inner part is None")
    build_part.part.label = label


class KeystoneReceiver(BasePartObject):
    _base_solid: Solid | None = None
    _applies_to = [BuildPart._tag]

    @classmethod
    def get_solid(cls) -> Solid:
        if not cls._base_solid:
            step_file = get_data_file("keystone-receiver.step")
            imported = import_step(step_file)
            if not isinstance(imported, Solid):
                raise TypeError(imported)
            cls._base_solid = imported
        solid = copy.copy(cls._base_solid)
        return solid

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


@dataclass
class Args:
    export: pathlib.Path | None
    ocp: bool = False


def main(*build_parts: BuildPart):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocp", default=False, action="store_true")
    parser.add_argument("--export", default=None, type=pathlib.Path)
    args = Args(**vars(parser.parse_args(sys.argv[1:])))

    if args.ocp:
        variables = {}
        for build_part in build_parts:
            if not build_part.part:
                continue
            variables[build_part.part.label] = build_part
        show_all(variables=variables)

    if args.export:
        shape = Compound(build_parts)
        if args.export.suffix == ".step":
            export_step(shape, args.export)
        else:
            raise ValueError(f"unknown export extension: {args.export}")

    if args.export:
        shape = Compound(build_parts)
        if args.export.suffix == ".step":
            export_step(shape, args.export)
        else:
            raise ValueError(f"unknown export extension: {args.export}")
