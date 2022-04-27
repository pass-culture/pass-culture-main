import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers import repository as offers_repository
from pcapi.core.offers.exceptions import UnapplicableModel
from pcapi.core.offers.offer_validation import _get_model
from pcapi.core.offers.offer_validation import parse_offer_validation_config


pytestmark = pytest.mark.usefixtures("db_session")

SIMPLE_OFFER_VALIDATION_CONFIG = """
        minimum_score: 0.6
        rules:
            - name: "check offer name"
              factor: 0
              conditions:
               - model: "Offer"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated:
                      - "offer ?"
            - name: "check CollectiveOffer name"
              factor: 0
              conditions:
               - model: "CollectiveOffer"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated:
                      - "collective offer ?"
            - name: "check CollectiveOfferTemplate name"
              factor: 0
              conditions:
               - model: "CollectiveOfferTemplate"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated:
                      - "templates ?"
        """


class GetModelTest:
    def test_offer(self):
        offer = offers_factories.OfferFactory()
        model = _get_model(offer, "Offer")
        assert offer is model
        assert isinstance(model, offers_models.Offer)

    def test_collective_offer(self):
        offer = educational_factories.CollectiveOfferFactory()
        model = _get_model(offer, "CollectiveOffer")
        assert offer is model
        assert isinstance(model, educational_models.CollectiveOffer)

    def test_collective_offer_template(self):
        offer = educational_factories.CollectiveOfferTemplateFactory()
        model = _get_model(offer, "CollectiveOfferTemplate")
        assert offer is model
        assert isinstance(model, educational_models.CollectiveOfferTemplate)

    def test_collective_stock(self):
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock)
        model = _get_model(offer, "CollectiveStock")
        assert model is stock
        assert isinstance(model, educational_models.CollectiveStock)

    def test_collective_stock_offer_fail(self):
        offer = offers_factories.OfferFactory()
        with pytest.raises(UnapplicableModel):
            _get_model(offer, "CollectiveStock")

    def test_collective_offer_template_venue(self):
        venue = offerers_factories.VenueFactory()
        offer = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        model = _get_model(offer, "Venue")
        assert model is venue
        assert isinstance(model, offerers_models.Venue)

    def test_collective_offer_venue(self):
        venue = offerers_factories.VenueFactory()
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock, venue=venue)
        model = _get_model(offer, "Venue")
        assert model is venue
        assert isinstance(model, offerers_models.Venue)

    def test_offer_venue(self):
        venue = offerers_factories.VenueFactory()
        offer = offers_factories.OfferFactory(venue=venue)
        model = _get_model(offer, "Venue")
        assert model is venue
        assert isinstance(model, offerers_models.Venue)

    def test_offer_offerer(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        model = _get_model(offer, "Offerer")
        assert model is offerer
        assert isinstance(model, offerers_models.Offerer)

    def test_collective_offer_template_offerer(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        model = _get_model(offer, "Offerer")
        assert model is offerer
        assert isinstance(model, offerers_models.Offerer)

    def test_collective_offer_offerer(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        stock = educational_factories.CollectiveStockFactory()
        offer = educational_factories.CollectiveOfferFactory(collectiveStock=stock, venue=venue)
        model = _get_model(offer, "Offerer")
        assert model is offerer
        assert isinstance(model, offerers_models.Offerer)


class ParseOfferValidationConfigTest:
    def test_parse_offer_validation_config(self):
        offers_api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        offer = offers_factories.OfferFactory()
        config = offers_repository.get_current_offer_validation_config()
        minimum_score, rule_items = parse_offer_validation_config(offer, config)
        assert len(rule_items) == 1
        assert minimum_score == 0.6
        assert len(rule_items[0].offer_validation_items) == 1
        assert rule_items[0].offer_validation_items[0].model == offer
        assert rule_items[0].offer_validation_items[0].condition["comparated"] == ["offer ?"]

    def test_parse_collective_offer_template_validation_config(self):
        offers_api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        offer = educational_factories.CollectiveOfferTemplateFactory()
        config = offers_repository.get_current_offer_validation_config()
        minimum_score, rule_items = parse_offer_validation_config(offer, config)
        assert len(rule_items) == 1
        assert minimum_score == 0.6
        assert len(rule_items[0].offer_validation_items) == 1
        assert rule_items[0].offer_validation_items[0].model == offer
        assert rule_items[0].offer_validation_items[0].condition["comparated"] == ["templates ?"]

    def test_parse_collective_offer_validation_config(self):
        offers_api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        offer = educational_factories.CollectiveOfferFactory()
        config = offers_repository.get_current_offer_validation_config()
        minimum_score, rule_items = parse_offer_validation_config(offer, config)
        assert len(rule_items) == 1
        assert minimum_score == 0.6
        assert len(rule_items[0].offer_validation_items) == 1
        assert rule_items[0].offer_validation_items[0].model == offer
        assert rule_items[0].offer_validation_items[0].condition["comparated"] == ["collective offer ?"]
