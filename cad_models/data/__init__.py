import pathlib

folder = pathlib.Path(__file__).parent


def get_data_file(filename: str) -> pathlib.Path:
    data_file = folder.joinpath(filename)
    if not data_file.exists():
        raise FileNotFoundError(data_file)
    return data_file
