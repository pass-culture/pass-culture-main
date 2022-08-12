sendinblue_requests: list[dict] = []
zendesk_requests: list[dict] = []
zendesk_sell_requests: list[dict] = []


def reset_sendinblue_requests() -> None:
    global sendinblue_requests  # pylint: disable=global-statement
    sendinblue_requests = []


def reset_zendesk_requests() -> None:
    global zendesk_requests  # pylint: disable=global-statement
    zendesk_requests = []


def reset_zendesk_sell_requests() -> None:
    global zendesk_sell_requests  # pylint: disable=global-statement
    zendesk_sell_requests = []
