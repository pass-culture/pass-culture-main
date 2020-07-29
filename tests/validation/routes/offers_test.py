import pytest

from models import ApiErrors, ThingType, EventType, OfferSQLEntity
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer
from validation.routes.offers import check_has_venue_id, check_offer_type_is_valid, check_offer_is_editable, \
    check_offer_name_length_is_valid, check_edition_for_allocine_offer_is_valid, check_user_has_rights_on_offerer


class CheckHasVenueIdTest:
    def test_raises_exception_when_venue_id_is_None(self):
        # Given
        venue_id = None

        # When
        with pytest.raises(ApiErrors) as error:
            check_has_venue_id(venue_id)

        # Then
        assert error.value.errors['venueId'] == ['Vous devez préciser un identifiant de lieu']

    def test_raises_does_not_raise_exception_when_venue_id(self):
        # Given
        venue_id = 'AE'

        # When
        try:
            check_has_venue_id(venue_id)
        except:
            assert False


class CheckOfferTypeIsValidTest:
    def test_raises_api_error_when_offer_type_is_invalid(self):
        # When
        with pytest.raises(ApiErrors) as error:
            check_offer_type_is_valid('')

        # Then
        assert error.value.errors['type'] == ['Le type de cette offre est inconnu']

    def test_does_not_raise_exception_when_ThingType_is_given(self):
        # When
        try:
            check_offer_type_is_valid(str(ThingType.JEUX_VIDEO))
        except:
            assert False

    def test_does_not_raise_exception_when_EventType_is_given(self):
        # When
        try:
            check_offer_type_is_valid(str(EventType.ACTIVATION))
        except:
            assert False


class CheckOfferNameIsValidTest:
    def test_raises_api_error_when_offer_name_is_too_long(self):
        # Given
        offer_title_too_long = 'Nom vraiment très long excédant la taille maximale (nom de plus de quatre-vingt-dix caractères)'

        # When
        with pytest.raises(ApiErrors) as error:
            check_offer_name_length_is_valid(offer_title_too_long)

        # Then
        assert error.value.errors['name'] == ['Le titre de l’offre doit faire au maximum 90 caractères.']

    def test_does_not_raise_exception_when_offer_name_length_is_valid(self):
        # Given
        offer_title_less_than_90_characters = 'Nom de moins de quatre-vingt-dix caractères'

        # When
        try:
            check_offer_name_length_is_valid(offer_title_less_than_90_characters)
        except:
            assert False


class CheckOfferIsEditableTest:
    def test_raises_error_when_offer_is_not_editable(self):
        # given
        offer = OfferSQLEntity()
        offer.lastProviderId = "42"

        # when
        with pytest.raises(ApiErrors) as error:
            check_offer_is_editable(offer)

        # then
        assert error.value.errors['global'] == ["Les offres importées ne sont pas modifiables"]

    def test_does_not_raise_error_when_offer_type_is_editable(self):
        # given
        offer = OfferSQLEntity()

        # when
        try:
            check_offer_is_editable(offer)
        except:
            assert False


class CheckEditionForAllocineOfferIsValidTest:
    def test_pass_when_fields_edited(self):
        # Given
        payload = {}

        # Then
        try:
            check_edition_for_allocine_offer_is_valid(payload)
        except:
            assert False

    def test_raises_exception_when_fields_are_not_editable(self):
        # Given
        payload = {
            'bookingEmail': 'offer@example.com',
            'isNational': True,
            'name': 'Nouvelle offre'
        }

        # When
        with pytest.raises(ApiErrors) as error:
            check_edition_for_allocine_offer_is_valid(payload)

        # Then
        assert error.value.errors['bookingEmail'] == ['Vous ne pouvez pas modifier ce champ']
        assert error.value.errors['isNational'] == ['Vous ne pouvez pas modifier ce champ']
        assert error.value.errors['name'] == ['Vous ne pouvez pas modifier ce champ']


class CheckUserHasRightsOnOffererTest:
    def test_should_raise_errors_when_user_offerer_is_not_validated(self):
        # Given
        user = create_user(is_admin=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user=user, offerer=offerer, validation_token='ABCD')

        # When
        with pytest.raises(ApiErrors) as errors:
            check_user_has_rights_on_offerer(user_offerer=user_offerer)

        # Then
        assert errors.value.errors == {'global': ["Vous n'avez pas les droits d'accès"
                                                  " suffisant pour accéder à cette information."]}

    def test_should_raise_errors_when_no_user_offerer(self):
        # Given
        user_offerer = None

        # When
        with pytest.raises(ApiErrors) as errors:
            check_user_has_rights_on_offerer(user_offerer=user_offerer)

        # Then
        assert errors.value.errors == {'global': ["Vous n'avez pas les droits d'accès"
                                                  " suffisant pour accéder à cette information."]}
