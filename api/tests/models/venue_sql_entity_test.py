import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models.api_errors import ApiErrors
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_offerer_cannot_have_address_and_isVirtual(app):
    # Given
    offerer = create_offerer(
        siren="123456789", address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
    )
    repository.save(offerer)

    venue = create_venue(offerer, name="Venue_name", booking_email="booking@email.com", is_virtual=True, siret=None)
    venue.address = "1 test address"

    # When
    with pytest.raises(ApiErrors):
        repository.save(venue)


@pytest.mark.usefixtures("db_session")
def test_offerer_not_isVirtual_and_has_siret_can_have_null_address(app):
    # Given
    offerer = create_offerer(
        siren="123456789", address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
    )
    repository.save(offerer)

    venue = create_venue(
        offerer,
        siret="12345678912345",
        name="Venue_name",
        booking_email="booking@email.com",
        address=None,
        postal_code="75000",
        city="Paris",
        departement_code="75",
        is_virtual=False,
    )

    # When
    try:
        repository.save(venue)
    except ApiErrors:
        # Then
        assert pytest.fail(
            "Should not fail with siret, not virtual, null address and postal code, city, departement code are given"
        )


@pytest.mark.usefixtures("db_session")
def test_offerer_not_isVirtual_and_has_siret_cannot_have_null_postal_code_nor_city_nor_departement_code(app):
    # Given
    offerer = create_offerer(
        siren="123456789", address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
    )
    repository.save(offerer)

    venue = create_venue(
        offerer,
        siret="12345678912345",
        name="Venue_name",
        booking_email="booking@email.com",
        address="3 rue de valois",
        postal_code=None,
        city=None,
        departement_code=None,
        is_virtual=False,
    )

    # When
    with pytest.raises(ApiErrors):
        repository.save(venue)


@pytest.mark.usefixtures("db_session")
def test_offerer_not_isVirtual_and_has_no_siret_cannot_have_null_address_nor_postal_code_nor_city_nor_departement_code(
    app,
):
    # Given
    offerer = create_offerer(
        siren="123456789", address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
    )
    repository.save(offerer)

    venue = create_venue(
        offerer,
        siret=None,
        name="Venue_name",
        booking_email="booking@email.com",
        address=None,
        postal_code=None,
        city=None,
        departement_code=None,
        is_virtual=False,
    )

    # When
    with pytest.raises(ApiErrors):
        repository.save(venue)


@pytest.mark.usefixtures("db_session")
def test_offerer_not_isVirtual_and_has_no_siret_and_has_address_and_postal_code_and_city_and_departement_code(app):
    # Given
    offerer = create_offerer(
        siren="123456789", address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
    )
    repository.save(offerer)

    venue = create_venue(
        offerer,
        siret=None,
        comment="fake comment",
        name="Venue_name",
        booking_email="booking@email.com",
        address="3 rue valois",
        postal_code="75000",
        city="Paris",
        departement_code="75",
        is_virtual=False,
    )

    # When
    try:
        repository.save(venue)

    except ApiErrors:
        # Then
        assert pytest.fail(
            "Should not fail with no siret, not virtual but address, postal code, city and departement code are given"
        )


@pytest.mark.usefixtures("db_session")
def test_offerer_cannot_create_a_second_virtual_venue(app):
    # Given
    offerer = create_offerer(
        siren="123456789", address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
    )
    repository.save(offerer)
    venue = create_venue(
        offerer,
        name="Venue_name",
        booking_email="booking@email.com",
        address=None,
        postal_code=None,
        city=None,
        departement_code=None,
        is_virtual=True,
        siret=None,
    )
    repository.save(venue)
    new_venue = create_venue(
        offerer,
        name="Venue_name",
        booking_email="booking@email.com",
        address=None,
        postal_code=None,
        city=None,
        departement_code=None,
        is_virtual=True,
        siret=None,
    )

    # When
    with pytest.raises(ApiErrors) as errors:
        repository.save(new_venue)

    # Then
    assert errors.value.errors["isVirtual"] == ["Un lieu pour les offres numériques existe déjà pour cette structure"]


@pytest.mark.usefixtures("db_session")
def test_offerer_cannot_update_a_second_venue_to_be_virtual(app):
    # Given
    siren = "132547698"
    offerer = create_offerer(
        siren=siren, address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
    )
    repository.save(offerer)
    venue = create_venue(
        offerer, address=None, postal_code=None, city=None, departement_code=None, is_virtual=True, siret=None
    )
    repository.save(venue)
    new_venue = create_venue(offerer, is_virtual=False, siret=siren + "98765")
    repository.save(new_venue)
    new_venue.isVirtual = True
    new_venue.postalCode = None
    new_venue.address = None
    new_venue.city = None
    new_venue.departementCode = None
    new_venue.siret = None

    # When
    with pytest.raises(ApiErrors) as errors:
        repository.save(new_venue)

    # Then
    assert errors.value.errors["isVirtual"] == ["Un lieu pour les offres numériques existe déjà pour cette structure"]


