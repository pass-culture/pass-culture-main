outbox = []


def reset_outbox():  # type: ignore [no-untyped-def]
    global outbox  # pylint: disable=global-statement
    outbox = []
