from redis import Redis

from pcapi import settings
from pcapi.core.users.models import User


def _sent_SMS_counter_key_name(user: User):  # type: ignore [no-untyped-def]
    return f"sent_SMS_counter_user_{user.id}"


def update_sent_SMS_counter(redis: Redis, user: User):  # type: ignore [no-untyped-def]
    key_name = _sent_SMS_counter_key_name(user)
    count = redis.incr(key_name)
    if count == 1:
        redis.expire(key_name, settings.SENT_SMS_COUNTER_TTL)


def is_SMS_sending_allowed(redis: Redis, user: User):  # type: ignore [no-untyped-def]
    sent_SMS_count = redis.get(_sent_SMS_counter_key_name(user))

    return not sent_SMS_count or int(sent_SMS_count) < settings.MAX_SMS_SENT_FOR_PHONE_VALIDATION
