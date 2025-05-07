from importlib import import_module
from pathlib import Path

from build123d import Compound

from cad_models.common import Model

models_folder = Path(__file__).parent


def import_model(model_name: str) -> Compound:
    model_name = model_name.replace("-", "_")
    module_name = f"cad_models.models.{model_name}"
    module = import_module(module_name)
    model_classes = []
    for key, value in vars(module).items():
        try:
            if not issubclass(value, Model):
                continue
        except:
            continue
        if not value.__module__ == module_name:
            continue
        model_classes.append(value)
    if not model_classes:
        raise ValueError(f"model class not found")
    if len(model_classes) > 1:
        raise ValueError("more than one model class found")
    model_class = model_classes[0]
    return model_class()


def list_model_names() -> list[str]:
    model_names = []
    for file in models_folder.iterdir():
        if file.name == "__init__.py":
            continue
        if file.name == "__pycache__":
            continue
        model_name = file.stem.replace("_", "-")
        try:
            import_model(model_name)
        except ValueError:
            continue
        model_names.append(model_name)
    return model_names
