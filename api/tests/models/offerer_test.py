import pytest

from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories


class OffererBankInformationTest:
    @pytest.mark.usefixtures("db_session")
    def test_bic_property_returns_bank_information_bic_when_offerer_has_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        offers_factories.BankInformationFactory(offerer=offerer, bic="BDFEFR2LCCB")
        assert offerer.bic == "BDFEFR2LCCB"

    @pytest.mark.usefixtures("db_session")
    def test_bic_property_returns_none_when_offerer_does_not_have_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        assert offerer.bic is None

    @pytest.mark.usefixtures("db_session")
    def test_iban_property_returns_bank_information_iban_when_offerer_has_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        offers_factories.BankInformationFactory(offerer=offerer, iban="FR7630007000111234567890144")
        assert offerer.iban == "FR7630007000111234567890144"

    @pytest.mark.usefixtures("db_session")
    def test_iban_property_returns_none_when_offerer_does_not_have_bank_information(self):
        offerer = offerers_factories.OffererFactory()
        assert offerer.iban is None

    @pytest.mark.usefixtures("db_session")
    def test_demarchesSimplifieesApplicationId_returns_id_if_status_is_draft(self):
        offerer = offerers_factories.OffererFactory()
        offers_factories.BankInformationFactory(
            offerer=offerer,
            applicationId=12345,
            status=BankInformationStatus.DRAFT,
        )
        assert offerer.demarchesSimplifieesApplicationId == 12345

    @pytest.mark.usefixtures("db_session")
    def test_demarchesSimplifieesApplicationId_returns_none_if_status_is_rejected(self):
        offerer = offerers_factories.OffererFactory()
        info = offers_factories.BankInformationFactory(
            offerer=offerer,
            applicationId=12345,
            status=BankInformationStatus.REJECTED,
        )
        offerer = info.offerer
        assert offerer.demarchesSimplifieesApplicationId is None


class IsValidatedTest:
    @pytest.mark.usefixtures("db_session")
    def test_is_validated_property(self):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, validationToken="token")
        assert offerer.isValidated

    @pytest.mark.usefixtures("db_session")
    def test_is_validated_property_when_still_offerer_has_validation_token(self):
        offerer = offerers_factories.OffererFactory(validationToken="token")
        offerers_factories.UserOffererFactory(offerer=offerer)
        assert not offerer.isValidated
