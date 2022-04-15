import datetime
import pathlib

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import validation
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import WithdrawalTypeEnum
import pcapi.core.providers.factories as providers_factories
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
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")

        validation.check_offer_existing_stocks_are_editable(offer)

    def test_non_allocine_provider_offer(self):
        offerer = providers_factories.APIProviderFactory()
        provider_offer = offers_factories.OfferFactory(lastProvider=offerer, idAtProvider="1")

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
                beginning=datetime.datetime.utcnow(),
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
            booking_limit_datetime=datetime.datetime.utcnow(),
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
                booking_limit_datetime=datetime.datetime.utcnow(),
            )
        assert error.value.errors["beginningDatetime"] == ["Ce paramètre est obligatoire"]

    def test_event_offer_must_have_booking_limit_datetime(self):
        offer = offers_factories.EventOfferFactory()

        with pytest.raises(ApiErrors) as error:
            validation.check_required_dates_for_stock(
                offer,
                beginning=datetime.datetime.utcnow(),
                booking_limit_datetime=None,
            )
        assert error.value.errors["bookingLimitDatetime"] == ["Ce paramètre est obligatoire"]

    def test_event_offer_ok_with_beginning_and_booking_limit_datetime(self):
        offer = offers_factories.EventOfferFactory()

        validation.check_required_dates_for_stock(
            offer,
            beginning=datetime.datetime.utcnow(),
            booking_limit_datetime=datetime.datetime.utcnow(),
        )


@pytest.mark.usefixtures("db_session")
class CheckStockCanBeCreatedForOfferTest:
    def test_approved_offer_not_from_provider(self):
        offer = offers_factories.OfferFactory(lastProvider=None)

        validation.check_stock_can_be_created_for_offer(offer)

    def test_offer_from_provider(self, app):
        provider = providers_factories.AllocineProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")

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
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")
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
        provider = providers_factories.APIProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_deletable(stock)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_recently_begun_event_stock(self):
        recently = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=recently)

        validation.check_stock_is_deletable(stock)

    def test_long_begun_event_stock(self):
        too_long_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)
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
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")
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
        provider = providers_factories.APIProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_past_event_stock(self):
        recently = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=recently)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == ["Les événements passés ne sont pas modifiables"]


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
class CheckOfferWithdrawalTest:
    def test_offer_can_have_no_withdrawal_informations(self):
        assert not validation.check_offer_withdrawal(
            withdrawal_type=None,
            withdrawal_delay=None,
            subcategory_id=None,
        )

    def test_withdrawable_event_offer_can_have_no_ticket_to_withdraw(self):
        assert not validation.check_offer_withdrawal(
            withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
            withdrawal_delay=None,
            subcategory_id=subcategories.CONCERT.id,
        )

    def test_withdrawable_event_offer_with_no_ticket_to_withdraw_cant_have_delay(self):
        with pytest.raises(exceptions.NoDelayWhenEventWithdrawalTypeHasNoTicket):
            validation.check_offer_withdrawal(
                withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
                withdrawal_delay=60 * 30,
                subcategory_id=subcategories.CONCERT.id,
            )

    def test_non_withdrawable_event_offer_cant_have_withdrawal(self):
        with pytest.raises(exceptions.NonWithdrawableEventOfferCantHaveWithdrawal):
            validation.check_offer_withdrawal(
                withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
                withdrawal_delay=None,
                subcategory_id=subcategories.JEU_EN_LIGNE.id,
            )

    @pytest.mark.parametrize(
        "withdrawal_type",
        [
            WithdrawalTypeEnum.BY_EMAIL,
            WithdrawalTypeEnum.ON_SITE,
        ],
    )
    def test_withdrawable_event_offer_with_withdrawal_with_a_delay(self, withdrawal_type):
        assert not validation.check_offer_withdrawal(
            withdrawal_type=withdrawal_type,
            withdrawal_delay=60 * 30,
            subcategory_id=subcategories.CONCERT.id,
        )

    @pytest.mark.parametrize(
        "withdrawal_type",
        [
            WithdrawalTypeEnum.BY_EMAIL,
            WithdrawalTypeEnum.ON_SITE,
        ],
    )
    def test_withdrawable_event_offer_with_ticket_must_have_delay(self, withdrawal_type):
        with pytest.raises(exceptions.EventWithTicketMustHaveDelay):
            validation.check_offer_withdrawal(
                withdrawal_type=withdrawal_type,
                withdrawal_delay=None,
                subcategory_id=subcategories.CONCERT.id,
            )

    @pytest.mark.parametrize(
        "subcategory_id",
        subcategories.WITHDRAWABLE_SUBCATEGORIES,
    )
    def test_withdrawable_event_offer_must_have_withdrawal_type(self, subcategory_id):
        assert not validation.check_offer_withdrawal(
            withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
            withdrawal_delay=None,
            subcategory_id=subcategory_id,
        )

    def test_withdrawable_event_offer_must_have_withdrawal(self):
        with pytest.raises(exceptions.WithdrawableEventOfferMustHaveWithdrawal):
            validation.check_offer_withdrawal(
                withdrawal_type=None,
                withdrawal_delay=None,
                subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
            )
