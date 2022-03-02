import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.models.api_errors import ApiErrors
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_offerer_can_have_null_address(app):
    # given
    offerer = create_offerer(address=None)

    try:
        # when
        repository.save(offerer)
    except ApiErrors:
        # then
        assert False


class OffererBankInformationTest:
    @pytest.mark.usefixtures("db_session")
    def test_bic_property_returns_bank_information_bic_when_offerer_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        offers_factories.BankInformationFactory(bic="BDFEFR2LCCB", offerer=offerer)

        # When
        bic = offerer.bic

        # Then
        assert bic == "BDFEFR2LCCB"

    @pytest.mark.usefixtures("db_session")
    def test_bic_property_returns_none_when_offerer_does_not_have_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        repository.save(offerer)

        # When
        bic = offerer.bic

        # Then
        assert bic is None

    @pytest.mark.usefixtures("db_session")
    def test_iban_property_returns_bank_information_iban_when_offerer_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        offers_factories.BankInformationFactory(iban="FR7630007000111234567890144", offerer=offerer)

        # When
        iban = offerer.iban

        # Then
        assert iban == "FR7630007000111234567890144"

    @pytest.mark.usefixtures("db_session")
    def test_iban_property_returns_none_when_offerer_does_not_have_bank_information(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        repository.save(offerer)

        # When
        iban = offerer.iban

        # Then
        assert iban is None

    @pytest.mark.usefixtures("db_session")
    def test_demarchesSimplifieesApplicationId_returns_id_if_status_is_draft(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        offers_factories.BankInformationFactory(
            applicationId=12345, offerer=offerer, status=BankInformationStatus.DRAFT, iban=None, bic=None
        )

        # When
        field = offerer.demarchesSimplifieesApplicationId

        # Then
        assert field == 12345

    @pytest.mark.usefixtures("db_session")
    def test_demarchesSimplifieesApplicationId_returns_none_if_status_is_rejected(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        offers_factories.BankInformationFactory(
            offerer=offerer, status=BankInformationStatus.REJECTED, iban=None, bic=None
        )

        # When
        field = offerer.demarchesSimplifieesApplicationId

        # Then
        assert field is None


class IsValidatedTest:
    @pytest.mark.usefixtures("db_session")
    def test_is_validated_property(self, app):
        # Given
        offerer = create_offerer(siren="123456789")
        user = users_factories.ProFactory(postalCode=None)
        user_offerer = create_user_offerer(user, offerer, validation_token=None)
        repository.save(user_offerer)

        # When
        isValidated = offerer.isValidated

        # Then
        assert isValidated is True

    @pytest.mark.usefixtures("db_session")
    def test_is_validated_property_when_still_offerer_has_validation_token(self, app):
        # Given
        offerer = create_offerer(siren="123456789", validation_token="AAZRER")
        user = users_factories.ProFactory(postalCode=None)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)

        # When
        isValidated = offerer.isValidated

        # Then
        assert isValidated is False
