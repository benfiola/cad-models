import argparse
import copy
import logging
import math
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


def hex_grid(width: float, height: float, radius: float, spacing: float) -> Sketch:
    with BuildSketch(mode=Mode.PRIVATE) as builder:
        actual_spacing = radius + (spacing / 2)
        count_x = int((width - radius) / (math.sqrt(3) * actual_spacing))
        count_y = int((height - radius) / (2 * actual_spacing))
        with HexLocations(actual_spacing, count_x, count_y, major_radius=False):
            RegularPolygon(radius, 6, major_radius=False)
    return builder.sketch


@dataclass
class MainArgs:
    export: pathlib.Path | None
    ocp: bool
    variant: str


TParameter = typing.TypeVar("TParameter", contravariant=True)


class BuildPartFn(typing.Protocol, typing.Generic[TParameter]):
    def __call__(self, p: TParameter) -> BuildPart: ...


def main(
    build_part_fns: BuildPartFn[TParameter] | list[BuildPartFn[TParameter]],
    variants: dict[str, TParameter] | TParameter,
):
    if not isinstance(build_part_fns, list):
        build_part_fns = [build_part_fns]
    if not isinstance(variants, dict):
        variants = {"default": variants}

    parser = argparse.ArgumentParser()
    parser.add_argument("--export", type=pathlib.Path, default=None)
    parser.add_argument("--ocp", default=False, action="store_true")
    parser.add_argument("--variant", default="default", choices=variants.keys())
    args = MainArgs(**vars(parser.parse_args()))

    parameters = variants.get(args.variant)
    if not parameters:
        raise ValueError(f"invalid variant: {args.variant}")

    parts = []
    for build_part_fn in build_part_fns:
        part = require(build_part_fn(parameters).part)
        parts.append(part)

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
