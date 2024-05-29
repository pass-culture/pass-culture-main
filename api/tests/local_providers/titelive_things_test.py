from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import ThingStockFactory
import pcapi.core.offers.models as offers_models
from pcapi.core.providers import constants as providers_constants
import pcapi.core.providers.factories as providers_factories
from pcapi.core.providers.repository import get_provider_by_local_class
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models
from pcapi.local_providers import TiteLiveThings
from pcapi.local_providers.titelive_things.titelive_things import BASE_VAT
from pcapi.local_providers.titelive_things.titelive_things import BOX_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import CALENDAR_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import COLUMN_INDICES
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_01_EXTRACURRICULAR
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_01_SCHOOL
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_01_YOUNG
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_02_AFTER_3_AND_BEFORE_6
from pcapi.local_providers.titelive_things.titelive_things import GTL_LEVEL_02_BEFORE_3
from pcapi.local_providers.titelive_things.titelive_things import LECTORAT_EIGHTEEN_ID
from pcapi.local_providers.titelive_things.titelive_things import OBJECT_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import PAPER_CONSUMABLE_SUPPORT_CODE
from pcapi.local_providers.titelive_things.titelive_things import POSTER_SUPPORT_CODE
from pcapi.models import offer_mixin
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.offer_mixin import OfferValidationType
from pcapi.utils.csr import get_closest_csr


EAN_TEST = "9782809455069"
EAN_TEST_TITLE = "Secret wars : marvel zombies n.1"
GTL_ID_TEST = "03030400"
CODE_CLIL_TEST = "4300"
BASE_DATA_LINE_PARTS = [
    EAN_TEST,
    EAN_TEST_TITLE,
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
    GTL_ID_TEST,
    CODE_CLIL_TEST,
    "3012420280013",
    "0",
    "110101",
    "",  #  \n
]


