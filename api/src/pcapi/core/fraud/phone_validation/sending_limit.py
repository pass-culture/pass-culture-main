from datetime import datetime
from datetime import timedelta
import typing

from redis import Redis

from pcapi import settings
from pcapi.core.users.models import User


def _sent_SMS_counter_key_name(user: User) -> str:
    return f"sent_SMS_counter_user_{user.id}"


def update_sent_SMS_counter(redis: Redis, user: User) -> None:
    key_name = _sent_SMS_counter_key_name(user)
    count = redis.incr(key_name)
    if count == 1:
        redis.expire(key_name, settings.SENT_SMS_COUNTER_TTL)


def is_SMS_sending_allowed(redis: Redis, user: User) -> bool:
    sent_SMS_count = redis.get(_sent_SMS_counter_key_name(user))

    return not sent_SMS_count or int(sent_SMS_count) < settings.MAX_SMS_SENT_FOR_PHONE_VALIDATION


def get_remaining_attempts(redis: Redis, user: User) -> int:
    sent_SMS_count = redis.get(_sent_SMS_counter_key_name(user))

    if sent_SMS_count:
        return max(settings.MAX_SMS_SENT_FOR_PHONE_VALIDATION - int(sent_SMS_count), 0)
    return settings.MAX_SMS_SENT_FOR_PHONE_VALIDATION


def get_attempt_limitation_expiration_time(redis: Redis, user: User) -> typing.Optional[datetime]:
    ttl = redis.ttl(_sent_SMS_counter_key_name(user))
    if ttl > 0:
        return datetime.utcnow() + timedelta(seconds=ttl)

    return None
