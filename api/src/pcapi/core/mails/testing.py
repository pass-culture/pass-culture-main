outbox: list = []


def reset_outbox() -> None:
    global outbox  # noqa: PLW0603 (global-statement)
    outbox = []
