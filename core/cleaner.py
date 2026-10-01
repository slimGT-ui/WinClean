from pathlib import Path

from core.safety import is_safe_to_delete


def clean_directory(path):
    path = Path(path)

    if not is_safe_to_delete(path):
        raise ValueError("Unsafe directory. Cleaning cancelled.")

    deleted_files = 0
    deleted_size = 0
    skipped_files = 0

    for item in path.rglob("*"):
        try:
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_files += 1
                deleted_size += size
        except (PermissionError, OSError):
            skipped_files += 1

    for item in sorted(path.rglob("*"), reverse=True):
        try:
            if item.is_dir():
                item.rmdir()
        except (PermissionError, OSError):
            pass

    return {
        "deleted_files": deleted_files,
        "deleted_size": deleted_size,
        "skipped_files": skipped_files,
    }
