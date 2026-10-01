import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from core.cleaner import clean_directory
from core.scanner import (
    find_large_files,
    get_recycle_bin_size,
    get_temp_path,
    scan_directory,
)
from core.recycle_bin import empty_recycle_bin
from core.full_scan import run_full_scan
from core.startup import get_startup_programs
from utils.formatting import format_size
from utils.logger import setup_logger

logger = setup_logger()


class WinCleanApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("WinClean")
        self.geometry("920x620")
        self.minsize(820, 540)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("vista")
        except tk.TclError:
            pass

        self._build_ui()
        self.refresh_dashboard()

    def _build_ui(self):
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x", pady=(0, 16))

        ttk.Label(
            header,
            text="WinClean",
            font=("Segoe UI", 24, "bold"),
        ).pack(side="left")

        ttk.Label(
            header,
            text="Windows cleanup & diagnostics",
            font=("Segoe UI", 10),
        ).pack(side="left", padx=(14, 0), pady=(10, 0))

        self.status = tk.StringVar(value="Ready")
        ttk.Label(header, textvariable=self.status).pack(
            side="right", pady=(10, 0)
        )

        progress_frame = ttk.Frame(root)
        progress_frame.pack(fill="x", pady=(0, 12))

        self.progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
        )
        self.progress.pack(fill="x")

        cards = ttk.Frame(root)
        cards.pack(fill="x", pady=(0, 16))

        self.temp_var = tk.StringVar(value="—")
        self.recycle_var = tk.StringVar(value="—")
        self.startup_var = tk.StringVar(value="—")

        self._card(cards, "TEMP", self.temp_var, 0)
        self._card(cards, "Recycle Bin", self.recycle_var, 1)
        self._card(cards, "Startup", self.startup_var, 2)

        actions = ttk.LabelFrame(root, text="Actions", padding=12)
        actions.pack(fill="x", pady=(0, 16))

        buttons = [
            ("Analyze TEMP", self.analyze_temp),
            ("Clean TEMP", self.clean_temp),
            ("Empty Recycle Bin", self.clean_recycle_bin),
            ("Find Large Files", self.find_large_files_dialog),
            ("Startup Programs", self.show_startup),
            ("Full Scan", self.full_scan),
            ("Refresh", self.refresh_dashboard),
        ]

        self.action_buttons = []
        for index, (label, command) in enumerate(buttons):
            button = ttk.Button(actions, text=label, command=command)
            button.grid(
                row=index // 4,
                column=index % 4,
                padx=6,
                pady=6,
                sticky="ew",
            )
            self.action_buttons.append(button)

        for column in range(4):
            actions.columnconfigure(column, weight=1)

        output_frame = ttk.LabelFrame(root, text="Output", padding=8)
        output_frame.pack(fill="both", expand=True)

        self.output = tk.Text(
            output_frame,
            wrap="word",
            height=15,
            font=("Consolas", 10),
            state="disabled",
        )
        self.output.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            output_frame, orient="vertical", command=self.output.yview
        )
        scrollbar.pack(side="right", fill="y")
        self.output.configure(yscrollcommand=scrollbar.set)

    def _card(self, parent, title, variable, column):
        frame = ttk.LabelFrame(parent, text=title, padding=12)
        frame.grid(row=0, column=column, padx=6, sticky="ew")
        parent.columnconfigure(column, weight=1)

        ttk.Label(
            frame,
            textvariable=variable,
            font=("Segoe UI", 14, "bold"),
        ).pack()

    def write(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.insert("end", text)
        self.output.configure(state="disabled")

    def append(self, text):
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def refresh_dashboard(self):
        self.status.set("Scanning...")
        self.update_idletasks()

        try:
            temp = scan_directory(get_temp_path())
            recycle = get_recycle_bin_size()
            startup = get_startup_programs()

            self.temp_var.set(format_size(temp["size"]))
            self.recycle_var.set(format_size(recycle))
            self.startup_var.set(str(len(startup)))
            self.status.set("Ready")

            self.write(
                "Dashboard refreshed.\n\n"
                f"TEMP: {format_size(temp['size'])} "
                f"({temp['files']} files)\n"
                f"Recycle Bin: {format_size(recycle)}\n"
                f"Startup entries: {len(startup)}"
            )
        except Exception as error:
            logger.exception("Dashboard refresh failed")
            self.status.set("Error")
            messagebox.showerror("WinClean", str(error))

    def analyze_temp(self):
        result = scan_directory(get_temp_path())
        self.write(
            "TEMP ANALYSIS\n"
            + "=" * 50
            + "\n"
            f"Path: {result['path']}\n"
            f"Files: {result['files']}\n"
            f"Size: {format_size(result['size'])}\n"
            f"Skipped: {result['skipped']}\n"
        )

    def clean_temp(self):
        result = scan_directory(get_temp_path())

        if result["files"] == 0:
            messagebox.showinfo("WinClean", "TEMP is already empty.")
            return

        answer = messagebox.askyesno(
            "Confirm cleanup",
            f"Delete {result['files']} files and free "
            f"approximately {format_size(result['size'])}?",
        )
        if not answer:
            return

        self.status.set("Cleaning...")
        self.update_idletasks()

        try:
            result = clean_directory(get_temp_path())
            self.write(
                "TEMP CLEANUP\n"
                + "=" * 50
                + "\n"
                f"Deleted: {result['deleted_files']} files\n"
                f"Freed: {format_size(result['deleted_size'])}\n"
                f"Skipped: {result['skipped_files']} files\n"
            )
            self.status.set("Ready")
            self.refresh_dashboard()
        except ValueError as error:
            self.status.set("Error")
            messagebox.showerror("Cleanup blocked", str(error))

    def clean_recycle_bin(self):
        size = get_recycle_bin_size()
        answer = messagebox.askyesno(
            "Confirm cleanup",
            "Empty the Recycle Bin permanently?\n\n"
            f"Current size: {format_size(size)}",
        )
        if not answer:
            return

        if empty_recycle_bin():
            self.write("Recycle Bin emptied successfully.")
            self.refresh_dashboard()
        else:
            messagebox.showerror(
                "WinClean",
                "Windows could not empty the Recycle Bin.",
            )

    def find_large_files_dialog(self):
        drive = filedialog.askdirectory(title="Choose a folder to scan")
        if not drive:
            return

        dialog = tk.Toplevel(self)
        dialog.title("Find Large Files")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="Minimum size:").grid(
            row=0, column=0, padx=12, pady=12
        )

        value = tk.StringVar(value="1")
        unit = tk.StringVar(value="GB")

        ttk.Entry(dialog, textvariable=value, width=10).grid(
            row=0, column=1, padx=6
        )
        ttk.Combobox(
            dialog,
            textvariable=unit,
            values=("MB", "GB", "TB"),
            state="readonly",
            width=7,
        ).grid(row=0, column=2, padx=6)

        def run():
            try:
                multiplier = {"MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
                minimum = float(value.get()) * multiplier[unit.get()]
                dialog.destroy()

                self.status.set("Scanning...")
                results = find_large_files(drive, int(minimum))

                lines = [
                    f"LARGE FILES >= {format_size(minimum)}",
                    "=" * 70,
                ]
                if not results:
                    lines.append("No matching files found.")
                else:
                    for index, item in enumerate(results[:100], 1):
                        lines.append(
                            f"{index:>3}. {format_size(item['size']):>12}  "
                            f"{item['path']}"
                        )
                self.write("\n".join(lines))
                self.status.set("Ready")
            except (ValueError, KeyError):
                messagebox.showerror("Invalid size", "Enter a valid number.")

        ttk.Button(dialog, text="Scan", command=run).grid(
            row=1, column=0, columnspan=3, pady=(0, 12)
        )

    def show_startup(self):
        programs = get_startup_programs()
        lines = ["STARTUP PROGRAMS", "=" * 80]

        if not programs:
            lines.append("No startup entries found.")
        else:
            for program in programs:
                lines.extend(
                    [
                        f"Name: {program['name']}",
                        f"Command: {program['command']}",
                        f"Location: {program['location']}",
                        "-" * 80,
                    ]
                )

        self.write("\n".join(lines))

    def full_scan(self):
        self.status.set("Starting full scan...")
        self.progress.configure(value=0, mode="determinate")
        self.write("WINCLEAN FULL SCAN\n" + "=" * 50 + "\n\nStarting scan...\n")

        for button in self.action_buttons:
            button.configure(state="disabled")

        def update_progress(percent, message):
            self.after(0, self._update_full_scan_progress, percent, message)

        def worker():
            try:
                result = run_full_scan(progress_callback=update_progress)
                self.after(0, self._finish_full_scan, result)
            except Exception as error:
                logger.exception("Full scan failed")
                self.after(0, self._full_scan_error, error)

        threading.Thread(target=worker, daemon=True).start()

    def _update_full_scan_progress(self, percent, message):
        if percent == 40 and "Scanning large files" in message:
            self.progress.configure(mode="indeterminate")
            self.progress.start(12)
        else:
            if self.progress.cget("mode") == "indeterminate":
                self.progress.stop()
                self.progress.configure(mode="determinate")

            self.progress.configure(value=percent)

        self.status.set(message)

    def _finish_full_scan(self, result):
        if self.progress.cget("mode") == "indeterminate":
            self.progress.stop()
            self.progress.configure(mode="determinate")

        self.progress.configure(value=100)

        temp = result["temp"]
        recycle = result["recycle_size"]
        large = result["large_files"]
        startup = result["startup"]
        reclaimable = result["reclaimable"]

        lines = [
            "WINCLEAN FULL SCAN",
            "=" * 50,
            f"TEMP: {format_size(temp['size'])} ({temp['files']} files)",
            f"Recycle Bin: {format_size(recycle)}",
            f"Large files >= 1 GB: {len(large)}",
            f"Startup programs: {len(startup)}",
            f"Potential reclaimable: {format_size(reclaimable)}",
            "",
            "The full scan does not delete anything.",
        ]

        self.write("\n".join(lines))
        self.status.set("Full scan complete")

        for button in self.action_buttons:
            button.configure(state="normal")

    def _full_scan_error(self, error):
        if self.progress.cget("mode") == "indeterminate":
            self.progress.stop()
            self.progress.configure(mode="determinate")

        self.progress.configure(value=0)
        self.status.set("Full scan failed")

        for button in self.action_buttons:
            button.configure(state="normal")

        messagebox.showerror("Full scan failed", str(error))


def launch_gui():
    app = WinCleanApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
