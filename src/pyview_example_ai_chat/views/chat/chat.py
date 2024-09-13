from pyview import LiveView, LiveViewSocket
from pyview.events import InfoEvent
from dataclasses import dataclass, field
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import Literal, Iterable
import os

import markdown as md
from markupsafe import Markup
from pyview.vendor.ibis import filters


@filters.register
def markdown(text):
    return Markup(
        md.markdown(
            text,
            extensions=["fenced_code", "codehilite"],
            extension_configs={"codehilite": {"css_class": "highlight"}},
        )
    )


client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@dataclass
class ChatMessage:
    message: str
    role: Literal["user", "assistant"] = "user"

    def append(self, message: str):
        self.message += message


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
    current_model: str = "gpt-4o-mini"
    available_models: list[str] = field(
        default_factory=lambda: [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ]
    )


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
        elif event == "change_model" and "model" in payload:
            socket.context.current_model = payload["model"][0]

    async def handle_info(self, event, socket: LiveViewSocket[ChatContext]):
        if event.name == "response":
            if event.payload:
                current_message = socket.context.current.messages[-1]
                current_message.append(event.payload)
            return

        input = socket.context.current.chat_input

        chat_completion = await client.chat.completions.create(
            messages=input,
            model=socket.context.current_model,
            stream=True,
        )

        socket.context.current.messages.append(
            ChatMessage(message="", role="assistant")
        )

        async for chunk in chat_completion:
            part = chunk.choices[0].delta.content
            socket.schedule_info_once(InfoEvent("response", part))

        socket.context.loading = False
