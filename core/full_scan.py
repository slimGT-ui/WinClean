from core.scanner import (
    get_temp_path,
    scan_directory,
    find_large_files,
    get_recycle_bin_size,
)
from core.startup import get_startup_programs
from utils.formatting import format_size


def run_full_scan(progress_callback=None):
    def progress(percent, message):
        if progress_callback:
            progress_callback(percent, message)

    progress(0, "Starting full scan...")

    progress(10, "Scanning TEMP...")
    temp = scan_directory(get_temp_path())

    progress(30, "Checking Recycle Bin...")
    recycle_size = get_recycle_bin_size()

    progress(40, "Scanning large files on C:\\...")

    def large_file_progress(scanned_files, found_files, current_path):
        # The total number of files is unknown until the scan finishes,
        # so the GUI uses an indeterminate bar during this stage.
        if progress_callback:
            name = current_path.name if current_path else "finishing..."
            progress_callback(
                40,
                f"Scanning large files... {scanned_files:,} files checked | "
                f"{found_files:,} large files found | {name}",
            )

    large = find_large_files(
        "C:\\",
        1024 ** 3,
        progress_callback=large_file_progress,
    )

    progress(90, "Checking startup programs...")
    startup = get_startup_programs()

    progress(100, "Full scan complete.")

    reclaimable = temp["size"]
    if recycle_size is not None:
        reclaimable += recycle_size

    return {
        "temp": temp,
        "recycle_size": recycle_size,
        "large_files": large,
        "startup": startup,
        "reclaimable": reclaimable,
    }
