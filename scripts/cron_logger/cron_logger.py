from scripts.cron_logger import cron_status


def build_cron_log_message(name: str, status: cron_status, traceback = None, duration:int = None):

    log_message = f"type=cron name={name} status={status}"

    if duration:
        log_message += f" duration={duration}"

    if traceback:
        oneline_stack = ''.join(traceback).replace('\n', ' ### ')
        log_message += f" stacktrace={oneline_stack}"

    return log_message
