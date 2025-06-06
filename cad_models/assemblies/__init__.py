from importlib import import_module
from pathlib import Path

from build123d import Compound

from cad_models.common import Assembly

assemblies_folder = Path(__file__).parent


def import_assembly(model_name: str) -> Compound:
    model_name = model_name.replace("-", "_")
    module_name = f"cad_models.assembly.{model_name}"
    module = import_module(module_name)
    assembly_classes = []
    for key, value in vars(module).items():
        try:
            if not issubclass(value, Assembly):
                continue
        except:
            continue
        if not value.__module__ == module_name:
            continue
        assembly_classes.append(value)
    if not assembly_classes:
        raise ValueError(f"assembly class not found")
    if len(assembly_classes) > 1:
        raise ValueError("more than one assembly class found")
    assembly_class = assembly_classes[0]
    return assembly_class()


def list_assembly_names() -> list[str]:
    assembly_names = []
    for file in assemblies_folder.iterdir():
        if file.name == "__init__.py":
            continue
        if file.name == "__pycache__":
            continue
        assembly_name = file.stem.replace("_", "-")
        try:
            import_assembly(assembly_name)
        except ValueError:
            continue
        assembly_names.append(assembly_name)
    return assembly_names
