from pathlib import Path

folder = Path(__file__).parent


def data_file(filename: str) -> Path:
    return folder.joinpath(filename)
