import datetime
import pathlib
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import validation
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.models.api_errors import ApiErrors

import tests


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"

pytestmark = pytest.mark.usefixtures("db_session")


class CheckCanEditStockSynchronizedStockTest:
    def test_allocine_offer(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")

        validation.check_can_edit_synchronized_stock(offer)

    def test_non_allocine_provider_offer(self):
        offerer = providers_factories.PublicApiProviderFactory()
        provider_offer = offers_factories.OfferFactory(lastProvider=offerer, idAtProvider="1")

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_can_edit_synchronized_stock(provider_offer)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_allowed_provider(self):
        provider = providers_factories.PublicApiProviderFactory()
        provider_offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")

        validation.check_can_edit_synchronized_stock(provider_offer, provider)

    def test_synchronized_offer_stock_quantity(self):
        provider = providers_factories.PublicApiProviderFactory()
        provider_offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")

        validation.check_can_edit_synchronized_stock(provider_offer, None, {"quantity"})

    @pytest.mark.parametrize(
        "attribute",
        ["price", "beginning_datetime", "booking_limit_datetime", "price_category", "id_at_provider"],
    )
    def test_non_allocine_provider_offer_stock_other_attribute(self, attribute):
        offerer = providers_factories.PublicApiProviderFactory()
        provider_offer = offers_factories.OfferFactory(lastProvider=offerer, idAtProvider="1")

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_can_edit_synchronized_stock(provider_offer, None, {attribute})

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]


class CheckCanInputIdAtProviderTest:
    def test_without_id_at_provider(self):
        validation.check_can_input_id_at_provider(None, None)

    def test_with_id_at_provider(self):
        provider = providers_factories.PublicApiProviderFactory()
        validation.check_can_input_id_at_provider(provider, "an id at provider")

    def test_raise_when_id_at_provider_given_without_a_provider(self):
        with pytest.raises(exceptions.OfferException) as error:
            validation.check_can_input_id_at_provider(None, "an id at provider")

        assert error.value.errors["idAtProvider"] == [
            "Une offre ne peut être créée ou éditée avec un idAtProvider si elle n'a pas de provider"
        ]


class CheckCanInputIdAtProviderForThisVenueTest:
    def test_without_id_at_provider(self):
        venue = offerers_factories.VenueFactory()
        validation.check_can_input_id_at_provider_for_this_venue(venue.id, None)

    def test_with_id_at_provider(self):
        venue = offerers_factories.VenueFactory()
        validation.check_can_input_id_at_provider_for_this_venue(venue.id, "an id at provider")

    def test_should_not_raise_when_id_at_provider_is_taken_by_offer(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        venue = offerers_factories.VenueFactory()
        id_at_provider = "tout_roule"

        offer = offers_factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
            venue=venue,
            idAtProvider=id_at_provider,
        )

        validation.check_can_input_id_at_provider_for_this_venue(venue.id, id_at_provider, offer_id=offer.id)

    def test_raise_when_id_at_provider_already_taken_by_other_offer(self):
        provider = providers_factories.PublicApiProviderFactory()
        offerer = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        venue = offerers_factories.VenueFactory()
        id_at_provider = "rolalala"

        # existing offer with `id_at_provider`
        offers_factories.OfferFactory(
            lastProvider=provider,
            name="Offer linked to a provider",
            venue=venue,
            idAtProvider=id_at_provider,
        )

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_can_input_id_at_provider_for_this_venue(venue.id, id_at_provider)

        assert error.value.errors["idAtProvider"] == ["`rolalala` is already taken by another venue offer"]


