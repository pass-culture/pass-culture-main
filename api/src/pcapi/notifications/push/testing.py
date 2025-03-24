requests: list[dict | list] = []


def reset_requests() -> None:
    global requests  # pylint: disable=global-statement  # noqa: PLW0603 (global-statement)
    requests = []
