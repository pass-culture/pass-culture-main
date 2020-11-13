import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.offers import validation
from pcapi.models.api_errors import ApiErrors


@pytest.mark.usefixtures("db_session")
class CheckOfferIsEditableTest:
    def test_raises_error_when_offer_is_not_editable(self):
        offerer = offerers_factories.ProviderFactory()
        offer = factories.OfferFactory(lastProvider=offerer, idAtProviders="1")

        with pytest.raises(ApiErrors) as error:
            validation.check_offer_is_editable(offer)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_does_not_raise_error_when_offer_type_is_editable(self):
        offer = factories.OfferFactory(lastProviderId=None)

        validation.check_offer_is_editable(offer)  # should not raise


@pytest.mark.usefixtures("db_session")
class CheckRequiredDatesForStock:
    def test_thing_offer_must_not_have_beginning(self):
        offer = factories.ThingOfferFactory()

        with pytest.raises(ApiErrors) as error:
            validation.check_required_dates_for_stock(
                offer,
                beginning=datetime.datetime.now(),
                booking_limit_datetime=None,
            )

        assert error.value.errors["global"] == [
            "Impossible de mettre une date de début si l'offre ne porte pas sur un événement"
        ]

    def test_thing_offer_ok_with_booking_limit_datetime(self):
        offer = factories.ThingOfferFactory()

        validation.check_required_dates_for_stock(
            offer,
            beginning=None,
            booking_limit_datetime=datetime.datetime.now(),
        )

    def test_thing_offer_ok_without_booking_limit_datetime(self):
        offer = factories.ThingOfferFactory()

        validation.check_required_dates_for_stock(
            offer,
            beginning=None,
            booking_limit_datetime=None,
        )

    def test_event_offer_must_have_beginning(self):
        offer = factories.EventOfferFactory()

        with pytest.raises(ApiErrors) as error:
            validation.check_required_dates_for_stock(
                offer,
                beginning=None,
                booking_limit_datetime=datetime.datetime.now(),
            )
        assert error.value.errors["beginningDatetime"] == ["Ce paramètre est obligatoire"]

    def test_event_offer_must_have_booking_limit_datetime(self):
        offer = factories.EventOfferFactory()

        with pytest.raises(ApiErrors) as error:
            validation.check_required_dates_for_stock(
                offer,
                beginning=datetime.datetime.now(),
                booking_limit_datetime=None,
            )
        assert error.value.errors["bookingLimitDatetime"] == ["Ce paramètre est obligatoire"]

    def test_event_offer_ok_with_beginning_and_booking_limit_datetime(self):
        offer = factories.EventOfferFactory()

        validation.check_required_dates_for_stock(
            offer,
            beginning=datetime.datetime.now(),
            booking_limit_datetime=datetime.datetime.now(),
        )


@pytest.mark.usefixtures("db_session")
class CheckStocksAreEditableForOfferTest:
    def should_fail_when_offer_is_from_provider(self, app):
        provider = offerers_factories.ProviderFactory()
        offer = factories.OfferFactory(lastProvider=provider, idAtProviders="1")

        with pytest.raises(ApiErrors) as error:
            validation.check_stocks_are_editable_for_offer(offer)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def should_not_raise_an_error_when_offer_is_not_from_provider(self):
        offer = factories.OfferFactory(lastProvider=None)
        validation.check_stocks_are_editable_for_offer(offer)  # should not raise