class CheckPricesForStockTest:
    def test_event_prices(self):
        offer = offers_factories.EventOfferFactory()
        validation.check_stock_price(0, offer)
        validation.check_stock_price(1.5, offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(310.5, offer)
        assert error.value.errors["price300"] == ["Le prix d’une offre ne peut excéder 300 euros."]

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(-1.5, offer)
        assert error.value.errors["price"] == ["Le prix doit être positif"]

    def test_event_prices_for_nc(self):
        venue = offerers_factories.CaledonianVenueFactory()
        offer = offers_factories.EventOfferFactory.create(name="Offre calédonienne EVENT", venue=venue)

        validation.check_stock_price(0, offer)
        validation.check_stock_price(20, offer)
        validation.check_stock_price(200, offer)  # limit

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(200.01, offer)
        assert error.value.errors["price23865"] == ["Le prix d’une offre ne peut excéder 23865 francs Pacifique."]

    def test_thing_prices(self):
        offer = offers_factories.ThingOfferFactory()
        validation.check_stock_price(0, offer)
        validation.check_stock_price(1.5, offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(310.5, offer)
        assert error.value.errors["price300"] == ["Le prix d’une offre ne peut excéder 300 euros."]

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(-1.5, offer)
        assert error.value.errors["price"] == ["Le prix doit être positif"]

    def test_thing_prices_for_nc(self):
        venue = offerers_factories.CaledonianVenueFactory()
        offer = offers_factories.ThingOfferFactory.create(name="Offre calédonienne THING", venue=venue)

        validation.check_stock_price(0, offer)
        validation.check_stock_price(20, offer)
        validation.check_stock_price(200, offer)  # limit

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(200.01, offer)
        assert error.value.errors["price23865"] == ["Le prix d’une offre ne peut excéder 23865 francs Pacifique."]

    def test_price_limitation_rule(self):
        offers_factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, rate=Decimal("0.5")
        )
        offer = offers_factories.ThingStockFactory(
            price=100,
            offer__subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            offer__lastValidationPrice=Decimal("80.00"),
        ).offer
        validation.check_stock_price(90, offer)
        validation.check_stock_price(65, offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(121, offer)
        assert error.value.errors["priceLimitationRule"] == [
            "Le prix indiqué est invalide, veuillez créer une nouvelle offre"
        ]

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(39, offer)
        assert error.value.errors["priceLimitationRule"] == [
            "Le prix indiqué est invalide, veuillez créer une nouvelle offre"
        ]

    def test_price_limitation_rule_ok_with_draft_offer(self):
        offers_factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, rate=Decimal("0.5")
        )
        offer = offers_factories.ThingStockFactory(
            price=100,
            offer__subcategoryId=subcategories.ACHAT_INSTRUMENT.id,
            offer__lastValidationPrice=Decimal("80.00"),
            offer__validation=OfferValidationStatus.DRAFT,
        ).offer
        validation.check_stock_price(90, offer)
        validation.check_stock_price(15, offer)

    def test_price_limitation_rule_with_no_last_validation_price(self):
        offers_factories.OfferPriceLimitationRuleFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, rate=Decimal("0.5")
        )
        offer = offers_factories.ThingOfferFactory(
            subcategoryId=subcategories.ACHAT_INSTRUMENT.id, lastValidationPrice=None
        )
        offers_factories.ThingStockFactory(price=80, offer=offer)
        offers_factories.ThingStockFactory(price=100, offer=offer)

        validation.check_stock_price(119, offer)
        validation.check_stock_price(41, offer)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(121, offer)
        assert error.value.errors["priceLimitationRule"] == [
            "Le prix indiqué est invalide, veuillez créer une nouvelle offre"
        ]

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_price(39, offer)
        assert error.value.errors["priceLimitationRule"] == [
            "Le prix indiqué est invalide, veuillez créer une nouvelle offre"
        ]


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
            "Impossible de mettre une date de début si l'offre ne porte pas sur un évènement"
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


class CheckStockCanBeCreatedForOfferTest:
    def test_offer_from_provider(self, app):
        provider = providers_factories.AllocineProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")

        with pytest.raises(ApiErrors) as error:
            validation.check_provider_can_create_stock(offer)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_allowed_provider(self, app):
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")

        validation.check_provider_can_create_stock(offer, provider)


class CheckStockIsDeletableTest:
    def test_rejected_offer(self):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.REJECTED)
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_stock_is_deletable(stock)

        assert error.value.errors["global"] == ["Les offres refusées ne sont pas modifiables"]

    def test_recently_begun_event_stock(self):
        recently = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=recently)

        validation.check_stock_is_deletable(stock)

    def test_long_begun_event_stock(self):
        too_long_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        stock = offers_factories.EventStockFactory(beginningDatetime=too_long_ago)

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_stock_is_deletable(stock)

        assert error.value.errors["global"] == [
            "L'évènement s'est terminé il y a plus de deux jours, la suppression est impossible."
        ]


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

    def test_cinema_provider_offer(self):
        boost_provider = get_provider_by_local_class("BoostStocks")
        offer = offers_factories.OfferFactory(lastProvider=boost_provider, idAtProvider="2")
        stock = offers_factories.StockFactory(offer=offer)

        validation.check_stock_is_updatable(stock)

    def test_rejected_offer(self):
        offer = offers_factories.OfferFactory(validation=OfferValidationStatus.REJECTED)
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == ["Les offres refusées ne sont pas modifiables"]

    def test_offer_from_non_allocine_provider(self):
        provider = providers_factories.PublicApiProviderFactory()
        offer = offers_factories.OfferFactory(lastProvider=provider, idAtProvider="1")
        stock = offers_factories.StockFactory(offer=offer)

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == ["Les offres importées ne sont pas modifiables"]

    def test_past_event_stock(self):
        recently = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        stock = offers_factories.EventStockFactory(beginningDatetime=recently)

        with pytest.raises(ApiErrors) as error:
            validation.check_stock_is_updatable(stock)

        assert error.value.errors["global"] == ["Les évènements passés ne sont pas modifiables"]

    def test_past_event_draft_stock(self):
        recently = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        stock = offers_factories.EventStockFactory(
            beginningDatetime=recently, offer__validation=OfferValidationStatus.DRAFT
        )
        validation.check_stock_is_updatable(stock)


