import logging

import pcapi.core.artist.factories as artist_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.artist import models as artist_models
from pcapi.core.categories import subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_offers_with_artists() -> None:
    logger.info("create_offers_with_artists")
    retention_user = db.session.query(users_models.User).filter_by(email="retention_structures@example.com").one()
    venue_list = (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.Offerer, offerers_models.Offerer.id == offerers_models.Venue.managingOffererId)
        .join(offerers_models.UserOfferer, offerers_models.UserOfferer.offererId == offerers_models.Offerer.id)
        .filter(offerers_models.UserOfferer.userId == retention_user.id)
        .all()
    )

    for venue in venue_list:
        book_offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            name="Un chouette livre avec artiste 🦉",
        )
        offers_factories.StockFactory(offer=book_offer)

        theater_offer = offers_factories.OfferFactory(
            venue=venue, subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id, name="Une pièce sympa avec artiste 🪙"
        )
        offers_factories.StockFactory(offer=theater_offer)

        # Book offer, just 1 artist link, linked to an Artist()
        author_artist = artist_factories.ArtistFactory()
        artist_factories.ArtistOfferLinkFactory(
            artist=author_artist,
            offer=book_offer,
            artist_type=artist_models.ArtistType.AUTHOR,
        )

        # Theater offer, several links: 1 author link to an Artist()
        # + 1 stage director not linked to an Artist
        # + 2 performers, 1 linked to an Artist, 1 not linked
        artist_factories.ArtistOfferLinkFactory(
            artist=author_artist,
            offer=theater_offer,
            artist_type=artist_models.ArtistType.AUTHOR,
        )
        stage_director_artist = artist_factories.ArtistFactory()
        artist_factories.ArtistOfferLinkFactory(
            artist=stage_director_artist,
            offer=theater_offer,
            artist_type=artist_models.ArtistType.STAGE_DIRECTOR,
        )
        performer_artist = artist_factories.ArtistFactory()
        artist_factories.ArtistOfferLinkFactory(
            artist=performer_artist,
            offer=theater_offer,
            artist_type=artist_models.ArtistType.PERFORMER,
        )
        artist_factories.ArtistOfferLinkFactory(
            custom_name="Michelle Vedette",
            offer=theater_offer,
            artist_type=artist_models.ArtistType.PERFORMER,
        )

    logger.info("created offers with artists")
