from dataclasses import dataclass, field
from typing import Literal, Optional
from openai.types.chat import ChatCompletionMessageParam
from datetime import datetime
import uuid


@dataclass
class ChatMessage:
    message: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    role: Literal["user", "assistant"] = "user"
    ts: datetime = field(default_factory=datetime.now)

    def append(self, message: str):
        self.message += message

    def to_chat_input(self) -> ChatCompletionMessageParam:
        return {"role": self.role, "content": self.message}  # type: ignore


@dataclass
class ChatSession:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    ts: datetime = field(default_factory=datetime.now)
    summary: Optional[str] = None
