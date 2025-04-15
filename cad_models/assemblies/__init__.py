from importlib import import_module
from pathlib import Path
from typing import Callable

from build123d import Compound

assemblies_folder = Path(__file__).parent


CreateModelFn = Callable[[], Compound]


def import_assembly(model_name: str) -> Compound:
    try:
        module = import_module(f"cad_models.models.{model_name}")
    except ImportError:
        raise ValueError("model module not found")
    create_model: CreateModelFn | None = getattr(module, "create", None)
    if not create_model:
        raise ValueError("model module does not have a create function")
    model = create_model()
    if not isinstance(model, Compound):
        raise ValueError("model create function does not return a build123d.BuildPart")
    return model


def list_assembly_names() -> list[str]:
    model_names = []
    for file in assemblies_folder.iterdir():
        if file.name == "__init__.py":
            continue
        if file.name == "__pycache__":
            continue
        model_names.append(file.stem)
    return model_names
