requests: list[dict] = []


def reset_requests() -> None:
    global requests  # noqa: PLW0603 (global-statement)
    requests = []
