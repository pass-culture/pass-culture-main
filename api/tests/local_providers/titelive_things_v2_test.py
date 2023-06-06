from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import ThingStockFactory
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
import pcapi.core.providers.models as providers_models
from pcapi.core.providers.repository import get_provider_by_local_class
from pcapi.local_providers import TiteLiveThings
from pcapi.local_providers.titelive_things.titelive_things_v2 import COLUMN_INDICES

BASE_DATA_LINE_PARTS = [
    "9782809455069",
    "Secret wars : marvel zombies n.1",
    "1905",
    "6",
    "Secret Wars : Marvel Zombies",
    "1",
    "4,90",
    "Panini Comics Mag",
    "Makassar",
    "24/12/2015",
    "BL",
    "2",
    "0",
    "26,0",
    "17,0",
    "0,0",
    "198",
    "Collectif",
    "18/10/2015",
    "30/04/2023",
    "5,50",
    "",
    "ANGLAIS (ETATS-UNIS)",
    "",
    "",
    "1",
    "Non précisée",
    "",
    "",
    "5621564",
    "0",
    "0",
    "0",
    "",
    "0",
    "0",
    "93",
    "0",
    "0",
    "0",
    "0",
    "0",
    "",
    "0",
    "20303",
    "0",
    "0",
    "412952",
    "",
    "0",
    "0",
    "0",
    "0",
    "0",
    "0",
    "1",
    "",
    "3030400",
]


class TiteliveThingsTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_create_1_thing_from_one_data_line_in_one_file(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "~".join(BASE_DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        product = offers_models.Product.query.one()
        assert product.extraData.get("bookFormat") == offers_models.BookFormat.BEAUX_LIVRES.value
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("isbn") == "9782809455069"
        assert product.extraData.get("ean") == "9782809455069"

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_a_school_book(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        # DATA_LINE_PARTS[COLUMN_INDICES["libelle_csr"]] = "Littérature scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["is_scolaire"]] = "1"
        # DATA_LINE_PARTS[COLUMN_INDICES["n_extraits_mp3"]] = "0"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_update_1_thing_from_one_data_line_in_one_file(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "~".join(BASE_DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")

        offers_factories.ProductFactory(
            name="Old name",
            idAtProviders="9782809455069",
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_things_provider.id,
        )
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        updated_product = offers_models.Product.query.first()
        assert updated_product.name == BASE_DATA_LINE_PARTS[COLUMN_INDICES["titre"]]
        assert updated_product.extraData.get("bookFormat") == offers_models.BookFormat.BEAUX_LIVRES.value

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    def test_does_not_create_thing_when_no_files_found(self, get_files_to_process_from_titelive_ftp, app):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = []

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_does_not_create_thing_when_missing_columns_in_data_line(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = BASE_DATA_LINE_PARTS[COLUMN_INDICES["ean13"]]
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_does_not_create_thing_when_too_many_columns_in_data_line(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "LE"
        # DATA_LINE_PARTS[COLUMN_INDICES["libelle_csr"]] = "Littérature scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["is_scolaire"]] = "1"
        # DATA_LINE_PARTS[COLUMN_INDICES["n_extraits_mp3"]] = "0"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_should_not_create_product_when_school_related_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["code_csr"]] = "2704"
        # DATA_LINE_PARTS[COLUMN_INDICES["libelle_csr"]] = "Littérature scolaire"
        # DATA_LINE_PARTS[COLUMN_INDICES["n_extraits_mp3"]] = ""
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_should_delete_product_when_reference_changes_to_school_related_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["code_csr"]] = "2704"
        # DATA_LINE_PARTS[COLUMN_INDICES["libelle_csr"]] = "Littérature scolaire"
        # DATA_LINE_PARTS[COLUMN_INDICES["n_extraits_mp3"]] = ""
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()
        offers_factories.ProductFactory(
            idAtProviders="9782809455069",
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_should_delete_product_when_non_valid_product_type(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "jeux de société"
        DATA_LINE_PARTS[COLUMN_INDICES["code_csr"]] = "1234"
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "O"
        # DATA_LINE_PARTS[COLUMN_INDICES["libelle_csr"]] = "Littérature scolaire"
        # DATA_LINE_PARTS[COLUMN_INDICES["n_extraits_mp3"]] = ""
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()
        offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            idAtProviders="9782809455069",
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
        )
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_should_log_error_when_trying_to_delete_product_with_associated_bookings(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line_parts = BASE_DATA_LINE_PARTS[:]
        data_line_parts[COLUMN_INDICES["titre"]] = "jeux de société"
        data_line_parts[COLUMN_INDICES["code_csr"]] = "1234"
        data_line_parts[COLUMN_INDICES["code_support"]] = "O"
        # data_line_parts[COLUMN_INDICES["libelle_csr"]] = "Littérature scolaire"
        # data_line_parts[COLUMN_INDICES["n_extraits_mp3"]] = ""
        data_line = "~".join(data_line_parts)
        get_lines_from_thing_file.return_value = iter([data_line])

        provider = providers_factories.TiteLiveThingsProviderFactory()
        bookings_factories.BookingFactory(
            stock__offer__product__dateModifiedAtLastProvider=datetime(2001, 1, 1),
            stock__offer__product__idAtProviders="9782809455069",
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
        assert provider_log_error.payload == "Error deleting product with ISBN: 9782809455069"

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_should_not_create_product_when_product_is_paper_press(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        # DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "9136205982"
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "R"
        DATA_LINE_PARTS[COLUMN_INDICES["taux_tva"]] = "2,10"
        data_line_1 = "~".join(DATA_LINE_PARTS)
        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["taux_tva"]] = "2,10"
        data_line_2 = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line_1, data_line_2])

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()
        products = offers_models.Product.query.all()
        product = products[0]

        # Then
        assert len(products) == 1
        assert product.extraData["isbn"] == "9782809455069"

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_should_delete_product_when_it_changes_to_paper_press_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "R"
        DATA_LINE_PARTS[COLUMN_INDICES["taux_tva"]] = "2,10"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()
        offers_factories.ProductFactory(
            idAtProviders="9782809455069",
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_should_not_delete_product_and_deactivate_associated_offer_when_it_changes_to_paper_press_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "R"
        DATA_LINE_PARTS[COLUMN_INDICES["taux_tva"]] = "2,10"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()

        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = ThingProductFactory(
            idAtProviders="9782809455069",
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
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_does_not_create_product_with_xxx_mark(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "xxx"
        DATA_LINE_PARTS[COLUMN_INDICES["auteurs"]] = "Xxx"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()
        titelive_things = TiteLiveThings()

        # When
        titelive_things.updateObjects()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things_v2.get_lines_from_thing_file")
    def test_deactivate_offers_with_product_with_xxx_mark(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        book_isbn = "9782809455069"

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["ean13"]] = book_isbn
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "xxx"
        DATA_LINE_PARTS[COLUMN_INDICES["auteurs"]] = "Xxx"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()
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
