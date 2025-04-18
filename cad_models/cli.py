from pathlib import Path

from build123d import export_stl
from click import argument, echo, group, option

from cad_models.models import import_model, list_model_names


@group()
def grp_main():
    pass


@grp_main.command("export-model")
@argument("model-name")
@option("--format")
@option("--output-file")
def cmd_export_model(model_name: str, format: str | None, output_file: str | None):
    if format is None:
        format = "stl"
    if output_file is None:
        output_file = Path.cwd().joinpath("dist", f"{model_name}.{format}")
    output_file: Path = Path(output_file)

    model = import_model(model_name)

    if not output_file.exists():
        output_file.mkdir(parents=True, exist_ok=True)

    if format == "stl":
        export_stl(model, output_file)
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
