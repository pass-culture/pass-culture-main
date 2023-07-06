from pcapi.routes import serialization


class PartialAccessibility(serialization.ConfiguredBaseModel):
    """Accessibility for people with disabilities. Fields are null for digital venues."""

    audio_disability_compliant: bool | None
    mental_disability_compliant: bool | None
    motor_disability_compliant: bool | None
    visual_disability_compliant: bool | None
