import os
import threading
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from database import DatabaseManager
from organizer import FolderOrganizer


class Dashboard(ctk.CTkFrame):
    """Dashboard view for Smart File Organizer Pro."""

    def __init__(
        self,
        parent,
        organizer: FolderOrganizer | None = None,
        db_manager: DatabaseManager | None = None,
        **kwargs
    ):
        super().__init__(parent, corner_radius=20, fg_color="#1f2937", **kwargs)

        self.organizer = organizer or FolderOrganizer()
        self.db_manager = db_manager
        self.selected_folder: str = ""
        self.stat_labels: dict[str, ctk.CTkLabel] = {}

        self.grid(row=0, column=0, sticky="nsew")

        self._configure_grid()
        self._build_header()
        self._build_controls()
        self._build_stats_cards()
        self._build_activity_panel()

        self._log_activity("Dashboard initialized successfully.")

    def _configure_grid(self) -> None:
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#111827")
        header_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="Smart File Organizer Pro",
            font=("Segoe UI", 28, "bold"),
            text_color="#f8fafc"
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Organize files intelligently with secure automation.",
            font=("Segoe UI", 14),
            text_color="#cbd5e1"
        )
        subtitle.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))

    def _build_controls(self) -> None:
        control_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#111827")
        control_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=0)

        self.folder_label = ctk.CTkLabel(
            control_frame,
            text="No folder selected",
            font=("Segoe UI", 13),
            text_color="#e2e8f0",
            anchor="w"
        )
        self.folder_label.grid(row=0, column=0, sticky="ew", padx=20, pady=20)

        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e", padx=20, pady=20)
        button_frame.grid_columnconfigure(0, weight=0)
        button_frame.grid_columnconfigure(1, weight=0)

        self.select_button = ctk.CTkButton(
            button_frame,
            text="Select Folder",
            width=170,
            command=self._select_folder,
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            font=("Segoe UI", 12, "bold")
        )
        self.select_button.grid(row=0, column=0, padx=(0, 12))

        self.organize_button = ctk.CTkButton(
            button_frame,
            text="Organize Files",
            width=170,
            command=self._organize_files,
            fg_color="#22c55e",
            hover_color="#4ade80",
            font=("Segoe UI", 12, "bold")
        )
        self.organize_button.grid(row=0, column=1)

        self.progress_frame = ctk.CTkFrame(control_frame, fg_color="#111827")
        self.progress_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_columnconfigure(1, weight=0)

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            orientation="horizontal",
            mode="determinate",
            width=1
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(12, 8), padx=(0, 12))
        self.progress_bar.set(0)

        self.progress_percent_label = ctk.CTkLabel(
            self.progress_frame,
            text="0%",
            font=("Segoe UI", 12, "bold"),
            text_color="#f8fafc"
        )
        self.progress_percent_label.grid(row=0, column=1, sticky="e", pady=(12, 8))

        self.progress_status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Ready to organize",
            font=("Segoe UI", 12),
            text_color="#cbd5e1"
        )
        self.progress_status_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self._progress_value = 0.0
        self._progress_animation_target = 0.0
        self._progress_animation_running = False
        self._last_logged_percent = -1

    def _build_stats_cards(self) -> None:
        stats_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#111827")
        stats_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        stats_frame.grid_rowconfigure(0, weight=1)

        categories = ["Images", "Documents", "Videos", "Others"]
        for index in range(len(categories)):
            stats_frame.grid_columnconfigure(index, weight=1, uniform="stats")

        for idx, category in enumerate(categories):
            card = ctk.CTkFrame(stats_frame, corner_radius=18, fg_color="#1f2937")
            card.grid(row=0, column=idx, padx=10, pady=10, sticky="nsew")
            card.grid_rowconfigure(0, weight=1)
            card.grid_rowconfigure(1, weight=0)
            card.grid_columnconfigure(0, weight=1)

            count_label = ctk.CTkLabel(
                card,
                text="0",
                font=("Segoe UI", 28, "bold"),
                text_color=self.organizer.category_color(category)
            )
            count_label.grid(row=0, column=0, sticky="sw", padx=20, pady=(20, 10))

            title_label = ctk.CTkLabel(
                card,
                text=category,
                font=("Segoe UI", 14),
                text_color="#cbd5e1"
            )
            title_label.grid(row=1, column=0, sticky="sw", padx=20, pady=(0, 20))

            self.stat_labels[category] = count_label

    def _build_activity_panel(self) -> None:
        activity_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#111827")
        activity_frame.grid(row=3, column=0, sticky="nsew")
        activity_frame.grid_columnconfigure(0, weight=1)
        activity_frame.grid_rowconfigure(1, weight=1)

        section_title = ctk.CTkLabel(
            activity_frame,
            text="Recent Activity",
            font=("Segoe UI", 18, "bold"),
            text_color="#f8fafc"
        )
        section_title.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        self.activity_text = ctk.CTkTextbox(
            activity_frame,
            corner_radius=16,
            fg_color="#0f172a",
            text_color="#e2e8f0",
            border_width=0,
            font=("Segoe UI", 12),
            width=1,
            height=200,
            wrap="word"
        )
        self.activity_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.activity_text.configure(state="disabled")

    def _select_folder(self) -> None:
        folder = filedialog.askdirectory(title="Select folder to organize")
        if not folder:
            self._log_activity("Folder selection cancelled.")
            return

        folder_path = Path(folder)
        if not folder_path.is_dir():
            messagebox.showerror("Error", "Selected path is not a folder.")
            return

        if not os.access(folder_path, os.R_OK):
            messagebox.showerror("Permission Error", "Cannot access selected folder.")
            return

        self.selected_folder = str(folder_path)
        self.folder_label.configure(text=self._shorten_path(folder_path))

        counts = self.organizer.scan_folder(self.selected_folder)
        self._update_stats(counts)
        self._set_progress(0, sum(counts.values()))
        self._log_activity(f"Selected folder: {self.selected_folder}")

    def _organize_files(self) -> None:
        if not self.selected_folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            self._log_activity("Organization failed: No folder selected.")
            return

        counts = self.organizer.scan_folder(self.selected_folder)
        total_files = sum(counts.values())
        if total_files == 0:
            messagebox.showinfo("No files", "No files were found to organize.")
            self._log_activity("No files found to organize.")
            self._set_progress(0, 0)
            return

        self.organize_button.configure(state="disabled")
        self._last_logged_percent = -1
        self._set_progress(0, total_files)
        self.progress_status_label.configure(text="Organizing files...")
        self._log_activity(f"Started organizing files in: {self.selected_folder}")

        def worker() -> None:
            try:
                counts, moved_files = self.organizer.organize_folder(
                    self.selected_folder,
                    progress_callback=self._thread_progress_update
                )
                self.after(0, self._on_organize_complete, counts, moved_files)
            except PermissionError:
                self.after(0, self._on_organize_error, PermissionError("Access denied while organizing files."))
            except Exception as error:
                self.after(0, self._on_organize_error, error)

        threading.Thread(target=worker, daemon=True).start()

    def _thread_progress_update(self, completed: int, total: int) -> None:
        self.after(0, self._set_progress, completed, total)
        self.after(0, self._log_progress, completed, total)

    def _log_progress(self, completed: int, total: int) -> None:
        if not total:
            return

        percent = int((completed / total) * 100)
        if percent == self._last_logged_percent:
            return

        should_log = False
        if total <= 20:
            should_log = True
        elif percent == 100:
            should_log = True
        elif percent % 10 == 0:
            should_log = True

        if should_log:
            self._log_activity(f"Organized {completed}/{total} files ({percent}%)")
            self._last_logged_percent = percent

    def _on_organize_complete(self, counts: dict[str, int], moved_files: list[dict[str, str]]) -> None:
        self._update_stats(counts)

        if self.db_manager is not None:
            for file_info in moved_files:
                self.db_manager.insert_log(
                    file_name=file_info["file_name"],
                    category=file_info["category"],
                    destination=file_info["destination"]
                )
            self._log_activity(f"Saved {len(moved_files)} history records.")

        self._set_progress(sum(counts.values()), sum(counts.values()))
        self.progress_status_label.configure(text="File organization completed")
        self.organize_button.configure(state="normal")
        self._log_activity("File organization completed successfully.")
        self._show_summary_popup(counts)

    def _on_organize_error(self, error: Exception) -> None:
        self.organize_button.configure(state="normal")
        self.progress_status_label.configure(text="Organization failed")
        self._log_activity(f"Unexpected error: {error}")
        messagebox.showerror("Error", f"Unexpected Error:\n{error}")

    def _set_progress(self, completed: int, total: int) -> None:
        progress = (completed / total) if total else 0.0
        progress = min(max(progress, 0.0), 1.0)
        self.progress_percent_label.configure(text=f"{int(progress * 100)}%")
        self.progress_status_label.configure(
            text=(f"Organized {completed}/{total} files" if total else "Ready to organize")
        )
        self._animate_progress_to(progress)

    def _animate_progress_to(self, target: float) -> None:
        self._progress_animation_target = target
        if self._progress_animation_running:
            return
        self._progress_animation_running = True
        self._step_progress_animation()

    def _step_progress_animation(self) -> None:
        current = self._progress_value
        target = self._progress_animation_target
        diff = target - current
        if abs(diff) < 0.01:
            self._progress_value = target
            self.progress_bar.set(target)
            self._progress_animation_running = False
            return

        self._progress_value = current + diff * 0.25
        self.progress_bar.set(self._progress_value)
        self.after(16, self._step_progress_animation)

    def _update_stats(self, counts: dict[str, int]) -> None:
        for category, count in counts.items():
            label = self.stat_labels.get(category)
            if label:
                label.configure(text=str(count))

    @staticmethod
    def _shorten_path(path: Path, max_length: int = 60) -> str:
        text = str(path)
        return text if len(text) <= max_length else f"...{text[-(max_length - 3):]}"

    def _show_summary_popup(self, counts: dict[str, int]) -> None:
        total_files = sum(counts.values())
        summary_dialog = ctk.CTkToplevel(self)
        summary_dialog.title("Organization Summary")
        summary_dialog.geometry("520x480")
        summary_dialog.resizable(False, False)
        summary_dialog.transient(self)
        summary_dialog.grab_set()
        summary_dialog.configure(fg_color="#111827")
        summary_dialog.grid_columnconfigure(0, weight=1)
        summary_dialog.grid_rowconfigure(2, weight=1)

        summary_header = ctk.CTkLabel(
            summary_dialog,
            text="Organization Summary",
            font=("Segoe UI", 20, "bold"),
            text_color="#f8fafc"
        )
        summary_header.grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

        summary_subtitle = ctk.CTkLabel(
            summary_dialog,
            text=f"{total_files} files organized successfully.",
            font=("Segoe UI", 13),
            text_color="#cbd5e1"
        )
        summary_subtitle.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 20))

        content_frame = ctk.CTkFrame(summary_dialog, corner_radius=18, fg_color="#1f2937")
        content_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        visible_counts = [(category, count) for category, count in counts.items() if count > 0]
        if not visible_counts:
            empty_summary = ctk.CTkLabel(
                content_frame,
                text="No files were organized.",
                font=("Segoe UI", 13),
                text_color="#94a3b8"
            )
            empty_summary.grid(row=0, column=0, sticky="w", padx=12, pady=14)
        else:
            for index, (category, count) in enumerate(visible_counts):
                row_color = self.organizer.category_color(category)
                category_frame = ctk.CTkFrame(
                    content_frame,
                    corner_radius=16,
                    fg_color="#0f172a",
                    border_width=1,
                    border_color="#334155"
                )
                category_frame.grid(row=index, column=0, sticky="ew", padx=12, pady=10)
                category_frame.grid_columnconfigure(1, weight=1)

                category_label = ctk.CTkLabel(
                    category_frame,
                    text=category,
                    font=("Segoe UI", 12, "bold"),
                    text_color=row_color
                )
                category_label.grid(row=0, column=0, sticky="w", padx=14, pady=14)

                count_label = ctk.CTkLabel(
                    category_frame,
                    text=str(count),
                    font=("Segoe UI", 14, "bold"),
                    text_color="#e2e8f0"
                )
                count_label.grid(row=0, column=1, sticky="e", padx=14, pady=14)

        close_button = ctk.CTkButton(
            summary_dialog,
            text="Close",
            width=120,
            fg_color="#22c55e",
            hover_color="#4ade80",
            command=summary_dialog.destroy,
            font=("Segoe UI", 12, "bold")
        )
        close_button.grid(row=3, column=0, sticky="e", padx=24, pady=(0, 24))

    def _log_activity(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}\n"

        self.activity_text.configure(state="normal")
        self.activity_text.insert("end", entry)
        self.activity_text.see("end")
        self.activity_text.configure(state="disabled")
