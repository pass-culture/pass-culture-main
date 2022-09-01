from pcapi import settings
from pcapi.core.subscription.dms import models as dms_models


INBOX_URL = "passculture://openInbox"
MAILTO_SUPPORT = f"mailto:{settings.SUPPORT_EMAIL_ADDRESS}"
REDIRECT_TO_DMS_VIEW = "passculture://verification-identite/demarches-simplifiees"
REDIRECT_TO_IDENTIFICATION = "passculture://verification-identite/identification"

MAILTO_SUPPORT_PARAMS = "?subject=%23{id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e"


def _generate_form_field_error(
    error_text_singular: str, error_text_plural: str, error_fields: list[dms_models.DmsFieldErrorDetails]
) -> str:
    field_text = ", ".join(field.get_field_label() for field in error_fields)
    if len(error_fields) == 1:
        user_message = error_text_singular.format(formatted_error_fields=field_text)
    else:
        user_message = error_text_plural.format(formatted_error_fields=field_text)

    return user_message
