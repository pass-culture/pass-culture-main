import dataclasses

from pcapi.models.api_errors import ApiErrors


@dataclasses.dataclass
class AccountApiError:
    code: str
    message: str


EMAIL_ALREADY_EXISTS = AccountApiError(
    code="EMAIL_ALREADY_EXISTS", message="Cet email est déjà utilisé par un autre compte."
)
EMAIL_UPDATE_LIMIT = AccountApiError(
    code="EMAIL_UPDATE_LIMIT", message="Tu ne peux pas modifier ton email plus de 2 fois par 72h."
)
EMAIL_UPDATE_PENDING = AccountApiError(
    code="EMAIL_UPDATE_PENDING", message="Tu as déjà une demande de modification d'email en cours."
)
WRONG_PASSWORD = AccountApiError(code="WRONG_PASSWORD", message="Le mot de passe est incorrect.")


class EmailAlreadyExistsError(ApiErrors):
    def __init__(self, errors: dict = None, status_code: int | None = None):
        super().__init__(
            errors={
                "message": EMAIL_ALREADY_EXISTS.message,
                "error_code": EMAIL_ALREADY_EXISTS.code,
            }
        )


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
