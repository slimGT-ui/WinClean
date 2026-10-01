# WinClean

**A small, safety-first Windows cleanup and diagnostics tool written in pure Python.**

English | [Русский](README.ru.md)

WinClean shows you what is taking up space on your PC and what starts with Windows, and lets you clear the safest things — the current user's TEMP folder and the Recycle Bin — after an explicit confirmation. Everything else is **read-only by design**.

It has two interfaces: a simple Tkinter GUI and an interactive CLI menu. It uses only the Python standard library, so there is nothing to install to run it from source.

## Features

| Feature | What it does | Changes anything? |
| --- | --- | --- |
| **Analyze TEMP** | Counts files and total size in your TEMP folder | No |
| **Clean TEMP** | Deletes files from the current user's TEMP folder | Yes, after confirmation |
| **Recycle Bin** | Shows its size and can empty it permanently | Yes, after confirmation |
| **Large-file finder** | Lists the biggest files in a chosen folder or drive (sorted by size) | No |
| **Startup programs** | Lists entries from `Run` registry keys (HKCU / HKLM) and Startup folders | No |
| **Full scan** | Runs all of the above checks and estimates reclaimable space | No |
| **Dashboard (GUI)** | Live TEMP / Recycle Bin / Startup counters, progress bar, output pane | — |
| **Local logging** | Writes a log file to your user profile | — |

## Safety

WinClean is intentionally conservative.

It does **not** automatically:

- delete Windows system files;
- delete Program Files;
- delete Documents, Desktop, or Downloads;
- remove startup entries;
- modify Windows Defender;
- disable Windows Update;
- delete large files — the finder only reports them.

How deletion is restricted:

- TEMP cleanup is allowed **only** inside `%USERPROFILE%\AppData\Local\Temp`. The path is resolved and checked before anything is removed; any other path is rejected.
- Both TEMP cleanup and Recycle Bin emptying require a confirmation (`Y/N` in the CLI, a dialog in the GUI).
- Emptying the Recycle Bin is **permanent** — files cannot be restored afterwards.
- Files that are locked or inaccessible are skipped and counted, not forced.
- The large-file scan skips `System Volume Information`, `$Recycle.Bin`, and `Recovery`.

## Requirements

- Windows 10 or Windows 11
- Python 3.12+ (with Tkinter, which is included in the standard python.org installer)
- No third-party packages

## Quick start

```powershell
git clone https://github.com/<your-username>/WinClean.git
cd WinClean
```

### GUI

```powershell
python run_gui.py
```

The window shows three counters (TEMP, Recycle Bin, Startup), a row of action buttons, and an output pane. **Full Scan** runs in a background thread so the window stays responsive, and does not delete anything.

### CLI

```powershell
python main.py
```

```text
========================================
              WinClean
========================================

[1] Analyze TEMP
[2] Clean TEMP
[3] Empty Recycle Bin
[4] Find Large Files
[5] Startup Programs
[6] Full Scan
[0] Exit
```

In the large-file finder you can enter a drive/folder and a minimum size such as `500MB`, `1GB`, or `5GB`. The CLI shows the top 50 results, the GUI shows the top 100.

> The Full Scan looks for files of **1 GB or larger on `C:\`**.

## Build a standalone EXE

Run:

```text
build.bat
```

The script installs PyInstaller and builds a single windowed executable:

```text
dist\WinClean.exe
```

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests also run automatically on every push and pull request via GitHub Actions (`windows-latest`, Python 3.12).

## Logs

WinClean writes a log file to:

```text
%LOCALAPPDATA%\WinClean\logs\winclean.log
```

It records application start/exit, blocked cleanups, cancelled operations, and unexpected errors.

## Project structure

```text
WinClean/
├── main.py              # CLI entry point (interactive menu)
├── run_gui.py           # GUI entry point
├── gui.py               # Tkinter interface
├── build.bat            # PyInstaller build script
├── core/
│   ├── scanner.py       # TEMP scan, large-file finder, Recycle Bin size
│   ├── cleaner.py       # TEMP cleanup
│   ├── safety.py        # Rules for what is allowed to be deleted
│   ├── recycle_bin.py   # Empty the Recycle Bin (Windows Shell API)
│   ├── startup.py       # Startup programs (registry + Startup folders)
│   └── full_scan.py     # Combined scan with progress reporting
├── utils/
│   ├── formatting.py    # Human-readable sizes
│   └── logger.py        # File logger
├── tests/               # Unit tests
├── .github/workflows/
│   └── tests.yml        # CI: run tests on Windows
├── .gitignore
├── LICENSE
└── requirements.txt
```

## Roadmap

- [x] CLI MVP
- [x] Safety layer
- [x] Recycle Bin support
- [x] Large-file finder
- [x] Startup analyzer
- [x] Full scan
- [x] GUI
- [x] Tests
- [x] GitHub Actions
- [x] PyInstaller build
- [ ] Application cache cleaners
- [ ] Disk-usage visualization
- [ ] Settings page
- [ ] System tray
- [ ] Release automation

## Disclaimer

WinClean deletes files when you confirm it to. Review what it reports before you confirm, and use it at your own risk (see the license).

## License

Released under the [MIT License](LICENSE).
