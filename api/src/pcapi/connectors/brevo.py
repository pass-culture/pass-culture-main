import brevo

from pcapi import settings


def get_client(use_pro_subaccount: bool, timeout: int) -> brevo.Brevo:
    api_key = settings.SENDINBLUE_PRO_API_KEY if use_pro_subaccount else settings.SENDINBLUE_API_KEY
    return brevo.Brevo(
        api_key=api_key,
        base_url=settings.EMAIL_BACKEND_URL or None,  # to avoid empty str
        timeout=timeout,
    )
