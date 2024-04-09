from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum


ACCESSIBILITY_MOCK = [
    {
        "access_modality": [],
        "audio_description": [acceslibre_enum.AUDIODESCRIPTION_PERMANENT.value],
        "deaf_and_hard_of_hearing_amenities": [acceslibre_enum.DEAF_AND_HARD_OF_HEARING_FIXED_INDUCTION_LOOP.value],
        "facilities": [acceslibre_enum.FACILITIES_ADAPTED.value],
        "sound_beacon": [],
        "trained_personnel": [acceslibre_enum.PERSONNEL_TRAINED.value],
        "transport_modality": [acceslibre_enum.PARKING_ADAPTED.value],
    },
    {
        "access_modality": [],
        "audio_description": [],
        "deaf_and_hard_of_hearing_amenities": [],
        "facilities": [acceslibre_enum.FACILITIES_UNADAPTED.value],
        "sound_beacon": [],
        "trained_personnel": [acceslibre_enum.PERSONNEL_UNTRAINED.value],
        "transport_modality": [acceslibre_enum.PARKING_UNAVAILABLE.value],
    },
    {
        "access_modality": [acceslibre_enum.EXTERIOR_ACCESS_ELEVATOR.value, acceslibre_enum.ENTRANCE_ELEVATOR.value],
        "audio_description": [acceslibre_enum.AUDIODESCRIPTION_OCCASIONAL.value],
        "deaf_and_hard_of_hearing_amenities": [
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value}, "
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value}"
        ],
        "facilities": [acceslibre_enum.FACILITIES_UNADAPTED.value],
        "sound_beacon": [acceslibre_enum.SOUND_BEACON.value],
        "trained_personnel": [],
        "transport_modality": [acceslibre_enum.PARKING_NEARBY.value],
    },
    {
        "access_modality": [acceslibre_enum.EXTERIOR_ONE_LEVEL.value, acceslibre_enum.ENTRANCE_PRM.value],
        "audio_description": [acceslibre_enum.AUDIODESCRIPTION_PERMANENT_SMARTPHONE.value],
        "deaf_and_hard_of_hearing_amenities": [
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_FIXED_INDUCTION_LOOP.value}, "
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value}, "
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SIGN_LANGUAGE.value}, "
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_CUED_SPEECH.value}, "
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value}, "
            f"{acceslibre_enum.DEAF_AND_HARD_OF_HEARING_OTHER.value}"
        ],
        "facilities": [acceslibre_enum.FACILITIES_ADAPTED.value],
        "sound_beacon": [acceslibre_enum.SOUND_BEACON.value],
        "trained_personnel": [acceslibre_enum.PERSONNEL_TRAINED.value],
        "transport_modality": [acceslibre_enum.PARKING_ADAPTED.value],
    },
    {
        "access_modality": [
            acceslibre_enum.EXTERIOR_ACCESS_RAMP.value,
            acceslibre_enum.ENTRANCE_HUMAN_HELP.value,
        ],
        "audio_description": [acceslibre_enum.AUDIODESCRIPTION_NO_DEVICE.value],
        "deaf_and_hard_of_hearing_amenities": [acceslibre_enum.DEAF_AND_HARD_OF_HEARING_OTHER.value],
        "facilities": [],
        "sound_beacon": [],
        "trained_personnel": [],
        "transport_modality": [acceslibre_enum.PARKING_UNAVAILABLE.value],
    },
    {
        "access_modality": [
            acceslibre_enum.EXTERIOR_ACCESS_HAS_DIFFICULTIES.value,
            acceslibre_enum.ENTRANCE_RAMP_NARROW.value,
        ],
        "audio_description": [],
        "deaf_and_hard_of_hearing_amenities": [acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SIGN_LANGUAGE.value],
        "facilities": [],
        "sound_beacon": [acceslibre_enum.SOUND_BEACON.value],
        "trained_personnel": [],
        "transport_modality": [acceslibre_enum.PARKING_UNAVAILABLE.value],
    },
    {
        "access_modality": [],
        "audio_description": [],
        "deaf_and_hard_of_hearing_amenities": [],
        "facilities": [],
        "sound_beacon": [],
        "trained_personnel": [],
        "transport_modality": [],
    },
]
