"""Conversation history, stored server side.

The client only knows the conversation id: it can never forge past assistant
turns. Keys are scoped by user, so a user cannot read another user's conversation.
"""

import json

from pcapi import settings
from pcapi.utils.redis import get_redis_client


def _get_key(user_id: int, conversation_id: str) -> str:
    return f"pcapi:pro_assistant:conversation:{user_id}:{conversation_id}"


def load_messages(user_id: int, conversation_id: str) -> list[dict] | None:
    raw_messages = get_redis_client().get(_get_key(user_id, conversation_id))
    if raw_messages is None:
        return None
    return json.loads(raw_messages)


def save_messages(user_id: int, conversation_id: str, messages: list[dict]) -> None:
    get_redis_client().set(
        _get_key(user_id, conversation_id),
        json.dumps(messages, ensure_ascii=False),
        ex=settings.PRO_ASSISTANT_CONVERSATION_TTL,
    )
