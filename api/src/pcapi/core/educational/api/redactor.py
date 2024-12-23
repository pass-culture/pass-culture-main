from typing import Any

from pcapi.core.educational import models
from pcapi.models import db


def save_redactor_preferences(redactor: models.EducationalRedactor, **preferences: Any) -> None:
    redactor.preferences = {**redactor.preferences, **preferences}
    db.session.add(redactor)
