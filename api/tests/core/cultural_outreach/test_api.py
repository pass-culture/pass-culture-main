import datetime
import logging

import pytest
import sqlalchemy as sa
import time_machine

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.cultural_outreach import api as cultural_outreach_api
from pcapi.core.cultural_outreach import models as cultural_outreach_models
from pcapi.core.cultural_outreach.exceptions import CulturalOutreachException
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus


pytestmark = pytest.mark.usefixtures("db_session")


class CreateCulturalOutreachClaimTest:
    @time_machine.travel("2026-04-21 12:00:00", tick=False)
    def test_creates_claim_for_allowed_activity(self, caplog):
        venue = offerers_factories.VenueFactory(activity=offerers_models.Activity.MUSEUM)
        offer = offers_factories.OfferFactory(venue=venue)

        with caplog.at_level(logging.INFO):
            cultural_outreach_api.create_cultural_outreach_claim(offer)

        claim = db.session.scalar(sa.select(cultural_outreach_models.CulturalOutreach))

        assert claim.offerId == offer.id
        assert claim.claimedDatetime == datetime.datetime(2026, 4, 21, 12, 0, 0)
        assert claim.status == cultural_outreach_models.CulturalOutreachStatus.PENDING

        assert len(caplog.records) == 1
        assert caplog.records[0].message == "Create cultural outreach claim"
        assert caplog.records[0].extra == {"offer_id": offer.id, "venue_id": offer.venueId}

    def test_raises_when_activity_is_not_allowed(self):
        venue = offerers_factories.VenueFactory(activity=offerers_models.Activity.CINEMA)
        offer = offers_factories.OfferFactory(venue=venue)

        with pytest.raises(CulturalOutreachException) as exc:
            cultural_outreach_api.create_cultural_outreach_claim(offer)

        assert exc.value.errors == {
            "global": ["Le secteur d'activité de la structure ne permet pas de déclarer une action de médiation"]
        }
        count = db.session.scalar(sa.select(sa.func.count()).select_from(cultural_outreach_models.CulturalOutreach))
        assert count == 0

    def test_raises_when_offer_is_pending_or_rejected(self):
        venue = offerers_factories.VenueFactory(activity=offerers_models.Activity.MUSEUM)
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.PENDING)

        with pytest.raises(CulturalOutreachException) as exc:
            cultural_outreach_api.create_cultural_outreach_claim(offer)

        assert exc.value.errors == {
            "global": ["Le statut de l'offre ne permet pas de déclarer une action de médiation"]
        }

    def test_raises_when_claim_already_exists(self):
        venue = offerers_factories.VenueFactory(activity=offerers_models.Activity.MUSEUM)
        offer = offers_factories.OfferFactory(venue=venue)
        cultural_outreach_api.create_cultural_outreach_claim(offer)

        with pytest.raises(CulturalOutreachException) as exc:
            cultural_outreach_api.create_cultural_outreach_claim(offer)

        assert exc.value.errors == {"global": ["Une action de médiation a déjà été déclarée pour cette offre"]}
