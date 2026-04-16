import logging

import pcapi.core.cultural_outreach.factories as cultural_outreach_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.categories import subcategories
from pcapi.core.cultural_outreach import models as cultural_outreach_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


CULTURAL_OUTREACH_VARIANTS = [
    (
        "Offre de médiation déclarée - en attente 📬",
        subcategories.LIVRE_PAPIER.id,
        cultural_outreach_models.CulturalOutreachStatus.PENDING,
        True,
    ),
    (
        "Offre de médiation non déclarée - qualifiée ✅",
        subcategories.SEANCE_CINE.id,
        cultural_outreach_models.CulturalOutreachStatus.QUALIFIED,
        False,
    ),
    (
        "Offre de médiation déclarée - qualifiée ✅",
        subcategories.SPECTACLE_REPRESENTATION.id,
        cultural_outreach_models.CulturalOutreachStatus.QUALIFIED,
        True,
    ),
    (
        "Offre de médiation non déclarée - disqualifiée ❌",
        subcategories.LIVRE_PAPIER.id,
        cultural_outreach_models.CulturalOutreachStatus.DISQUALIFIED,
        False,
    ),
    (
        "Offre de médiation déclarée - disqualifiée ❌",
        subcategories.SEANCE_CINE.id,
        cultural_outreach_models.CulturalOutreachStatus.DISQUALIFIED,
        True,
    ),
]


@log_func_duration
def create_industrial_cultural_outreach() -> None:
    logger.info("create_industrial_cultural_outreach")
    retention_user = db.session.query(users_models.User).filter_by(email="retention_structures@example.com").one()
    venue_list = (
        db.session.query(offerers_models.Venue)
        .join(offerers_models.Offerer, offerers_models.Offerer.id == offerers_models.Venue.managingOffererId)
        .join(offerers_models.UserOfferer, offerers_models.UserOfferer.offererId == offerers_models.Offerer.id)
        .filter(offerers_models.UserOfferer.userId == retention_user.id)
        .all()
    )

    created = 0
    for venue in venue_list:
        for name, subcategory_id, status, claimed in CULTURAL_OUTREACH_VARIANTS:
            offer = offers_factories.OfferFactory(
                venue=venue,
                subcategoryId=subcategory_id,
                name=name,
            )
            offers_factories.StockFactory(offer=offer)
            kwargs = {"offer": offer, "status": status}
            if not claimed:
                cultural_outreach_factories.CulturalOutreachFactory.create(**kwargs)
            cultural_outreach_factories.ClaimedCulturalOutreachFactory.create(**kwargs)
            created += 1

    logger.info("created %d cultural outreach offers", created)
