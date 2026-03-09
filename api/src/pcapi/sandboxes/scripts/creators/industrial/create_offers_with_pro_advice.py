import logging

import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_offers_with_pro_advice() -> None:
    logger.info("create_offers_with_pro_advice")
    retention_user = db.session.query(users_models.User).filter_by(email="retention_structures@example.com").one()
    venue_list = (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.Offerer, offerers_models.Offerer.id == offerers_models.Venue.managingOffererId)
        .join(offerers_models.UserOfferer, offerers_models.UserOfferer.offererId == offerers_models.Offerer.id)
        .filter(offerers_models.UserOfferer.userId == retention_user.id)
        .all()
    )

    for venue in venue_list:
        # Synced physical event with pro advice
        synced_event_offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            name="Événement synchronisé avec reco 🔮",
            lastProvider=providers_factories.ProviderFactory(),
        )
        offers_factories.StockFactory(offer=synced_event_offer)
        offers_factories.ProAdviceFactory.create(
            offer=synced_event_offer,
            content="Cet événement physique synchronisé est génial.",
            author="L'organisateur du rond point",
        )

        # Physical event with pro advice
        event_offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id,
            name="Événement physique avec reco 🏷️",
        )
        offers_factories.StockFactory(offer=event_offer)
        offers_factories.ProAdviceFactory.create(
            offer=event_offer,
            content="Cet événement physique est dingue.",
        )

        # Physical product with pro advice
        product_offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            name="Produit physique avec reco 💬",
        )
        offers_factories.StockFactory(offer=product_offer)
        offers_factories.ProAdviceFactory.create(
            offer=product_offer,
            content="Ce produit physique est incroyable.",
            author="Le libraire du coin",
        )

        # Digital product with pro advice
        digital_offer = offers_factories.OfferFactory(
            venue=venue,
            subcategoryId=subcategories.VOD.id,
            name="Produit numérique avec reco 📝",
            url="http://example.com/digital",
        )
        offers_factories.StockFactory(offer=digital_offer)
        offers_factories.ProAdviceFactory.create(
            offer=digital_offer,
            content="Ce produit numérique est super.",
        )

    logger.info("created offers with pro advice")
