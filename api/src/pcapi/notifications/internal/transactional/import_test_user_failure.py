from pcapi import settings
from pcapi.notifications.internal import send_internal_message


def send() -> None:
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "L'import d'utilisateurs depuis le fichier Google a échoué. Une fois le problème corrigé,"
                "veuillez relancer le script `rebuild_staging.sh` dans un pod console de staging.",
            },
        }
    ]
    send_internal_message(settings.SLACK_REBUILD_STAGING_CHANNEL, blocks=blocks, icon_emoji=":bomb:")