def run_titelive_things():
    titelive_things = TiteLiveThings()

    titelive_things.updateObjects()
    titelive_things.postTreatment()


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

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        product = offers_models.Product.query.one()
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("ean") == EAN_TEST
        assert product.extraData.get("gtl_id") == GTL_ID_TEST
        closest_csr = get_closest_csr(GTL_ID_TEST)
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == CODE_CLIL_TEST

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_create_1_thing_from_one_data_line_in_one_file_when_gtl_not_has_lpad_zero(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = GTL_ID_TEST[1:]

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        product = offers_models.Product.query.one()
        assert product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value
        assert product.subcategoryId == subcategories.LIVRE_PAPIER.id
        assert product.extraData.get("ean") == EAN_TEST
        assert product.extraData.get("gtl_id") == GTL_ID_TEST
        closest_csr = get_closest_csr(GTL_ID_TEST)
        assert product.extraData.get("csr_id") == closest_csr.get("csr_id")
        assert product.extraData.get("rayon") == closest_csr.get("label")
        assert product.extraData.get("code_clil") == CODE_CLIL_TEST

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_gtl_school_book(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = f"{GTL_LEVEL_01_SCHOOL}000000"

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_vat_20(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["taux_tva"]] = BASE_VAT

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_extracurricular(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre parascolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = f"{GTL_LEVEL_01_EXTRACURRICULAR}000000"

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.parametrize(
        "support_code",
        [
            CALENDAR_SUPPORT_CODE,
            POSTER_SUPPORT_CODE,
            PAPER_CONSUMABLE_SUPPORT_CODE,
            BOX_SUPPORT_CODE,
            OBJECT_SUPPORT_CODE,
        ],
    )
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_non_eligible_support_code(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app, support_code
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = support_code

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_create_product_when_product_is_gtl_school_book_but_in_product_whitelist(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        fraud_factories.ProductWhitelistFactory(ean=BASE_DATA_LINE_PARTS[0])
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = f"{GTL_LEVEL_01_SCHOOL}000000"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_lectorat_eighteen(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["id_lectorat"]] = LECTORAT_EIGHTEEN_ID

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.parametrize(
        "level_02_code_gtl",
        [
            GTL_LEVEL_02_BEFORE_3,
            GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ],
    )
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_small_young(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app, level_02_code_gtl
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = f"{GTL_LEVEL_01_YOUNG}{level_02_code_gtl}0000"

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.parametrize(
        "title",
        [
            "bryan pass toeic",
            "toefl yes we can",
        ],
    )
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_does_not_create_product_when_product_is_toeic_or_toefl(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app, title
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = title

        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

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

        offers_factories.ProductFactory(
            name="Old name",
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_things_provider.id,
        )

        # When
        run_titelive_things()

        # Then
        updated_product = offers_models.Product.query.first()
        assert updated_product.name == EAN_TEST_TITLE
        assert updated_product.extraData.get("bookFormat") == providers_constants.BookFormat.BEAUX_LIVRES.value

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    def test_does_not_create_thing_when_no_files_found(self, get_files_to_process_from_titelive_ftp, app):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = []

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

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

        data_line = EAN_TEST
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

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
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "LE"
        DATA_LINE_PARTS[COLUMN_INDICES["scolaire"]] = "1"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

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
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = f"{GTL_LEVEL_01_SCHOOL}000000"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        providers_factories.TiteLiveThingsProviderFactory()
        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_reject_product_when_gtl_changes_to_school_related_product(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "livre scolaire"
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = f"{GTL_LEVEL_01_SCHOOL}000000"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()
        product = offers_factories.ProductFactory(
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "ean": EAN_TEST,
            },
        )
        offer = offers_factories.OfferFactory(product=product)
        users_factories.FavoriteFactory(offer=offer)

        assert product.isGcuCompatible is True
        assert users_models.Favorite.query.count() == 1
        assert offer.validation != offers_models.OfferValidationStatus.REJECTED

        # When
        run_titelive_things()

        # Then
        product = offers_models.Product.query.one()
        offer = offers_models.Offer.query.one()
        assert product.isGcuCompatible is False
        assert users_models.Favorite.query.count() == 0
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert offer.lastValidationType == offer_mixin.OfferValidationType.CGU_INCOMPATIBLE_PRODUCT

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_reject_product_when_gtl_changes_to_extracurricular_related_product_and_unknown_gtl(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["genre_tite_live"]] = f"{GTL_LEVEL_01_EXTRACURRICULAR}666666"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()
        product = offers_factories.ProductFactory(
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "ean": EAN_TEST,
            },
        )
        offer = offers_factories.OfferFactory(product=product)
        users_factories.FavoriteFactory(offer=offer)

        assert product.isGcuCompatible is True
        assert users_models.Favorite.query.count() == 1
        assert offer.validation != offers_models.OfferValidationStatus.REJECTED

        # When
        run_titelive_things()

        # Then
        product = offers_models.Product.query.one()
        offer = offers_models.Offer.query.one()
        assert product.isGcuCompatible is False
        assert users_models.Favorite.query.count() == 0
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert offer.lastValidationType == offer_mixin.OfferValidationType.CGU_INCOMPATIBLE_PRODUCT

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_reject_product_when_non_valid_product_type(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "jeux de société"
        DATA_LINE_PARTS[COLUMN_INDICES["code_rayon_csr"]] = "1234"
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "O"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()
        product = offers_factories.ProductFactory(
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            extraData={
                "ean": EAN_TEST,
            },
        )

        assert product.isGcuCompatible is True
        # When
        run_titelive_things()

        # Then
        product = offers_models.Product.query.one()
        assert product.isGcuCompatible is False

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_not_create_product_when_product_is_paper_press(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["ean"]] = "9999999999999"
        DATA_LINE_PARTS[COLUMN_INDICES["code_support"]] = "R"
        DATA_LINE_PARTS[COLUMN_INDICES["taux_tva"]] = "2,10"
        data_line_1 = "~".join(DATA_LINE_PARTS)
        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["taux_tva"]] = "2,10"
        data_line_2 = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line_1, data_line_2])

        providers_factories.TiteLiveThingsProviderFactory()

        # When
        run_titelive_things()

        products = offers_models.Product.query.all()
        product = products[0]

        # Then
        assert len(products) == 1
        assert product.extraData["ean"] == EAN_TEST

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_reject_product_when_it_changes_to_paper_press_product(
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
        product = offers_factories.ProductFactory(
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            extraData={
                "ean": EAN_TEST,
            },
        )

        assert product.isGcuCompatible is True

        # When
        run_titelive_things()

        # Then
        product = offers_models.Product.query.one()
        assert product.isGcuCompatible is False

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_should_not_reject_product_and_deactivate_associated_offer_when_it_changes_to_paper_press_product(
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
            idAtProviders=EAN_TEST,
            name="Presse papier",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            extraData={"ean": EAN_TEST},
        )
        offer = ThingOfferFactory(product=product, venue=venue)
        stock = ThingStockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(stock=stock)
        assert offer.validation != offers_models.OfferValidationStatus.REJECTED

        # When
        run_titelive_things()

        # Then
        offer = offers_models.Offer.query.one()
        assert offer.validation == offers_models.OfferValidationStatus.REJECTED
        assert offers_models.Product.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
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

        # When
        run_titelive_things()

        # Then
        assert offers_models.Product.query.count() == 0

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_deactivate_offers_with_product_with_xxx_mark(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        book_ean = EAN_TEST

        DATA_LINE_PARTS = BASE_DATA_LINE_PARTS[:]
        DATA_LINE_PARTS[COLUMN_INDICES["ean"]] = book_ean
        DATA_LINE_PARTS[COLUMN_INDICES["titre"]] = "xxx"
        DATA_LINE_PARTS[COLUMN_INDICES["auteurs"]] = "Xxx"
        data_line = "~".join(DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_provider = providers_factories.TiteLiveThingsProviderFactory()

        offerer = offerers_factories.OffererFactory(siren="123456789")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        product = ThingProductFactory(
            idAtProviders=book_ean,
            name="Presse papier",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_provider.id,
            extraData={"ean": book_ean},
        )
        offer = ThingOfferFactory(product=product, venue=venue, isActive=True)

        # When
        run_titelive_things()

        # Then
        refreshed_offer = offers_models.Offer.query.filter_by(id=offer.id).one_or_none()
        refreshed_product = offers_models.Product.query.filter_by(id=product.id).one_or_none()
        assert refreshed_product.name == "xxx"
        assert refreshed_offer.isActive is False
        assert refreshed_offer.name == "xxx"

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_approve_product_from_inappropriate_thing(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "~".join(BASE_DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")

        offers_factories.ProductFactory(
            name="Old name",
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_things_provider.id,
            isGcuCompatible=False,
            extraData={
                "ean": EAN_TEST,
            },
        )

        # When
        run_titelive_things()

        # Then
        updated_product = offers_models.Product.query.first()
        assert updated_product.name == EAN_TEST_TITLE
        assert updated_product.isGcuCompatible

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_approve_product_and_offers_from_inappropriate_thing(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "~".join(BASE_DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")

        product = offers_factories.ProductFactory(
            name="Old name",
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_things_provider.id,
            isGcuCompatible=False,
            extraData={
                "ean": EAN_TEST,
            },
        )

        offers_factories.OfferFactory(
            product=product,
            validation=OfferValidationStatus.REJECTED,
            lastValidationType=OfferValidationType.CGU_INCOMPATIBLE_PRODUCT,
        )

        # When
        run_titelive_things()

        # Then
        updated_product = offers_models.Product.query.first()
        assert updated_product.name == EAN_TEST_TITLE
        assert updated_product.isGcuCompatible

        offers = offers_models.Offer.query.all()
        assert all(offer.validation == OfferValidationStatus.APPROVED for offer in offers)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_files_to_process_from_titelive_ftp")
    @patch("pcapi.local_providers.titelive_things.titelive_things.get_lines_from_thing_file")
    def test_update_offers_extra_data_from_thing(
        self, get_lines_from_thing_file, get_files_to_process_from_titelive_ftp, app
    ):
        # Given
        get_files_to_process_from_titelive_ftp.return_value = ["Quotidien30.tit"]

        data_line = "~".join(BASE_DATA_LINE_PARTS)
        get_lines_from_thing_file.return_value = iter([data_line])

        titelive_things_provider = get_provider_by_local_class("TiteLiveThings")

        product = offers_factories.ProductFactory(
            name="Old name",
            description="old description",
            idAtProviders=EAN_TEST,
            dateModifiedAtLastProvider=datetime(2001, 1, 1),
            lastProviderId=titelive_things_provider.id,
            isGcuCompatible=False,
            extraData={
                "ean": EAN_TEST,
            },
        )

        offers_factories.OfferFactory(product=product, extraData={"gtl_id": "01223344"})

        # When
        run_titelive_things()

        # Then
        offer = offers_models.Offer.query.one()

        assert offer.name == "Secret wars : marvel zombies n.1"
        assert offer.description.startswith("A passionate description of offer")
        assert offer.extraData["gtl_id"] == "03030400"
        assert offer.extraData["csr_id"] == "1901"
        assert offer.extraData["code_clil"] == "4300"
        assert not offer.extraData.get("isbn")
        assert not offer.extraData.get("dewey")
        assert offer.extraData["rayon"] == "Bandes dessinées adultes / Comics"
        assert offer.extraData["author"] == "Collectif"
        assert offer.extraData["bookFormat"] == "BEAUX LIVRES"
        assert offer.extraData["prix_livre"] == "4.90"
        assert offer.extraData["editeur"] == "Panini Comics Mag"
        assert not offer.extraData.get("comic_series")
        assert offer.extraData["distributeur"] == "Makassar"
        assert offer.extraData["date_parution"] == "24/12/2015"
