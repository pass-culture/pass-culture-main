outbox: list = []


def reset_outbox() -> None:
    global outbox  # pylint: disable=global-statement
    outbox = []
