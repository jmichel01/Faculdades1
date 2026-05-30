import sqlite3
import datetime
import logging
from contextlib import contextmanager
from typing import Generator
from config.settings import Settings

sqlite3.register_converter("date", lambda b: datetime.date.fromisoformat(b.decode()))
sqlite3.register_converter("timestamp", lambda b: datetime.datetime.fromisoformat(b.decode()))

logger = logging.getLogger("optilogix.database")

class DatabaseConnectionManager:
    
    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator[sqlite3.Connection, None, None]:
        conn = None
        try:
            conn = sqlite3.connect(
                str(Settings.DB_PATH),
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            )
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.row_factory = sqlite3.Row
            
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"SQLite database error: {e}", exc_info=True)
            raise e
        finally:
            if conn:
                conn.close()
#A
