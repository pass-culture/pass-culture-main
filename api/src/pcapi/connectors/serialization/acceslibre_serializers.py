import typing

import pydantic as pydantic_v2
import pydantic.v1 as pydantic_v1

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum


def build_models(cls: typing.Type) -> type:
    """Build all classes with the same ancestor (cls)

    cls should either be pydantic v1's BaseModel or pydantic v2's one.
    This builds the main ExternalAccessibilityDataModel class with all of
    its depencies that should inherit from the same base model (mixing
    v1 and v2 does not seem to work).
    """
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

    class MotorDisabilityModel(cls):
        facilities: str = acceslibre_enum.UNKNOWN.value
        exterior: str = acceslibre_enum.UNKNOWN.value
        entrance: str = acceslibre_enum.UNKNOWN.value
        parking: str = acceslibre_enum.UNKNOWN.value

    class AudioDisabilityModel(cls):
        deafAndHardOfHearing: list[str] = [acceslibre_enum.UNKNOWN.value]

    class VisualDisabilityModel(cls):
        soundBeacon: str = acceslibre_enum.UNKNOWN.value
        audioDescription: list[str] = [acceslibre_enum.UNKNOWN.value]

    class MentalDisabilityModel(cls):
        trainedPersonnel: str = acceslibre_enum.UNKNOWN.value

    class _ExternalAccessibilityDataModel(cls):
        isAccessibleMotorDisability: bool = False
        isAccessibleAudioDisability: bool = False
        isAccessibleVisualDisability: bool = False
        isAccessibleMentalDisability: bool = False
        motorDisability: MotorDisabilityModel = MotorDisabilityModel()
        audioDisability: AudioDisabilityModel = AudioDisabilityModel()
        visualDisability: VisualDisabilityModel = VisualDisabilityModel()
        mentalDisability: MentalDisabilityModel = MentalDisabilityModel()

        @classmethod
        def from_accessibility_infos(cls, accessibility_infos: dict | None) -> "_ExternalAccessibilityDataModel":
            if not accessibility_infos:
                return _ExternalAccessibilityDataModel()
            accessibility_data = cls.parse_obj(accessibility_infos)
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

    return _ExternalAccessibilityDataModel


# TODO(jbaudet - 02/2026): remove this akward build_models function
# once the pydantic v2 migration is done (at least for the
# ExternalAccessibilityDataModel model).
# This is not great but useful since the main class depends on many
# other and all should either inherit from pydantic v1's base model
# or pydantic v2's. This avoids a huge copy/paste with tons of V2
# suffixed classes.
if not typing.TYPE_CHECKING:
    ExternalAccessibilityDataModel = build_models(pydantic_v1.BaseModel)
    ExternalAccessibilityDataModelV2 = build_models(pydantic_v2.BaseModel)
else:
    # These two class definition have one goal: please mypy.
    # They can be removed as soon as this pydantic migration is done.
    class ExternalAccessibilityDataModel(pydantic_v1.BaseModel):
        @classmethod
        def from_accessibility_infos(cls, accessibility_infos: dict | None) -> "ExternalAccessibilityDataModel":
            return cls()

    class ExternalAccessibilityDataModelV2(pydantic_v2.BaseModel):
        @classmethod
        def from_accessibility_infos(cls, accessibility_infos: dict | None) -> "ExternalAccessibilityDataModelV2":
            return cls()
