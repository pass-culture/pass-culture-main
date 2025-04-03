outbox: list = []


def reset_outbox() -> None:
    global outbox  # pylint: disable=global-statement  # noqa: PLW0603 (global-statement)
    outbox = []
