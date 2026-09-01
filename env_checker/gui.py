import threading
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from env_checker.installer import install_dependencies
from env_checker.models import CheckResult, Status
from env_checker.runner import run_checks

COLOR_OK = "#2e7d32"
COLOR_BAD = "#c62828"
COLOR_WARN = "#f9a825"
COLOR_ROW_OK = "#e8f5e9"
COLOR_ROW_BAD = "#ffebee"
COLOR_ROW_WARN = "#fff8e1"


class DependencyRow:
    def __init__(
        self,
        parent: tk.Frame,
        result: CheckResult,
        on_toggle: Callable[[], None],
    ) -> None:
        self.result = result
        bg = COLOR_ROW_OK if result.passed else COLOR_ROW_BAD
        if result.status == Status.WARN:
            bg = COLOR_ROW_WARN

        self.frame = tk.Frame(parent, bg=bg, pady=4, padx=4)
        self.frame.pack(fill=tk.X, padx=4, pady=2)

        self.var = tk.BooleanVar(value=result.needs_update)
        self.checkbox = tk.Checkbutton(
            self.frame,
            variable=self.var,
            bg=bg,
            activebackground=bg,
            command=on_toggle,
        )
        if not result.updatable:
            self.checkbox.config(state=tk.DISABLED)
            self.var.set(False)
        self.checkbox.pack(side=tk.LEFT, padx=(4, 8))

        indicator_color = COLOR_OK if result.passed else COLOR_BAD
        if result.status == Status.WARN:
            indicator_color = COLOR_WARN
        self.indicator = tk.Label(
            self.frame,
            text="●",
            fg=indicator_color,
            bg=bg,
            font=("Segoe UI", 14),
            width=2,
        )
        self.indicator.pack(side=tk.LEFT)

        tk.Label(
            self.frame,
            text=result.name,
            font=("Segoe UI", 10, "bold"),
            bg=bg,
            width=16,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        tk.Label(
            self.frame,
            text=result.required,
            font=("Segoe UI", 10),
            bg=bg,
            width=22,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        installed_color = COLOR_OK if result.passed else COLOR_BAD
        if result.status == Status.WARN:
            installed_color = COLOR_WARN
        tk.Label(
            self.frame,
            text=result.installed,
            font=("Segoe UI", 10),
            fg=installed_color,
            bg=bg,
            width=14,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        status_text = "Good" if result.passed else result.status.label
        tk.Label(
            self.frame,
            text=status_text,
            font=("Segoe UI", 10),
            fg=installed_color,
            bg=bg,
            width=10,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

    def is_selected(self) -> bool:
        return self.var.get() and self.result.updatable

    def set_selected(self, value: bool) -> None:
        if self.result.updatable:
            self.var.set(value)


class EnvCheckerApp:
    def __init__(self, config: dict, config_dir: Path) -> None:
        self.config = config
        self.config_dir = config_dir
        self.rows: list[DependencyRow] = []
        self.installing = False

        self.root = tk.Tk()
        self.root.title("Work Environment Setup")
        self.root.minsize(820, 560)
        self.root.configure(bg="#f5f5f5")

        frappe_ver = config.get("frappe_version", "v16")
        header = tk.Frame(self.root, bg="#1e3a5f", padx=16, pady=12)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="Work Environment Setup",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#1e3a5f",
        ).pack(anchor=tk.W)
        tk.Label(
            header,
            text=f"Frappe {frappe_ver} — green = OK, red = needs update",
            font=("Segoe UI", 10),
            fg="#b0c4de",
            bg="#1e3a5f",
        ).pack(anchor=tk.W)

        toolbar = tk.Frame(self.root, bg="#f5f5f5", padx=12, pady=8)
        toolbar.pack(fill=tk.X)
        self.recheck_btn = ttk.Button(toolbar, text="Recheck", command=self.refresh)
        self.recheck_btn.pack(side=tk.LEFT)

        self.summary_label = tk.Label(
            toolbar,
            text="",
            font=("Segoe UI", 10),
            bg="#f5f5f5",
            fg="#333",
        )
        self.summary_label.pack(side=tk.LEFT, padx=(16, 0))

        list_container = tk.Frame(self.root, bg="#f5f5f5")
        list_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        header_row = tk.Frame(list_container, bg="#e0e0e0", pady=6, padx=8)
        header_row.pack(fill=tk.X, padx=4, pady=(0, 4))
        tk.Label(header_row, text="", width=3, bg="#e0e0e0").pack(side=tk.LEFT)
        tk.Label(header_row, text="", width=2, bg="#e0e0e0").pack(side=tk.LEFT)
        tk.Label(
            header_row,
            text="Dependency",
            font=("Segoe UI", 9, "bold"),
            bg="#e0e0e0",
            width=16,
            anchor=tk.W,
        ).pack(side=tk.LEFT)
        tk.Label(
            header_row,
            text="Required",
            font=("Segoe UI", 9, "bold"),
            bg="#e0e0e0",
            width=22,
            anchor=tk.W,
        ).pack(side=tk.LEFT)
        tk.Label(
            header_row,
            text="Installed",
            font=("Segoe UI", 9, "bold"),
            bg="#e0e0e0",
            width=14,
            anchor=tk.W,
        ).pack(side=tk.LEFT)
        tk.Label(
            header_row,
            text="Status",
            font=("Segoe UI", 9, "bold"),
            bg="#e0e0e0",
            width=10,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        canvas = tk.Canvas(list_container, bg="#f5f5f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=canvas.yview)
        self.rows_frame = tk.Frame(canvas, bg="#f5f5f5")
        self.rows_frame.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self.rows_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        log_frame = tk.LabelFrame(
            self.root,
            text="Install log",
            font=("Segoe UI", 9),
            padx=8,
            pady=6,
        )
        log_frame.pack(fill=tk.X, padx=12, pady=(4, 0))
        self.log_text = tk.Text(
            log_frame,
            height=6,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#1e1e1e",
            fg="#d4d4d4",
        )
        self.log_text.pack(fill=tk.X)

        button_bar = tk.Frame(self.root, bg="#f5f5f5", padx=12, pady=12)
        button_bar.pack(fill=tk.X)

        self.update_selected_btn = ttk.Button(
            button_bar,
            text="Update selected",
            command=self.update_selected,
        )
        self.update_selected_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.update_all_btn = ttk.Button(
            button_bar,
            text="Update all",
            command=self.update_all,
        )
        self.update_all_btn.pack(side=tk.LEFT)

        tk.Label(
            button_bar,
            text="sudo may prompt for your password in the terminal",
            font=("Segoe UI", 9),
            fg="#666",
            bg="#f5f5f5",
        ).pack(side=tk.RIGHT)

        self.refresh()

    def log(self, message: str) -> None:
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def set_installing(self, active: bool) -> None:
        self.installing = active
        state = tk.DISABLED if active else tk.NORMAL
        self.recheck_btn.config(state=state)
        self.update_selected_btn.config(state=state)
        self.update_all_btn.config(state=state)

    def refresh(self) -> None:
        if self.installing:
            return

        for row in self.rows:
            row.frame.destroy()
        self.rows.clear()

        results = run_checks(self.config)
        ok_count = sum(1 for r in results if r.passed)
        total = len(results)
        issues = total - ok_count

        if issues == 0:
            self.summary_label.config(text=f"All {total} checks passed", fg=COLOR_OK)
        else:
            self.summary_label.config(
                text=f"{ok_count}/{total} passed — {issues} need attention",
                fg=COLOR_BAD,
            )

        for result in results:
            row = DependencyRow(self.rows_frame, result, self._on_toggle)
            self.rows.append(row)

    def _on_toggle(self) -> None:
        pass

    def _get_selected_ids(self) -> list[str]:
        return [row.result.id for row in self.rows if row.is_selected()]

    def update_selected(self) -> None:
        ids = self._get_selected_ids()
        if not ids:
            self.log("No dependencies selected for update.")
            return
        self._run_install(ids)

    def update_all(self) -> None:
        for row in self.rows:
            if row.result.needs_update:
                row.set_selected(True)
        ids = self._get_selected_ids()
        if not ids:
            self.log("Nothing to update — all dependencies are OK.")
            return
        self._run_install(ids)

    def _run_install(self, dep_ids: list[str]) -> None:
        self.set_installing(True)
        self.log(f"\nStarting update for: {', '.join(dep_ids)}")

        def worker() -> None:
            install_dependencies(dep_ids, self.config, self._log_threadsafe, self.config_dir)
            self.root.after(0, self._install_done)

        threading.Thread(target=worker, daemon=True).start()

    def _log_threadsafe(self, message: str) -> None:
        self.root.after(0, lambda: self.log(message))

    def _install_done(self) -> None:
        self.log("Update finished. Rechecking versions...")
        self.set_installing(False)
        self.refresh()

    def run(self) -> None:
        self.root.mainloop()


def main(config: dict, config_dir: Path) -> None:
    app = EnvCheckerApp(config, config_dir)
    app.run()
