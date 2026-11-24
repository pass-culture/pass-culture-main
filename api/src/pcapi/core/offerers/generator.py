import decimal

import faker
import sqlalchemy as sa

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.geography import factories as geography_factories
from pcapi.core.geography.constants import TIME_ZONE_COUNTRY_CODE
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import utils as offerers_utils
from pcapi.models import db
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import timespan_str_to_numrange


def _create_offerer() -> offerers_models.Offerer:
    fake = faker.Faker(["fr-FR"])
    max_siren = db.session.scalar(
        sa.select(
            sa.func.max(
                sa.cast(sa.func.substr(offerers_models.Offerer.siren, 1, siren_utils.SIREN_LENGTH - 1), sa.Integer)
            )
        ).filter(offerers_models.Offerer.siren.notlike("NC%"))
    )

    new_siren = siren_utils.complete_siren_or_siret(f"{(max_siren or 0) + 1:0>8}")
    offerer = offerers_factories.OffererFactory.create(siren=new_siren, name=f"Structure TEST - {fake.company()}")
    db.session.add(offerer)
    return offerer


def create_venue(
    activity: offerers_models.Activity,
    timezone: str,
    name: str | None = None,
) -> offerers_models.Venue:
    offerer = _create_offerer()
    fake = faker.Faker(["fr-FR"])
    latitude, longitude, _, _, _ = fake.local_latlng(country_code=TIME_ZONE_COUNTRY_CODE[timezone]) or (
        geography_factories.DEFAULT_LATITUDE,
        geography_factories.DEFAULT_LONGITUDE,
        0,
        0,
        0,
    )
    address = geography_factories.AddressFactory(
        street=fake.street_address(),
        postalCode=fake.postcode(),
        latitude=decimal.Decimal(latitude),
        longitude=decimal.Decimal(longitude),
        timezone=timezone,
    )
    venue: offerers_models.Venue = offerers_factories.VenueFactory.create(
        activity=activity,
        managingOfferer=offerer,
        name=name or offerer.name,
        venueTypeCode=offerers_utils.ACTIVITY_NAME_TO_VENUE_TYPE_CODE_MAPPING[activity.name],
        offererAddress__address=address,
        withdrawalDetails=fake.paragraph(nb_sentences=6),
        description=fake.paragraph(nb_sentences=20),
    )
    db.session.add(venue)
    accessibility_provider = offerers_factories.AccessibilityProviderFactory.build(
        venue=venue,
        externalAccessibilityData={
            "access_modality": [acceslibre_enum.EXTERIOR_ONE_LEVEL.value, acceslibre_enum.ENTRANCE_PRM.value],
            "audio_description": [acceslibre_enum.AUDIODESCRIPTION_PERMANENT_SMARTPHONE.value],
            "deaf_and_hard_of_hearing_amenities": [
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_FIXED_INDUCTION_LOOP.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_PORTABLE_INDUCTION_LOOP.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SIGN_LANGUAGE.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_CUED_SPEECH.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_SUBTITLE.value,
                acceslibre_enum.DEAF_AND_HARD_OF_HEARING_OTHER.value,
            ],
            "facilities": [acceslibre_enum.FACILITIES_ADAPTED.value],
            "sound_beacon": [acceslibre_enum.SOUND_BEACON.value],
            "trained_personnel": [acceslibre_enum.PERSONNEL_TRAINED.value],
            "transport_modality": [acceslibre_enum.PARKING_ADAPTED.value],
        },
    )
    db.session.add(accessibility_provider)
    opening_hours1 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.MONDAY,
        timespan=timespan_str_to_numrange([("10:00", "21:00")]),
        venue=venue,
    )
    opening_hours2 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.TUESDAY,
        timespan=timespan_str_to_numrange([("10:00", "13:00"), ("15:00", "21:00")]),
        venue=venue,
    )
    opening_hours3 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.WEDNESDAY,
        timespan=timespan_str_to_numrange([("10:00", "21:00")]),
        venue=venue,
    )
    opening_hours4 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.THURSDAY,
        timespan=timespan_str_to_numrange([("10:00", "13:00"), ("15:00", "21:00")]),
        venue=venue,
    )
    opening_hours5 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.FRIDAY,
        timespan=timespan_str_to_numrange([("10:00", "12:00"), ("13:30", "21:00")]),
        venue=venue,
    )
    opening_hours6 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.SUNDAY,
        timespan=timespan_str_to_numrange([("9:00", "21:00")]),
        venue=venue,
    )
    opening_hours7 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.SATURDAY,
        timespan=timespan_str_to_numrange([("9:00", "12:00"), ("13:30", "20:30")]),
        venue=venue,
    )
    db.session.add_all(
        [opening_hours1, opening_hours2, opening_hours3, opening_hours4, opening_hours5, opening_hours6, opening_hours7]
    )
    return venue
