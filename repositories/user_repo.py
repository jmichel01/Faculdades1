import sqlite3
from typing import List, Optional
from database.connection import DatabaseConnectionManager
from models.domain import User
from repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    """
    CRUD repository for the User entity.
    """
    def __init__(self) -> None:
        super().__init__("optilogix.repository.user")

    def save(self, user: User) -> User:
        query = """
            INSERT INTO users (username, role)
            VALUES (?, ?)
            ON CONFLICT(username) DO UPDATE SET role = excluded.role
            RETURNING id, created_at;
        """
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (user.username, user.role))
            row = cursor.fetchone()
            if row:
                user.id = row["id"]
                user.created_at = row["created_at"]
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        query = "SELECT id, username, role, created_at FROM users WHERE username = ?"
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row["id"],
                    username=row["username"],
                    role=row["role"],
                    created_at=row["created_at"]
                )
        return None

    def list_all(self) -> List[User]:
        query = "SELECT id, username, role, created_at FROM users ORDER BY username ASC"
        users = []
        with DatabaseConnectionManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                users.append(User(
                    id=row["id"],
                    username=row["username"],
                    role=row["role"],
                    created_at=row["created_at"]
                ))
        return users
