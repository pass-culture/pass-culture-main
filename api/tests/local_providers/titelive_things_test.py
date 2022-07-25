from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import ThingStockFactory
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import TiteLiveThings
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.repository import repository


BASE_DATA_LINE_PARTS = [
    "9782895026310",
    "2895026319",
    "nouvelles du Chili",
    "",
    "0203",
    "1",
    "",
    "",
    "",
    "18,99",
    "LES EDITIONS DE L'INSTANT MEME",
    "EPAGINE",
    "11/05/2011",
    "BL",
    "2",
    "0",
    "0,0",
    "0,0",
    "0,0",
    "0",
    "0",
    "0",
    "0",
    "Collectif",
    "15/01/2013",
    "02/03/2018",
    "5,50",
    "Littérature Hispano-Portugaise",
    "",
    "",
    "",
    "",
    "",
    "1",
    "3012420280013",
    "",
    "",
    "",
    "",
    "",
    "0",
    "",
    "369",
    "860",
    "3694440",
    "",
]


class TiteliveThingsTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_create_1_thing_from_one_data_line_in_one_file(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "~".join(BASE_DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        product = offers_models.Product.query.one()
        assert product.extraData.get("bookFormat") == offers_models.BookFormat.BEAUX_LIVRES.value
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("isbn") == "9782895026310"

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_a_school_book(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[2] = "livre scolaire"
        DATA_LINE_PARTS[27] = "Littérature scolaire"
        DATA_LINE_PARTS[39] = "1"
        DATA_LINE_PARTS[40] = "0"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_update_1_thing_from_one_data_line_in_one_file(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "~".join(BASE_DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")

        product = create_product_with_thing_subcategory(
            id_at_providers="9782895026310",
            thing_name="Toto à la playa",
            date_modified_at_last_provider=datetime(2001, 1, 1),
            last_provider_id=titelive_things_provider.id,
        )
        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        repository.save(product)
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        updated_product = offers_models.Product.query.first()
        assert updated_product.name == "nouvelles du Chili"
        assert updated_product.extraData.get("bookFormat") == offers_models.BookFormat.BEAUX_LIVRES.value

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    def test_does_not_create_thing_when_no_files_found(self, get_files_to_process_from_titelive_ftp, app):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = []

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_thing_when_missing_columns_in_data_line(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "9782895026310"
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_thing_when_too_many_columns_in_data_line(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[13] = "LE"
        DATA_LINE_PARTS[27] = "Littérature scolaire"
        DATA_LINE_PARTS[39] = "1"
        DATA_LINE_PARTS[40] = "0"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_not_create_product_when_school_related_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[2] = "livre scolaire"
        DATA_LINE_PARTS[4] = "2704"
        DATA_LINE_PARTS[27] = "Littérature scolaire"
        DATA_LINE_PARTS[40] = ""
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_delete_product_when_reference_changes_to_school_related_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[2] = "livre scolaire"
        DATA_LINE_PARTS[4] = "2704"
        DATA_LINE_PARTS[27] = "Littérature scolaire"
        DATA_LINE_PARTS[40] = ""
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.ProviderFactory(localClass="TiteLiveThings")
        repository.save(titelive_provider)
        product = create_product_with_thing_subcategory(
            id_at_providers="9782895026310",
            thing_name="Toto à la playa",
            date_modified_at_last_provider=datetime(2001, 1, 1),
            last_provider_id=titelive_provider.id,
        )
        repository.save(product)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_delete_product_when_non_valid_product_type(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[2] = "jeux de société"
        DATA_LINE_PARTS[4] = "1234"
        DATA_LINE_PARTS[13] = "O"
        DATA_LINE_PARTS[27] = "Littérature scolaire"
        DATA_LINE_PARTS[40] = ""
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.ProviderFactory(localClass="TiteLiveThings")
        product = create_product_with_thing_subcategory(
            id_at_providers="9782895026310",
            thing_name="Toto à la playa",
            date_modified_at_last_provider=datetime(2001, 1, 1),
            last_provider_id=titelive_provider.id,
        )
        repository.save(product)
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_log_error_when_trying_to_delete_product_with_associated_bookings(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line_parts = BASE_DATA_LINE_PARTS[:]
        data_line_parts[2] = "jeux de société"
        data_line_parts[4] = "1234"
        data_line_parts[13] = "O"
        data_line_parts[27] = "Littérature scolaire"
        data_line_parts[40] = ""
        data_line = "~".join(data_line_parts)
        get_lines_from_thing_file.return_value = iter([data_line])

        provider = providers_factories.ProviderFactory(localClass="TiteLiveThings")
        bookings_factories.BookingFactory(
            stock__offer__product__dateModifiedAtLastProvider=datetime(2001, 1, 1),
            stock__offer__product__idAtProviders="9782895026310",
            stock__offer__product__lastProviderId=provider.id,
            stock__offer__product__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        # When
        titelive_things = TiteLiveThings()
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 1
        provider_log_error = providers_models.LocalProviderEvent.query.filter_by(
            type=providers_models.LocalProviderEventType.SyncError
        ).one()
        assert provider_log_error.payload == "Error deleting product with ISBN: 9782895026310"

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_not_create_product_when_product_is_paper_press(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[1] = "9136205982"
        DATA_LINE_PARTS[13] = "R"
        DATA_LINE_PARTS[26] = "2,10"
        data_line_1 = "~".join(DATA_LINE_PARTS)
        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[26] = "2,10"
        data_line_2 = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line_1, data_line_2])

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()
        products = offers_models.Product.query.all()
        product = products[0]

        # Then
        assert len(products) == 1
        assert product.extraData["isbn"] == "9782895026310"

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_delete_product_when_it_changes_to_paper_press_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[13] = "R"
        DATA_LINE_PARTS[26] = "2,10"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.ProviderFactory(localClass="TiteLiveThings")
        repository.save(titelive_provider)
        product = create_product_with_thing_subcategory(
            id_at_providers="9782895026310",
            thing_name="Presse papier",
            date_modified_at_last_provider=datetime(2001, 1, 1),
            last_provider_id=titelive_provider.id,
        )
        repository.save(product)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_not_delete_product_and_deactivate_associated_offer_when_it_changes_to_paper_press_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[13] = "R"
        DATA_LINE_PARTS[26] = "2,10"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.ProviderFactory(localClass="TiteLiveThings")
        repository.save(titelive_provider)

        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = ThingProductFactory(
            idAtProviders="9782895026310",
            name="Presse papier",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
        )
        offer = ThingOfferFactory(product=product, venue=venue, isActive=True)
        stock = ThingStockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(stock=stock)

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        offer = offers_models.Offer.query.one()
        assert offer.isActive is False
        assert offers_models.Product.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_with_xxx_mark(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[2] = "xxx"
        DATA_LINE_PARTS[23] = "Xxx"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.ProviderFactory(localClass="TiteLiveThings")
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_deactivate_offers_with_product_with_xxx_mark(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        book_isbn = "9782895026310"

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[1] = book_isbn
        DATA_LINE_PARTS[2] = "xxx"
        DATA_LINE_PARTS[23] = "Xxx"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.ProviderFactory(localClass="TiteLiveThings")
        repository.save(titelive_provider)
        titelive_things = TiteLiveThings()

        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = ThingProductFactory(
            idAtProviders=book_isbn,
            name="Presse papier",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            extraData={"isbn": book_isbn},
        )
        offer = ThingOfferFactory(product=product, venue=venue, isActive=True)

        # When
        titelive_things.updateObjects()

        # Then
        refreshed_offer = offers_models.Offer.query.get(offer.id)
        refreshed_product = offers_models.Product.query.get(product.id)
        assert refreshed_product.name == "xxx"
        assert refreshed_offer.isActive == False
        assert refreshed_offer.name == "xxx"
