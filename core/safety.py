from pathlib import Path


def is_safe_to_delete(path):
    path = Path(path).resolve()
    temp_path = (Path.home() / "AppData" / "Local" / "Temp").resolve()

    try:
        path.relative_to(temp_path)
        return True
    except ValueError:
        return False