class CheckImageTest:
    def test_ok(self):
        image_as_bytes = (IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        validation.check_image(
            image_as_bytes,
            accepted_types=("jpeg", "jpg"),
            min_width=400,
            min_height=400,
        )

    def test_ok_converted_mpo(self):
        # This image is a MPO image file converted to JPEG
        image_as_bytes = (IMAGES_DIR / "converted-mpo.jpg").read_bytes()
        validation.check_image(
            image_as_bytes,
            accepted_types=("jpeg", "jpg", "mpo"),
            min_width=400,
            min_height=400,
        )

    def test_ok_converted_webp(self):
        image_as_bytes = (IMAGES_DIR / "wrbp-type-image.webp").read_bytes()
        validation.check_image(
            image_as_bytes,
            accepted_types=("jpeg", "jpg", "webp"),
            min_width=400,
            min_height=400,
        )

    def test_image_too_small_with_width_and_height_constraint(self):
        image_as_bytes = (IMAGES_DIR / "mouette_portrait.jpg").read_bytes()
        with pytest.raises(exceptions.ImageTooSmall) as error:
            validation.check_image(
                image_as_bytes,
                accepted_types=("jpeg", "jpg"),
                min_width=400,
                min_height=400,
            )
        assert str(error.value) == "Utilisez une image plus grande (supérieure à 400px par 400px)"

    def test_image_too_small_with_width_constraint(self):
        image_as_bytes = (IMAGES_DIR / "mouette_portrait.jpg").read_bytes()
        with pytest.raises(exceptions.ImageTooSmall) as error:
            validation.check_image(
                image_as_bytes,
                accepted_types=("jpeg", "jpg"),
                min_width=400,
                min_height=None,
            )
        assert str(error.value) == "Utilisez une image plus grande (supérieure à 400px de large)"

    def test_image_too_small_with_height_constraint(self):
        image_as_bytes = (IMAGES_DIR / "mouette_portrait.jpg").read_bytes()
        with pytest.raises(exceptions.ImageTooSmall) as error:
            validation.check_image(
                image_as_bytes,
                accepted_types=("jpeg", "jpg"),
                min_width=None,
                min_height=1000,
            )
        assert str(error.value) == "Utilisez une image plus grande (supérieure à 1000px de haut)"

    def test_image_too_small_with_no_min_constraint_should_not_raise(self):
        image_as_bytes = (IMAGES_DIR / "mouette_portrait.jpg").read_bytes()
        validation.check_image(
            image_as_bytes,
            accepted_types=("jpeg", "jpg"),
            min_width=None,
            min_height=None,
        )

    def test_fake_jpeg(self):
        image_as_bytes = (IMAGES_DIR / "mouette_fake_jpg.jpg").read_bytes()
        with pytest.raises(exceptions.UnidentifiedImage):
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


class CheckValidationStatusTest:
    @pytest.mark.parametrize(
        "validation_status",
        [OfferValidationStatus.APPROVED, OfferValidationStatus.DRAFT, OfferValidationStatus.PENDING],
    )
    def test_approved_offer(self, validation_status):
        offer = offers_factories.OfferFactory(validation=validation_status)

        validation.check_validation_status(offer)

    def test_rejected_offer(self):
        rejected_offer = offers_factories.OfferFactory(validation=OfferValidationStatus.REJECTED)

        with pytest.raises(exceptions.OfferException) as error:
            validation.check_validation_status(rejected_offer)

        assert error.value.errors["global"] == ["Les offres refusées ne sont pas modifiables"]


class CheckOfferWithdrawalTest:
    def test_offer_can_have_no_withdrawal_informations(self):
        assert not validation.check_offer_withdrawal(
            withdrawal_type=None, withdrawal_delay=None, subcategory_id=None, booking_contact=None, provider=None
        )

    def test_withdrawable_event_offer_can_have_no_ticket_to_withdraw(self):
        assert not validation.check_offer_withdrawal(
            withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
            withdrawal_delay=None,
            subcategory_id=subcategories.CONCERT.id,
            booking_contact="booking@conta.ct",
            provider=None,
        )

    def test_withdrawable_event_offer_with_no_ticket_to_withdraw_cant_have_delay(self):
        with pytest.raises(exceptions.OfferException) as error:
            validation.check_offer_withdrawal(
                withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
                withdrawal_delay=60 * 30,
                subcategory_id=subcategories.CONCERT.id,
                booking_contact="booking@conta.ct",
                provider=None,
            )

        assert error.value.errors["offer"] == [
            "Il ne peut pas y avoir de délai de retrait lorsqu'il s'agit d'un évènement sans ticket"
        ]

    def test_non_withdrawable_event_offer_can_have_withdrawal(self):
        provider = providers_factories.ProviderFactory(
            bookingExternalUrl="https://toto.fr/book", cancelExternalUrl="https://toto.fr/cancel"
        )
        assert not validation.check_offer_withdrawal(
            withdrawal_type=WithdrawalTypeEnum.IN_APP,
            withdrawal_delay=None,
            subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
            booking_contact="toto@mail.fr",
            provider=provider,
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
            booking_contact="booking@conta.ct",
            provider=None,
        )

    @pytest.mark.parametrize(
        "withdrawal_type",
        [
            WithdrawalTypeEnum.BY_EMAIL,
            WithdrawalTypeEnum.ON_SITE,
        ],
    )
    def test_withdrawable_event_offer_with_ticket_must_have_delay(self, withdrawal_type):
        with pytest.raises(exceptions.OfferException) as error:
            validation.check_offer_withdrawal(
                withdrawal_type=withdrawal_type,
                withdrawal_delay=None,
                subcategory_id=subcategories.CONCERT.id,
                booking_contact="booking@conta.ct",
                provider=None,
            )

        assert error.value.errors["offer"] == ["Un évènement avec ticket doit avoir un délai de renseigné"]

    @pytest.mark.parametrize(
        "subcategory_id",
        subcategories.WITHDRAWABLE_SUBCATEGORIES,
    )
    def test_withdrawable_event_offer_must_have_withdrawal_type(self, subcategory_id):
        assert not validation.check_offer_withdrawal(
            withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
            withdrawal_delay=None,
            subcategory_id=subcategory_id,
            booking_contact="booking@conta.ct",
            provider=None,
        )

    def test_withdrawable_event_offer_must_have_withdrawal(self):
        with pytest.raises(exceptions.OfferException) as error:
            validation.check_offer_withdrawal(
                withdrawal_type=None,
                withdrawal_delay=None,
                subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
                booking_contact="booking@conta.ct",
                provider=None,
            )

        assert error.value.errors["offer"] == [
            "Une offre qui a un ticket retirable doit avoir un type de retrait renseigné",
        ]

    def test_withdrawable_event_offer_must_have_booking_contact(self):
        with pytest.raises(exceptions.OfferException) as error:
            validation.check_offer_withdrawal(
                withdrawal_type=WithdrawalTypeEnum.NO_TICKET,
                withdrawal_delay=None,
                subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
                booking_contact=None,
                provider=None,
            )

        assert error.value.errors["offer"] == [
            "Une offre qui a un ticket retirable doit avoir l'email du contact de réservation",
        ]

    def test_withdrawable_event_offer_with_ticketing_service_at_provider_level_can_be_in_app(self):
        provider = providers_factories.PublicApiProviderFactory(name="Technical provider")

        assert not validation.check_offer_withdrawal(
            withdrawal_type=WithdrawalTypeEnum.IN_APP,
            withdrawal_delay=None,
            subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
            booking_contact="booking@conta.ct",
            provider=provider,
        )

    def test_withdrawable_event_offer_with_ticketing_service_at_venue_level_can_be_in_app(self):
        provider = providers_factories.ProviderFactory(name="Technical provider")
        venue_provider = providers_factories.VenueProviderFactory(provider=provider)
        providers_factories.VenueProviderExternalUrlsFactory(venueProvider=venue_provider)

        validation.check_offer_withdrawal(
            withdrawal_type=WithdrawalTypeEnum.IN_APP,
            withdrawal_delay=None,
            subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
            booking_contact="booking@conta.ct",
            provider=provider,
            venue_provider=venue_provider,
        )

    def test_withdrawable_event_offer_without_provider_cannot_be_in_app(self):
        with pytest.raises(exceptions.OfferException) as error:
            validation.check_offer_withdrawal(
                withdrawal_type=WithdrawalTypeEnum.IN_APP,
                withdrawal_delay=None,
                subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
                booking_contact="booking@conta.ct",
                provider=None,
            )
        assert error.value.errors["offer"] == [
            "Vous devez supporter l'interface de billeterie pour créer des offres avec billet",
        ]

    def test_withdrawable_event_offer_with_provider_without_a_ticketing_service_implementation_cannot_be_in_app(self):
        # A provider without bookingExternalUrl or cancelExternalUrl
        provider = providers_factories.ProviderFactory(name="Technical provider", localClass=None)
        with pytest.raises(exceptions.OfferException) as error:
            validation.check_offer_withdrawal(
                withdrawal_type=WithdrawalTypeEnum.IN_APP,
                withdrawal_delay=None,
                subcategory_id=subcategories.FESTIVAL_MUSIQUE.id,
                booking_contact="booking@conta.ct",
                provider=provider,
            )

        assert error.value.errors["offer"] == [
            "Vous devez supporter l'interface de billeterie pour créer des offres avec billet",
        ]


class CheckOfferExtraDataTest:
    def test_invalid_ean_extra_data(self):
        with pytest.raises(ApiErrors) as error:
            validation.check_offer_extra_data(
                subcategories.JEU_EN_LIGNE.id, {}, offerers_factories.VenueFactory(), False, ean=12345678
            )
        assert error.value.errors["ean"] == ["L'EAN doit être une chaîne de caractères"]

        with pytest.raises(ApiErrors) as error:
            validation.check_offer_extra_data(
                subcategories.JEU_EN_LIGNE.id, {}, offerers_factories.VenueFactory(), False, ean="invalid ean"
            )
        assert error.value.errors["ean"] == ["L'EAN doit être composé de 13 chiffres"]

    def test_valid_ean_extra_data(self):
        assert (
            validation.check_offer_extra_data(
                subcategories.JEU_EN_LIGNE.id,
                {},
                offerers_factories.VenueFactory(),
                False,
                ean="1234567891234",
            )
            is None
        )

    def test_valid_show_types(self):
        assert (
            validation.check_offer_extra_data(
                subcategories.SPECTACLE_REPRESENTATION.id,
                {"showType": "200", "showSubType": "201"},
                offerers_factories.VenueFactory(),
                True,
            )
            is None
        )

    def test_valid_music_types(self):
        assert (
            validation.check_offer_extra_data(
                subcategories.CONCERT.id,
                {"musicType": "530", "musicSubType": "533"},
                offerers_factories.VenueFactory(),
                False,
            )
            is None
        )

    def test_invalid_show_type_code(self):
        with pytest.raises(ApiErrors) as error:
            validation.check_offer_extra_data(
                subcategories.JEU_EN_LIGNE.id, {"showType": "1"}, offerers_factories.VenueFactory(), False
            )

        assert error.value.errors["showType"] == ["should be in allowed values"]

    def test_invalid_show_type_format(self):
        with pytest.raises(ApiErrors) as error:
            validation.check_offer_extra_data(
                subcategories.JEU_EN_LIGNE.id, {"showType": "one"}, offerers_factories.VenueFactory(), False
            )

        assert error.value.errors["showType"] == ["should be an int or an int string"]

    def test_ean_already_exists(self):
        offer = offers_factories.OfferFactory(ean="1234567891234")

        with pytest.raises(ApiErrors) as error:
            validation.check_offer_extra_data(
                subcategories.LIVRE_PAPIER.id, {}, offer.venue, False, ean="1234567891234"
            )

        assert error.value.errors["ean"] == [
            "Une offre avec cet EAN existe déjà. Vous pouvez la retrouver dans l'onglet Offres."
        ]

    def test_allow_creation_with_inactive_ean(self):
        offer = offers_factories.OfferFactory(ean="1234567891234", isActive=False)
        assert (
            validation.check_offer_extra_data(
                subcategories.LIVRE_PAPIER.id, {}, offer.venue, False, ean="1234567891234"
            )
            is None
        )


class CheckBookingLimitDatetimeTest:
    @pytest.mark.parametrize(
        "stock_factory, offer_factory, venue_factory",
        [
            (
                educational_factories.CollectiveStockFactory,
                educational_factories.CollectiveOfferFactory,
                offerers_factories.VenueFactory,
            ),
            (
                offers_factories.StockFactory,
                offers_factories.DigitalOfferFactory,
                offerers_factories.VirtualVenueFactory,
            ),
            (offers_factories.StockFactory, offers_factories.OfferFactory, offerers_factories.VenueFactory),
        ],
    )
    def test_check_booking_limit_datetime_should_raise_because_booking_limit_is_one_hour_after(
        self, stock_factory, offer_factory, venue_factory
    ):
        venue = venue_factory(departementCode=71)
        offer = offer_factory(venueId=venue.id)
        if stock_factory == educational_factories.CollectiveStockFactory:
            stock = stock_factory(collectiveOfferId=offer.id)
        else:
            stock = stock_factory(offerId=offer.id)

        beginning_date = datetime.datetime(2024, 7, 19, 8)
        booking_limit_date = beginning_date + datetime.timedelta(hours=1)
        with pytest.raises(exceptions.BookingLimitDatetimeTooLate):
            validation.check_booking_limit_datetime(
                stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date
            )

    def test_check_booking_limit_datetime_should_raise(self):
        stock = offers_factories.StockFactory()
        collective_stock = educational_factories.CollectiveStockFactory()

        beginning_date = datetime.datetime(2024, 7, 19, 8)
        booking_limit_date = beginning_date + datetime.timedelta(days=1)

        # with stock
        with pytest.raises(exceptions.BookingLimitDatetimeTooLate):
            validation.check_booking_limit_datetime(
                stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date
            )

        # with collective stock
        with pytest.raises(exceptions.BookingLimitDatetimeTooLate):
            validation.check_booking_limit_datetime(
                collective_stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date
            )

        with pytest.raises(exceptions.BookingLimitDatetimeTooLate):
            validation.check_booking_limit_datetime(
                None, beginning=beginning_date, booking_limit_datetime=booking_limit_date
            )

    @pytest.mark.parametrize(
        "stock_factory", [offers_factories.StockFactory, educational_factories.CollectiveStockFactory]
    )
    def test_check_booking_limit_datetime_should_not_raise_because_a_date_is_missing(self, stock_factory):
        stock = stock_factory()

        beginning_date = datetime.datetime(2024, 7, 19, 8)
        booking_limit_date = beginning_date + datetime.timedelta(days=1)

        validation.check_booking_limit_datetime(stock, beginning=None, booking_limit_datetime=booking_limit_date)
        validation.check_booking_limit_datetime(stock, beginning=beginning_date, booking_limit_datetime=None)

    @pytest.mark.parametrize(
        "offer_factory",
        [offers_factories.OfferFactory, offers_factories.EventOfferFactory, offers_factories.DigitalOfferFactory],
    )
    def test_check_booking_limit_datetime_should_not_raise_with_timezone(self, offer_factory):
        oa = offerers_factories.OffererAddressFactory(address__departmentCode="974")
        offer = offer_factory(venue__timezone=71, offererAddress=oa)
        stock = offers_factories.StockFactory(offer=offer)

        beginning_date = datetime.datetime(2024, 7, 19, 8, tzinfo=datetime.timezone.utc)
        booking_limit_date = beginning_date - datetime.timedelta(hours=1)

        try:
            validation.check_booking_limit_datetime(
                stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date
            )
        except exceptions.BookingLimitDatetimeTooLate as e:
            assert False, f"Should not raise exception {e}"

    @pytest.mark.parametrize(
        "time_zone_expected,",
        [
            ZoneInfo("Indian/Reunion"),  # "offer.offerer_address.address.timezone",
            ZoneInfo("America/Guadeloupe"),  #  "offer.venue.offererAddress.address.timezone",
            ZoneInfo("Europe/Paris"),  # "offer.venue.timezone",
        ],
    )
    def test_check_booking_limit_datetime_priorisation_order(self, time_zone_expected):
        oa = (
            offerers_factories.OffererAddressFactory(address__departmentCode="974", address__inseeCode="97410")
            if time_zone_expected == ZoneInfo("Indian/Reunion")
            else None
        )
        if time_zone_expected in [ZoneInfo("Indian/Reunion"), ZoneInfo("America/Guadeloupe")]:
            venue = offerers_factories.VenueFactory(
                departementCode=71,
                offererAddress__address__departmentCode="971",
                offererAddress__address__inseeCode="97103",
                offererAddress__address__timezone="America/Guadeloupe",
            )  # oa guadeloupe venue#france
        else:
            venue = offerers_factories.VirtualVenueFactory(departementCode=71)
        offer = offers_factories.OfferFactory(offererAddress=oa, venue=venue)  # reunion
        stock = offers_factories.StockFactory(offer=offer)
        beginning_date = datetime.datetime(2024, 7, 19, 8, tzinfo=datetime.timezone.utc)
        booking_limit_date = beginning_date - datetime.timedelta(hours=1)

        # It's ok to ignore the tuple unpacking warning here because we are testing the value of beginning
        # and it should fails if check_booking_limit_datetime returns an empty list
        beginning, booking_limit_datetime = validation.check_booking_limit_datetime(
            stock, beginning=beginning_date, booking_limit_datetime=booking_limit_date
        )
        assert beginning.tzinfo == booking_limit_datetime.tzinfo == time_zone_expected


class CheckOfferIsBookableBeforeStockBookingLimitDatetimeTest:
    @pytest.mark.parametrize(
        "offer_publication_datetime,offer_booking_allowed_datetime,stocks_datetime,expected_errors",
        [
            (
                datetime.datetime(2025, 6, 27),
                None,
                datetime.datetime(2025, 6, 26),
                {
                    "bookingLimitDatetime": [
                        "the stock will not be published before its `bookingLimitDatetime`. Either change `bookingLimitDatetime` to a later date, or update the offer `publicationDatetime`"
                    ]
                },
            ),
            (
                None,
                datetime.datetime(2025, 6, 27),
                datetime.datetime(2025, 6, 26),
                {
                    "bookingLimitDatetime": [
                        "the stock will not be bookable before its `bookingLimitDatetime`. Either change `bookingLimitDatetime` to a later date, or update the offer `bookingAllowedDatetime`"
                    ]
                },
            ),
            (
                datetime.datetime(2025, 6, 29),
                datetime.datetime(2025, 6, 27),
                datetime.datetime(2025, 6, 26),
                {
                    "bookingLimitDatetime": [
                        "the stock will not be published before its `bookingLimitDatetime`. Either change `bookingLimitDatetime` to a later date, or update the offer `publicationDatetime`",
                        "the stock will not be bookable before its `bookingLimitDatetime`. Either change `bookingLimitDatetime` to a later date, or update the offer `bookingAllowedDatetime`",
                    ],
                },
            ),
        ],
    )
    def test_should_raise(
        self,
        offer_publication_datetime,
        offer_booking_allowed_datetime,
        stocks_datetime,
        expected_errors,
    ):
        with pytest.raises(exceptions.OfferException) as exc:
            offer = offers_factories.OfferFactory(
                publicationDatetime=offer_publication_datetime,
                bookingAllowedDatetime=offer_booking_allowed_datetime,
            )
            validation.check_offer_is_bookable_before_stock_booking_limit_datetime(offer, stocks_datetime)

        assert exc.value.errors == expected_errors

    @pytest.mark.parametrize(
        "offer_publication_datetime,offer_booking_allowed_datetime,stocks_datetime",
        [
            (datetime.datetime(2025, 6, 23), None, datetime.datetime(2025, 6, 26)),
            (None, datetime.datetime(2025, 6, 24), datetime.datetime(2025, 6, 26)),
        ],
    )
    def test_should_NOT_raise(
        self,
        offer_publication_datetime,
        offer_booking_allowed_datetime,
        stocks_datetime,
    ):
        offer = offers_factories.OfferFactory(
            publicationDatetime=offer_publication_datetime,
            bookingAllowedDatetime=offer_booking_allowed_datetime,
        )
        validation.check_offer_is_bookable_before_stock_booking_limit_datetime(offer, stocks_datetime)


class CheckPublicationDateTest:
    def test_check_publication_date_should_raise(self):
        with pytest.raises(exceptions.OfferException):
            validation.check_publication_date(datetime.datetime.utcnow() + datetime.timedelta(days=750))

    def test_check_publication_date_should_raise_not_raise(self):
        for i in [0, 15, 30, 45]:
            publication_date = datetime.datetime.utcnow().replace(minute=0) + datetime.timedelta(hours=1, minutes=i)
            assert validation.check_publication_date(publication_date) is None


class CheckOffererIsEligibleForHeadlineOffersTest:
    def test_check_offerer_is_eligible_for_headline_offers(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.VenueFactory(isPermanent=True, isVirtual=False, managingOfferer=offerer)
        offerers_factories.VirtualVenueFactory(isPermanent=False, managingOfferer=offerer)

        assert validation.check_offerer_is_eligible_for_headline_offers(offerer.id) is None

        another_venue = offerers_factories.VenueFactory(isPermanent=False, isVirtual=False, managingOfferer=offerer)
        with pytest.raises(exceptions.OffererCanNotHaveHeadlineOffer) as exc:
            validation.check_offerer_is_eligible_for_headline_offers(offerer.id)
            msg = "This offerer can not have headline offers"
            assert exc.value.errors["headlineOffer"] == [msg]

        another_venue.isPermanent = True
        with pytest.raises(exceptions.OffererCanNotHaveHeadlineOffer) as exc:
            validation.check_offerer_is_eligible_for_headline_offers(offerer.id)
            msg = "This offerer can not have headline offers"
            assert exc.value.errors["headlineOffer"] == [msg]

    def test_check_offer_is_eligible_to_be_headline(self):
        offerer = offerers_factories.OffererFactory()
        permanent_venue = offerers_factories.VenueFactory(isPermanent=True, isVirtual=False, managingOfferer=offerer)
        virtual_venue = offerers_factories.VirtualVenueFactory(isPermanent=False, managingOfferer=offerer)
        offer = offers_factories.ThingOfferFactory(venue=permanent_venue)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)
        digital_offer = offers_factories.DigitalOfferFactory(venue=virtual_venue)
        offers_factories.StockFactory(offer=digital_offer)
        offers_factories.MediationFactory(offer=digital_offer)
        offers_factories.MediationFactory(offer=digital_offer)
        offer_without_image = offers_factories.OfferFactory(venue=permanent_venue)
        offers_factories.StockFactory(offer=offer_without_image)

        assert validation.check_offerer_is_eligible_for_headline_offers(offerer.id) is None
        assert validation.check_offer_is_eligible_to_be_headline(offer) is None

        with pytest.raises(exceptions.VirtualOfferCanNotBeHeadline) as exc:
            validation.check_offer_is_eligible_to_be_headline(digital_offer)
            msg = "Digital offers can not be set to the headline"
            assert exc.value.errors["headlineOffer"] == [msg]

        with pytest.raises(exceptions.OfferWithoutImageCanNotBeHeadline) as exc:
            validation.check_offer_is_eligible_to_be_headline(offer_without_image)
            msg = "Offers without images can not be set to the headline"
            assert exc.value.errors["headlineOffer"] == [msg]


class CheckOfferNameDoesNotContainEanTest:
    @pytest.mark.parametrize(
        "offer_name",
        [
            "Mon offre de filou - 3759217254634",
            "4759217254634",
            "[3759217254634] J'essaye de mettre mon offre en avant",
        ],
    )
    def test_check_offer_name_does_not_contain_ean_should_raise(self, offer_name):
        with pytest.raises(exceptions.OfferException):
            validation.check_offer_name_does_not_contain_ean(offer_name)


class CheckOfferCanHaveActivationCodesTest:
    def test_check_offer_can_have_activation_codes_should_not_raise(self):
        digital_offer = offers_factories.DigitalOfferFactory()
        validation.check_offer_can_have_activation_codes(digital_offer)

    def test_check_offer_can_have_activation_codes_should_raise(self):
        physical_offer = offers_factories.OfferFactory()

        with pytest.raises(ApiErrors) as exc:
            validation.check_offer_can_have_activation_codes(physical_offer)

        assert exc.value.errors == {
            "global": ["Impossible de créer des codes d'activation sur une offre qui n'est pas un bien numérique"]
        }

        digital_event_offer = offers_factories.DigitalOfferFactory(subcategoryId=subcategories.RENCONTRE_EN_LIGNE.id)

        with pytest.raises(ApiErrors) as exc:
            validation.check_offer_can_have_activation_codes(digital_event_offer)

        assert exc.value.errors == {
            "global": ["Impossible de créer des codes d'activation sur une offre qui n'est pas un bien numérique"]
        }
