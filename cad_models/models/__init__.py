from importlib import import_module
from pathlib import Path

from build123d import Compound

models_folder = Path(__file__).parent


def import_model(model_name: str) -> Compound:
    module_name = model_name.replace("-", "_")
    try:
        module = import_module(f"cad_models.models.{module_name}")
    except ImportError:
        raise ValueError("model module not found")
    model_cls: type[Compound] = getattr(module, "Model", None)
    if not model_cls:
        raise ValueError("model module does not have a Model class")
    if not issubclass(model_cls, Compound):
        raise ValueError("Model class not a build123d.Compound subclass")
    return model_cls()


def list_model_names() -> list[str]:
    model_names = []
    for file in models_folder.iterdir():
        if file.name == "__init__.py":
            continue
        if file.name == "__pycache__":
            continue
        model_name = file.stem.replace("_", "-")
        model_names.append(model_name)
    return model_names
