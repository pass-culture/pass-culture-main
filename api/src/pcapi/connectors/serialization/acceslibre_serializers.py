import pydantic

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.routes.serialization import HttpBodyModel


ENTRANCE_FIELDS = {field.value for field in acceslibre_enum if field.name.startswith("ENTRANCE")}

EXTERIOR_FIELDS = {field.value for field in acceslibre_enum if field.name.startswith("EXTERIOR")}

IS_NOT_MOTOR_COMPLIANT = {
    acceslibre_enum.EXTERIOR_ACCESS_HAS_DIFFICULTIES.value,
    acceslibre_enum.ENTRANCE_NOT_ONE_LEVEL.value,
    acceslibre_enum.PARKING_UNAVAILABLE.value,
    acceslibre_enum.FACILITIES_UNADAPTED.value,
}

IS_NOT_MENTAL_COMPLIANT = {
    acceslibre_enum.PERSONNEL_MISSING.value,
    acceslibre_enum.PERSONNEL_UNTRAINED.value,
}


class MotorDisabilityModel(HttpBodyModel):
    facilities: str = acceslibre_enum.UNKNOWN.value
    exterior: str = acceslibre_enum.UNKNOWN.value
    entrance: str = acceslibre_enum.UNKNOWN.value
    parking: str = acceslibre_enum.UNKNOWN.value


class AudioDisabilityModel(HttpBodyModel):
    deafAndHardOfHearing: list[str] = [acceslibre_enum.UNKNOWN.value]


class VisualDisabilityModel(HttpBodyModel):
    soundBeacon: str = acceslibre_enum.UNKNOWN.value
    audioDescription: list[str] = [acceslibre_enum.UNKNOWN.value]


class MentalDisabilityModel(HttpBodyModel):
    trainedPersonnel: str = acceslibre_enum.UNKNOWN.value


class ExternalAccessibilityDataModel(HttpBodyModel):
    isAccessibleMotorDisability: bool = False
    isAccessibleAudioDisability: bool = False
    isAccessibleVisualDisability: bool = False
    isAccessibleMentalDisability: bool = False
    motorDisability: MotorDisabilityModel = MotorDisabilityModel()
    audioDisability: AudioDisabilityModel = AudioDisabilityModel()
    visualDisability: VisualDisabilityModel = VisualDisabilityModel()
    mentalDisability: MentalDisabilityModel = MentalDisabilityModel()

    model_config = pydantic.ConfigDict(extra="ignore")

    @classmethod
    def from_accessibility_infos(cls, accessibility_infos: dict | None) -> "ExternalAccessibilityDataModel":
        if not accessibility_infos:
            return cls()
        accessibility_data = cls.model_validate(accessibility_infos)
        for key, value in accessibility_infos.items():
            match key:
                case "access_modality":
                    # access_modality is a list, which has either exterior or entrance access informations, both or None
                    for item in value:
                        if item in EXTERIOR_FIELDS:
                            accessibility_data.motorDisability.exterior = item
                        elif item in ENTRANCE_FIELDS:
                            accessibility_data.motorDisability.entrance = item
                        accessibility_data.isAccessibleMotorDisability = (
                            item not in IS_NOT_MOTOR_COMPLIANT or accessibility_data.isAccessibleMotorDisability
                        )

                case "facilities":
                    for item in value:
                        accessibility_data.motorDisability.facilities = item
                        accessibility_data.isAccessibleMotorDisability = (
                            item not in IS_NOT_MOTOR_COMPLIANT or accessibility_data.isAccessibleMotorDisability
                        )

                case "deaf_and_hard_of_hearing_amenities":
                    if value:
                        # In acceslibre widget, deaf and hard of hearing can have several values in a list
                        accessibility_data.audioDisability.deafAndHardOfHearing = value
                        accessibility_data.isAccessibleAudioDisability = True

                case "audio_description":
                    if value:
                        # In acceslibre widget, audiodescription can have several values in a list
                        accessibility_data.visualDisability.audioDescription = value
                        accessibility_data.isAccessibleVisualDisability = True

                case "sound_beacon":
                    for item in value:
                        accessibility_data.visualDisability.soundBeacon = item
                        accessibility_data.isAccessibleVisualDisability = True

                case "trained_personnel":
                    for item in value:
                        accessibility_data.mentalDisability.trainedPersonnel = item
                        accessibility_data.isAccessibleMentalDisability = item not in IS_NOT_MENTAL_COMPLIANT

                case "transport_modality":
                    for item in value:
                        accessibility_data.motorDisability.parking = item
                        accessibility_data.isAccessibleMotorDisability = (
                            item not in IS_NOT_MOTOR_COMPLIANT or accessibility_data.isAccessibleMotorDisability
                        )

        return accessibility_data
