import datetime
import pathlib

import pytest
import requests

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import validation
from pcapi.core.offers.models import OfferValidationStatus
import pcapi.core.payments.factories as payments_factories
from pcapi.models.api_errors import ApiErrors

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class CheckOfferExistingStocksAreEditableTest:
    def test_approved_offer(self):
        offer = offers_factories.OfferFactory()

        validation.check_offer_existing_stocks_are_editable(offer)

    def test_pending_offer(self):
        pending_validation_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)

        with pytest.raises(ApiErrors) as error:
            validation.check_offer_existing_stocks_are_editable(pending_validation_offer)

        assert error.value.errors["global"] == [
            "Les offres refusées ou en attente de validation ne sont pas modifiables"
        ]

    def test_allocine_offer(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")

        validation.check_offer_existing_stocks_are_editable(offer)

    def test_non_allocine_provider_offer(self):
        offerer = offerers_factories.APIProviderFactory()
        provider_offer = offers_factories.OfferFactory(lastProvider=offerer, idAtProviders="1")

        with pytest.raises(ApiErrors) as error:
            validation.check_offer_existing_stocks_are_editable(provider_offer)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]


@pytest.mark.usefixtures("db_session")
class CheckPricesForStockTest:
    def test_event_prices(self):
        offer = offers_factories.EventOfferFactory()
        validation.check_stock_price(0, offer)
        validation.check_stock_price(1.5, offer)
        validation.check_stock_price(310.5, offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(-1.5, offer)
        assert error.value.errors["price"] == ["Le prix doit être positif"]

    def test_thing_prices(self):
        offer = offers_factories.ThingOfferFactory()
        validation.check_stock_price(0, offer)
        validation.check_stock_price(1.5, offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(-1.5, offer)
        assert error.value.errors["price"] == ["Le prix doit être positif"]


@pytest.mark.usefixtures("db_session")
class CheckRequiredDatesForStockTest:
    def test_thing_offer_must_not_have_beginning(self):
        offer = offers_factories.ThingOfferFactory()

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
        offer = offers_factories.ThingOfferFactory()

        validation.check_required_dates_for_stock(
            offer,
            beginning=None,
            booking_limit_datetime=datetime.datetime.now(),
        )

    def test_thing_offer_ok_without_booking_limit_datetime(self):
        offer = offers_factories.ThingOfferFactory()

        validation.check_required_dates_for_stock(
            offer,
            beginning=None,
            booking_limit_datetime=None,
        )

    def test_event_offer_must_have_beginning(self):
        offer = offers_factories.EventOfferFactory()

        with pytest.raises(ApiErrors) as error:
            validation.check_required_dates_for_stock(
                offer,
                beginning=None,
                booking_limit_datetime=datetime.datetime.now(),
            )
        assert error.value.errors["beginningDatetime"] == ["Ce paramètre est obligatoire"]

    def test_event_offer_must_have_booking_limit_datetime(self):
        offer = offers_factories.EventOfferFactory()

        with pytest.raises(ApiErrors) as error:
            validation.check_required_dates_for_stock(
                offer,
                beginning=datetime.datetime.now(),
                booking_limit_datetime=None,
            )
        assert error.value.errors["bookingLimitDatetime"] == ["Ce paramètre est obligatoire"]

    def test_event_offer_ok_with_beginning_and_booking_limit_datetime(self):
        offer = offers_factories.EventOfferFactory()

        validation.check_required_dates_for_stock(
            offer,
            beginning=datetime.datetime.now(),
            booking_limit_datetime=datetime.datetime.now(),
        )


@pytest.mark.usefixtures("db_session")
class CheckStockCanBeCreatedForOfferTest:
    def test_approved_offer_not_from_provider(self):
        offer = offers_factories.OfferFactory(lastProvider=None)

        validation.check_stock_can_be_created_for_offer(offer)

    def test_offer_from_provider(self, app):
        provider = offerers_factories.AllocineProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_can_be_created_for_offer(offer)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_pending_offer_not_from_provider(self):
        offer = offers_factories.OfferFactory(lastProvider=None, validation=OfferValidationStatus.PENDING)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_can_be_created_for_offer(offer)

        assert error.value.errors["global"] == [
            "Les offres refusées ou en attente de validation ne sont pas modifiables"
        ]


@pytest.mark.usefixtures("db_session")
class CheckStockIsDeletableTest:
    def test_approved_offer(self):
        offer = offers_factories.OfferFactory()
        stock = offers_factories.StockFactory(offer=offer)

        validation.check_stock_is_deletable(stock)

    def test_allocine_offer(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = offers_factories.StockFactory(offer=offer)

        validation.check_stock_is_deletable(stock)

    def test_non_approved_offer(self):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_deletable(stock)

        assert error.value.errors["global"] == [
            "Les offres refusées ou en attente de validation ne sont pas modifiables"
        ]

    def test_offer_from_non_allocine_provider(self):
        provider = offerers_factories.APIProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_deletable(stock)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_recently_begun_event_stock(self):
        recently = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=recently)

        validation.check_stock_is_deletable(stock)

    def test_long_begun_event_stock(self):
        too_long_ago = datetime.datetime.now() - datetime.timedelta(days=3)
        stock = offers_factories.EventStockFactory(beginningDatetime=too_long_ago)

        with pytest.raises(exceptions.TooLateToDeleteStock) as error:
            validation.check_stock_is_deletable(stock)

        assert error.value.errors["global"] == [
            "L'événement s'est terminé il y a plus de deux jours, la suppression est impossible."
        ]


@pytest.mark.usefixtures("db_session")
class CheckStockIsUpdatableTest:
    def test_approved_offer(self):
        offer = offers_factories.OfferFactory()
        stock = offers_factories.StockFactory(offer=offer)

        validation.check_stock_is_updatable(stock)

    def test_allocine_offer(self):
        provider = offerers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = offers_factories.StockFactory(offer=offer)

        validation.check_stock_is_updatable(stock)

    def test_non_approved_offer(self):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == [
            "Les offres refusées ou en attente de validation ne sont pas modifiables"
        ]

    def test_offer_from_non_allocine_provider(self):
        provider = offerers_factories.APIProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProviders="1")
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_past_event_stock(self):
        recently = datetime.datetime.now() - datetime.timedelta(minutes=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=recently)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == ["Les événements passés ne sont pas modifiables"]


class GetDistantImageTest:
    def test_ok_with_headers(self, requests_mock):
        remote_image_url = "https://example.com/image.jpg"
        requests_mock.get(
            remote_image_url,
            headers={"content-type": "image/jpeg", "content-length": "4"},
            content=b"\xff\xd8\xff\xd9",
        )

        validation.get_distant_image(
            url=remote_image_url,
            accepted_types=("jpeg", "jpg"),
            max_size=100000,
        )

    def test_ok_without_headers(self, requests_mock):
        remote_image_url = "https://example.com/image.jpg"
        requests_mock.get(
            remote_image_url,
            headers={},
            content=b"\xff\xd8\xff\xd9",
        )

        validation.get_distant_image(
            url=remote_image_url,
            accepted_types=("jpeg", "jpg"),
            max_size=100000,
        )

    def test_unaccessible_file(self, requests_mock):
        remote_image_url = "https://example.com/this-goes-nowhere"
        requests_mock.get(
            remote_image_url,
            status_code=404,
        )

        with pytest.raises(exceptions.FailureToRetrieve):
            validation.get_distant_image(
                url=remote_image_url,
                accepted_types=("jpeg", "jpg"),
                max_size=100000,
            )

    def test_content_length_header_too_large(self, requests_mock):
        remote_image_url = "https://example.com/image.jpg"
        requests_mock.get(
            remote_image_url,
            headers={"content-type": "image/jpeg", "content-length": "2000"},
            content=b"\xff\xd8\xff\xd9",
        )

        with pytest.raises(exceptions.FileSizeExceeded):
            validation.get_distant_image(
                url=remote_image_url,
                accepted_types=("jpeg", "jpg", "png"),
                max_size=1000,
            )

    def test_content_type_header_not_accepted(self, requests_mock):
        remote_image_url = "https://example.com/image.gif"
        requests_mock.get(
            remote_image_url,
            headers={"content-type": "image/gif", "content-length": "27661"},
        )

        with pytest.raises(exceptions.UnacceptedFileType):
            validation.get_distant_image(
                url=remote_image_url,
                accepted_types=("jpeg", "jpg", "png"),
                max_size=100000,
            )

    def test_timeout(self, requests_mock):
        remote_image_url = "https://example.com/image.jpg"
        requests_mock.get(remote_image_url, exc=requests.exceptions.ConnectTimeout)

        with pytest.raises(exceptions.FailureToRetrieve):
            validation.get_distant_image(
                url=remote_image_url,
                accepted_types=("jpeg", "jpg"),
                max_size=100000,
            )

    def test_content_too_large(self, requests_mock):
        remote_image_url = "https://example.com/image.jpg"
        requests_mock.get(remote_image_url, content=b"1234567890")

        with pytest.raises(exceptions.FileSizeExceeded):
            validation.get_distant_image(
                url=remote_image_url,
                accepted_types=("jpeg", "jpg", "png"),
                max_size=5,
            )


class CheckImageTest:
    def test_ok(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        validation.check_image(
            image_as_bytes,
            accepted_types=("jpeg", "jpg"),
            min_width=400,
            min_height=400,
        )

    def test_image_too_small(self):
        image_as_bytes = (IMAGES_DIR / "mouette_portrait.jpg").read_bytes()
        with pytest.raises(exceptions.ImageTooSmall):
            validation.check_image(
                image_as_bytes,
                accepted_types=("jpeg", "jpg"),
                min_width=400,
                min_height=400,
            )

    def test_fake_jpeg(self):
        image_as_bytes = (IMAGES_DIR / "mouette_fake_jpg.jpg").read_bytes()
        with pytest.raises(exceptions.UnacceptedFileType):
            validation.check_image(
                image_as_bytes,
                accepted_types=("jpeg", "jpg"),
                min_width=1,
                min_height=1,
            )

    def test_wrong_format(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        with pytest.raises(exceptions.UnacceptedFileType):
            validation.check_image(
                image_as_bytes,
                accepted_types=("png",),
                min_width=1,
                min_height=1,
            )


@pytest.mark.usefixtures("db_session")
class CheckValidationStatusTest:
    def test_approved_offer(self):
        approved_offer = offers_factories.OfferFactory()

        validation.check_validation_status(approved_offer)

    def test_draft_offer(self):
        draft_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.DRAFT)

        validation.check_validation_status(draft_offer)

    def test_pending_offer(self):
        pending_validation_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.PENDING)

        with pytest.raises(ApiErrors) as error:
            validation.check_validation_status(pending_validation_offer)

        assert error.value.errors["global"] == [
            "Les offres refusées ou en attente de validation ne sont pas modifiables"
        ]

    def test_rejected_offer(self):
        rejected_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.REJECTED)

        with pytest.raises(ApiErrors) as error:
            validation.check_validation_status(rejected_offer)

        assert error.value.errors["global"] == [
            "Les offres refusées ou en attente de validation ne sont pas modifiables"
        ]


@pytest.mark.usefixtures("db_session")
def test_check_stock_has_no_custom_reimbursement_rule():
    stock = offers_factories.StockFactory()
    validation.check_stock_has_no_custom_reimbursement_rule(stock)  # should not raise

    payments_factories.CustomReimbursementRuleFactory(offer=stock.offer)
    with pytest.raises(ApiErrors) as error:
        validation.check_stock_has_no_custom_reimbursement_rule(stock)
    assert error.value.errors["price"] == ["Vous ne pouvez pas modifier le prix de cette offre"]
