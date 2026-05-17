from pathlib import Path


class FolderOrganizer:
    """Encapsulates folder scanning and file organization logic."""

    CATEGORY_EXTENSIONS = {
        "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"},
        "Documents": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".rtf"},
        "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"},
        "Others": set()
    }

    HIDDEN_FILE_NAMES = {"desktop.ini", "thumbs.db"}

    def category_color(self, category: str) -> str:
        return {
            "Images": "#38bdf8",
            "Documents": "#c084fc",
            "Videos": "#fb7185",
            "Others": "#facc15"
        }.get(category, "#94a3b8")

    def scan_folder(self, folder_path: str) -> dict[str, int]:
        path = Path(folder_path)
        if not path.is_dir():
            raise ValueError("Folder path must be a directory.")

        counts = {category: 0 for category in self.CATEGORY_EXTENSIONS}
        for item in path.iterdir():
            if self._should_skip_item(item):
                continue

            if item.is_file():
                category = self._classify_file(item.suffix.lower())
                counts[category] += 1
        return counts

    def organize_folder(self, folder_path: str) -> tuple[dict[str, int], list[dict[str, str]]]:
        path = Path(folder_path)
        if not path.is_dir():
            raise ValueError("Folder path must be a directory.")

        files = [item for item in path.iterdir() if item.is_file() and not self._should_skip_item(item)]
        counts = {category: 0 for category in self.CATEGORY_EXTENSIONS}
        moved_files: list[dict[str, str]] = []

        for item in files:
            category = self._classify_file(item.suffix.lower())
            destination_folder = path / category
            destination_folder.mkdir(parents=True, exist_ok=True)

            destination = destination_folder / item.name
            if destination.exists():
                destination = self._resolve_destination(destination)

            item.replace(destination)

            counts[category] += 1
            moved_files.append(
                {
                    "file_name": item.name,
                    "category": category,
                    "destination": str(destination)
                }
            )

        return counts, moved_files

    def _resolve_destination(self, destination: Path) -> Path:
        stem = destination.stem
        suffix = destination.suffix
        directory = destination.parent
        index = 1

        while True:
            candidate = directory / f"{stem}_{index}{suffix}"
            if not candidate.exists():
                return candidate
            index += 1

    def _should_skip_item(self, item: Path) -> bool:
        if item.name.startswith('.'):
            return True

        if item.name.lower() in self.HIDDEN_FILE_NAMES:
            return True

        if item.is_dir() and item.name in self.CATEGORY_EXTENSIONS:
            return True

        return False

    def _classify_file(self, extension: str) -> str:
        for category, extensions in self.CATEGORY_EXTENSIONS.items():
            if extension in extensions:
                return category
        return "Others"
