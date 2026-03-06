from pcapi import settings

from ..api import send_internal_message


def send(names: list[str]) -> None:
    message = "Index PostgreSQL invalide" if len(names) == 1 else "Indexes PostgreSQL invalides"
    send_internal_message(
        channel=settings.SLACK_DATABASE_ALERT_CHANNEL,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{message} en environnement {settings.ENV} : {', '.join(names)}",
                },
            }
        ],
        icon_emoji=":warning:",
    )
