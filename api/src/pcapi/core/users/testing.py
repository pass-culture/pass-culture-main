sendinblue_requests = []


def reset_sendinblue_requests():  # type: ignore [no-untyped-def]
    global sendinblue_requests  # pylint: disable=global-statement
    sendinblue_requests = []
