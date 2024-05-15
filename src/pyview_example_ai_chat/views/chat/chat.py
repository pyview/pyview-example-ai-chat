from pyview import LiveView, LiveViewSocket
from pyview.events import InfoEvent
from dataclasses import dataclass, field
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import Literal, Iterable
import os

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@dataclass
class ChatMessage:
    message: str
    role: Literal["user", "assistant"] = "user"


@dataclass
class ChatRecord:
    messages: list[ChatMessage] = field(default_factory=list)

    @property
    def chat_input(self) -> Iterable[ChatCompletionMessageParam]:
        return [{"role": m.role, "content": m.message} for m in self.messages]  # type: ignore


@dataclass
class ChatContext:
    current: ChatRecord = field(default_factory=ChatRecord)
    loading: bool = False


class ChatView(LiveView[ChatContext]):
    async def mount(self, socket: LiveViewSocket[ChatContext], _session):
        socket.context = ChatContext()

    async def handle_event(self, event, payload, socket: LiveViewSocket[ChatContext]):
        if event == "send" and "message" in payload:
            socket.context.loading = True
            socket.context.current.messages.append(
                ChatMessage(message=payload["message"][0])
            )
            socket.schedule_info_once(InfoEvent("chat"))

    async def handle_info(self, event, socket: LiveViewSocket[ChatContext]):
        input = socket.context.current.chat_input

        chat_completion = await client.chat.completions.create(
            messages=input,
            model="gpt-3.5-turbo",
        )

        message = chat_completion.choices[0].message

        socket.context.current.messages.append(
            ChatMessage(message=message.content or "", role=message.role)
        )
        socket.context.loading = False
