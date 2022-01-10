import pytest

from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offers.factories import BankInformationFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.scripts.business_unit.create_bu import create_all_business_units


@pytest.mark.usefixtures("db_session")
def test_create_bu():
    expected_results = {
        "bu_with_siret": 0,
        "bu_without_siret": 0,
    }

    # Offerer 1
    offerer = OffererFactory()
    # TODO generate iban and bic in factory: iban = IBAN.generate('DE', bank_code='10010010', account_code='12345')
    # <IBAN=DE40100100100000012345>
    # >>> iban.checksum_digits
    # '40'

    # For german banks you can also generate BIC-objects from local bank-codes

    # >>> bic = BIC.from_bank_code('DE', '43060967')
    # >>> bic.formatted
    # 'GENO DE M1 GLS'

    offerer_bank_information = BankInformationFactory(offerer=offerer)

    expected_results["bu_with_siret"] += 1
    VenueFactory(managingOfferer=offerer, businessUnit=None)
    VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=offerer_bank_information.bic,
        iban=offerer_bank_information.iban,
    )

    expected_results["bu_with_siret"] += 1
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None)
    bank_information = BankInformationFactory(venue=venue)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=bank_information.bic,
        iban=bank_information.iban,
    )

    expected_results["bu_without_siret"] += 1
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")
    bank_information = BankInformationFactory(venue=venue)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=bank_information.bic,
        iban=bank_information.iban,
    )

    # Offerer 2
    offerer = OffererFactory()
    offerer_bank_information = BankInformationFactory(offerer=offerer)

    expected_results["bu_with_siret"] += 1
    VenueFactory(managingOfferer=offerer, businessUnit=None)
    expected_results["bu_with_siret"] += 1
    VenueFactory(managingOfferer=offerer, businessUnit=None)
    expected_results["bu_without_siret"] += 1
    VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=offerer_bank_information.bic,
        iban=offerer_bank_information.iban,
    )

    expected_results["bu_with_siret"] += 1
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None)
    BankInformationFactory(venue=venue)

    expected_results["bu_without_siret"] += 1
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")
    bank_information = BankInformationFactory(venue=venue)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=bank_information.bic,
        iban=bank_information.iban,
    )

    # Offerer 3
    offerer = OffererFactory()

    expected_results["bu_with_siret"] += 0
    expected_results["bu_without_siret"] += 0
    VenueFactory(managingOfferer=offerer, businessUnit=None)
    VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")

    expected_results["bu_without_siret"] += 1
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=offerer_bank_information.bic,
        iban=offerer_bank_information.iban,
    )

    expected_results["bu_with_siret"] += 1
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None)
    bank_information = BankInformationFactory(venue=venue)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=bank_information.bic,
        iban=bank_information.iban,
    )

    expected_results["bu_without_siret"] += 1
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")
    bank_information = BankInformationFactory(venue=venue)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=bank_information.bic,
        iban=bank_information.iban,
    )

    create_all_business_units()
    bu_with_siret = BusinessUnit.query.filter(BusinessUnit.siret != None).all()
    bu_without_siret = BusinessUnit.query.filter(BusinessUnit.siret == None).all()

    results = {
        "bu_with_siret": len(bu_with_siret),
        "bu_without_siret": len(bu_without_siret),
    }
    assert results["bu_with_siret"] == expected_results["bu_with_siret"]
    assert results["bu_without_siret"] == expected_results["bu_without_siret"]


@pytest.mark.usefixtures("db_session")
def test_business_unit_without_siret_name():
    offerer = OffererFactory()
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")
    bank_information = BankInformationFactory(venue=venue)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=bank_information.bic,
        iban=bank_information.iban,
    )
    venue = VenueFactory(managingOfferer=offerer, businessUnit=None, siret=None, comment="no siret")
    bank_information = BankInformationFactory(venue=venue)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        comment="no siret",
    )
    BankInformationFactory(
        venue=venue,
        bic=bank_information.bic,
        iban=bank_information.iban,
    )

    create_all_business_units()
    business_unit = BusinessUnit.query.order_by("name").all()
    assert business_unit[0].name == "Point de remboursement #1"
    assert business_unit[1].name == "Point de remboursement #2"


@pytest.mark.usefixtures("db_session")
def test_create_single_bu_without_siret_on_offerer_cb():
    expected_results = {
        "bu_with_siret": 0,
        "bu_without_siret": 0,
    }

    offerer = OffererFactory()
    BankInformationFactory(offerer=offerer)
    venue = VenueFactory(
        managingOfferer=offerer,
        businessUnit=None,
        siret=None,
        isVirtual=True,
    )
    OfferFactory(venue=venue)

    create_all_business_units()
    business_units = BusinessUnit.query.all()

    assert len(business_units) == 1
