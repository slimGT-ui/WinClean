from pathlib import Path
import ctypes
import os


def get_temp_path():
    return Path(os.environ.get("TEMP", Path.home() / "AppData" / "Local" / "Temp"))


def scan_directory(path):
    path = Path(path)
    total_size = 0
    file_count = 0
    skipped_count = 0

    if not path.exists():
        return {"path": path, "files": 0, "size": 0, "skipped": 0}

    for item in path.rglob("*"):
        try:
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
        except (PermissionError, OSError):
            skipped_count += 1

    return {
        "path": path,
        "files": file_count,
        "size": total_size,
        "skipped": skipped_count,
    }


def find_large_files(root, minimum_size, progress_callback=None):
    root = Path(root).resolve()

    if not root.exists() or not root.is_dir():
        raise ValueError(f"Directory does not exist: {root}")

    results = []
    scanned_files = 0

    for current_root, dirs, files in os.walk(root, topdown=True):
        dirs[:] = [
            d for d in dirs
            if d not in {
                "System Volume Information",
                "$Recycle.Bin",
                "Recovery",
            }
        ]

        for filename in files:
            path = Path(current_root) / filename
            scanned_files += 1

            try:
                size = path.stat().st_size
                if size >= minimum_size:
                    results.append({"path": path, "size": size})
            except (PermissionError, OSError):
                pass

            if progress_callback and scanned_files % 100 == 0:
                progress_callback(scanned_files, len(results), path)

    results.sort(key=lambda item: item["size"], reverse=True)

    if progress_callback:
        progress_callback(scanned_files, len(results), None)

    return results


def get_recycle_bin_size():
    if os.name != "nt":
        return None

    class SHQUERYRBINFO(ctypes.Structure):
        _fields_ = [
            ("cbSize", ctypes.c_ulong),
            ("i64Size", ctypes.c_longlong),
            ("i64NumItems", ctypes.c_longlong),
        ]

    info = SHQUERYRBINFO()
    info.cbSize = ctypes.sizeof(info)

    try:
        result = ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(info))
        if result != 0:
            return None
        return info.i64Size
    except (AttributeError, OSError):
        return None
