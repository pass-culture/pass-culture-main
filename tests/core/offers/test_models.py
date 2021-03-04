import datetime

import pytest

import pcapi.core.offerers.factories as providers_factories
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.models.offer_type import ThingType
from pcapi.utils.date import DateTimes


@pytest.mark.usefixtures("db_session")
class OfferDateRangeTest:
    def test_thing_offer(self):
        offer = factories.ThingOfferFactory()
        factories.StockFactory(offer=offer)
        assert offer.dateRange == DateTimes()

    def test_event_offer(self):
        offer = factories.EventOfferFactory()
        first = datetime.datetime.now() + datetime.timedelta(days=1)
        last = datetime.datetime.now() + datetime.timedelta(days=5)
        factories.StockFactory(offer=offer, beginningDatetime=first)
        factories.StockFactory(offer=offer, beginningDatetime=last)
        assert offer.dateRange == DateTimes(first, last)

    def test_single_stock(self):
        offer = factories.EventOfferFactory()
        stock = factories.StockFactory(offer=offer)
        assert offer.dateRange == DateTimes(stock.beginningDatetime, stock.beginningDatetime)

    def test_no_stock(self):
        offer = factories.EventOfferFactory()
        assert offer.dateRange == DateTimes()

    def test_deleted_stock_is_ignored(self):
        offer = factories.EventOfferFactory()
        factories.StockFactory(offer=offer, isSoftDeleted=True)
        assert offer.dateRange == DateTimes()


class OfferIsDigitalTest:
    def test_is_digital(self):
        offer = models.Offer(url="")
        assert not offer.isDigital
        offer.url = "http://example.com/offer"
        assert offer.isDigital


class OfferTypeTest:
    def test_offer_type(self):
        offer = models.Offer(type=str(ThingType.LIVRE_EDITION))
        assert offer.offerType == {
            "conditionalFields": ["author", "isbn"],
            "proLabel": "Livres papier ou numérique, abonnements lecture",
            "appLabel": "Livre ou carte lecture",
            "offlineOnly": False,
            "onlineOnly": False,
            "sublabel": "Lire",
            "description": "S’abonner à un quotidien d’actualité ?"
            " À un hebdomadaire humoristique ? "
            "À un mensuel dédié à la nature ? "
            "Acheter une BD ou un manga ? "
            "Ou tout simplement ce livre dont tout le monde parle ?",
            "value": "ThingType.LIVRE_EDITION",
            "type": "Thing",
            "isActive": True,
            "canExpire": True,
        }


@pytest.mark.usefixtures("db_session")
class OfferHasBookingLimitDatetimesPassedTest:
    def test_with_stock_with_no_booking_limit_datetime(self):
        stock = factories.StockFactory(bookingLimitDatetime=None)
        offer = stock.offer
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = factories.StockFactory(offer=offer, isSoftDeleted=True, bookingLimitDatetime=past)
        assert not offer.hasBookingLimitDatetimesPassed

    def test_with_stocks_with_booking_limit_datetime(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = factories.StockFactory(bookingLimitDatetime=past)
        assert stock.offer.hasBookingLimitDatetimesPassed


@pytest.mark.usefixtures("db_session")
class OfferActiveMediationTest:
    def test_active_mediation(self):
        mediation1 = factories.MediationFactory()
        offer = mediation1.offer
        mediation2 = factories.MediationFactory(offer=offer)
        assert offer.activeMediation == mediation2

    def test_ignore_inactive_mediations(self):
        mediation = factories.MediationFactory(isActive=False)
        assert mediation.offer.activeMediation is None


@pytest.mark.usefixtures("db_session")
class OfferIsEditableTest:
    def test_editable_if_not_from_provider(self):
        offer = factories.OfferFactory()
        assert offer.isEditable

    def test_editable_if_from_allocine(self):
        provider = providers_factories.ProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider)
        assert offer.isEditable

    def test_not_editabe_if_from_another_provider(self):
        provider = providers_factories.ProviderFactory(localClass="TiteLiveStocks")
        offer = factories.OfferFactory(lastProvider=provider)
        assert not offer.isEditable


@pytest.mark.usefixtures("db_session")
class OfferThumbUrlTest:
    def test_use_mediation(self):
        mediation = factories.MediationFactory(thumbCount=1)
        offer = mediation.offer
        assert offer.thumbUrl.startswith("http")
        assert offer.thumbUrl == mediation.thumbUrl

    def test_use_product(self):
        product = factories.ProductFactory(thumbCount=1)
        offer = factories.OfferFactory(product=product)
        assert offer.thumbUrl.startswith("http")
        assert offer.thumbUrl == product.thumbUrl

    def test_defaults_to_none(self):
        offer = models.Offer()
        assert offer.thumbUrl == None


class OfferCategoryTest:
    def test_offer_category(self):
        offer = models.Offer(type=str(ThingType.JEUX_VIDEO))
        assert offer.offer_category == "JEUX_VIDEO"


@pytest.mark.usefixtures("db_session")
class OfferValidationTest:
    def test_factory_object_defaults_to_approved(self):
        offer = factories.OfferFactory()
        assert offer.validation == OfferValidationStatus.APPROVED
