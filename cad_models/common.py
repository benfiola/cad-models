import argparse
import pathlib
import sys
from dataclasses import dataclass

from build123d import BuildPart, Compound, export_step
from ocp_vscode.show import show_all


@dataclass
class Args:
    export: pathlib.Path | None
    ocp: bool = False


def main(*parts: BuildPart):
    parser = argparse.ArgumentParser()
    parser.add_argument("--ocp", default=False, action="store_true")
    parser.add_argument("--export", default=None, type=pathlib.Path)
    args = Args(**vars(parser.parse_args(sys.argv[1:])))

    if args.ocp:
        show_all()
    if args.export:
        shape = Compound(parts)
        if args.export.suffix == ".step":
            export_step(shape, args.export)
        else:
            raise ValueError(f"unknown export extension: {args.export}")
