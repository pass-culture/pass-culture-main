import typing

from pcapi import settings


# Queues for asynchronous call to external services
CELERY_EXTERNAL_CALLS_DEFAULT_QUEUE_NAME = "celery.external_calls.default"  # Default priority
CELERY_EXTERNAL_CALLS_PRIORITY_QUEUE_NAME = "celery.external_calls.priority"  # High priority

# Queues for asynchronous call to internal functions
CELERY_INTERNAL_CALLS_DEFAULT_QUEUE_NAME = "celery.internal_calls.default"  # Default priority
CELERY_INTERNAL_CALLS_PRIORITY_QUEUE_NAME = "celery.internal_calls.priority"  # High priority

CELERY_BASE_SETTINGS: typing.Final = dict(
    broker_url=settings.REDIS_URL,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # We must prefix celery queues with "celery." to easily monitor
    # their length using the redis prometheus exporter
    task_routes={
        "tasks.mails.default.*": {"queue": CELERY_EXTERNAL_CALLS_DEFAULT_QUEUE_NAME},
        "tasks.mails.priority.*": {"queue": CELERY_EXTERNAL_CALLS_PRIORITY_QUEUE_NAME},
        "tasks.ubble.default.*": {"queue": CELERY_EXTERNAL_CALLS_DEFAULT_QUEUE_NAME},
        "tasks.ubble.priority.*": {"queue": CELERY_EXTERNAL_CALLS_PRIORITY_QUEUE_NAME},
        "tasks.offers.default.*": {"queue": CELERY_INTERNAL_CALLS_DEFAULT_QUEUE_NAME},
        "tasks.offers.priority.*": {"queue": CELERY_INTERNAL_CALLS_PRIORITY_QUEUE_NAME},
        "tasks.operations.default.*": {"queue": CELERY_INTERNAL_CALLS_PRIORITY_QUEUE_NAME},
        "tasks.batch_updates.default.*": {"queue": CELERY_INTERNAL_CALLS_DEFAULT_QUEUE_NAME},
        "tasks.batch_updates.priority.*": {"queue": CELERY_INTERNAL_CALLS_PRIORITY_QUEUE_NAME},
        "tasks.api_particulier.default.*": {"queue": CELERY_EXTERNAL_CALLS_DEFAULT_QUEUE_NAME},
    },
    task_ignore_result=True,
)
