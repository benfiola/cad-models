from importlib import import_module
from pathlib import Path
from typing import Callable

from build123d import Compound, import_step, import_stl

import cad_models.external_models as external_models
import cad_models.models as models

models_folder = Path(models.__file__).parent
external_models_folder = Path(external_models.__file__).parent


def import_external_model(file: str) -> Compound:
    path = Path(external_models_folder).joinpath(file)
    if str(path).endswith(".step"):
        model = import_step(path)
    elif str(path).endswith(".stl"):
        face = import_stl(path)
        model = Compound([], children=[face])
    else:
        raise ValueError(f"unknown file type")
    return model


CreateModelFn = Callable[[], Compound]


def import_model(model_name: str) -> Compound:
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


def list_model_names() -> list[str]:
    model_names = []
    for file in models_folder.iterdir():
        if file.name == "__init__.py":
            continue
        if file.name == "__pycache__":
            continue
        model_names.append(file.stem)
    return model_names
