from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

from redis import Redis

from pcapi import settings
from pcapi.core.users.models import User


@dataclass
class PhoneValidationCodeAttempts:
    remaining: int
    attempts: int


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


def get_remaining_sms_sending_attempts(redis: Redis, user: User) -> int:
    sent_SMS_count = redis.get(_sent_SMS_counter_key_name(user))

    if sent_SMS_count:
        return max(settings.MAX_SMS_SENT_FOR_PHONE_VALIDATION - int(sent_SMS_count), 0)
    return settings.MAX_SMS_SENT_FOR_PHONE_VALIDATION


def get_attempt_limitation_expiration_time(redis: Redis, user: User) -> datetime | None:
    ttl = redis.ttl(_sent_SMS_counter_key_name(user))
    if ttl > 0:
        return datetime.utcnow() + timedelta(seconds=ttl)

    return None


def get_code_validation_attempts(redis: Redis, user: User) -> PhoneValidationCodeAttempts:
    phone_validation_attempts_key = f"phone_validation_attempts_user_{user.id}"
    phone_validation_attempts = redis.get(phone_validation_attempts_key)

    if phone_validation_attempts:
        remaining_attempts = max(settings.MAX_PHONE_VALIDATION_ATTEMPTS - int(phone_validation_attempts), 0)
        return PhoneValidationCodeAttempts(attempts=int(phone_validation_attempts), remaining=remaining_attempts)

    return PhoneValidationCodeAttempts(attempts=0, remaining=settings.MAX_PHONE_VALIDATION_ATTEMPTS)
