from pyview import LiveView, LiveViewSocket
from pyview.events import InfoEvent
from dataclasses import dataclass, field
from openai import AsyncOpenAI
from pyview_example_ai_chat.views.chat.models.chat_message import (
    ChatMessage,
    ChatSession,
)
from pyview_example_ai_chat.views.chat.storage.chat_storage import (
    ChatStorage,
    SqliteChatStorage,
)
from pyview_example_ai_chat.views.chat.summarize import summarize_chat_session
import os


client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


@dataclass
class ChatContext:
    current_session: ChatSession = field(default_factory=ChatSession)
    messages: list[ChatMessage] = field(default_factory=list)
    all_sessions: list[ChatSession] = field(default_factory=list)

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


chat_storage: ChatStorage = SqliteChatStorage()


class ChatView(LiveView[ChatContext]):
    async def mount(self, socket: LiveViewSocket[ChatContext], _session):
        socket.context = ChatContext(all_sessions=chat_storage.list_chat_sessions())

    async def handle_event(self, event, payload, socket: LiveViewSocket[ChatContext]):
        if event == "send" and "message" in payload:
            socket.context.loading = True
            socket.context.current_session = chat_storage.save_chat_session(
                socket.context.current_session
            )
            new_message = ChatMessage(message=payload["message"][0], role="user")
            chat_storage.save_chat_message(
                socket.context.current_session.id, new_message
            )

            socket.context.messages.append(new_message)
            socket.schedule_info_once(InfoEvent("chat"))

        elif event == "change_model" and "model" in payload:
            socket.context.current_model = payload["model"][0]
        elif event == "new_chat":
            socket.context = ChatContext(all_sessions=chat_storage.list_chat_sessions())
            await socket.push_patch("/")

    async def handle_info(self, event, socket: LiveViewSocket[ChatContext]):
        if event.name == "summarize":
            chat_storage.save_chat_message(
                socket.context.current_session.id, socket.context.messages[-1]
            )
            socket.context.current_session.summary = await summarize_chat_session(
                client, socket.context.messages
            )
            chat_storage.save_chat_session(socket.context.current_session)
            await socket.push_patch(
                "/", {"topic_id": socket.context.current_session.id}
            )
            return

        if event.name == "response":
            if event.payload:
                current_message = socket.context.messages[-1]
                current_message.append(event.payload)
            return

        input = [m.to_chat_input() for m in socket.context.messages]

        chat_completion = await client.chat.completions.create(
            messages=input,
            model=socket.context.current_model,
            stream=True,
        )

        new_message = ChatMessage(message="", role="assistant")
        chat_storage.save_chat_message(socket.context.current_session.id, new_message)
        socket.context.messages.append(new_message)

        async for chunk in chat_completion:
            part = chunk.choices[0].delta.content
            socket.schedule_info_once(InfoEvent("response", part))

        socket.schedule_info_once(InfoEvent("summarize"))
        socket.context.loading = False

    async def handle_params(self, url, params, socket: LiveViewSocket[ChatContext]):
        if "topic_id" in params:
            topic_id = params["topic_id"][0]
            chat_session = chat_storage.get_chat_session(topic_id)
            if not chat_session:
                if socket.connected:
                    await socket.push_patch("/", {})
                return
            socket.context.current_session, socket.context.messages = chat_session
            socket.context.all_sessions = chat_storage.list_chat_sessions()
