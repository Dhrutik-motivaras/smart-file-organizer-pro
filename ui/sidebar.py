import customtkinter as ctk
from typing import Callable, Optional


class Sidebar(ctk.CTkFrame):
    """Sidebar navigation panel for Smart File Organizer Pro."""

    def __init__(
        self,
        parent,
        on_page_change: Optional[Callable[[str], None]] = None,
        active_page: str = "dashboard",
        **kwargs
    ) -> None:
        super().__init__(parent, width=240, corner_radius=0, fg_color="#111827", **kwargs)

        self.on_page_change = on_page_change
        self.active_page = active_page
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self.grid(row=0, column=0, sticky="ns")
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_branding()
        self._build_navigation()
        self._build_exit_button(parent)
        self._refresh_active_state()

    def _build_branding(self) -> None:
        self.logo = ctk.CTkLabel(
            self,
            text="Smart Organizer Pro",
            font=("Segoe UI", 20, "bold"),
            text_color="#f8fafc"
        )
        self.logo.grid(row=0, column=0, pady=(30, 24), padx=20, sticky="w")

        self.subtitle = ctk.CTkLabel(
            self,
            text="Organize your files with intelligence.",
            font=("Segoe UI", 11),
            text_color="#94a3b8"
        )
        self.subtitle.grid(row=1, column=0, pady=(0, 24), padx=20, sticky="w")

    def _build_navigation(self) -> None:
        self.dashboard_btn = self._create_nav_button("dashboard", "Dashboard")
        self.history_btn = self._create_nav_button("history", "History")

        self.dashboard_btn.grid(row=2, column=0, pady=(0, 10), padx=20, sticky="ew")
        self.history_btn.grid(row=3, column=0, pady=(0, 10), padx=20, sticky="ew")

    def _build_exit_button(self, parent) -> None:
        self.grid_rowconfigure(5, weight=1)

        self.exit_btn = ctk.CTkButton(
            self,
            text="Exit",
            fg_color="#ef4444",
            hover_color="#f87171",
            command=parent.quit,
            font=("Segoe UI", 12, "bold")
        )
        self.exit_btn.grid(row=6, column=0, pady=30, padx=20, sticky="ew")

    def _create_nav_button(self, page_key: str, text: str) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=text,
            fg_color="#0f172a",
            hover_color="#1f2937",
            text_color="#e2e8f0",
            font=("Segoe UI", 13, "bold"),
            command=lambda: self._on_navigation(page_key)
        )
        self.nav_buttons[page_key] = button
        return button

    def _on_navigation(self, page_key: str) -> None:
        if self.active_page == page_key:
            return

        self.active_page = page_key
        self._refresh_active_state()

        if self.on_page_change:
            self.on_page_change(page_key)

    def _refresh_active_state(self) -> None:
        for page_key, button in self.nav_buttons.items():
            if page_key == self.active_page:
                button.configure(
                    fg_color="#1d4ed8",
                    hover_color="#2563eb",
                    text_color="#ffffff"
                )
            else:
                button.configure(
                    fg_color="#0f172a",
                    hover_color="#1f2937",
                    text_color="#cbd5e1"
                )

    def set_active_page(self, page_key: str) -> None:
        self.active_page = page_key
        self._refresh_active_state()