@pytest.mark.usefixtures("db_session")
def test_venue_raises_exception_when_is_virtual_and_has_siret(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret="12345678912345")

    # when
    with pytest.raises(ApiErrors):
        repository.save(venue)


@pytest.mark.usefixtures("db_session")
def test_venue_raises_exception_when_no_siret_and_no_comment(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret=None, comment=None)

    # when
    with pytest.raises(ApiErrors):
        repository.save(venue)


@pytest.mark.usefixtures("db_session")
def test_venue_raises_exception_when_siret_and_comment_but_virtual(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret=None, comment="hello I've comment and siret but i'm virtual", is_virtual=True)

    # when
    with pytest.raises(ApiErrors):
        repository.save(venue)


@pytest.mark.usefixtures("db_session")
def test_venue_should_not_raise_exception_when_siret_and_comment(app):
    # given
    offerer = create_offerer()
    venue = create_venue(
        offerer, siret="02345678912345", comment="hello I have some comment and siret !", is_virtual=False
    )

    # when
    try:
        repository.save(venue)

    except ApiErrors:
        # Then
        assert pytest.fail("Should not fail with comment and siret but not virtual")


@pytest.mark.usefixtures("db_session")
def test_venue_should_not_raise_exception_when_no_siret_but_comment(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret=None, comment="hello I have some comment but no siret :(", is_virtual=False)

    # when
    try:
        repository.save(venue)

    except ApiErrors:
        # Then
        assert pytest.fail("Should not fail with comment but not virtual nor siret")


class DepartementCodeTest:
    @pytest.mark.usefixtures("db_session")
    def test_venue_in_overseas_department_has_a_three_digit_departement_code(self, app):
        # Given
        offerer = create_offerer(
            siren="123456789", address="1 rue Test", city="Test city", postal_code="93000", name="Test offerer"
        )
        venue = create_venue(
            offerer,
            siret="12345678912345",
            name="Venue_name",
            booking_email="booking@email.com",
            address="1 test address",
            postal_code="97300",
            city="Cayenne",
            is_virtual=False,
        )
        repository.save(venue)

        # When
        departementCode = venue.departementCode

        # Then
        assert departementCode == "973"


class VenueBankInformationTest:
    @pytest.mark.usefixtures("db_session")
    def test_bic_property_returns_bank_information_bic_when_venue_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret="12345678912345")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", venue=venue)

        # When
        bic = venue.bic

        # Then
        assert bic == "BDFEFR2LCCB"

    @pytest.mark.usefixtures("db_session")
    def test_bic_property_returns_none_when_does_not_have_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret="12345678912345")
        repository.save(venue)

        # When
        bic = venue.bic

        # Then
        assert bic is None

    @pytest.mark.usefixtures("db_session")
    def test_iban_property_returns_bank_information_iban_when_venue_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret="12345678912345")
        offers_factories.BankInformationFactory(iban="FR7630007000111234567890144", venue=venue)

        # When
        iban = venue.iban

        # Then
        assert iban == "FR7630007000111234567890144"

    @pytest.mark.usefixtures("db_session")
    def test_iban_property_returns_none_when_venue_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret="12345678912345")
        repository.save(venue)

        # When
        iban = venue.iban

        # Then
        assert iban is None

    @pytest.mark.usefixtures("db_session")
    def test_demarchesSimplifieesApplicationId_returns_id_if_status_is_draft(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret="12345678912345")
        offers_factories.BankInformationFactory(
            applicationId=12345, venue=venue, status=BankInformationStatus.DRAFT, iban=None, bic=None
        )

        # When
        field = venue.demarchesSimplifieesApplicationId

        # Then
        assert field == 12345

    @pytest.mark.usefixtures("db_session")
    def test_demarchesSimplifieesApplicationId_returns_none_if_status_is_rejected(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        venue = create_venue(offerer, siret="12345678912345")
        offers_factories.BankInformationFactory(venue=venue, status=BankInformationStatus.REJECTED, iban=None, bic=None)

        # When
        field = venue.demarchesSimplifieesApplicationId

        # Then
        assert field is None
