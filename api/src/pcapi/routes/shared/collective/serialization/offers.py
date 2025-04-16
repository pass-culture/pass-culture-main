from pydantic.v1 import validator

from pcapi.core.educational.models import StudentLevels
from pcapi.models.feature import FeatureToggle


def validate_students(student_levels: list[str] | None) -> list[StudentLevels]:
    if not student_levels:
        raise ValueError("La liste des niveaux scolaires ne peut pas être vide")

    output = []
    for student_level in student_levels:
        try:
            level = _feth_student_level(student_level)
        except ValueError:
            permitted = _permitted_levels()
            msg = f'Value is not a valid enumeration member; permitted: ["{permitted}"]'
            raise ValueError(msg)

        if not FeatureToggle.ENABLE_MARSEILLE.is_active() and student_level in StudentLevels.primary_levels():
            raise ValueError(f"Ce niveau ('{level}') n'est pas encore autorisé")

        output.append(level)
    return output


def _permitted_levels() -> str:
    if FeatureToggle.ENABLE_MARSEILLE.is_active():
        return '", "'.join(StudentLevels.__members__.keys())

    restricted_levels = [level.name for level in StudentLevels if level not in StudentLevels.primary_levels()]
    return '", "'.join(restricted_levels)


def _feth_student_level(level: str) -> StudentLevels:
    """Fetch student level from enum name or value (try both)"""
    try:
        return StudentLevels(level)
    except ValueError:
        try:
            return StudentLevels[level]
        except Exception:
            raise ValueError("Unknown student level")


def students_validator(field_name: str) -> classmethod:
    return validator(field_name, allow_reuse=True)(validate_students)
