from core.scanner import get_temp_path, scan_directory, find_large_files, get_recycle_bin_size
from core.cleaner import clean_directory
from core.recycle_bin import empty_recycle_bin
from core.startup import get_startup_programs
from core.full_scan import run_full_scan
from utils.formatting import format_size
from utils.logger import setup_logger

logger = setup_logger()


def show_menu():
    print()
    print("=" * 40)
    print("              WinClean")
    print("=" * 40)
    print()
    print("[1] Analyze TEMP")
    print("[2] Clean TEMP")
    print("[3] Empty Recycle Bin")
    print("[4] Find Large Files")
    print("[5] Startup Programs")
    print("[6] Full Scan")
    print("[0] Exit")
    print()


def analyze_temp():
    temp_path = get_temp_path()
    print("\nScanning TEMP...")
    result = scan_directory(temp_path)

    print()
    print("TEMP Scan")
    print("-" * 40)
    print(f"Path:     {result['path']}")
    print(f"Files:    {result['files']}")
    print(f"Size:     {format_size(result['size'])}")
    print(f"Skipped:  {result['skipped']}")


def clean_temp():
    temp_path = get_temp_path()
    result = scan_directory(temp_path)

    print()
    print("TEMP Cleaner")
    print("-" * 40)
    print(f"Files found: {result['files']}")
    print(f"Size:        {format_size(result['size'])}")
    print()

    if result["files"] == 0:
        print("Nothing to clean.")
        return

    confirm = input("Delete these files? [Y/N]: ").strip().lower()
    if confirm != "y":
        print("Cleaning cancelled.")
        return

    print("\nCleaning TEMP...")

    try:
        result = clean_directory(temp_path)
    except ValueError as error:
        print(f"\nError: {error}")
        logger.error("TEMP cleaning blocked: %s", error)
        return

    print("\nCleaning complete!")
    print(f"Deleted: {result['deleted_files']} files")
    print(f"Freed:   {format_size(result['deleted_size'])}")
    print(f"Skipped: {result['skipped_files']} files")


def clean_recycle_bin():
    size = get_recycle_bin_size()

    print()
    print("Recycle Bin")
    print("-" * 40)

    if size is not None:
        print(f"Size: {format_size(size)}")
    else:
        print("Size: unavailable")

    print()
    print("This will permanently delete all files")
    print("currently stored in the Recycle Bin.")
    print()

    confirm = input("Empty Recycle Bin? [Y/N]: ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    print("\nEmptying Recycle Bin...")

    if empty_recycle_bin():
        print("Recycle Bin emptied successfully.")
    else:
        print("Failed to empty Recycle Bin.")


def large_files():
    drive = input("\nDrive to scan [C:\\]: ").strip() or "C:\\"
    minimum = input("Minimum size [1GB]: ").strip() or "1GB"

    try:
        minimum_bytes = parse_size(minimum)
    except ValueError:
        print("Invalid size. Examples: 500MB, 1GB, 5GB")
        return

    print(f"\nScanning {drive} for files >= {format_size(minimum_bytes)}...")
    print("This may take a while.\n")

    try:
        results = find_large_files(drive, minimum_bytes)
    except ValueError as error:
        print(f"Error: {error}")
        return

    if not results:
        print("No matching files found.")
        return

    print(f"Found {len(results)} files:")
    print("-" * 70)

    for index, item in enumerate(results[:50], start=1):
        print(f"{index:>2}. {format_size(item['size']):>10}  {item['path']}")

    if len(results) > 50:
        print(f"\nShowing first 50 of {len(results)} files.")


def parse_size(value):
    value = value.strip().upper()

    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }

    for unit, multiplier in units.items():
        if value.endswith(unit):
            number = value[:-len(unit)].strip()
            return int(float(number) * multiplier)

    return int(value)


def startup_programs():
    programs = get_startup_programs()

    print()
    print("Startup Programs")
    print("-" * 80)

    if not programs:
        print("No startup entries found.")
        return

    for program in programs:
        print(f"Name:     {program['name']}")
        print(f"Command:  {program['command']}")
        print(f"Location: {program['location']}")
        print("-" * 80)


def main():
    logger.info("WinClean started")

    while True:
        show_menu()
        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                analyze_temp()
            elif choice == "2":
                clean_temp()
            elif choice == "3":
                clean_recycle_bin()
            elif choice == "4":
                large_files()
            elif choice == "5":
                startup_programs()
            elif choice == "6":
                run_full_scan()
            elif choice == "0":
                logger.info("WinClean exited")
                print("\nExiting WinClean...")
                break
            else:
                print("\nUnknown option. Try again.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            logger.info("Operation cancelled by user")
        except Exception as error:
            print(f"\nUnexpected error: {error}")
            logger.exception("Unexpected error")


if __name__ == "__main__":
    main()
