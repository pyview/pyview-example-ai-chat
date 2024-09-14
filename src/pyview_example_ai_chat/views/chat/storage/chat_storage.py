from typing import Protocol, Optional
from pyview_example_ai_chat.views.chat.models.chat_message import (
    ChatSession,
    ChatMessage,
)
import sqlite3
import uuid


class ChatStorage(Protocol):
    def list_chat_sessions(self) -> list[ChatSession]: ...
    def get_chat_session(
        self, id: str
    ) -> Optional[tuple[ChatSession, list[ChatMessage]]]: ...
    def save_chat_session(self, session: ChatSession) -> ChatSession: ...
    def save_chat_message(
        self, session_id: str, message: ChatMessage
    ) -> ChatMessage: ...


class SqliteChatStorage(ChatStorage):
    def __init__(self, db_file: str = "chats.db") -> None:
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                ts TEXT,
                summary TEXT
            )
            """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                message TEXT,
                role TEXT,
                ts TEXT
            )
            """
        )
        self.conn.commit()

    def list_chat_sessions(self) -> list[ChatSession]:
        self.cursor.execute("SELECT * FROM chat_sessions")
        return [
            ChatSession(id=row[0], ts=row[1], summary=row[2])
            for row in self.cursor.fetchall()
        ]

    def get_chat_session(
        self, id: str
    ) -> Optional[tuple[ChatSession, list[ChatMessage]]]:
        self.cursor.execute("SELECT * FROM chat_sessions WHERE id=?", (id,))

        row = self.cursor.fetchone()
        if row is None:
            return None
        session = ChatSession(id=id, ts=row[1], summary=row[2])
        self.cursor.execute("SELECT * FROM chat_messages WHERE session_id=?", (id,))
        messages = [
            ChatMessage(id=row[0], message=row[2], role=row[3], ts=row[4])
            for row in self.cursor.fetchall()
        ]
        return session, messages

    def save_chat_session(self, session: ChatSession) -> ChatSession:
        if session.id is None:
            session.id = uuid.uuid4().hex
        self.cursor.execute(
            "INSERT OR REPLACE INTO chat_sessions (id, ts, summary) VALUES (?, ?, ?)",
            (session.id, session.ts, session.summary),
        )
        self.conn.commit()
        return session

    def save_chat_message(self, session_id: str, message: ChatMessage) -> ChatMessage:
        self.cursor.execute(
            """
            INSERT OR REPLACE INTO chat_messages (id, session_id, message, role, ts)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message.id, session_id, message.message, message.role, message.ts),
        )
        self.conn.commit()
        return message
