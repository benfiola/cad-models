from build123d import export_stl
from click import argument, echo, group

from cad_models.assemblies import import_assembly, list_assembly_names


@group()
def grp_main():
    pass


@grp_main.command("export-assembly")
@argument("assembly-name")
@argument("output")
def cmd_export_assembly(assembly_name: str, output: str):
    assembly = import_assembly(assembly_name)
    export_stl(assembly, output)


@grp_main.command("list-assemblies")
def cmd_list_assemblies():
    for assembly_name in sorted(list_assembly_names()):
        echo(assembly_name)


def main():
    grp_main()


if __name__ == "__main__":
    main()
