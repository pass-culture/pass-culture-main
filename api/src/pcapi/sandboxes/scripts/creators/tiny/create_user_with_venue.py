import datetime
import logging
import pathlib

from pcapi.core.artist import factories as artist_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.core.educational.utils import UAI_FOR_FAKE_TOKEN
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.storage_utils import add_image_to_offer
from pcapi.sandboxes.thumbs import generic_pictures
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def _create_tiny_works_and_artists(offer: offers_models.Offer) -> None:
    director = artist_factories.ArtistFactory.create(name="Camille Martin", main_role="stage_director")
    performer = artist_factories.ArtistFactory.create(name="Alex Dubois", main_role="performer")
    author = artist_factories.ArtistFactory.create(name="Lou Bernard", main_role="author")
    performance = discoveries_models.Work(
        title=offer.name, media_type=discoveries_models.WorkMediaType.PERFORMING_ART, release_year=2026
    )
    book = discoveries_models.Work(title="Les petites aventures", media_type=discoveries_models.WorkMediaType.BOOK)
    album = discoveries_models.Work(title="Petites melodies", media_type=discoveries_models.WorkMediaType.MUSIC)
    product = offers_models.Product(
        name=offer.name,
        subcategoryId=offer.subcategoryId,
        description=offer.description,
        durationMinutes=offer.durationMinutes,
        extraData=dict(offer.extraData) if offer.extraData is not None else None,
        work=performance,
    )
    offer.product = product
    db.session.add_all(
        [
            product,
            discoveries_models.WorkArtist(work=performance, artist=director, role="stage_director"),
            discoveries_models.WorkArtist(work=performance, artist=performer, role="performer"),
            discoveries_models.WorkArtist(work=book, artist=author, role="author"),
            discoveries_models.WorkArtist(work=album, artist=performer, role="performer"),
        ]
    )
    db.session.flush()
    for artist, artist_type in (
        (director, artist_models.ArtistType.STAGE_DIRECTOR),
        (performer, artist_models.ArtistType.PERFORMER),
    ):
        db.session.add_all(
            [
                artist_models.ArtistProductLink(artist_id=artist.id, product_id=product.id, artist_type=artist_type),
                artist_models.ArtistOfferLink(artist_id=artist.id, offer_id=offer.id, artist_type=artist_type),
            ]
        )
    db.session.flush()
    logger.info(
        "created tiny works %s and artists %s",
        [performance.id, book.id, album.id],
        [director.id, performer.id, author.id],
    )


def create_tiny_venue() -> None:
    logger.info("start create tiny venue")
    email = "tom.pouce@example.com"
    user_offerer = UserOffererFactory.create(
        user__email=email, offerer__name="Ma petite entreprise", user__firstName="Tom", user__lastName="Pouce"
    )
    logger.info(f"You can connect to pro with : {email}")
    venue = VenueFactory.create(
        name="Petit lieu",
        managingOfferer=user_offerer.offerer,
        adageId="123546",
        collectiveInterventionArea=ALL_INTERVENTION_AREA,
        collectiveEmail="email@exemple.com",
        isPermanent=True,
    )
    landscape_image_path = pathlib.Path(generic_pictures.__path__[0]) / "landscape_01.jpg"
    offerers_api.save_venue_banner(
        user=user_offerer.user,
        venue=venue,
        content=landscape_image_path.read_bytes(),
        image_credit="industrial sandbox picture provider",
        image_alternative_text="Image de mon petit lieu",
    )
    offer_event = EventOfferFactory.create(
        name="Conférence gesticulée",
        venue=venue,
        subcategoryId=subcategories.CONFERENCE.id,
    )
    _create_tiny_works_and_artists(offer_event)
    stock = EventStockFactory.create(
        offer=offer_event,
        quantity=10,
        beginningDatetime=date_utils.get_naive_utc_now().replace(second=0, microsecond=0) + datetime.timedelta(days=20),
    )
    BookingFactory.create(quantity=1, stock=stock)

    domain = db.session.query(educational_models.EducationalDomain).first()
    template = educational_factories.CollectiveOfferTemplateFactory.create(
        name="Conférence gesticulée",
        venue=venue,
        bookingEmails=[email],
        domains=[domain],
    )
    add_image_to_offer(template, "collective_offer_1.png")
    educational_institution = find_educational_institution_by_uai_code(UAI_FOR_FAKE_TOKEN)
    collective_offer = educational_factories.PublishedCollectiveOfferFactory(
        name="Ma petite offre réservable",
        venue=venue,
        domains=[domain],
        institution=educational_institution,
    )
    add_image_to_offer(
        collective_offer, "collective_offer_2.jpg", alternative_text="Image de ma petite offre réservable"
    )
    educational_factories.PlaylistFactory.create(
        distanceInKm=50,
        collective_offer_template=template,
        type=educational_models.PlaylistType.NEW_OFFER,
        institution=educational_institution,
    )
    educational_factories.PlaylistFactory.create(
        distanceInKm=50,
        collective_offer_template=template,
        type=educational_models.PlaylistType.NEW_OFFERER,
        institution=educational_institution,
        venue=venue,
    )

    logger.info("end create tiny venue with 1 booked offers, individual & collective")
