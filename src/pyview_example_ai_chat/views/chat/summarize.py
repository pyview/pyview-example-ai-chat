from pyview_example_ai_chat.views.chat.models.chat_message import ChatMessage
from openai import AsyncOpenAI
from typing import Optional


async def summarize_chat_session(
    client: AsyncOpenAI, messages: list[ChatMessage]
) -> Optional[str]:
    conversation = "\n".join([f"{m.role}: {m.message}" for m in messages])

    prompt = f"""
Please write a short summary title of the conversion below (max 25 characters), no quotes or special characters:

{conversation}
"""

    chat_completion = await client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="gpt-4-turbo",
    )

    summary = chat_completion.choices[0].message.content
    return summary
