from pcapi.core.educational.models import StudentLevels
from pcapi.models.feature import FeatureToggle


def validate_students(student_levels: list[str] | list[StudentLevels] | None) -> list[StudentLevels]:
    if not student_levels:
        raise ValueError("La liste des niveaux scolaires ne peut pas être vide")

    output = []
    for student_level in student_levels:
        try:
            if isinstance(student_level, str):
                level = _fetch_student_level(student_level)
            else:
                level = student_level

        except ValueError:
            permitted = _permitted_levels()
            msg = f'Value is not a valid enumeration member; permitted: ["{permitted}"]'
            raise ValueError(msg)

        if not FeatureToggle.ENABLE_MARSEILLE.is_active() and level in StudentLevels.primary_levels():
            raise ValueError(f"Ce niveau ('{level.name}') n'est pas encore autorisé")

        output.append(level)
    return output


def _permitted_levels() -> str:
    if FeatureToggle.ENABLE_MARSEILLE.is_active():
        return '", "'.join(StudentLevels.__members__.keys())

    restricted_levels = [level.name for level in StudentLevels if level not in StudentLevels.primary_levels()]
    return '", "'.join(restricted_levels)


def _fetch_student_level(level: str) -> StudentLevels:
    """Fetch student level from enum name or value (try both)"""
    try:
        return StudentLevels(level)
    except ValueError:
        try:
            return StudentLevels[level]
        except Exception:
            raise ValueError("Unknown student level")
