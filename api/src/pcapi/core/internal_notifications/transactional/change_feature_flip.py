from pcapi import settings
from pcapi.core.internal_notifications.api import send_internal_message
from pcapi.core.users.models import User
from pcapi.models.feature import Feature
from pcapi.utils import urls


def send(feature: Feature, current_user: User) -> None:
    env_prefix = "" if settings.IS_PROD else f"""[{settings.ENV}] """
    status_icon = ":white_check_mark:" if feature.isActive else ":x:"
    edit_link = urls.build_backoffice_feature_flipping_link()

    text = f"""{env_prefix}{status_icon} *{feature.name}* est passé à *{feature.isActive}*\nPar le user_email {current_user.email}. <{edit_link}|Modifier>"""

    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]

    send_internal_message(settings.SLACK_CHANGE_FEATURE_FLIP_CHANNEL, blocks=blocks, icon_emoji=":rubber-duck:")
