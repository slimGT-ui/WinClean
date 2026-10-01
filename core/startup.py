import os
import winreg


RUN_PATHS = [
    (
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "HKCU",
    ),
    (
        winreg.HKEY_LOCAL_MACHINE,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM",
    ),
]


def get_startup_programs():
    programs = []

    for hive, path, location in RUN_PATHS:
        try:
            with winreg.OpenKey(hive, path) as key:
                index = 0

                while True:
                    try:
                        name, command, _ = winreg.EnumValue(key, index)
                        programs.append(
                            {
                                "name": name,
                                "command": str(command),
                                "location": location,
                            }
                        )
                        index += 1
                    except OSError:
                        break

        except (PermissionError, FileNotFoundError, OSError):
            continue

    startup_folders = [
        os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
        ),
        os.path.expandvars(
            r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
        ),
    ]

    for folder in startup_folders:
        if not os.path.isdir(folder):
            continue

        try:
            for item in os.listdir(folder):
                programs.append(
                    {
                        "name": item,
                        "command": os.path.join(folder, item),
                        "location": "Startup Folder",
                    }
                )
        except OSError:
            continue

    return programs
