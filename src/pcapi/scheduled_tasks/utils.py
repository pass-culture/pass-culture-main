import apscheduler.events as cron_events
import apscheduler.schedulers.base as base_schedulers
import sentry_sdk


def sentry_listener(event: cron_events.JobExecutionEvent) -> None:
    if event.exception:
        exc_info = type(event.exception), event.exception, event.exception.__traceback__
        sentry_sdk.capture_exception(exc_info)


def activate_sentry(scheduler: base_schedulers.BaseScheduler) -> None:
    scheduler.add_listener(sentry_listener, cron_events.EVENT_JOB_ERROR)
