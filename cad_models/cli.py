from build123d import export_stl
from click import argument, echo, group

from cad_models.models import import_model, list_model_names


@group()
def grp_main():
    pass


@grp_main.command("export-model")
@argument("model-name")
@argument("output")
def cmd_export_model(model_name: str, output: str):
    model = import_model(model_name)
    export_stl(model, output)


@grp_main.command("list-models")
def cmd_list_models():
    for model_name in sorted(list_model_names()):
        echo(model_name)


def main():
    grp_main()


if __name__ == "__main__":
    main()
