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
from pcapi.utils import siren as siren_utils
from pcapi.utils.date import timespan_str_to_numrange


OFFER_DESCRIPTION = (
    "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum "
    "sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies "
    "nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, "
    "aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum "
    "felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate "
    "eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus "
    "in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean "
    "imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. "
    "Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed "
    "ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt "
    "tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus "
    "tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget "
    "bibendum sodales, augue velit cursus nunc."
)


def create_offerer() -> offerers_models.Offerer:
    max_siren = db.session.execute(
        sa.select(sa.func.max(sa.cast(offerers_models.Offerer.siren, sa.Integer))).filter(
            offerers_models.Offerer.siren.notlike("NC%")
        )
    ).scalar()

    new_siren_nr = str((max_siren or 0) + 1)
    new_siren = siren_utils.complete_siren_or_siret(f"{new_siren_nr:08}")
    offerer = offerers_factories.OffererFactory.build(siren=new_siren)
    db.session.add(offerer)
    return offerer


@log_func_duration
def create_accessibility_offers() -> dict:
    offerer = create_offerer()
    venue = offerers_factories.VenueFactory.create(
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
        description=OFFER_DESCRIPTION,
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
        description=OFFER_DESCRIPTION,
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
        description=OFFER_DESCRIPTION,
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
        description=OFFER_DESCRIPTION,
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
