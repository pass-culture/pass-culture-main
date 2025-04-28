sendinblue_requests: list[dict] = []
zendesk_requests: list[dict] = []
zendesk_sell_requests: list[dict] = []


def reset_sendinblue_requests() -> None:
    global sendinblue_requests  # noqa: PLW0603 (global-statement)
    sendinblue_requests = []


def reset_zendesk_requests() -> None:
    global zendesk_requests  # noqa: PLW0603 (global-statement)
    zendesk_requests = []


def reset_zendesk_sell_requests() -> None:
    global zendesk_sell_requests  # noqa: PLW0603 (global-statement)
    zendesk_sell_requests = []
