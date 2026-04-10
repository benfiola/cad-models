import argparse
import pathlib
import sys
from dataclasses import dataclass

from build123d import BuildPart, Compound, export_step
from ocp_vscode.show import show_all


def set_label(build_part: BuildPart, label: str):
    if not build_part.part:
        raise ValueError("inner part is None")
    build_part.part.label = label


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
