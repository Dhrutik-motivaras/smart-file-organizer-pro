import csv

import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Optional

from database import DatabaseManager


class HistoryPage(ctk.CTkFrame):
    """Displays file organization history from the SQLite database."""

    def __init__(self, parent, db_manager: Optional[DatabaseManager] = None, **kwargs):
        super().__init__(parent, corner_radius=20, fg_color="#1f2937", **kwargs)

        if db_manager is None:
            raise ValueError("DatabaseManager must be passed to HistoryPage")
        
        self.db_manager = db_manager
        self.full_logs: list[dict] = []
        self.log_rows: list[tuple[ctk.CTkFrame, dict]] = []
        self.search_var = ctk.StringVar()

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_controls()
        self._build_log_view()
        self.refresh_logs()

    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#111827")
        header_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="History",
            font=("Segoe UI", 24, "bold"),
            text_color="#f8fafc"
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Review your file organization activity and manage history records.",
            font=("Segoe UI", 12),
            text_color="#cbd5e1"
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 0))

    def _build_controls(self) -> None:
        control_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#111827")
        control_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=0)
        control_frame.grid_columnconfigure(2, weight=0)
        control_frame.grid_columnconfigure(3, weight=0)

        self.status_label = ctk.CTkLabel(
            control_frame,
            text="",
            font=("Segoe UI", 12),
            text_color="#94a3b8"
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=20, pady=20)

        self.refresh_button = ctk.CTkButton(
            control_frame,
            text="Refresh",
            width=120,
            fg_color="#0ea5e9",
            hover_color="#38bdf8",
            command=self.refresh_logs,
            font=("Segoe UI", 12, "bold")
        )
        self.refresh_button.grid(row=0, column=1, padx=(0, 10), pady=20)

        self.clear_button = ctk.CTkButton(
            control_frame,
            text="Clear History",
            width=140,
            fg_color="#ef4444",
            hover_color="#f87171",
            command=self._confirm_clear_history,
            font=("Segoe UI", 12, "bold")
        )
        self.clear_button.grid(row=0, column=2, padx=(0, 10), pady=20)

        self.export_button = ctk.CTkButton(
            control_frame,
            text="Export CSV",
            width=140,
            fg_color="#f59e0b",
            hover_color="#fbbf24",
            command=self._export_csv,
            font=("Segoe UI", 12, "bold")
        )
        self.export_button.grid(row=0, column=3, padx=(0, 20), pady=20)

        search_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        search_row.grid(row=1, column=0, columnspan=4, sticky="ew", padx=20, pady=(0, 20))
        search_row.grid_columnconfigure(0, weight=1)
        search_row.grid_columnconfigure(1, weight=0)

        self.search_entry = ctk.CTkEntry(
            search_row,
            textvariable=self.search_var,
            placeholder_text="Search by file name, category, or destination...",
            width=560,
            fg_color="#0f172a",
            text_color="#e2e8f0",
            placeholder_text_color="#64748b",
            border_width=1,
            border_color="#334155",
            corner_radius=16,
            font=("Segoe UI", 12)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.clear_search_button = ctk.CTkButton(
            search_row,
            text="✕",
            width=42,
            fg_color="#334155",
            hover_color="#475569",
            command=self._clear_search,
            font=("Segoe UI", 14, "bold")
        )
        self.clear_search_button.grid(row=0, column=1, sticky="e")

        self.search_var.trace_add("write", lambda *_: self._filter_logs())

    def _build_log_view(self) -> None:
        log_frame = ctk.CTkFrame(self, corner_radius=20, fg_color="#111827")
        log_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        header_row = ctk.CTkFrame(log_frame, corner_radius=12, fg_color="#1f2937")
        header_row.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        for column_index in range(4):
            header_row.grid_columnconfigure(column_index, weight=1)

        headers = ["File Name", "Category", "Destination", "Date / Time"]
        for index, text in enumerate(headers):
            header = ctk.CTkLabel(
                header_row,
                text=text,
                font=("Segoe UI", 12, "bold"),
                text_color="#cbd5e1"
            )
            header.grid(row=0, column=index, sticky="w", padx=10)

        self.scrollable_logs = ctk.CTkScrollableFrame(
            log_frame,
            corner_radius=16,
            fg_color="#0f172a",
            border_width=0
        )
        self.scrollable_logs.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scrollable_logs.grid_columnconfigure(0, weight=1)

    def refresh_logs(self) -> None:
        try:
            self.full_logs = self.db_manager.fetch_logs(order_desc=True)
        except Exception as error:
            self._show_error("Unable to load history.", error)
            return

        self._render_logs(self.full_logs)
        self._filter_logs()
        self.status_label.configure(text=f"Loaded {len(self.full_logs)} records.")

    def _render_logs(self, logs: list[dict]) -> None:
        for widget in self.scrollable_logs.winfo_children():
            widget.destroy()
        self.log_rows = []

        if not logs:
            empty_label = ctk.CTkLabel(
                self.scrollable_logs,
                text="No history records found.",
                font=("Segoe UI", 13),
                text_color="#94a3b8"
            )
            empty_label.grid(padx=20, pady=20, sticky="w")
            return

        for row_index, log_entry in enumerate(logs):
            row_frame = self._render_log_row(row_index, log_entry)
            self.log_rows.append((row_frame, log_entry))

    def _render_log_row(self, row_index: int, log_entry: dict) -> ctk.CTkFrame:
        row_frame = ctk.CTkFrame(
            self.scrollable_logs,
            corner_radius=14,
            fg_color="#1f2937"
        )
        row_frame.grid(
            row=row_index,
            column=0,
            sticky="ew",
            padx=12,
            pady=8
        )
        for column_index in range(4):
            row_frame.grid_columnconfigure(column_index, weight=1)

        values = [
            log_entry.get("file_name", ""),
            log_entry.get("category", ""),
            log_entry.get("destination", ""),
            log_entry.get("date_time", "")
        ]

        for col_index, text in enumerate(values):
            label = ctk.CTkLabel(
                row_frame,
                text=text,
                font=("Segoe UI", 11),
                text_color="#e2e8f0",
                wraplength=300 if col_index == 2 else 200,
                justify="left"
            )
            label.grid(row=0, column=col_index, sticky="w", padx=10, pady=14)

        return row_frame

    def _filter_logs(self) -> None:
        query = self.search_var.get().strip().lower()
        if not self.log_rows:
            return

        matched_count = 0
        for row_frame, log_entry in self.log_rows:
            searchable = " ".join(
                [
                    str(log_entry.get("file_name", "")),
                    str(log_entry.get("category", "")),
                    str(log_entry.get("destination", ""))
                ]
            ).lower()
            if query and query not in searchable:
                row_frame.grid_remove()
            else:
                row_frame.grid()
                matched_count += 1

        self.status_label.configure(
            text=(f"Showing {matched_count} of {len(self.full_logs)} records" if query else f"Loaded {len(self.full_logs)} records.")
        )

    def _clear_search(self) -> None:
        self.search_var.set("")
        self._filter_logs()

    def _export_csv(self) -> None:
        if not self.full_logs:
            messagebox.showinfo("Export CSV", "No history records are available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export history to CSV",
            initialfile="history_export.csv"
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=["file_name", "category", "destination", "date_time"]
                )
                writer.writeheader()
                for log in self.full_logs:
                    writer.writerow({
                        key: log.get(key, "") for key in writer.fieldnames
                    })

            messagebox.showinfo("Export Complete", f"History exported successfully to:\n{file_path}")
            self.status_label.configure(text=f"Exported {len(self.full_logs)} records to CSV.")
        except Exception as error:
            self._show_error("Unable to export CSV.", error)

    def _confirm_clear_history(self) -> None:
        confirm = messagebox.askyesno(
            title="Clear History",
            message="Are you sure you want to clear all history records?"
        )
        if not confirm:
            return

        try:
            self.db_manager.clear_logs()
            self.refresh_logs()
            self.status_label.configure(text="History cleared successfully.")
        except Exception as error:
            self._show_error("Unable to clear history.", error)

    def _show_error(self, title: str, error: Exception) -> None:
        messagebox.showerror(title, str(error))
        self.status_label.configure(text="Error loading history.")
