import os
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
            font=("Segoe UI", 12)
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
        self._log_activity(f"Selected folder: {self.selected_folder}")

    def _organize_files(self) -> None:
        if not self.selected_folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            self._log_activity("Organization failed: No folder selected.")
            return

        try:
            self._log_activity(f"Started organizing files in: {self.selected_folder}")
            counts, moved_files = self.organizer.organize_folder(self.selected_folder)
            self._update_stats(counts)

            if self.db_manager is not None:
                for file_info in moved_files:
                    self.db_manager.insert_log(
                        file_name=file_info["file_name"],
                        category=file_info["category"],
                        destination=file_info["destination"]
                    )
                self._log_activity(f"Saved {len(moved_files)} history records.")

            self._log_activity("File organization completed successfully.")
            messagebox.showinfo("Success", "Files organized successfully.")
        except PermissionError:
            messagebox.showerror("Permission Error", "Access denied while organizing files.")
            self._log_activity("Permission error occurred.")
        except Exception as error:
            messagebox.showerror("Error", f"Unexpected Error:\n{error}")
            self._log_activity(f"Unexpected error: {error}")

    def _update_stats(self, counts: dict[str, int]) -> None:
        for category, count in counts.items():
            label = self.stat_labels.get(category)
            if label:
                label.configure(text=str(count))

    @staticmethod
    def _shorten_path(path: Path, max_length: int = 60) -> str:
        text = str(path)
        return text if len(text) <= max_length else f"...{text[-(max_length - 3):]}"

    def _log_activity(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}\n"

        self.activity_text.configure(state="normal")
        self.activity_text.insert("end", entry)
        self.activity_text.see("end")
        self.activity_text.configure(state="disabled")
