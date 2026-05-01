import argparse
import copy
import logging
import pathlib
import typing
from dataclasses import dataclass
from typing import ClassVar

from build123d import *
from ocp_vscode.show import show_object

from cad_models.data import get_data_file

logger = logging.getLogger("build123d")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

U = 1.75 * IN


SomeObj = typing.TypeVar("SomeObj")


def require(obj: SomeObj | None) -> SomeObj:
    if not obj:
        raise ValueError("obj is None")
    return obj


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
            cls._solid = solid
        return copy.copy(cls._solid)

    @classmethod
    def depth(cls) -> float:
        return cls.get_solid().bounding_box().size.Y

    @classmethod
    def height(cls) -> float:
        return cls.get_solid().bounding_box().size.Z

    @classmethod
    def width(cls) -> float:
        return cls.get_solid().bounding_box().size.X

    def __init__(
        self,
        rotation: RotationLike | tuple[float, float, float] = (0, 0, 0),
        align: Align | tuple[Align, Align, Align] | None = (
            Align.CENTER,
            Align.CENTER,
            Align.CENTER,
        ),
        mode: Mode = Mode.ADD,
    ):
        solid = self.get_solid()
        super().__init__(solid, rotation, align, mode)
        face = solid.faces().filter_by(Axis.Y).sort_by(Axis.Y)[0]
        joint_location = Location(face.location_at(0.5, 0.5).position, (0, 0, 0))
        RigidJoint("joint", self, joint_location)


@dataclass
class MainArgs:
    export: pathlib.Path | None
    ocp: bool


def main(*build_parts: BuildPart):
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", type=pathlib.Path, default=None)
    parser.add_argument("--ocp", default=False, action="store_true")
    args = MainArgs(**vars(parser.parse_args()))

    parts = [require(bp.part) for bp in build_parts]
    packed = pack(parts, 5 * MM, align_z=True)

    if args.ocp:
        show_object(packed)

    if args.export:
        extension = args.export.suffix
        if extension == ".step":
            compound = Compound(children=[*packed])
            export_step(compound, args.export)
        elif extension == ".3mf":
            mesher = Mesher()
            mesher.add_shape(packed)
            mesher.write(args.export)
        else:
            raise ValueError(f"invalid export file extension: {extension}")
