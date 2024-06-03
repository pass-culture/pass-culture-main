from pcapi import settings
from pcapi.core.users.models import User
from pcapi.models.feature import Feature
from pcapi.notifications.internal import send_internal_message
from pcapi.utils import urls


def send(feature: Feature, current_user: User) -> None:
    env_prefix = "" if settings.IS_PROD else """[{}] """.format(settings.ENV)
    status_icon = ":white_check_mark:" if feature.isActive else ":x:"
    edit_link = urls.build_backoffice_feature_flipping_link()

    text = """{env}{status} *{name}* est passé à *{is_active}*\nPar le user_email {email}. <{link}|Modifier>""".format(
        env=env_prefix,
        status=status_icon,
        name=feature.name,
        is_active=feature.isActive,
        email=current_user.email,
        link=edit_link,
    )

    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": text}}]

    send_internal_message(settings.SLACK_CHANGE_FEATURE_FLIP_CHANNEL, blocks=blocks, icon_emoji=":rubber-duck:")
