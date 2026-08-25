"""
Anonymous statistics about the bonus credit, stored in Redis then logged in batch by a cron.

Bonus credit fraud checks are deleted as soon as a bonus is granted, so the data team cannot count
in database which source granted how many bonus credits. On top of that, we cannot log a grant when
it happens: an disability log emitted at the very same instant than a bonus recredit would disclose
that the recredit comes from a disability allowance.

Both problems are solved by incrementing counters in Redis - which produces no log -
and by logging them in batch through a cron.

Nothing that could identify a beneficiary is recorded here: no user id, no name, no birth date, no
attempt timestamp. The only timestamps published are the ones of the cron runs.
"""

import datetime
import logging
import typing

import redis.exceptions

from pcapi import settings
from pcapi.core.subscription import models as subscription_models
from pcapi.utils import date as date_utils
from pcapi.utils.redis import get_redis_client


logger = logging.getLogger(__name__)

COUNTERS_TECHNICAL_MESSAGE_ID = "bonus_credit.statistics.counters"
ATTEMPT_TECHNICAL_MESSAGE_ID = "bonus_credit.statistics.first_attempt_delays"

_KEY_PREFIX = "pcapi:statistics:bonus_credit"
_COUNTERS_KEY = f"{_KEY_PREFIX}:counters"
_DELAYS_KEY = f"{_KEY_PREFIX}:delays"

# the counters and the delays are published on their own schedule: the counters wait for the
# disability grants to hide in the crowd while the delays are published on every run
_COUNTERS_PUBLISHED_AT_KEY = f"{_KEY_PREFIX}:counters_published_at"
_DELAYS_PUBLISHED_AT_KEY = f"{_KEY_PREFIX}:delays_published_at"

_ERRORS_FIELD = "errors"
_GRANTS_FIELD = "grants"
_ATTEMPTS_FIELD = "attempts_until_grant"


def record_first_bonus_attempt(seconds_since_eighteenth_recredit: int) -> None:
    """
    Increments the delay bucket of a beneficiary filling their first bonus form. The delay is
    bucketed here and never stored as is, so that not even Redis holds a delay precise enough to be
    joined back to a beneficiary.

    The first attempt delays measure how long a beneficiary takes to fill either manual bonus form
    after their eighteenth recredit, so that `BONUS_CREDIT_DELAY` and `BONUS_CREDIT_DELAY_JITTER` can
    be set past the median.
    """
    # A bucket histogram is needed to prevent guessing disability bonus credits through info subtraction using attempt timings.
    _DELAY_BUCKET_LOWER_BOUNDS = [
        0,  # less than one hour
        60 * 60,  # one hour
        6 * 60 * 60,  # six hours
        24 * 60 * 60,  # one day
        2 * 24 * 60 * 60,  # two days
        3 * 24 * 60 * 60,  # three days
        7 * 24 * 60 * 60,  # one week
        14 * 24 * 60 * 60,  # two weeks
        28 * 24 * 60 * 60,  # four weeks
        42 * 24 * 60 * 60,  # six weeks
        70 * 24 * 60 * 60,  # ten weeks
    ]
    bucket_lower_bound = max(
        bound for bound in _DELAY_BUCKET_LOWER_BOUNDS if bound <= seconds_since_eighteenth_recredit
    )
    get_redis_client().hincrby(_DELAYS_KEY, str(bucket_lower_bound), 1)


def record_bonus_attempt(
    bonus_type: subscription_models.FraudCheckType,
    reason_codes: list[subscription_models.FraudReasonCode],
    attempts_until_grant: int | None = None,
) -> None:
    """
    Increments the counters of a single completed bonus credit attempt. Never logs anything about
    the attempt itself, and never records anything but counters: see this module docstring.

    reason_codes: the causes that prevented the bonus credits
    attempts_until_grant: how many bonus forms the beneficiary had filled, this attempt
    included, when it granted them their bonus credit. None when the attempt granted nothing, zero
    when the bonus credit was granted by an automatic attempt.
    """
    if bonus_type not in subscription_models.BONUS_CREDIT_CHECK_TYPES:
        return

    redis_client = get_redis_client()
    with redis_client.pipeline(transaction=True) as pipeline:
        for reason_code in reason_codes:
            pipeline.hincrby(_COUNTERS_KEY, f"{_ERRORS_FIELD}|{bonus_type.value}|{reason_code.value}", 1)

        if attempts_until_grant is not None:
            pipeline.hincrby(_COUNTERS_KEY, f"{_GRANTS_FIELD}|{bonus_type.value}", 1)
            pipeline.hincrby(_COUNTERS_KEY, f"{_ATTEMPTS_FIELD}|{attempts_until_grant}", 1)

        pipeline.execute()


