import dataclasses

import pcapi.utils.date as date_utils
from pcapi import settings
from pcapi.models.api_errors import ApiErrors


@dataclasses.dataclass
class AccountApiError:
    code: str
    message: str


EMAIL_UPDATE_LIMIT = AccountApiError(
    code="EMAIL_UPDATE_LIMIT",
    message=f"Tu ne peux pas modifier ton email plus de {settings.MAX_EMAIL_UPDATE_ATTEMPTS} fois en {date_utils.format_time_in_second_to_human_readable(settings.EMAIL_UPDATE_ATTEMPTS_TTL)}.",
)
EMAIL_UPDATE_PENDING = AccountApiError(
    code="EMAIL_UPDATE_PENDING", message="Tu as déjà une demande de modification d'email en cours."
)
WRONG_PASSWORD = AccountApiError(code="WRONG_PASSWORD", message="Le mot de passe est incorrect.")


class EmailUpdateLimitError(ApiErrors):
    def __init__(self) -> None:
        super().__init__(
            errors={
                "message": EMAIL_UPDATE_LIMIT.message,
                "error_code": EMAIL_UPDATE_LIMIT.code,
            }
        )


class EmailUpdatePendingError(ApiErrors):
    def __init__(self) -> None:
        super().__init__(
            errors={
                "message": EMAIL_UPDATE_PENDING.message,
                "error_code": EMAIL_UPDATE_PENDING.code,
            }
        )


class WrongPasswordError(ApiErrors):
    def __init__(self) -> None:
        super().__init__(errors={"message": WRONG_PASSWORD.message, "error_code": WRONG_PASSWORD.code})
