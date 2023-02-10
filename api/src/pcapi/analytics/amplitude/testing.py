requests = []  # type: ignore [var-annotated]


def reset_requests() -> None:
    global requests  # pylint: disable=global-statement
    requests = []
