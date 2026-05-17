'''from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class DatabaseManager:
    """Manages SQLite storage for Smart File Organizer Pro."""

    DEFAULT_TABLE_NAME = "file_logs"
    DEFAULT_DATABASE_FILE = "database/files.db"

    def __init__(
        self,
        database_path: Optional[str] = None,
        table_name: str = DEFAULT_TABLE_NAME
    ) -> None:

        # Database Path
        self.database_path = Path(
            database_path or self.DEFAULT_DATABASE_FILE
        )

        # Create database folder automatically
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.table_name = table_name

        self._connection: Optional[sqlite3.Connection] = None

        self._connect()

        self._create_table_if_needed()

    # --------------------------------------------------
    # DATABASE CONNECTION
    # --------------------------------------------------

    def _connect(self) -> None:

        try:

            self._connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False
            )

            self._connection.row_factory = sqlite3.Row

        except sqlite3.Error as error:

            raise RuntimeError(
                f"Unable to connect to database: {error}"
            ) from error

    # --------------------------------------------------
    # CREATE TABLE
    # --------------------------------------------------

    def _create_table_if_needed(self) -> None:

        query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                file_name TEXT NOT NULL,

                category TEXT NOT NULL,

                destination TEXT NOT NULL,

                date_time TEXT NOT NULL
            );
        """

        self._execute(query)

    # --------------------------------------------------
    # EXECUTE QUERY
    # --------------------------------------------------

    def _execute(
        self,
        query: str,
        parameters: Optional[tuple] = None
    ) -> sqlite3.Cursor:

        if self._connection is None:

            raise RuntimeError(
                "Database connection is not initialized."
            )

        try:

            cursor = self._connection.cursor()

            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            self._connection.commit()

            return cursor

        except sqlite3.Error as error:

            raise RuntimeError(
                f"Database execution failed: {error}"
            ) from error

    # --------------------------------------------------
    # INSERT LOG
    # --------------------------------------------------

    def insert_log(
        self,
        file_name: str,
        category: str,
        destination: str,
        date_time: Optional[str] = None
    ) -> None:
        """Insert file organization log."""

        timestamp = (
            date_time
            or datetime.now().isoformat(
                sep=" ",
                timespec="seconds"
            )
        )

        query = f"""
            INSERT INTO {self.table_name}
            (
                file_name,
                category,
                destination,
                date_time
            )
            VALUES (?, ?, ?, ?);
        """

        self._execute(
            query,
            (
                file_name,
                category,
                destination,
                timestamp
            )
        )

    # --------------------------------------------------
    # FETCH LOGS
    # --------------------------------------------------

    def fetch_logs(
        self,
        limit: Optional[int] = None,
        order_desc: bool = True
    ) -> List[Dict[str, Any]]:
        """Fetch organization history logs."""

        order_direction = (
            "DESC"
            if order_desc
            else "ASC"
        )

        limit_clause = (
            f"LIMIT {limit}"
            if limit is not None and limit > 0
            else ""
        )

        query = f"""
            SELECT
                file_name,
                category,
                destination,
                date_time
            FROM {self.table_name}
            ORDER BY date_time
            {order_direction}
            {limit_clause};
        """

        cursor = self._execute(query)

        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    # --------------------------------------------------
    # CLEAR LOGS
    # --------------------------------------------------

    def clear_logs(self) -> None:
        """Delete all stored logs."""

        query = f"""
            DELETE FROM {self.table_name};
        """

        self._execute(query)

    # --------------------------------------------------
    # CLOSE DATABASE
    # --------------------------------------------------

    def close(self) -> None:
        """Close SQLite connection safely."""

        if self._connection:

            self._connection.close()

            self._connection = None

    # --------------------------------------------------
    # CONTEXT MANAGER SUPPORT
    # --------------------------------------------------

    def __enter__(self) -> DatabaseManager:

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ) -> None:

        self.close()'''


from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class DatabaseManager:
    """Manages SQLite storage for Smart File Organizer Pro."""

    DEFAULT_TABLE_NAME = "file_logs"
    DEFAULT_DATABASE_FILE = "database/files.db"

    def __init__(
        self,
        database_path: Optional[str] = None,
        table_name: str = DEFAULT_TABLE_NAME
    ) -> None:

        # ✅ Single fixed DB path (IMPORTANT FOR YOUR BUG FIX)
        self.database_path = Path(database_path or self.DEFAULT_DATABASE_FILE)

        # Create folder if not exists
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.table_name = table_name
        self._connection: Optional[sqlite3.Connection] = None

        self._connect()
        self._create_table_if_needed()

    # --------------------------------------------------
    # CONNECT DB
    # --------------------------------------------------
    def _connect(self) -> None:
        try:
            self._connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row

        except sqlite3.Error as error:
            raise RuntimeError(f"Database connection failed: {error}") from error

    # --------------------------------------------------
    # CREATE TABLE
    # --------------------------------------------------
    def _create_table_if_needed(self) -> None:
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            category TEXT NOT NULL,
            destination TEXT NOT NULL,
            date_time TEXT NOT NULL
        );
        """
        self._execute(query)

    # --------------------------------------------------
    # EXECUTE QUERY
    # --------------------------------------------------
    def _execute(
        self,
        query: str,
        parameters: Optional[tuple] = None
    ) -> sqlite3.Cursor:

        if not self._connection:
            raise RuntimeError("Database not connected.")

        try:
            cursor = self._connection.cursor()

            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            self._connection.commit()
            return cursor

        except sqlite3.Error as error:
            raise RuntimeError(f"Database error: {error}") from error

    # --------------------------------------------------
    # INSERT LOG (FIXED)
    # --------------------------------------------------
    def insert_log(
        self,
        file_name: str,
        category: str,
        destination: str,
        date_time: Optional[str] = None
    ) -> None:

        timestamp = date_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = f"""
        INSERT INTO {self.table_name}
        (file_name, category, destination, date_time)
        VALUES (?, ?, ?, ?);
        """

        self._execute(query, (file_name, category, destination, timestamp))

    # --------------------------------------------------
    # FETCH LOGS (FIXED FOR HISTORY PAGE)
    # --------------------------------------------------
    def fetch_logs(
        self,
        limit: Optional[int] = None,
        order_desc: bool = True
    ) -> List[Dict[str, Any]]:

        order = "DESC" if order_desc else "ASC"
        limit_clause = f"LIMIT {limit}" if limit and limit > 0 else ""

        query = f"""
        SELECT file_name, category, destination, date_time
        FROM {self.table_name}
        ORDER BY id {order}
        {limit_clause};
        """

        cursor = self._execute(query)
        return [dict(row) for row in cursor.fetchall()]

    # --------------------------------------------------
    # CLEAR HISTORY
    # --------------------------------------------------
    def clear_logs(self) -> None:
        self._execute(f"DELETE FROM {self.table_name};")

    # --------------------------------------------------
    # CLOSE CONNECTION
    # --------------------------------------------------
    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    # --------------------------------------------------
    # CONTEXT SUPPORT
    # --------------------------------------------------
    def __enter__(self) -> DatabaseManager:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()