from pathlib import Path

from build123d import export_step, export_stl
from click import argument, echo, group, option

from cad_models.models import import_model, list_model_names


@group()
def grp_main():
    pass


@grp_main.command("export-model")
@argument("model-name")
@option("--format")
@option("--output-file", type=Path)
def cmd_export_model(model_name: str, format: str | None, output_file: Path | None):
    if format is None:
        format = "step"
    if output_file is None:
        output_file = Path.cwd().joinpath("dist", f"{model_name}.{format}")
    output_file = Path(output_file)

    model = import_model(model_name)

    if not output_file.exists():
        output_file.parent.mkdir(parents=True, exist_ok=True)
    if output_file.exists():
        output_file.unlink()

    if format == "stl":
        export_stl(model, output_file)
    elif format == "step":
        export_step(model, output_file)
    else:
        raise ValueError(f"unknown format: {format}")


@grp_main.command("list-models")
def cmd_list_models():
    for model_name in sorted(list_model_names()):
        echo(model_name)


def main():
    grp_main()


if __name__ == "__main__":
    main()
