import customtkinter as ctk

from database import DatabaseManager
from organizer import FolderOrganizer
from ui.dashborad import Dashboard
from ui.history_page import HistoryPage
from ui.sidebar import Sidebar


class App(ctk.CTk):
    """Main application window for Smart File Organizer Pro."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Smart File Organizer Pro")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        self._configure_theme()
        self._configure_root_grid()

        self.db_manager = DatabaseManager()
        self.organizer = FolderOrganizer()
        self.pages: dict[str, ctk.CTkFrame] = {}

        self.sidebar = Sidebar(self, on_page_change=self.show_page, active_page="dashboard")
        self.page_container = ctk.CTkFrame(self, fg_color="transparent")
        self.page_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)

        self._build_pages()
        self.show_page("dashboard")

    def _configure_theme(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _configure_root_grid(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _build_pages(self) -> None:
        self.pages["dashboard"] = Dashboard(
            self.page_container,
            organizer=self.organizer,
            db_manager=self.db_manager
        )
        self.pages["history"] = HistoryPage(
            self.page_container,
            db_manager=self.db_manager
        )

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_key: str) -> None:
        if page_key not in self.pages:
            return

        for key, page in self.pages.items():
            page.grid_remove() if key != page_key else page.grid()

        if page_key == "history" and hasattr(self.pages[page_key], "refresh_logs"):
            self.pages[page_key].refresh_logs()

        self.sidebar.set_active_page(page_key)

    def on_closing(self) -> None:
        self.db_manager.close()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
