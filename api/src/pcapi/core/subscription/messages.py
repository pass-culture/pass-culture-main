from pcapi import settings
from pcapi.core.subscription import models


MAILTO_SUPPORT = f"mailto:{settings.SUPPORT_EMAIL_ADDRESS}"
MAILTO_SUPPORT_PARAMS = "?subject=%23{id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e"

MAINTENANCE_PAGE_MESSAGE = models.SubscriptionMessage(
    user_message="La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite.",
    call_to_action=None,
    pop_over_icon=models.PopOverIcon.CLOCK,
)

REDIRECT_TO_DMS_VIEW_LINK = "passculture://verification-identite/demarches-simplifiees"
REDIRECT_TO_DMS_CALL_TO_ACTION = models.CallToActionMessage(
    title="Accéder au site Démarches-Simplifiées",
    link=REDIRECT_TO_DMS_VIEW_LINK,
    icon=models.CallToActionIcon.EXTERNAL,
)


def compute_support_call_to_action(user_id: int) -> models.CallToActionMessage:
    return models.CallToActionMessage(
        title="Contacter le support",
        link=MAILTO_SUPPORT + MAILTO_SUPPORT_PARAMS.format(id=user_id),
        icon=models.CallToActionIcon.EMAIL,
    )
