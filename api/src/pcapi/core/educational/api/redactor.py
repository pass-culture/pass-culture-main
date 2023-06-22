from typing import Any

from pcapi.core.educational import models
from pcapi.repository import repository


def save_redactor_preferences(redactor: models.EducationalRedactor, **preferences: Any) -> None:
    redactor.preferences = {**redactor.preferences, **preferences}
    repository.save(redactor)
