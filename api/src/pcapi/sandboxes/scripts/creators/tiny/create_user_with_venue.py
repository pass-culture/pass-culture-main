import datetime
import logging
import pathlib

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.constants import ALL_INTERVENTION_AREA
from pcapi.core.educational.repository import find_educational_institution_by_uai_code
from pcapi.core.educational.utils import UAI_FOR_FAKE_TOKEN
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.storage_utils import add_image_to_offer
from pcapi.sandboxes.thumbs import generic_pictures
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


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
