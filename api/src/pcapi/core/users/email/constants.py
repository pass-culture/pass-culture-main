from pcapi.core.users import models


EMAIL_HISTORY_EVENT_TYPE_LABELS = {
    models.EmailHistoryEventTypeEnum.UPDATE_REQUEST: "Demande de changement d'email",
    models.EmailHistoryEventTypeEnum.NEW_EMAIL_SELECTION: "Saisie d'une nouvelle adresse email",
    models.EmailHistoryEventTypeEnum.CONFIRMATION: "Confirmation de changement d'email",
    models.EmailHistoryEventTypeEnum.CANCELLATION: "Annulation de changement d'email",
    models.EmailHistoryEventTypeEnum.VALIDATION: "Validation de changement d'email",
    models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION: "Validation de changement d'email (interne)",
    models.EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST: "Demande de changement d'email (interne)",
    models.EmailHistoryEventTypeEnum.ADMIN_UPDATE: "Changement d'email (interne)",
}

assert set(EMAIL_HISTORY_EVENT_TYPE_LABELS) == set(models.EmailHistoryEventTypeEnum)

ADMIN_EMAIL_HISTORY_EVENT_TYPES = {
    models.EmailHistoryEventTypeEnum.ADMIN_UPDATE_REQUEST,
    models.EmailHistoryEventTypeEnum.ADMIN_VALIDATION,
    models.EmailHistoryEventTypeEnum.ADMIN_UPDATE,
}