def log_bonus_credit_counters() -> None:
    try:
        counters, counters_published_at = _read_from_redis(_COUNTERS_KEY, _COUNTERS_PUBLISHED_AT_KEY)
    except redis.exceptions.RedisError:
        logger.exception("Could not read the bonus credit counters from Redis")
        return

    if not counters:
        logger.info("No bonus credit statistics to report")
        return

    now = date_utils.get_naive_utc_now()
    can_publish_counters = bool(counters) and _are_disability_grants_hidden(counters)
    if not can_publish_counters:
        logger.info("Quotient Familial crowd is not thick enough")
        return

    try:
        _consume(_COUNTERS_KEY, _COUNTERS_PUBLISHED_AT_KEY, counters, now)
    except redis.exceptions.RedisError:
        logger.exception("Could not consume the bonus credit counters")
        return

    logger.info(
        "Bonus credit counters",
        extra={
            "published_at": now.isoformat(),
            "counters_since": counters_published_at,
            "counters": _build_counters_payload(counters) if can_publish_counters else None,
        },
        technical_message_id=COUNTERS_TECHNICAL_MESSAGE_ID,
    )


def log_first_bonus_credit_attempt_delays() -> None:
    try:
        delays, delays_published_at = _read_from_redis(_DELAYS_KEY, _DELAYS_PUBLISHED_AT_KEY)
    except redis.exceptions.RedisError:
        logger.exception("Could not read the first bonus credit attempt statistics from Redis")
        return

    if not delays:
        logger.info("No bonus credit attempt delays to report")
        return

    now = date_utils.get_naive_utc_now()
    try:
        _consume(_DELAYS_KEY, _DELAYS_PUBLISHED_AT_KEY, delays, now)
    except redis.exceptions.RedisError:
        logger.exception("Could not consume the first bonus credit attempt statistics")
        return

    logger.info(
        "Bonus credit first attempt delays",
        extra={
            "published_at": now.isoformat(),
            "first_attempt_delays_since": delays_published_at,
            "first_attempt_delays": delays,
        },
        technical_message_id=ATTEMPT_TECHNICAL_MESSAGE_ID,
    )


def _read_from_redis(key: str, published_at_key: str) -> tuple[dict[str, int], str | None]:
    redis_client = get_redis_client()
    with redis_client.pipeline(transaction=True) as pipeline:
        pipeline.hgetall(key)
        pipeline.get(published_at_key)
        counters, published_at = pipeline.execute()

    non_empty_counters = {field: int(count) for field, count in counters.items() if int(count) > 0}
    return non_empty_counters, published_at


def _consume(key: str, published_at_key: str, counters: dict[str, int], published_at: datetime.datetime) -> None:
    redis_client = get_redis_client()
    with redis_client.pipeline(transaction=True) as pipeline:
        for field, count in counters.items():
            # subtract instead of setting to zero to prevent overwrite in case of concurrent writes
            pipeline.hincrby(key, field, -count)
        pipeline.set(published_at_key, published_at.isoformat())
        pipeline.execute()


def _are_disability_grants_hidden(counters: dict[str, int]) -> bool:
    _DISABILITY_TYPES = (
        subscription_models.FraudCheckType.AAH_BONUS_CREDIT,
        subscription_models.FraudCheckType.AEEH_BONUS_CREDIT,
    )
    disability_bonuses = sum(counters.get(f"{_GRANTS_FIELD}|{bonus_type.value}", 0) for bonus_type in _DISABILITY_TYPES)
    quotient_bonuses = counters.get(f"{_GRANTS_FIELD}|{subscription_models.FraudCheckType.QF_BONUS_CREDIT.value}", 0)

    is_crowd_big_enough = quotient_bonuses >= settings.MIN_QUOTIENT_FAMILIAL_BONUSES_TO_PUBLISH
    is_crowd_dense_enough = quotient_bonuses >= settings.MIN_QUOTIENT_FAMILIAL_PER_DISABILITY_BONUS * disability_bonuses

    return is_crowd_big_enough and is_crowd_dense_enough


def _build_counters_payload(counters: dict[str, int]) -> dict[str, typing.Any]:
    payload: dict[str, typing.Any] = {
        _GRANTS_FIELD: {},
        _ERRORS_FIELD: {},
        _ATTEMPTS_FIELD: {},
    }

    for field, count in counters.items():
        field_parts = field.split("|")

        if len(field_parts) == 2 and field_parts[0] in (_GRANTS_FIELD, _ATTEMPTS_FIELD):
            field, bonus_type = field_parts
            payload[field][bonus_type] = count

        elif len(field_parts) == 3 and field_parts[0] == _ERRORS_FIELD:
            error_field, bonus_type, reason_code = field_parts
            payload[error_field].setdefault(bonus_type, {})[reason_code] = count

        else:
            logger.error("Unexpected bonus credit statistics counter %s", field)

    return payload
