import datetime

import sqlalchemy as sa

from pcapi.connectors.acceslibre import ExpectedFieldsEnum as acceslibre_enum
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.utils import date as date_utils
from pcapi.utils.date import timespan_str_to_numrange


def create_offerer() -> offerers_models.Offerer:
    max_siren = db.session.execute(
        sa.select(sa.func.max(sa.cast(offerers_models.Offerer.siren, sa.Integer))).filter(
            offerers_models.Offerer.siren.notlike("NC%")
        )
    ).scalar()
    assert max_siren
    new_siren = str(max_siren + 1)
    offerer = offerers_factories.OffererFactory.build(siren=new_siren)
    db.session.add(offerer)
    return offerer


@log_func_duration
def create_accessibility_offers() -> dict:
    offerer = create_offerer()
    venue = offerers_factories.VenueFactory.build(
        managingOfferer=offerer,
        name="Lieu - Audit Access42",
        venueTypeCode=offerers_models.VenueTypeCode.MOVIE,
        offererAddress__address__street="21 Rue du Simplon",
        offererAddress__address__postalCode="75018",
        withdrawalDetails=(
            "Pour vous faire mieux connaître d’où vient l’erreur de ceux qui blâment la volupté, et qui louent en "
            "quelque sorte la douleur, je vais entrer dans une explication plus étendue, et vous faire voir tout ce "
            "qui a été dit là-dessus par l’inventeur de la vérité, et, pour ainsi dire, par l’architecte de la vie "
            "heureuse."
        ),
        description=(
            "J’en dis autant de ceux qui, par mollesse d’esprit, c’est-à-dire par la crainte de la peine et de la "
            "douleur, manquent aux devoirs de la vie. Et il est très facile de rendre raison de ce que j’avance. "
            "Car, lorsque nous sommes tout à fait libres, et que rien ne nous empêche de faire ce qui peut nous donner "
            "le plus de plaisir, nous pouvons nous livrer entièrement à la volupté et chasser toute sorte de douleur ; "
            "mais, dans les temps destinés aux devoirs de la société ou à la nécessité des affaires, souvent il faut "
            "faire divorce avec la volupté, et ne se point refuser à la peine."
        ),
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
        timespan=timespan_str_to_numrange([("15:00", "19:00")]),
        venue=venue,
    )
    opening_hours2 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.TUESDAY,
        timespan=timespan_str_to_numrange([("10:00", "13:00"), ("15:00", "19:00")]),
        venue=venue,
    )
    opening_hours3 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.WEDNESDAY,
        timespan=timespan_str_to_numrange([("10:00", "19:00")]),
        venue=venue,
    )
    opening_hours4 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.THURSDAY,
        timespan=timespan_str_to_numrange([("10:00", "13:00"), ("15:00", "19:00")]),
        venue=venue,
    )
    opening_hours5 = offerers_factories.OpeningHoursFactory.build(
        weekday=offerers_models.Weekday.FRIDAY,
        timespan=timespan_str_to_numrange([("10:00", "12:00"), ("16:00", "19:00")]),
        venue=venue,
    )
    db.session.add_all([opening_hours1, opening_hours2, opening_hours3, opening_hours4, opening_hours5])

    offer1 = offers_factories.OfferFactory.build(
        name="Offre cinéma - Audit Access42",
        venue=venue,
        subcategoryId=subcategories.SEANCE_CINE.id,
        publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
    )
    db.session.add(offer1)
    mediation1 = offers_factories.MediationFactory.build(offer=offer1, credit="Michèlle photo")
    db.session.add(mediation1)
    offer_metadata = offers_factories.OfferMetaDataFactory.build(
        videoUrl="https://www.youtube.com/watch?v=e_04ZrNroTo",
        videoDuration=229,
        videoExternalId="e_04ZrNroTo",
        videoThumbnailUrl="https://i.ytimg.com/vi/e_04ZrNroTo/hqdefault.jpg",
        videoTitle="Wheels on the Bus | @CoComelon Nursery Rhymes & Kids Songs",
        offer=offer1,
    )
    db.session.add(offer_metadata)
    stock1 = offers_factories.StockFactory.build(offer=offer1)
    db.session.add(stock1)

    offer2 = offers_factories.OfferFactory.build(
        venue=venue,
        name="Offre livre - Audit Access42",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
    )
    db.session.add(offer2)
    mediation2 = offers_factories.MediationFactory.build(offer=offer2, credit="Michel photo")
    db.session.add(mediation2)
    stock2 = offers_factories.StockFactory.build(offer=offer2)
    db.session.add(stock2)
    offer3 = offers_factories.OfferFactory.build(
        venue=venue,
        name="Ne pas auditer - Offre livre - Audit Access42",
        subcategoryId=subcategories.CARTE_JEUNES.id,
        publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
    )
    db.session.add(offer3)
    mediation3 = offers_factories.MediationFactory.build(offer=offer3, credit="Andrée photo")
    db.session.add(mediation3)
    stock3 = offers_factories.StockFactory.create(offer=offer3)
    db.session.add(stock3)
    offer4 = offers_factories.OfferFactory.build(
        venue=venue,
        name="Ne pas auditer - Offre numérique - Audit Access42",
        subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
        publicationDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
    )
    db.session.add(offer4)
    mediation4 = offers_factories.MediationFactory.build(offer=offer4, credit="André photo")
    db.session.add(mediation4)
    stock4 = offers_factories.StockFactory.create(offer=offer4)
    db.session.add(stock4)

    db.session.commit()

    return {
        "venueId": venue.id,
        "venueName": venue.name,
        "offers": [
            {"id": offer1.id, "name": offer1.name},
            {"id": offer2.id, "name": offer2.name},
            {"id": offer3.id, "name": offer3.name},
            {"id": offer4.id, "name": offer4.name},
        ],
    }
