from models import ApiErrors
from models.bank_information import BankInformationStatus
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer, \
    create_bank_information
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product


@clean_database
def test_nOffers(app):
    # given
    offerer = create_offerer()
    venue_1 = create_venue(offerer, siret='12345678912345')
    venue_2 = create_venue(offerer, siret='67891234512345')
    venue_3 = create_venue(offerer, siret='23451234567891')
    offer_v1_1 = create_offer_with_thing_product(venue_1)
    offer_v1_2 = create_offer_with_event_product(venue_1)
    offer_v2_1 = create_offer_with_event_product(venue_2)
    offer_v2_2 = create_offer_with_event_product(venue_2)
    offer_v3_1 = create_offer_with_thing_product(venue_3)
    repository.save(offer_v1_1, offer_v1_2, offer_v2_1, offer_v2_2, offer_v3_1)

    # when
    n_offers = offerer.nOffers

    # then
    assert n_offers == 5


@clean_database
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
    @clean_database
    def test_bic_property_returns_bank_information_bic_when_offerer_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        bank_information = create_bank_information(
            bic='BDFEFR2LCCB', offerer=offerer)
        repository.save(bank_information)

        # When
        bic = offerer.bic

        # Then
        assert bic == 'BDFEFR2LCCB'

    @clean_database
    def test_bic_property_returns_none_when_offerer_does_not_have_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        repository.save(offerer)

        # When
        bic = offerer.bic

        # Then
        assert bic is None

    @clean_database
    def test_iban_property_returns_bank_information_iban_when_offerer_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        bank_information = create_bank_information(iban='FR7630007000111234567890144',
                                                   offerer=offerer)
        repository.save(bank_information)

        # When
        iban = offerer.iban

        # Then
        assert iban == 'FR7630007000111234567890144'

    @clean_database
    def test_iban_property_returns_none_when_offerer_does_not_have_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        repository.save(offerer)

        # When
        iban = offerer.iban

        # Then
        assert iban is None

    @clean_database
    def test_demarchesSimplifieesApplicationId_returns_id_if_status_is_draft(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        bank_information = create_bank_information(
            application_id=12345, offerer=offerer, status=BankInformationStatus.DRAFT, iban=None, bic=None)
        repository.save(bank_information)

        # When
        field = offerer.demarchesSimplifieesApplicationId

        # Then
        assert field == 12345

    @clean_database
    def test_demarchesSimplifieesApplicationId_returns_none_if_status_is_rejected(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        bank_information = create_bank_information(
            offerer=offerer, status=BankInformationStatus.REJECTED, iban=None, bic=None)
        repository.save(bank_information)

        # When
        field = offerer.demarchesSimplifieesApplicationId

        # Then
        assert field is None


class IsValidatedTest:
    @clean_database
    def test_is_validated_property(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        user = create_user(postal_code=None)
        user_offerer = create_user_offerer(
            user, offerer, validation_token=None)
        repository.save(user_offerer)

        # When
        isValidated = offerer.isValidated

        # Then
        assert isValidated is True

    @clean_database
    def test_is_validated_property_when_still_offerer_has_validation_token(self, app):
        # Given
        offerer = create_offerer(siren='123456789', validation_token='AAZRER')
        user = create_user(postal_code=None)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)

        # When
        isValidated = offerer.isValidated

        # Then
        assert isValidated is False


class AppendUserHasAccessAttributeTest:
    def test_adds_a_new_propery(self):
        # Given
        current_user = create_user()
        offerer = create_offerer()

        # When
        offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

        # Then
        assert hasattr(offerer, 'userHasAccess')

    def test_should_return_false_when_current_user_has_no_rights_on_offerer(self, app):
        # Given
        current_user = create_user()
        offerer = create_offerer()

        # When
        offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

        # Then
        assert offerer.userHasAccess is False

    @clean_database
    def test_should_return_true_when_current_user_access_to_offerer_is_validated(self, app):
        # Given
        current_user = create_user(postal_code=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(
            current_user, offerer, validation_token=None)
        repository.save(user_offerer)

        # When
        offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

        # Then
        assert offerer.userHasAccess is True

    @clean_database
    def test_should_return_false_when_current_user_access_to_offerer_is_not_validated(self, app):
        # Given
        current_user = create_user(postal_code=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(
            current_user, offerer, validation_token='TOKEN')
        repository.save(user_offerer)

        # When
        offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

        # Then
        assert offerer.userHasAccess is False

    @clean_database
    def test_should_return_false_when_current_user_has_no_access(self, app):
        # Given
        current_user = create_user(
            email='current@example.net', postal_code=None)
        user = create_user(postal_code=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(
            user, offerer, validation_token=None)
        repository.save(user_offerer)

        # When
        offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

        # Then
        assert offerer.userHasAccess is False

    @clean_database
    def test_should_return_true_when_current_user_is_admin(self, app):
        # Given
        current_user = create_user(
            email='current@example.net', is_admin=True, postal_code=None)
        user = create_user(postal_code=None)
        offerer = create_offerer()
        user_offerer = create_user_offerer(
            user, offerer, validation_token=None)
        repository.save(user_offerer)

        # When
        offerer.append_user_has_access_attribute(user_id=current_user.id, is_admin=current_user.isAdmin)

        # Then
        assert offerer.userHasAccess is True
